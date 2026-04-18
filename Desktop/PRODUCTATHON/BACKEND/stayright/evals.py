"""
Offline-style evals for Stayright (calls run_agent / parse_refinement — needs ANTHROPIC_API_KEY).

Run:  python3 evals.py
"""

from __future__ import annotations

import os
import sys
from typing import Any, Callable

from agent import get_shortlist, parse_refinement, run_agent

# --- shared helpers ---

GENERIC_BANNED = (
    "great amenities",
    "excellent location",
    "wonderful stay",
    "perfect for everyone",
)

# Longer phrases first for amenity mention detection (eval4).
_AMENITY_PHRASES: list[tuple[str, tuple[str, ...]]] = [
    ("fast_wifi", ("fast wi-fi", "fast wifi")),
    ("quiet_rooms", ("quiet rooms", "quiet room")),
    ("room_service", ("room service",)),
    ("business_center", ("business center",)),
    ("airport_shuttle", ("airport shuttle",)),
    ("kids_club", ("kids club",)),
    ("heritage_experience", ("heritage experience", "heritage stay")),
    ("wifi", ("wi-fi", "wifi")),
    ("spa", ("spa",)),
    ("pool", ("pool", "swimming pool")),
    ("gym", ("gym", "fitness")),
    ("restaurant", ("restaurant", "dining")),
    ("parking", ("parking",)),
    ("rooftop", ("rooftop",)),
]


def _hotel_amenities(h: dict[str, Any]) -> set[str]:
    raw = h.get("amenities") or []
    return {a for a in raw if isinstance(a, str)}


def _union_shortlist_amenities(shortlist: list[dict[str, Any]]) -> set[str]:
    u: set[str] = set()
    for row in shortlist:
        h = row.get("hotel") or {}
        u |= _hotel_amenities(h)
    return u


def _amenity_keys_mentioned_in_response(text: str) -> set[str]:
    """Map free-text response to canonical amenity keys (conservative)."""
    t = text.lower()
    found: set[str] = set()
    for key, phrases in _AMENITY_PHRASES:
        for p in phrases:
            if p in t:
                found.add(key)
                break
    return found


def _budget_int(intent: dict[str, Any]) -> int | None:
    b = intent.get("budget_per_night")
    if isinstance(b, bool) or b is None:
        return None
    if isinstance(b, (int, float)):
        return int(b)
    return None


def _satisfies_amenity_mention(union: set[str], key: str) -> bool:
    """Wi-fi style mentions satisfied if property has wifi or fast_wifi."""
    if key == "wifi":
        return bool(union & {"wifi", "fast_wifi"})
    if key == "fast_wifi":
        return bool(union & {"fast_wifi", "wifi"})
    return key in union


def _check_hotels_have_amenities(
    shortlist: list[dict[str, Any]], must_keys: list[str]
) -> list[str]:
    """Return list of violation messages (empty if all pass)."""
    violations: list[str] = []
    if not shortlist:
        violations.append("shortlist is empty")
        return violations
    for row in shortlist:
        h = row.get("hotel") or {}
        hid = h.get("id", "?")
        name = h.get("name", "?")
        ha = _hotel_amenities(h)
        missing = [a for a in must_keys if a not in ha]
        if missing:
            violations.append(f"hotel {hid} {name!r} missing {missing}")
    return violations


def eval1_amenity_precision() -> bool:
    """
    10 cases: (query, must_have keys) — every shortlisted hotel must have every key.
    Pass: 10/10 (no violations).
    """
    cases: list[tuple[str, list[str]]] = [
        (
            "Delhi solo work trip 4 nights need reliable fast wifi and quiet rooms for calls, budget 22000",
            ["fast_wifi", "quiet_rooms"],
        ),
        (
            "Bangalore 3 nights work near tech corridor budget 9000, gym on site is a must",
            ["gym"],
        ),
        (
            "Jaipur family trip with kids 4 nights, swimming pool is mandatory, under 7000 rupees per night",
            ["pool"],
        ),
        (
            "Delhi 2 nights transit near airport early flight budget 6000, parking and airport shuttle required",
            ["parking", "airport_shuttle"],
        ),
        (
            "Jaipur work meetings C-Scheme area 5 nights budget 9000, fast wifi and quiet rooms are must-haves",
            ["fast_wifi", "quiet_rooms"],
        ),
        (
            "Bangalore leisure weekend budget 25000, rooftop access is non-negotiable for me",
            ["rooftop"],
        ),
        (
            "Delhi corporate stay Nehru Place 3 nights budget 12000, need business center and fast wifi",
            ["business_center", "fast_wifi"],
        ),
        (
            "Jaipur Amer fort area heritage experience trip 3 nights budget 4500, heritage experience must",
            ["heritage_experience"],
        ),
        (
            "Bangalore Whitefield work 5 nights budget 9000, quiet rooms and gym are both required",
            ["quiet_rooms", "gym"],
        ),
        (
            "Delhi Karol Bagh budget area 2 nights budget 4000, restaurant and parking are must-haves",
            ["restaurant", "parking"],
        ),
    ]

    passed = 0
    print("\n=== eval1_amenity_precision (threshold 10/10) ===\n")
    for i, (query, must_keys) in enumerate(cases, start=1):
        label = f"case {i}/{len(cases)}"
        try:
            out = run_agent(query, session_intent=None, is_refinement=False)
        except Exception as e:
            print(f"{label}  FAIL  run_agent error: {e}")
            continue
        shortlist = out.get("shortlist") or []
        vio = _check_hotels_have_amenities(shortlist, must_keys)
        if vio:
            print(f"{label}  FAIL  {vio[0]}")
        else:
            print(f"{label}  PASS")
            passed += 1

    ok = passed == len(cases)
    print(f"\neval1_amenity_precision overall: {'PASS' if ok else 'FAIL'} ({passed}/{len(cases)})\n")
    return ok


def eval2_constraint_change() -> bool:
    """
    4 refinements: budget drop, add amenity, budget increase, add quiet rooms.
    Pass: 4/4.
    """
    checks: list[tuple[str, str, str, Callable[[dict, list, dict, list], tuple[bool, str]]]] = [
        (
            "budget_drop",
            "Delhi solo work trip 3 nights fast wifi quiet rooms budget 30000",
            "Please lower my nightly budget to 7000 rupees maximum.",
            lambda i1, s1, i2, s2: (
                bool(s2)
                and all((r.get("hotel") or {}).get("price_per_night", 999999) <= 7000 for r in s2),
                "all refined hotels price <= 7000 and shortlist non-empty",
            ),
        ),
        (
            "add_amenity",
            "Bangalore 3 nights work trip budget 15000 solo",
            "I also need an on-site gym as a must-have.",
            lambda i1, s1, i2, s2: (
                bool(s2) and all("gym" in _hotel_amenities(r.get("hotel") or {}) for r in s2),
                "all refined hotels include gym",
            ),
        ),
        (
            "budget_increase",
            "Jaipur 2 nights shoestring budget 1000 rupees per night solo backpacker",
            "Actually raise my budget to 6000 rupees per night so I have more choices.",
            lambda i1, s1, i2, s2: (
                _budget_int(i2) is not None
                and _budget_int(i1) is not None
                and _budget_int(i2) > _budget_int(i1)
                and bool(s2)
                and all(
                    (r.get("hotel") or {}).get("price_per_night", 999999) <= _budget_int(i2)
                    for r in s2
                ),
                "intent budget increased and every refined hotel respects new nightly cap",
            ),
        ),
        (
            "add_quiet_rooms",
            "Delhi work trip 3 nights budget 20000 fast wifi solo",
            "Add quiet rooms to my must-have list for sleeping.",
            lambda i1, s1, i2, s2: (
                bool(s2)
                and all(
                    "quiet_rooms" in _hotel_amenities(r.get("hotel") or {}) for r in s2
                ),
                "all refined hotels have quiet_rooms",
            ),
        ),
    ]

    passed = 0
    print("\n=== eval2_constraint_change (threshold 4/4) ===\n")
    for name, initial_q, refine_q, checker in checks:
        try:
            first = run_agent(initial_q, session_intent=None, is_refinement=False)
            intent1 = first["intent"]
            s1 = first.get("shortlist") or []
            intent2 = parse_refinement(refine_q, intent1)
            s2 = get_shortlist(intent2).get("shortlist") or []
        except Exception as e:
            print(f"{name}  FAIL  error: {e}")
            continue
        ok, reason = checker(intent1, s1, intent2, s2)
        if ok:
            print(f"{name}  PASS  ({reason})")
            passed += 1
        else:
            print(f"{name}  FAIL  ({reason})")

    overall = passed == len(checks)
    print(f"\neval2_constraint_change overall: {'PASS' if overall else 'FAIL'} ({passed}/{len(checks)})\n")
    return overall


def eval3_reasoning_relevance() -> bool:
    """
    5 cases: (query, keywords that should appear); ban generic fluff phrases.
    Pass: >= 4/5 cases pass.
    """
    cases: list[tuple[str, list[str]]] = [
        (
            "Delhi solo 3 nights work trip need fast wifi budget 9000",
            ["delhi", "work", "wifi", "solo", "budget"],
        ),
        (
            "Jaipur family 4 nights with kids pool budget 7000",
            ["jaipur", "family", "kids", "pool", "budget"],
        ),
        (
            "Bangalore Koramangala weekend leisure cafes vibe budget 5000",
            ["bangalore", "leisure", "budget", "koramangala"],
        ),
        (
            "Delhi Aerocity one night transit flight morning airport shuttle budget 5000",
            ["delhi", "airport", "transit", "night", "budget"],
        ),
        (
            "Jaipur heritage Amer fort area 3 nights culture budget 3500",
            ["jaipur", "heritage", "amer", "budget", "nights"],
        ),
    ]

    def case_ok(response: str, keywords: list[str]) -> tuple[bool, str]:
        low = response.lower()
        if any(b in low for b in GENERIC_BANNED):
            return False, "contains banned generic phrase"
        if not any(kw.lower() in low for kw in keywords):
            return False, "no keyword hit"
        return True, "keyword hit, no banned phrase"

    passed = 0
    print("\n=== eval3_reasoning_relevance (threshold 4/5) ===\n")
    for i, (query, kws) in enumerate(cases, start=1):
        try:
            out = run_agent(query, session_intent=None, is_refinement=False)
            text = out.get("response_text") or ""
        except Exception as e:
            print(f"case {i}  FAIL  {e}")
            continue
        ok, reason = case_ok(text, kws)
        print(f"case {i}  {'PASS' if ok else 'FAIL'}  ({reason})")
        if ok:
            passed += 1

    overall = passed >= 4
    print(f"\neval3_reasoning_relevance overall: {'PASS' if overall else 'FAIL'} ({passed}/{len(cases)} cases ok)\n")
    return overall


def eval4_hallucination_guard() -> bool:
    """
    For each query: any amenity-like phrase in the response must appear on at least one shortlisted hotel.
    Pass: 0 hallucinations across all 5 tests.
    """
    queries = [
        "Delhi work trip 3 nights fast wifi quiet rooms budget 12000 solo",
        "Jaipur leisure pool spa weekend budget 20000 couple",
        "Bangalore gym and rooftop work trip budget 25000 solo",
        "Delhi family kids club and pool 4 nights budget 15000",
        "Jaipur event banquet parking airport shuttle budget 12000",
    ]

    print("\n=== eval4_hallucination_guard (threshold 0 hallucinations) ===\n")
    hallucinations = 0
    for i, query in enumerate(queries, start=1):
        try:
            out = run_agent(query, session_intent=None, is_refinement=False)
            text = out.get("response_text") or ""
            shortlist = out.get("shortlist") or []
        except Exception as e:
            print(f"case {i}  FAIL  run_agent error: {e}")
            hallucinations += 1
            continue

        mentioned = _amenity_keys_mentioned_in_response(text)
        union = _union_shortlist_amenities(shortlist)
        bad: list[str] = []
        for key in sorted(mentioned):
            if not _satisfies_amenity_mention(union, key):
                bad.append(key)
        if bad:
            print(f"case {i}  FAIL  amenities in text not backed by shortlist: {bad}")
            hallucinations += len(bad)
        else:
            print(f"case {i}  PASS  (mentioned amenity keys: {sorted(mentioned) or 'none'})")

    ok = hallucinations == 0
    print(f"\neval4_hallucination_guard overall: {'PASS' if ok else 'FAIL'} (hallucination count: {hallucinations})\n")
    return ok


def _run_all() -> dict[str, bool]:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set; evals will fail on API calls.", file=sys.stderr)
    return {
        "eval1_amenity_precision": eval1_amenity_precision(),
        "eval2_constraint_change": eval2_constraint_change(),
        "eval3_reasoning_relevance": eval3_reasoning_relevance(),
        "eval4_hallucination_guard": eval4_hallucination_guard(),
    }


def main() -> None:
    results = _run_all()
    print("\n" + "=" * 56)
    print(f"{'Eval':<34} {'Result':>10}")
    print("-" * 56)
    for name, ok in results.items():
        print(f"{name:<34} {'PASS' if ok else 'FAIL':>10}")
    print("=" * 56)
    all_pass = all(results.values())
    print(f"\nSuite: {'ALL PASS' if all_pass else 'SOME FAILURES'}\n")


if __name__ == "__main__":
    main()
