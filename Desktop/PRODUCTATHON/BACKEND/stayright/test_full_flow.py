#!/usr/bin/env python3
"""
End-to-end smoke test against a running Stayright API (default http://localhost:5000).

Requires: pip install requests
Run the server first: python app.py
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests", file=sys.stderr)
    sys.exit(2)

BASE_URL = os.environ.get("STAYRIGHT_TEST_URL", "http://localhost:5000").rstrip("/")
SESSION_ID = "smoketest"
DISCOVER_BODY = {
    "message": "3 nights Delhi solo work trip fast wifi budget 8000",
    "session_id": SESSION_ID,
}
REFINE_BODY = {"message": "drop budget to 5000", "session_id": SESSION_ID}


def _fmt(val: Any, max_len: int = 500) -> str:
    s = json.dumps(val, ensure_ascii=False) if not isinstance(val, str) else val
    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s


def main() -> None:
    failures: list[tuple[int, str]] = []
    passed = 0

    def record_pass(step: int) -> None:
        nonlocal passed
        print(f"Step {step}: PASS")
        passed += 1

    def record_fail(step: int, msg: str) -> None:
        print(f"Step {step}: FAIL")
        failures.append((step, msg))

    # --- Step 1 ---
    r = None
    data: dict[str, Any] = {}
    step1_err: str | None = None
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=30)
        if r.headers.get("content-type", "").startswith("application/json"):
            parsed = r.json()
            data = parsed if isinstance(parsed, dict) else {}
    except Exception as e:
        step1_err = str(e)

    if step1_err:
        record_fail(1, f"request or JSON error: {step1_err}")
    elif r is not None and r.status_code == 200 and data == {"status": "ok"}:
        record_pass(1)
    else:
        status = r.status_code if r is not None else None
        record_fail(
            1,
            f"expected HTTP 200 and {{\"status\": \"ok\"}}; "
            f"actual status={status}, body={_fmt(data)}",
        )

    # --- Step 2 ---
    discover_hotels: list[dict[str, Any]] = []
    r2 = None
    d2: dict[str, Any] = {}
    step2_err: str | None = None
    try:
        r2 = requests.post(
            f"{BASE_URL}/api/discover",
            json=DISCOVER_BODY,
            headers={"Content-Type": "application/json"},
            timeout=180,
        )
        if r2.headers.get("content-type", "").startswith("application/json"):
            parsed = r2.json()
            d2 = parsed if isinstance(parsed, dict) else {}
    except Exception as e:
        step2_err = str(e)

    resp_str = d2.get("response") if isinstance(d2.get("response"), str) else None
    hotels = d2.get("hotels")
    intent = d2.get("intent") if isinstance(d2.get("intent"), dict) else {}
    purpose = intent.get("purpose")

    if step2_err:
        record_fail(2, f"request or JSON error: {step2_err}")
    elif r2 is None or r2.status_code != 200:
        st = r2.status_code if r2 is not None else None
        record_fail(2, f"expected HTTP 200; actual status={st}, body={_fmt(d2)}")
    elif not resp_str or not resp_str.strip():
        record_fail(
            2,
            f"expected non-empty response string; actual response field={_fmt(d2.get('response'))}",
        )
    elif not isinstance(hotels, list) or len(hotels) == 0:
        record_fail(
            2,
            f"expected non-empty hotels list; actual hotels={_fmt(hotels)}",
        )
    elif purpose != "work":
        record_fail(
            2,
            f'expected intent.purpose == "work"; actual purpose={_fmt(purpose)}',
        )
    else:
        discover_hotels = hotels
        record_pass(2)

    # --- Step 3 ---
    r3 = None
    d3: dict[str, Any] = {}
    step3_err: str | None = None
    try:
        r3 = requests.post(
            f"{BASE_URL}/api/refine",
            json=REFINE_BODY,
            headers={"Content-Type": "application/json"},
            timeout=180,
        )
        if r3.headers.get("content-type", "").startswith("application/json"):
            parsed = r3.json()
            d3 = parsed if isinstance(parsed, dict) else {}
    except Exception as e:
        step3_err = str(e)

    refine_hotels = d3.get("hotels") if isinstance(d3.get("hotels"), list) else []
    bad_prices: list[str] = []
    if step3_err:
        record_fail(3, f"request or JSON error: {step3_err}")
    elif r3 is None or r3.status_code != 200:
        st = r3.status_code if r3 is not None else None
        record_fail(3, f"expected HTTP 200; actual status={st}, body={_fmt(d3)}")
    else:
        for h in refine_hotels:
            if not isinstance(h, dict):
                bad_prices.append("non-dict hotel entry")
                continue
            p = h.get("price_per_night")
            name = h.get("name", "?")
            if not isinstance(p, (int, float)) or isinstance(p, bool):
                bad_prices.append(f"{name}: missing or invalid price_per_night={_fmt(p)}")
            elif float(p) > 5000:
                bad_prices.append(f"{name}: price_per_night={p} (expected <= 5000)")
        if bad_prices:
            record_fail(
                3,
                "expected all hotels price_per_night <= 5000; "
                + "; ".join(bad_prices[:10])
                + (" ..." if len(bad_prices) > 10 else ""),
            )
        else:
            record_pass(3)

    # --- Step 4 ---
    first_id: int | None = None
    if discover_hotels and isinstance(discover_hotels[0], dict):
        raw_id = discover_hotels[0].get("id")
        if isinstance(raw_id, int):
            first_id = raw_id
        elif isinstance(raw_id, str) and raw_id.isdigit():
            first_id = int(raw_id)

    if first_id is None:
        record_fail(
            4,
            f"skipped: need integer hotel id from step 2; first hotel={_fmt(discover_hotels[0] if discover_hotels else None)}",
        )
    else:
        r4 = None
        d4: dict[str, Any] = {}
        step4_err: str | None = None
        try:
            r4 = requests.get(
                f"{BASE_URL}/api/explain/{first_id}",
                params={"session_id": SESSION_ID},
                timeout=30,
            )
            if r4.headers.get("content-type", "").startswith("application/json"):
                parsed = r4.json()
                d4 = parsed if isinstance(parsed, dict) else {}
        except Exception as e:
            step4_err = str(e)

        if step4_err:
            record_fail(4, f"request or JSON error: {step4_err}")
        elif r4 is None or r4.status_code != 200:
            st = r4.status_code if r4 is not None else None
            record_fail(4, f"expected HTTP 200; actual status={st}, body={_fmt(d4)}")
        elif "composite_score" not in d4:
            record_fail(
                4,
                f"expected composite_score in JSON; actual keys={list(d4.keys())}, body={_fmt(d4)}",
            )
        else:
            record_pass(4)

    # --- Step 5 ---
    ids: list[int] = []
    for h in discover_hotels[:2]:
        if not isinstance(h, dict):
            continue
        hid = h.get("id")
        if isinstance(hid, int):
            ids.append(hid)
        elif isinstance(hid, str) and hid.isdigit():
            ids.append(int(hid))

    if len(ids) < 2:
        record_fail(
            5,
            f"need two hotel ids from step 2; got {ids} from hotels len={len(discover_hotels)}",
        )
    else:
        r5 = None
        d5: dict[str, Any] = {}
        step5_err: str | None = None
        try:
            r5 = requests.post(
                f"{BASE_URL}/api/compare",
                json={"hotel_ids": ids, "session_id": SESSION_ID},
                headers={"Content-Type": "application/json"},
                timeout=120,
            )
            if r5.headers.get("content-type", "").startswith("application/json"):
                parsed = r5.json()
                d5 = parsed if isinstance(parsed, dict) else {}
        except Exception as e:
            step5_err = str(e)

        comp = d5.get("comparison") if isinstance(d5.get("comparison"), str) else None
        if step5_err:
            record_fail(5, f"request or JSON error: {step5_err}")
        elif r5 is None or r5.status_code != 200:
            st = r5.status_code if r5 is not None else None
            record_fail(5, f"expected HTTP 200; actual status={st}, body={_fmt(d5)}")
        elif not comp or len(comp) < 50:
            record_fail(
                5,
                f"expected comparison string length >= 50; actual len={len(comp or '')}, value={_fmt(comp)}",
            )
        else:
            record_pass(5)

    # --- Step 6 ---
    empty_verdicts: list[str] = []
    for h in discover_hotels:
        if not isinstance(h, dict):
            empty_verdicts.append("(non-dict)")
            continue
        gv = h.get("guest_verdict")
        name = h.get("name", "?")
        if not isinstance(gv, str) or not gv.strip():
            empty_verdicts.append(f"{name}: guest_verdict={_fmt(gv)}")
    if not discover_hotels:
        record_fail(6, "no hotels from step 2 to check guest_verdict")
    elif empty_verdicts:
        record_fail(
            6,
            "expected non-empty guest_verdict for every step-2 hotel; "
            + "; ".join(empty_verdicts[:10])
            + (" ..." if len(empty_verdicts) > 10 else ""),
        )
    else:
        record_pass(6)

    print()
    print(f"{passed}/6 passed")

    if passed == 6:
        print("SYSTEM READY FOR DEMO")
        sys.exit(0)
    else:
        for step, msg in failures:
            print(f"Step {step} failed — {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
