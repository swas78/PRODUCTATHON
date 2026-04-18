"""Travel intent extraction via Anthropic Claude."""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any

import anthropic

ALLOWED_AMENITIES = frozenset(
    {
        "fast_wifi",
        "wifi",
        "pool",
        "gym",
        "spa",
        "restaurant",
        "room_service",
        "business_center",
        "quiet_rooms",
        "parking",
        "airport_shuttle",
        "kids_club",
        "rooftop",
        "heritage_experience",
    }
)
ALLOWED_TRAVELER = frozenset({"solo", "couple", "family", "group"})
ALLOWED_PURPOSE = frozenset({"work", "leisure", "family", "event", "budget", "transit"})

# Amenity → weight per trip purpose (higher = more important for that purpose).
PURPOSE_WEIGHTS: dict[str, dict[str, float]] = {
    "work": {
        "fast_wifi": 2.0,
        "quiet_rooms": 1.8,
        "business_center": 1.5,
        "gym": 1.0,
        "restaurant": 0.8,
        "room_service": 0.7,
        "wifi": 0.6,
        "parking": 0.9,
        "airport_shuttle": 1.0,
        "spa": 0.5,
        "pool": 0.3,
        "kids_club": 0.2,
        "rooftop": 0.5,
        "heritage_experience": 0.4,
    },
    "family": {
        "kids_club": 2.5,
        "pool": 2.0,
        "restaurant": 1.2,
        "parking": 1.3,
        "room_service": 1.0,
        "wifi": 0.8,
        "fast_wifi": 0.7,
        "quiet_rooms": 1.0,
        "airport_shuttle": 0.9,
        "gym": 0.5,
        "spa": 0.6,
        "business_center": 0.4,
        "rooftop": 0.6,
        "heritage_experience": 0.8,
    },
    "leisure": {
        "pool": 1.8,
        "spa": 1.5,
        "heritage_experience": 1.4,
        "rooftop": 1.3,
        "restaurant": 1.0,
        "gym": 0.9,
        "room_service": 0.8,
        "quiet_rooms": 0.6,
        "wifi": 0.5,
        "fast_wifi": 0.5,
        "parking": 0.7,
        "kids_club": 0.8,
        "airport_shuttle": 0.5,
        "business_center": 0.3,
    },
    "event": {
        "business_center": 1.8,
        "restaurant": 1.5,
        "parking": 1.6,
        "room_service": 1.2,
        "airport_shuttle": 1.0,
        "fast_wifi": 1.4,
        "quiet_rooms": 1.0,
        "rooftop": 1.1,
        "heritage_experience": 1.0,
        "spa": 0.6,
        "pool": 0.8,
        "gym": 0.7,
        "wifi": 0.8,
        "kids_club": 0.4,
    },
    "budget": {
        "wifi": 1.5,
        "fast_wifi": 1.2,
        "parking": 1.0,
        "restaurant": 0.9,
        "room_service": 0.5,
        "quiet_rooms": 0.7,
        "airport_shuttle": 0.8,
        "gym": 0.4,
        "pool": 0.3,
        "spa": 0.2,
        "business_center": 0.5,
        "kids_club": 0.4,
        "rooftop": 0.3,
        "heritage_experience": 0.6,
    },
    "transit": {
        "airport_shuttle": 2.5,
        "wifi": 1.4,
        "fast_wifi": 1.3,
        "quiet_rooms": 1.2,
        "restaurant": 1.0,
        "room_service": 0.9,
        "parking": 1.1,
        "business_center": 0.8,
        "gym": 0.4,
        "pool": 0.3,
        "spa": 0.3,
        "kids_club": 0.3,
        "rooftop": 0.4,
        "heritage_experience": 0.3,
    },
}

SYSTEM_PROMPT = """You extract structured hotel-search intent from a single user message about travel in India.

OUTPUT FORMAT (strict):
- Return ONLY a single JSON object. No preamble, no explanation, no markdown code fences, no trailing text.
- Use double quotes for all JSON strings.

REQUIRED JSON keys (always present):
- "destination": string — city or area they want to stay in; use empty string "" only if truly unspecified.
- "duration": integer nights, or null if not stated or unclear.
- "traveler_type": one of "solo" | "couple" | "family" | "group". Infer from words like alone, solo, with wife/husband/partner, kids, family, friends, team, group.
- "purpose": one of "work" | "leisure" | "family" | "event" | "budget" | "transit". Pick the best primary fit.
- "must_have": array of strings — amenity keys the user clearly requires (see allowed amenity keys below).
- "nice_to_have": array of strings — amenities that would help but are not strictly required.
- "budget_per_night": integer INR per night, or null if not stated or not inferable.
- "location_preference": string neighbourhood/area preference, or null if none.
- "child_friendly_required": boolean.
- "confidence": object — your judgment of how explicit vs inferred each part of the intent is (see CONFIDENCE SCHEMA below).

CONFIDENCE SCHEMA (required sibling to the intent fields):
- "overall": float between 0 and 1 — your estimate of how much of the trip picture was clearly stated in their words versus guessed; higher means more explicit.
- For EACH of these keys, use exactly one of "high" | "medium" | "low":
  - "destination": high only if they named a city or area clearly; low if vague or default-empty.
  - "duration": high if nights/dates stated; low if null in output; medium if lightly implied.
  - "traveler_type": high if they said solo/couple/family/group clearly; medium if inferred; low if thin guess.
  - "purpose": high if trip type clearly stated; medium if inferred from context; low if shaky.
  - "budget": same idea for the nightly budget line (high if they gave a number or clear cap; medium if loosely implied; low if you defaulted or left null).
  - "must_have": high if they named specific needs; medium if partly inferred; low if empty or very thin.
  - "nice_to_have": high if they listed helpful extras; medium if mild hints; low if empty.
  - "location_preference": high if neighbourhood stated; low if null; medium if weak area hint.
  - "child_friendly_required": high if kids/family context explicit; medium if soft inference; low if default false with no signal.

ALLOWED amenity keys (use only these spellings in must_have and nice_to_have):
fast_wifi, wifi, pool, gym, spa, restaurant, room_service, business_center, quiet_rooms, parking, airport_shuttle, kids_club, rooftop, heritage_experience

RULES (apply in addition to the user's words):
1) If the message indicates a work trip, business travel, meetings, or "work" context → set purpose to "work" and ensure "fast_wifi" and "quiet_rooms" appear in must_have (add them if missing; dedupe arrays).
2) If the message mentions kids, children, toddler, baby, or family travel clearly centered on children → set child_friendly_required to true and ensure "pool" is in nice_to_have (add if missing; dedupe).
3) If the user says cheap, budget, affordable, low cost, shoestring, or similar → set purpose to "budget". If they give no numeric budget, set budget_per_night to 3000 (INR). If they do state a number, use that integer for budget_per_night.
4) Deduplicate must_have and nice_to_have; an item should not appear in both — if conflict, prefer must_have.
5) Normalize numbers: "3 nights" → duration 3; "8000 per night" or "budget 8000" → budget_per_night 8000 when clearly nightly INR.

Be conservative: only put amenities in must_have when the user implied a real need, except where rules 1–3 explicitly force additions."""

MODEL = "claude-sonnet-4-20250514"


def warmup_anthropic() -> None:
    """
    One minimal Claude round-trip to reduce cold-start latency before demos.

    Requires ANTHROPIC_API_KEY in the environment.
    """
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return
        client = anthropic.Anthropic(api_key=api_key)
        client.messages.create(
            model=MODEL,
            max_tokens=16,
            messages=[{"role": "user", "content": "Reply with only the word: ok"}],
        )
    except Exception:
        return


CONCIERGE_SYSTEM_PROMPT = """You are a warm, well-informed hotel concierge helping someone pick a place to stay in India.

You may receive earlier turns of the same conversation as real message history before the latest request—keep your tone consistent and do not contradict what you already told them unless new facts clearly override it.

How you write:
- Use natural, conversational English—like a trusted friend who knows hotels and listens closely.
- Stay at or under 300 words in total. Count as you write; if you are long, tighten before you finish.
- Tie your advice to how they actually phrased things (their nights, city, budget words, “work trip,” kids, and so on)—avoid generic travel filler that could apply to anyone.

How you structure the answer (follow in order):
1) If the trip brief begins with a LOW_PARSER_CONFIDENCE block (overall confidence under 0.6), your very first sentence MUST be one short clarifying question that targets the biggest unknown (companions, dates, area, or nightly budget). After that question, you may add a brief bridging phrase, then continue. Otherwise, start with exactly one opening sentence that acknowledges their situation and echoes phrases or details from how they actually described the trip (their original words).
2) For each shortlisted property, number it (1., 2., …). Give the hotel name and the nightly rate using the ₹ symbol with comma thousands where helpful (for example ₹8,200 per night). Follow with two or three sentences on why that hotel fits what they said they need—tie your reasoning to their wording (work trip, kids, budget cap, nights in town, and so on).
3) In each hotel block, call out one specific standout detail drawn only from the facts you were given (a neighbourhood, a shuttle, a rooftop, guest feedback themes, etc.)—avoid vague praise.
4) End with exactly one short sentence suggesting one practical way to narrow things further (budget band, neighbourhood, trip dates, must-haves they could flex, etc.). If you opened with a clarifying question in step 1, this closing line can gently invite them to answer it.

Hard bans—do not include any of these tokens or obvious close variants anywhere in your reply:
JSON, score, composite, null, great amenities, excellent location, wonderful stay, perfect for everyone, suitable for all

Also avoid naming internal tools, schemas, or “parsed” data; speak only as a concierge to the traveler.

If the briefing ends with a CONCIERGE RELAXATION NOTICE block, the shortlist was produced only after easing some constraints. You must acknowledge that naturally in your own words (often near the opening), in a warm, concise way—similar in spirit to noting their exact budget did not yield matches so you stretched it slightly, without sounding mechanical.

Formatting: plain sentences and the numbered hotel sections described above; no markdown code fences."""

COMPARE_SYSTEM_PROMPT = """You compare two specific hotels in India for the same traveler, using only the facts supplied in the user message.

Goal:
- Judge them head-to-head for that traveler’s stated trip purpose (work, leisure, family, event, budget, or transit as given)—not a generic vacation pitch.

Required shape (use their real purpose word in the bracket slot; use real hotel names from the facts):
1) Open with a line of this form (adapt wording slightly if needed for grammar, keep the logic):
   "For your [purpose] trip, [Hotel A name] wins on [specific factual edge] but [Hotel B name] is better if [specific factual edge]."
2) Immediately follow with decision guidance:
   "If [specific, concrete condition tied to their trip or the facts], pick [A or B]. If [other concrete condition], pick [the other]."
3) End with one short, decisive sentence that states which hotel you recommend for them overall in this comparison, or when to pick which if both stay in play—still only one closing sentence.

Style:
- At most 150 words total. Count as you write.
- Be concrete: prices in ₹, neighbourhoods, amenities, ratings, review themes—only what you were given.
- No markdown fences, no bullet lists, no JSON.

Banned fluff (do not write these or close variants): great amenities, excellent location, wonderful stay, perfect for everyone, suitable for all, world-class, unbeatable, hidden gem, something for everyone."""


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text)
    return text.strip()


def _filter_amenities(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []
    out: list[str] = []
    for x in items:
        if isinstance(x, str) and x in ALLOWED_AMENITIES and x not in out:
            out.append(x)
    return out


def _normalize_intent(data: dict[str, Any]) -> dict[str, Any]:
    dest = data.get("destination")
    destination = dest.strip() if isinstance(dest, str) else ""

    duration_raw = data.get("duration")
    duration: int | None
    if duration_raw is None:
        duration = None
    elif isinstance(duration_raw, bool):
        duration = None
    elif isinstance(duration_raw, (int, float)):
        duration = int(duration_raw)
    else:
        duration = None

    tt = data.get("traveler_type")
    traveler_type = tt if isinstance(tt, str) and tt in ALLOWED_TRAVELER else "solo"

    pur = data.get("purpose")
    purpose = pur if isinstance(pur, str) and pur in ALLOWED_PURPOSE else "leisure"

    must_have = _filter_amenities(data.get("must_have"))
    nice_to_have = _filter_amenities(data.get("nice_to_have"))

    for a in must_have:
        if a in nice_to_have:
            nice_to_have = [x for x in nice_to_have if x != a]

    budget_raw = data.get("budget_per_night")
    if budget_raw is None:
        budget_per_night: int | None = None
    elif isinstance(budget_raw, bool):
        budget_per_night = None
    elif isinstance(budget_raw, (int, float)):
        budget_per_night = int(budget_raw)
    else:
        budget_per_night = None

    loc = data.get("location_preference")
    if loc is None or (isinstance(loc, str) and not loc.strip()):
        location_preference: str | None = None
    elif isinstance(loc, str):
        location_preference = loc.strip()
    else:
        location_preference = None

    cfr = data.get("child_friendly_required")
    child_friendly_required = bool(cfr) if cfr is not None else False

    return {
        "destination": destination,
        "duration": duration,
        "traveler_type": traveler_type,
        "purpose": purpose,
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "budget_per_night": budget_per_night,
        "location_preference": location_preference,
        "child_friendly_required": child_friendly_required,
    }


CONFIDENCE_LEVELS = frozenset({"high", "medium", "low"})
CONFIDENCE_WEIGHTS = {"high": 1.0, "medium": 0.62, "low": 0.34}
CONFIDENCE_ORDER = (
    "destination",
    "duration",
    "traveler_type",
    "purpose",
    "budget",
    "must_have",
    "nice_to_have",
    "location_preference",
    "child_friendly_required",
)


def _missing_info_from_intent(intent: dict[str, Any]) -> list[str]:
    """Intent keys whose value is null or an empty destination string."""
    missing: list[str] = []
    if intent.get("duration") is None:
        missing.append("duration")
    if intent.get("budget_per_night") is None:
        missing.append("budget_per_night")
    if intent.get("location_preference") is None:
        missing.append("location_preference")
    dest = intent.get("destination")
    if not (isinstance(dest, str) and dest.strip()):
        missing.append("destination")
    return sorted(set(missing))


def _confidence_key_in_missing_info(conf_key: str, missing_info: list[str]) -> bool:
    if conf_key == "budget":
        return "budget_per_night" in missing_info
    return conf_key in missing_info


def _coerce_confidence_level(raw: Any) -> str:
    if isinstance(raw, str) and raw.strip().lower() in CONFIDENCE_LEVELS:
        return raw.strip().lower()
    return "low"


def _raw_model_confidence(mc: dict[str, Any], conf_key: str) -> Any:
    if conf_key == "budget":
        if "budget" in mc:
            return mc.get("budget")
        return mc.get("budget_per_night")
    return mc.get(conf_key)


def _build_confidence_from_model(model_conf: Any, intent: dict[str, Any]) -> dict[str, Any]:
    """
    Merge model-reported levels with deterministic missing_info and a stable overall score.
    """
    mc = model_conf if isinstance(model_conf, dict) else {}
    missing_info = _missing_info_from_intent(intent)
    levels: dict[str, str] = {}
    for ck in CONFIDENCE_ORDER:
        if _confidence_key_in_missing_info(ck, missing_info):
            levels[ck] = "low"
            continue
        raw = _raw_model_confidence(mc, ck)
        if raw is None:
            levels[ck] = "medium"
        else:
            lv = _coerce_confidence_level(raw)
            if lv == "low":
                levels[ck] = "medium"
            else:
                levels[ck] = lv
    weights = [CONFIDENCE_WEIGHTS[levels[k]] for k in CONFIDENCE_ORDER]
    overall = round(sum(weights) / len(weights), 2)
    out: dict[str, Any] = {"overall": overall}
    for k in CONFIDENCE_ORDER:
        out[k] = levels[k]
    out["missing_info"] = missing_info
    return out


def _hotels_json_path() -> Path:
    return Path(__file__).resolve().parent / "hotels.json"


def _intent_destination_norm(intent: dict[str, Any]) -> str:
    d = intent.get("destination")
    return d.strip().casefold() if isinstance(d, str) else ""


def _hotel_city_norm(hotel: dict[str, Any]) -> str:
    c = hotel.get("city")
    return c.strip().casefold() if isinstance(c, str) else ""


def _hotel_amenity_set(hotel: dict[str, Any]) -> set[str]:
    raw = hotel.get("amenities")
    if not isinstance(raw, list):
        return set()
    return {a for a in raw if isinstance(a, str)}


def _copy_intent_for_scoring(intent: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in intent.items() if k != "confidence"}
    out["must_have"] = list(intent.get("must_have") or [])
    out["nice_to_have"] = list(intent.get("nice_to_have") or [])
    return out


def _has_numeric_budget(intent: dict[str, Any]) -> bool:
    b = intent.get("budget_per_night")
    return b is not None and isinstance(b, (int, float)) and not isinstance(b, bool)


def _location_pref_matches(hotel: dict[str, Any], pref: str) -> bool:
    p = pref.strip().casefold()
    if not p:
        return True
    area = hotel.get("area") if isinstance(hotel.get("area"), str) else ""
    name = hotel.get("name") if isinstance(hotel.get("name"), str) else ""
    city = hotel.get("city") if isinstance(hotel.get("city"), str) else ""
    hay = f"{area} {name} {city}".casefold()
    return p in hay


def score_hotel(hotel: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any] | None:
    dest = _intent_destination_norm(intent)
    if dest and _hotel_city_norm(hotel) != dest:
        return None

    loc = intent.get("location_preference")
    if isinstance(loc, str) and loc.strip():
        if not _location_pref_matches(hotel, loc):
            return None

    budget = intent.get("budget_per_night")
    if (
        budget is not None
        and isinstance(budget, (int, float))
        and not isinstance(budget, bool)
    ):
        price = hotel.get("price_per_night")
        if isinstance(price, (int, float)) and not isinstance(price, bool):
            if int(price) > int(budget):
                return None

    if intent.get("child_friendly_required") and not hotel.get("child_friendly"):
        return None

    amenities = _hotel_amenity_set(hotel)
    must_have = intent.get("must_have") or []
    if not isinstance(must_have, list):
        must_have = []
    must_list = [m for m in must_have if isinstance(m, str)]
    for m in must_list:
        if m not in amenities:
            return None

    nice_to_have = intent.get("nice_to_have") or []
    if not isinstance(nice_to_have, list):
        nice_to_have = []
    nice_list = [n for n in nice_to_have if isinstance(n, str)]

    matched_must = [m for m in must_list if m in amenities]
    matched_nice = [n for n in nice_list if n in amenities]

    must_score = 1.0 if (not must_list or all(m in amenities for m in must_list)) else 0.0

    if not nice_list:
        nice_score = 0.5
    else:
        nice_score = len(matched_nice) / len(nice_list)

    purpose = intent.get("purpose")
    if not isinstance(purpose, str) or purpose not in PURPOSE_WEIGHTS:
        purpose = "leisure"
    weights = PURPOSE_WEIGHTS[purpose]
    total_w = sum(weights.values())
    if total_w <= 0:
        purpose_score = 0.0
    else:
        purpose_score = sum(weights[a] for a in amenities if a in weights) / total_w

    review_count = hotel.get("review_count")
    if isinstance(review_count, (int, float)) and not isinstance(review_count, bool):
        review_score = min(float(review_count) / 10000.0, 1.0)
    else:
        review_score = 0.0

    composite = (
        must_score * 0.60
        + nice_score * 0.20
        + purpose_score * 0.15
        + review_score * 0.05
    )

    return {
        "hotel": hotel,
        "composite": composite,
        "must_score": must_score,
        "nice_score": nice_score,
        "purpose_score": purpose_score,
        "review_score": review_score,
        "matched_must": matched_must,
        "matched_nice": matched_nice,
    }


def _rank_hotels(hotels: list[dict[str, Any]], intent: dict[str, Any], top_n: int) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for h in hotels:
        s = score_hotel(h, intent)
        if s is not None:
            scored.append(s)
    scored.sort(
        key=lambda r: (
            -r["composite"],
            -float(r["hotel"].get("rating") or 0.0),
        )
    )
    return scored[:top_n]


def _annotate_shortlist_with_relaxation(
    rows: list[dict[str, Any]], applied_reasons: list[str]
) -> list[dict[str, Any]]:
    if not applied_reasons:
        return [
            {
                **row,
                "relaxed": False,
                "relaxed_reason": None,
            }
            for row in rows
        ]
    reason = "; ".join(applied_reasons)
    return [{**row, "relaxed": True, "relaxed_reason": reason} for row in rows]


def get_shortlist(intent: dict[str, Any], top_n: int = 4) -> dict[str, Any]:
    """
    Return a dict:
    - On success: {"empty": False, "shortlist": [...]} with each row possibly marked relaxed.
    - After all fallback rounds fail: {"empty": True, "reason": "no_match", "shortlist": []}.
    """
    path = _hotels_json_path()
    with path.open(encoding="utf-8") as f:
        hotels: list[dict[str, Any]] = json.load(f)

    rows = _rank_hotels(hotels, intent, top_n)
    if rows:
        return {
            "empty": False,
            "shortlist": _annotate_shortlist_with_relaxation(rows, []),
        }

    mod = _copy_intent_for_scoring(intent)
    applied: list[str] = []

    if _has_numeric_budget(mod):
        b = float(mod["budget_per_night"])
        mod["budget_per_night"] = int(math.ceil(b * 1.2))
        applied.append("budget_adjusted_by_20_percent")
        rows = _rank_hotels(hotels, mod, top_n)
        if rows:
            return {
                "empty": False,
                "shortlist": _annotate_shortlist_with_relaxation(rows, list(applied)),
            }

    if mod.get("nice_to_have"):
        mod["nice_to_have"] = []
        applied.append("nice_to_have_cleared")
        rows = _rank_hotels(hotels, mod, top_n)
        if rows:
            return {
                "empty": False,
                "shortlist": _annotate_shortlist_with_relaxation(rows, list(applied)),
            }

    loc_val = mod.get("location_preference")
    if isinstance(loc_val, str) and loc_val.strip():
        mod["location_preference"] = None
        applied.append("location_preference_cleared")
        rows = _rank_hotels(hotels, mod, top_n)
        if rows:
            return {
                "empty": False,
                "shortlist": _annotate_shortlist_with_relaxation(rows, list(applied)),
            }

    return {"empty": True, "reason": "no_match", "shortlist": []}


def _amenity_label(key: str) -> str:
    return key.replace("_", " ")


def _format_intent_readable(intent: dict[str, Any]) -> str:
    dest = intent.get("destination") or ""
    dest_line = dest.strip() if isinstance(dest, str) else ""
    dur = intent.get("duration")
    if isinstance(dur, bool):
        dur_line = "not specified"
    elif isinstance(dur, int):
        dur_line = f"{dur} nights"
    else:
        dur_line = "not specified"
    tt = intent.get("traveler_type", "solo")
    purpose = intent.get("purpose", "leisure")
    must = intent.get("must_have") or []
    nice = intent.get("nice_to_have") or []
    must_txt = ", ".join(_amenity_label(m) for m in must) if must else "none listed"
    nice_txt = ", ".join(_amenity_label(n) for n in nice) if nice else "none listed"
    budget = intent.get("budget_per_night")
    if budget is not None and isinstance(budget, (int, float)) and not isinstance(budget, bool):
        budget_line = f"₹{int(budget):,} per night cap"
    else:
        budget_line = "not specified"
    loc = intent.get("location_preference")
    if isinstance(loc, str) and loc.strip():
        loc_line = loc.strip()
    else:
        loc_line = "none"
    kids = "yes" if intent.get("child_friendly_required") else "no"
    lines = [
        "What we understood from their message:",
        f"- City they care about: {dest_line or 'not specified'}",
        f"- Length of stay: {dur_line}",
        f"- Who is traveling: {tt}",
        f"- Trip purpose tag: {purpose}",
        f"- Non-negotiables (things they need): {must_txt}",
        f"- Helpful extras if available: {nice_txt}",
        f"- Nightly budget: {budget_line}",
        f"- Area preference: {loc_line}",
        f"- Needs a child-friendly property: {kids}",
    ]
    conf = intent.get("confidence")
    if isinstance(conf, dict):
        ov = conf.get("overall")
        lines.append(f"- Interpreter confidence (0 to 1 overall): {ov}")
        mi = conf.get("missing_info") or []
        if isinstance(mi, list) and mi:
            lines.append(f"- Search fields still not set or empty: {', '.join(str(x) for x in mi)}")
    return "\n".join(lines)


def _match_percentage(entry: dict[str, Any]) -> int:
    c = float(entry.get("composite") or 0.0)
    return int(max(0, min(100, round(c * 100))))


def _build_recommendation_user_content(
    user_message: str, intent: dict[str, Any], shortlist: list[dict[str, Any]]
) -> str:
    parts: list[str] = []
    parts.append("TRAVELER'S LATEST MESSAGE (this turn—use their exact wording when you refer to what they said):\n")
    parts.append(user_message.strip())
    parts.append("\n\nPARSED TRIP BRIEF (plain English, for you only—do not quote this like a form):\n")
    parts.append(_format_intent_readable(intent))
    parts.append("\n\nSHORTLISTED PROPERTIES (facts to ground your advice):\n")
    for i, row in enumerate(shortlist, start=1):
        h = row.get("hotel") or {}
        name = h.get("name", "Unknown")
        area = h.get("area", "")
        city = h.get("city", "")
        price = h.get("price_per_night")
        stars = h.get("stars", "")
        rating = h.get("rating", "")
        amenities = h.get("amenities") or []
        am_txt = ", ".join(_amenity_label(str(a)) for a in amenities if isinstance(a, str))
        tags = h.get("review_tags") or []
        tag_txt = "; ".join(str(t) for t in tags if isinstance(t, str))
        pct = _match_percentage(row)
        loc_bits = ", ".join(x for x in (area, city) if isinstance(x, str) and x.strip())
        price_txt = f"₹{int(price):,}" if isinstance(price, (int, float)) and not isinstance(price, bool) else "price on request"
        parts.append(f"{i}. {name}\n")
        parts.append(f"   Area / city: {loc_bits or 'not given'}\n")
        parts.append(f"   Nightly rate: {price_txt}\n")
        parts.append(f"   Star category: {stars}\n")
        parts.append(f"   Guest rating (out of five): {rating}\n")
        parts.append(f"   On-site features: {am_txt or 'not listed'}\n")
        parts.append(f"   Match percentage (how well this lines up with their mix of needs): {pct}%\n")
        parts.append(f"   Review highlights from guests: {tag_txt or 'not listed'}\n\n")
    return "".join(parts)


def _humanize_relaxed_reason_codes(relaxed_reason: str) -> str:
    bits: list[str] = []
    for part in relaxed_reason.split(";"):
        p = part.strip()
        if p == "budget_adjusted_by_20_percent":
            bits.append("the nightly budget cap was raised by about twenty percent")
        elif p == "nice_to_have_cleared":
            bits.append('optional "nice to have" preferences were set aside')
        elif p == "location_preference_cleared":
            bits.append("a tight neighbourhood preference was widened to the full city")
        elif p:
            bits.append(p)
    return "; ".join(bits) if bits else relaxed_reason


def _relaxation_notice_for_concierge(relaxed_reason: str) -> str:
    human = _humanize_relaxed_reason_codes(relaxed_reason)
    return (
        "\nCONCIERGE RELAXATION NOTICE (for you only—do not read headers aloud):\n"
        f"The shortlist exists because the matcher eased some constraints in this order: {human}.\n"
        "Acknowledge this briefly and naturally in your reply (often in the opening), in your own words, tied to what they said "
        "about their trip—for example that their exact budget line did not surface matches so you nudged it upward slightly. "
        "Stay warm and concise; never scold the traveler.\n"
    )


def _last_turn_messages_for_api(
    conversation_history: list[dict[str, Any]] | None,
    *,
    max_turns: int = 3,
) -> list[dict[str, str]]:
    """
    Return the last up to `max_turns` user–assistant pairs as Anthropic message dicts
    (oldest first), trimmed so the sequence can precede a new user message.
    """
    if not conversation_history or max_turns <= 0:
        return []
    cleaned: list[dict[str, str]] = []
    for m in conversation_history:
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        content = m.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            continue
        cleaned.append({"role": role, "content": content})
    if not cleaned:
        return []
    max_messages = max_turns * 2
    tail = cleaned[-max_messages:]
    while tail and tail[0].get("role") == "assistant":
        tail = tail[1:]
    while tail and tail[-1].get("role") == "user" and len(tail) % 2 == 1:
        tail = tail[:-1]
    return tail


def _empty_shortlist_message(
    intent: dict[str, Any], *, waterfall_exhausted: bool = False
) -> str:
    budget = intent.get("budget_per_night")
    must = intent.get("must_have") or []
    child = bool(intent.get("child_friendly_required"))
    hints: list[str] = []
    if budget is not None and isinstance(budget, (int, float)) and not isinstance(budget, bool):
        hints.append("nudge the nightly budget up a notch")
    if isinstance(must, list) and must:
        hints.append("let one must-have slip to a nice-to-have instead")
    if child:
        hints.append("keep child-friendly places but ease another filter, like area or price")
    if not hints:
        hints.append("widen the budget a little or trim one firm requirement")
    relax = hints[0] if len(hints) == 1 else "; ".join(hints[:2])
    body = (
        "I could not find any hotels that fit every hard rule at once—something in the mix "
        "(city, price cap, must-have list, or family-only stays) is tighter than what is available right now. "
        f"You might get matches if you {relax}. Tell me what you are willing to adjust and I will run another pass."
    )
    if waterfall_exhausted:
        prefix = (
            "I already tried their original filters, then nudged the nightly budget where we could, "
            "set aside optional extras, and loosened any neighbourhood pin—and still came up empty. "
        )
        return prefix + body
    return body


def _intent_field_empty_for_merge(key: str, value: Any) -> bool:
    if key == "destination":
        return not (isinstance(value, str) and value.strip())
    if key == "duration":
        return value is None or isinstance(value, bool)
    if key == "budget_per_night":
        return value is None or isinstance(value, bool)
    if key == "location_preference":
        return value is None or (isinstance(value, str) and not value.strip())
    if key in ("must_have", "nice_to_have"):
        return not value
    return False


def _merge_intent_with_session(parsed: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    out = dict(parsed)
    for key in (
        "destination",
        "duration",
        "must_have",
        "nice_to_have",
        "budget_per_night",
        "location_preference",
    ):
        if key not in session:
            continue
        cur = out.get(key)
        if _intent_field_empty_for_merge(key, cur):
            out[key] = session[key]
    return out


def _fallback_intent_from_keywords(user_message: str) -> dict[str, Any]:
    """Best-effort intent when Claude parsing fails (confidence.overall = 0.3)."""
    text = (user_message or "").lower()

    destination = ""
    if "bangalore" in text or "bengaluru" in text:
        destination = "Bangalore"
    elif "jaipur" in text:
        destination = "Jaipur"
    elif "delhi" in text or "new delhi" in text:
        destination = "Delhi"

    duration: int | None = None
    m = re.search(r"(\d+)\s*nights?", text)
    if m:
        duration = int(m.group(1))

    budget_per_night: int | None = None
    for pattern in (
        r"₹\s*([\d,]+)",
        r"rs\.?\s*([\d,]+)",
        r"inr\s*([\d,]+)",
        r"budget\s*(?:of\s*)?([\d,]+)",
        r"under\s*([\d,]+)",
    ):
        m = re.search(pattern, user_message or "", flags=re.IGNORECASE)
        if m:
            budget_per_night = int(m.group(1).replace(",", ""))
            break

    purpose = "leisure"
    if re.search(r"\b(work|business|meeting|office)\b", text):
        purpose = "work"
    elif re.search(r"\b(family|kids|children|child)\b", text):
        purpose = "family"
    elif re.search(r"\b(cheap|budget|affordable|shoestring)\b", text):
        purpose = "budget"
    elif re.search(r"\b(transit|layover|airport|flight)\b", text):
        purpose = "transit"
    elif re.search(r"\b(wedding|event|conference|banquet)\b", text):
        purpose = "event"

    traveler_type = "solo"
    if re.search(r"\b(couple|partner|spouse|wife|husband)\b", text):
        traveler_type = "couple"
    elif re.search(r"\b(family|kids|children)\b", text):
        traveler_type = "family"
    elif re.search(r"\b(group|team|friends)\b", text):
        traveler_type = "group"
    elif re.search(r"\b(solo|alone)\b", text):
        traveler_type = "solo"

    must_have: list[str] = []
    if purpose == "work" or re.search(r"\b(work|business|meeting)\b", text):
        must_have.extend(["fast_wifi", "quiet_rooms"])
    if re.search(r"\b(wifi|wi-?fi)\b", text) and "fast_wifi" not in must_have:
        must_have.append("fast_wifi")
    must_have = list(dict.fromkeys(must_have))

    nice_to_have: list[str] = []
    if "pool" in text:
        nice_to_have.append("pool")

    child_friendly_required = bool(re.search(r"\b(kids?|children|toddler|baby)\b", text))

    raw = {
        "destination": destination,
        "duration": duration,
        "traveler_type": traveler_type,
        "purpose": purpose,
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "budget_per_night": budget_per_night,
        "location_preference": None,
        "child_friendly_required": child_friendly_required,
    }
    intent = _normalize_intent(raw)
    missing = _missing_info_from_intent(intent)
    intent["confidence"] = {
        "overall": 0.3,
        "destination": "low",
        "duration": "low",
        "traveler_type": "low",
        "purpose": "low",
        "budget": "low",
        "must_have": "low",
        "nice_to_have": "low",
        "location_preference": "low",
        "child_friendly_required": "low",
        "missing_info": missing,
    }
    return intent


def _fallback_recommendation_text(shortlist: list[dict[str, Any]]) -> str:
    lines = [
        "I found some options for you. "
        "Here are the top matches based on your request.",
    ]
    for row in shortlist:
        h = row.get("hotel") or {}
        name = h.get("name") or "Hotel"
        price = h.get("price_per_night")
        if isinstance(price, (int, float)) and not isinstance(price, bool):
            lines.append(f"- {name}: ₹{int(price):,} per night")
        else:
            lines.append(f"- {name}")
    return "\n".join(lines)


def _refinement_fallback_intent(current_intent: dict[str, Any]) -> dict[str, Any]:
    base = {k: v for k, v in current_intent.items() if k != "confidence"}
    out = _normalize_intent(base)
    out["confidence"] = _build_confidence_from_model({}, out)
    return out


def generate_recommendation(
    user_message: str,
    intent: dict[str, Any],
    shortlist: list[dict[str, Any]],
    conversation_history: list[dict[str, Any]] | None = None,
    shortlist_meta: dict[str, Any] | None = None,
) -> str:
    meta = shortlist_meta if isinstance(shortlist_meta, dict) else {}
    if not shortlist:
        exhausted = bool(meta.get("empty") and meta.get("reason") == "no_match")
        return _empty_shortlist_message(intent, waterfall_exhausted=exhausted)

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return _fallback_recommendation_text(shortlist)

        prior_messages = _last_turn_messages_for_api(conversation_history, max_turns=3)
        low_conf_prefix = ""
        ic = intent.get("confidence")
        if isinstance(ic, dict):
            ov = ic.get("overall")
            if isinstance(ov, (int, float)) and not isinstance(ov, bool) and float(ov) < 0.6:
                low_conf_prefix = (
                    "LOW_PARSER_CONFIDENCE (overall {:.2f}; several trip details were guessed or left open):\n".format(
                        float(ov)
                    )
                    + "You MUST begin your answer with exactly one short clarifying question aimed at the biggest gap "
                    "(who is traveling, dates or nights, neighbourhood, or nightly budget—pick the most important unknown). "
                    "Use a warm, conversational tone in the spirit of: \"Just to make sure I get this right — are you "
                    "travelling solo or with someone? Here are my best guesses in the meantime:\" but write fresh wording. "
                    "Then continue with the hotel rundown as usual.\n\n"
                )
        current_turn = low_conf_prefix + _build_recommendation_user_content(
            user_message, intent, shortlist
        )
        if any(row.get("relaxed") for row in shortlist):
            rr = ""
            for row in shortlist:
                if row.get("relaxed"):
                    rr = str(row.get("relaxed_reason") or "").strip()
                    break
            if rr:
                current_turn += _relaxation_notice_for_concierge(rr)
        messages: list[dict[str, str]] = prior_messages + [{"role": "user", "content": current_turn}]

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=MODEL,
            max_tokens=900,
            system=CONCIERGE_SYSTEM_PROMPT,
            messages=messages,
        )
        parts: list[str] = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        text = "".join(parts).strip()
        if not text:
            return _fallback_recommendation_text(shortlist)
        return text
    except Exception:
        return _fallback_recommendation_text(shortlist)


def _hotel_snapshot_for_compare(h: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id",
        "name",
        "city",
        "area",
        "stars",
        "price_per_night",
        "rating",
        "amenities",
        "review_tags",
        "review_count",
        "child_friendly",
        "purpose_fit",
        "distance_center_km",
    )
    return {k: h.get(k) for k in keys}


def _build_comparison_user_content(
    hotel_a: dict[str, Any],
    hotel_b: dict[str, Any],
    intent: dict[str, Any],
) -> str:
    trip = {
        "destination": intent.get("destination"),
        "duration_nights": intent.get("duration"),
        "traveler_type": intent.get("traveler_type"),
        "purpose": intent.get("purpose"),
        "budget_per_night_inr": intent.get("budget_per_night"),
        "must_have_amenities": intent.get("must_have") or [],
        "nice_to_have_amenities": intent.get("nice_to_have") or [],
        "location_preference": intent.get("location_preference"),
        "child_friendly_required": intent.get("child_friendly_required"),
    }
    payload = {
        "trip_profile": trip,
        "hotel_A": _hotel_snapshot_for_compare(hotel_a),
        "hotel_B": _hotel_snapshot_for_compare(hotel_b),
    }
    return (
        "Use the JSON below only as facts; answer in plain prose per your system instructions.\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


def _fallback_hotel_comparison(
    hotel_a: dict[str, Any], hotel_b: dict[str, Any], intent: dict[str, Any]
) -> str:
    purpose = intent.get("purpose") if isinstance(intent.get("purpose"), str) else "stay"
    na = hotel_a.get("name") or "Hotel A"
    nb = hotel_b.get("name") or "Hotel B"
    pa, pb = hotel_a.get("price_per_night"), hotel_b.get("price_per_night")
    ra, rb = hotel_a.get("rating"), hotel_b.get("rating")
    if (
        isinstance(pa, (int, float))
        and not isinstance(pa, bool)
        and isinstance(pb, (int, float))
        and not isinstance(pb, bool)
    ):
        return (
            f"For your {purpose} trip, {na} is ₹{int(pa):,} per night (guest rating {ra}) and {nb} is ₹{int(pb):,} "
            f"per night (rating {rb}). If budget is the tie-breaker, lean toward whichever rate feels lighter; "
            f"otherwise compare reviews and pick the vibe you prefer."
        )
    return (
        f"For your {purpose} trip, both {na} and {nb} stayed in your shortlist—line them up on price and rating on "
        f"the cards and pick whichever fits your plans."
    )


def generate_hotel_comparison(
    hotel_a: dict[str, Any],
    hotel_b: dict[str, Any],
    intent: dict[str, Any],
) -> str:
    """
    Head-to-head comparison for two hotels, grounded in intent + hotel facts.

    On missing key or API errors, returns a short deterministic comparison from hotel facts.
    """
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return _fallback_hotel_comparison(hotel_a, hotel_b, intent)

        user_content = _build_comparison_user_content(hotel_a, hotel_b, intent)
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=COMPARE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        parts: list[str] = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        text = "".join(parts).strip()
        return text if text else _fallback_hotel_comparison(hotel_a, hotel_b, intent)
    except Exception:
        return _fallback_hotel_comparison(hotel_a, hotel_b, intent)


GUEST_VERDICT_KEY = "guest_verdict"


def enrich_with_sentiment(hotel: dict, purpose: str) -> str:
    """
    One-sentence "guest voice" line from review_tags for this trip purpose.

    Result is stored on ``hotel[guest_verdict]`` so repeat calls are cheap.
    Uses a small Claude request (max_tokens 80, user message only).

    On missing key or API errors, stores and returns an empty string without raising.
    """
    cached = hotel.get(GUEST_VERDICT_KEY)
    if isinstance(cached, str) and cached.strip():
        return cached.strip()

    tags_raw = hotel.get("review_tags") or []
    tags = [t.strip() for t in tags_raw if isinstance(t, str) and t.strip()]
    if not tags:
        line = "There are not enough themed guest snippets yet to distil a single consensus line."
        hotel[GUEST_VERDICT_KEY] = line
        return line

    purpose_clean = purpose.strip().lower() if isinstance(purpose, str) else "leisure"
    if purpose_clean not in ALLOWED_PURPOSE:
        purpose_clean = "leisure"

    name = hotel.get("name") if isinstance(hotel.get("name"), str) else "This hotel"
    tag_txt = "; ".join(tags)
    user_prompt = (
        f"Write exactly ONE sentence that sounds like the shared voice of recent guests at \"{name}\", "
        f"for someone on a {purpose_clean} trip. Ground it ONLY in these review tag phrases: {tag_txt}. "
        "No greeting, no bullet points, no quotation marks around the full sentence. "
        "Sound like candid consensus, not ad copy. Cap at 35 words.\n\n"
        "Tone reference (do not copy): Business guests consistently highlight the reliable WiFi and how undisturbed "
        "they feel in the rooms. / Families keep coming back for the pool — guests say kids are genuinely happy here."
    )

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            hotel[GUEST_VERDICT_KEY] = ""
            return ""

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=MODEL,
            max_tokens=80,
            messages=[{"role": "user", "content": user_prompt}],
        )
        parts: list[str] = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        line = "".join(parts).strip()
        if not line:
            line = "Guests mention a mix of small wins in recent feedback—worth scanning reviews before you lock this in."
        hotel[GUEST_VERDICT_KEY] = line
        return line
    except Exception:
        hotel[GUEST_VERDICT_KEY] = ""
        return ""


def enrich_shortlist_with_sentiment(
    shortlist: list[dict[str, Any]], intent: dict[str, Any]
) -> None:
    purpose = intent.get("purpose")
    if not isinstance(purpose, str) or purpose not in ALLOWED_PURPOSE:
        purpose = "leisure"
    for row in shortlist:
        h = row.get("hotel")
        if not isinstance(h, dict):
            continue
        enrich_with_sentiment(h, purpose)


def run_agent(
    user_message: str,
    session_intent: dict[str, Any] | None = None,
    is_refinement: bool = False,
    conversation_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    intent = parse_intent(user_message)
    if is_refinement and isinstance(session_intent, dict) and session_intent:
        intent = _merge_intent_with_session(intent, session_intent)
    sl_res = get_shortlist(intent)
    shortlist = sl_res.get("shortlist") or []
    enrich_shortlist_with_sentiment(shortlist, intent)
    prior = list(conversation_history or [])
    response_text = generate_recommendation(
        user_message,
        intent,
        shortlist,
        conversation_history=prior,
        shortlist_meta=sl_res,
    )
    new_history = prior + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response_text},
    ]
    return {
        "intent": intent,
        "shortlist": shortlist,
        "response_text": response_text,
        "conversation_history": new_history,
    }


def parse_intent(user_message: str) -> dict[str, Any]:
    """
    Call Claude to extract structured travel intent from natural language.

    The returned dict includes a nested ``confidence`` object (overall score, per-field
    high/medium/low, and ``missing_info``) alongside the usual intent keys.

    On any failure (including missing API key), falls back to keyword-only intent with
    ``confidence.overall`` of 0.3.
    """
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return _fallback_intent_from_keywords(user_message)

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        parts: list[str] = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        raw = "".join(parts)
        cleaned = _strip_markdown_fences(raw)
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            return _fallback_intent_from_keywords(user_message)
        intent = _normalize_intent(data)
        intent["confidence"] = _build_confidence_from_model(data.get("confidence"), intent)
        return intent
    except Exception:
        return _fallback_intent_from_keywords(user_message)


_REFINEMENT_AMENITY_HINT = ", ".join(sorted(ALLOWED_AMENITIES))

REFINEMENT_SYSTEM_PROMPT = f"""You refine an existing hotel-search intent for India using a short follow-up from the same traveler.

You will receive:
1) CURRENT_INTENT_JSON — the current intent object as JSON.
2) USER_REFINEMENT — what they want to adjust in plain language.

Return ONLY a JSON object (no markdown fences, no commentary). Include ONLY keys that should change compared to CURRENT_INTENT_JSON.

Allowed keys: destination, duration, traveler_type, purpose, must_have, nice_to_have, budget_per_night, location_preference, child_friendly_required.

Rules:
- budget_per_night: integer INR per night, or null only if they clearly remove a nightly budget cap.
- duration: integer nights, or null if they drop the length or it becomes unclear.
- traveler_type: one of solo | couple | family | group.
- purpose: one of work | leisure | family | event | budget | transit.
- must_have and nice_to_have: arrays using ONLY these amenity keys (exact spelling): {_REFINEMENT_AMENITY_HINT}.
  When the user adds or removes amenities, return the full updated array for that key.
- child_friendly_required: boolean.
- If the user loosens a constraint, reflect that honestly (for example fewer must_have items or a higher budget).

Do not echo CURRENT_INTENT_JSON back wholesale—only emit keys that change."""


def parse_refinement(refinement_message: str, current_intent: dict[str, Any]) -> dict[str, Any]:
    """
    Call Claude to interpret a refinement message and merge updates into current_intent.

    On failure, returns the previous intent unchanged (re-normalized) with refreshed confidence.
    """
    allowed_patch_keys = {
        "destination",
        "duration",
        "traveler_type",
        "purpose",
        "must_have",
        "nice_to_have",
        "budget_per_night",
        "location_preference",
        "child_friendly_required",
    }

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return _refinement_fallback_intent(current_intent)

        payload_obj = {k: v for k, v in current_intent.items() if k != "confidence"}
        payload = json.dumps(payload_obj, ensure_ascii=False)
        user_content = (
            f"CURRENT_INTENT_JSON:\n{payload}\n\nUSER_REFINEMENT:\n{refinement_message.strip()}"
        )

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=REFINEMENT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        parts: list[str] = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        raw = "".join(parts)
        cleaned = _strip_markdown_fences(raw)
        patch = json.loads(cleaned)
        if not isinstance(patch, dict):
            return _refinement_fallback_intent(current_intent)

        merged = dict(current_intent)
        merged.pop("confidence", None)
        for key, value in patch.items():
            if key in allowed_patch_keys:
                merged[key] = value
        out = _normalize_intent(merged)
        out["confidence"] = _build_confidence_from_model({}, out)
        return out
    except Exception:
        return _refinement_fallback_intent(current_intent)


if __name__ == "__main__":
    sample = "3 nights Delhi solo work trip need fast wifi budget 8000"
    print(parse_intent(sample))
