"""Flask REST API for Stayright hotel discovery and refinement."""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, g, jsonify, request
from flask_cors import CORS

from agent import (
    enrich_shortlist_with_sentiment,
    generate_hotel_comparison,
    generate_recommendation,
    get_shortlist,
    parse_refinement,
    run_agent,
)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
REQUESTS_LOG_PATH = Path(__file__).resolve().parent / "requests.log"
DEMO_QUERY = "3 nights Delhi solo work trip fast wifi budget 8000"


@app.before_request
def _request_timer_start() -> None:
    g._request_started_perf = time.perf_counter()


@app.after_request
def _log_request_metadata(response):
    started = getattr(g, "_request_started_perf", None)
    elapsed_ms = (time.perf_counter() - started) * 1000 if started is not None else 0.0
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    line = f"{ts}\t{request.method} {request.path}\t{elapsed_ms:.1f}ms\n"
    try:
        with REQUESTS_LOG_PATH.open("a", encoding="utf-8") as logf:
            logf.write(line)
    except OSError:
        pass
    return response

sessions: dict[str, dict[str, Any]] = {}


def _hotels_from_shortlist(shortlist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in shortlist:
        h = row.get("hotel") or {}
        out.append(
            {
                "id": h.get("id"),
                "name": h.get("name"),
                "city": h.get("city"),
                "area": h.get("area"),
                "stars": h.get("stars"),
                "price_per_night": h.get("price_per_night"),
                "rating": h.get("rating"),
                "amenities": h.get("amenities") or [],
                "review_tags": h.get("review_tags") or [],
                "match_score": round(float(row.get("composite") or 0.0), 4),
                "child_friendly": bool(h.get("child_friendly")),
                "guest_verdict": h.get("guest_verdict") or "",
            }
        )
    return out


def _explain_breakdown(row: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
    hotel = row.get("hotel") or {}
    name = hotel.get("name") or ""
    comp = float(row.get("composite") or 0.0)
    must_s = float(row.get("must_score") or 0.0)
    nice_s = float(row.get("nice_score") or 0.0)
    purpose_s = float(row.get("purpose_score") or 0.0)
    review_s = float(row.get("review_score") or 0.0)

    must_list = [m for m in (intent.get("must_have") or []) if isinstance(m, str)]
    nice_list = [n for n in (intent.get("nice_to_have") or []) if isinstance(n, str)]
    matched_nice = [x for x in (row.get("matched_nice") or []) if isinstance(x, str)]

    if must_list:
        must_detail = (
            f"Every one of the {len(must_list)} firm requirements you set is available at this property."
        )
    else:
        must_detail = (
            "You did not list hard must-haves, so this block is treated as fully satisfied by default."
        )

    if not nice_list:
        nice_detail = (
            "You did not name optional extras, so this slice uses the neutral baseline instead of a match ratio."
        )
    else:
        nice_detail = (
            f"The hotel matches {len(matched_nice)} of your {len(nice_list)} optional preferences."
        )

    purpose_label = intent.get("purpose")
    if not isinstance(purpose_label, str) or not purpose_label.strip():
        purpose_label = "leisure"
    purpose_detail = (
        f"About {purpose_s * 100:.0f}% alignment between what this hotel offers and what typically "
        f"matters on a {purpose_label} trip."
    )

    rc = hotel.get("review_count")
    if isinstance(rc, (int, float)) and not isinstance(rc, bool):
        rc_int = int(rc)
        review_detail = (
            f"This score reflects roughly {rc_int} guest reviews, scaled so even very popular hotels "
            f"plateau once they pass about ten thousand ratings."
        )
    else:
        review_detail = "Review volume was missing or unclear, so this part of the blend stays conservative."

    return {
        "hotel_name": name,
        "composite_score": round(comp, 6),
        "components": [
            {
                "name": "must_have_alignment",
                "score": must_s,
                "weight_percent": 60,
                "detail": must_detail,
            },
            {
                "name": "nice_to_have_alignment",
                "score": nice_s,
                "weight_percent": 20,
                "detail": nice_detail,
            },
            {
                "name": "purpose_alignment",
                "score": purpose_s,
                "weight_percent": 15,
                "detail": purpose_detail,
            },
            {
                "name": "review_signal",
                "score": review_s,
                "weight_percent": 5,
                "detail": review_detail,
            },
        ],
    }


@app.post("/api/discover")
def api_discover():
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    session_id = data.get("session_id")
    if not message or not isinstance(message, str):
        return jsonify({"error": "message is required and must be a string"}), 400
    if not session_id or not isinstance(session_id, str):
        return jsonify({"error": "session_id is required and must be a string"}), 400

    # Fresh discover: no prior turns (new search for this session_id).
    result = run_agent(
        message,
        session_intent=None,
        is_refinement=False,
        conversation_history=[],
    )

    intent = result["intent"]
    shortlist = result["shortlist"]
    sessions[session_id] = {
        "intent": intent,
        "shortlist": shortlist,
        "conversation_history": result.get("conversation_history") or [],
    }

    return jsonify(
        {
            "response": result["response_text"],
            "hotels": _hotels_from_shortlist(shortlist),
            "intent": intent,
            "confidence": intent.get("confidence"),
        }
    )


@app.post("/api/refine")
def api_refine():
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    session_id = data.get("session_id")
    if not message or not isinstance(message, str):
        return jsonify({"error": "message is required and must be a string"}), 400
    if not session_id or not isinstance(session_id, str):
        return jsonify({"error": "session_id is required and must be a string"}), 400

    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Unknown session_id; call /api/discover first"}), 404

    current_intent = session["intent"]
    new_intent = parse_refinement(message, current_intent)

    sl_res = get_shortlist(new_intent)
    shortlist = sl_res.get("shortlist") or []
    enrich_shortlist_with_sentiment(shortlist, new_intent)
    history: list[dict[str, Any]] = list(session.get("conversation_history") or [])
    response_text = generate_recommendation(
        message,
        new_intent,
        shortlist,
        conversation_history=history,
        shortlist_meta=sl_res,
    )
    history.extend(
        [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response_text},
        ]
    )
    sessions[session_id] = {
        "intent": new_intent,
        "shortlist": shortlist,
        "conversation_history": history,
    }

    return jsonify(
        {
            "response": response_text,
            "hotels": _hotels_from_shortlist(shortlist),
            "intent": new_intent,
            "confidence": new_intent.get("confidence"),
        }
    )


@app.post("/api/compare")
def api_compare():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    hotel_ids = data.get("hotel_ids")

    if not session_id or not isinstance(session_id, str):
        return jsonify({"error": "session_id is required and must be a string"}), 400
    if not isinstance(hotel_ids, list) or len(hotel_ids) != 2:
        return jsonify({"error": "hotel_ids must be an array of exactly two hotel ids"}), 400

    try:
        id_a = int(hotel_ids[0])
        id_b = int(hotel_ids[1])
    except (TypeError, ValueError):
        return jsonify({"error": "hotel_ids must be integers"}), 400

    if id_a == id_b:
        return jsonify({"error": "hotel_ids must be two different hotels"}), 400

    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Unknown session_id; call /api/discover first"}), 404

    shortlist = session.get("shortlist") or []
    intent = session.get("intent") or {}

    ha: dict[str, Any] | None = None
    hb: dict[str, Any] | None = None
    for row in shortlist:
        h = row.get("hotel") or {}
        hid = h.get("id")
        if hid == id_a:
            ha = h
        if hid == id_b:
            hb = h

    if ha is None or hb is None:
        return jsonify({"error": "One or both hotels are not in the current session shortlist"}), 404

    comparison = generate_hotel_comparison(ha, hb, intent)

    return jsonify({"comparison": comparison})


@app.get("/api/explain/<int:hotel_id>")
def api_explain(hotel_id: int):
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id query parameter is required"}), 400

    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Unknown session_id"}), 404

    shortlist = session.get("shortlist") or []
    intent = session.get("intent") or {}
    row: dict[str, Any] | None = None
    for r in shortlist:
        h = r.get("hotel") or {}
        if h.get("id") == hotel_id:
            row = r
            break
    if row is None:
        return jsonify({"error": "Hotel not in current session shortlist"}), 404

    return jsonify(_explain_breakdown(row, intent))


@app.get("/api/health")
def api_health():
    return jsonify({"status": "ok"})


@app.get("/api/demo")
def api_demo():
    """
    Run a fixed discover-style query to warm Claude and the scoring path before live demos.

    Returns the same JSON shape as POST /api/discover (without mutating client sessions).
    """
    result = run_agent(
        DEMO_QUERY,
        session_intent=None,
        is_refinement=False,
        conversation_history=[],
    )
    intent = result["intent"]
    shortlist = result["shortlist"]
    return jsonify(
        {
            "response": result["response_text"],
            "hotels": _hotels_from_shortlist(shortlist),
            "intent": intent,
            "confidence": intent.get("confidence"),
        }
    )


def _require_anthropic_key_or_exit() -> None:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: ANTHROPIC_API_KEY is not set. Export a valid Anthropic API key before starting the server.\n"
            "Example: export ANTHROPIC_API_KEY='your-key-here'",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stayright Flask API")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode (default: off for demos).",
    )
    args = parser.parse_args()
    _require_anthropic_key_or_exit()
    app.run(host="0.0.0.0", port=5000, debug=args.debug, use_reloader=False)
