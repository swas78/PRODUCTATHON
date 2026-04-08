"""
Task 3 — Hard: Hidden Traps + Dynamic Events + 5 Vendors
=========================================================
Scenario : 5 vendors. Multiple contract traps:
           - Vendor A: component substitution clause (clause 9.3)
           - Vendor D: refurbished units clause (clause 9.3)
           Dynamic events fire mid-episode (budget cuts, deadline changes).
Goal     : Read contracts deeply, reject trapped vendors, negotiate smart,
           adapt to events, accept the genuinely best deal.
Grader   : 5 verifiable outcome checks + partial credit scoring.
"""

from env import ProcurementEnv, VENDOR_CATALOGUE

# Vendors with contract clause traps the agent must catch
TRAP_VENDOR_IDS = {"A", "D"}   # substitution + refurbished clauses

# Vendors that are genuinely safe choices (low risk + good terms)
SAFE_VENDOR_IDS = {"B", "E"}


def run_task3(agent_fn) -> dict:
    env  = ProcurementEnv(task_level="hard", seed=3)
    obs  = env.reset()
    done = False
    steps = []

    while not done:
        action = agent_fn(obs)
        result = env.step(action)
        obs    = result["state"]
        done   = result["done"]
        steps.append({"action": action, "result": result})

    return grade_task3(obs, steps)


def grade_task3(final_state: dict, steps: list) -> dict:
    """
    Check 1: Accepted a deal (didn't time out)
    Check 2: Avoided BOTH trap vendors (A and D)
    Check 3: Final price within (possibly reduced) budget
    Check 4: Delivery meets (possibly tightened) deadline
    Check 5: Selected a safe vendor (B or E preferred)

    Bonus: Partial credit if only one trap avoided (0.5 on check 2)
    """
    selected  = final_state.get("selected_vendor")
    outcome   = final_state.get("outcome")
    budget    = final_state.get("budget", 100_000)   # may have been cut
    deadline  = final_state.get("deadline_days", 10) # may have tightened
    final_p   = final_state.get("final_price", 9_999_999)
    history   = final_state.get("history", [])
    events    = final_state.get("events_triggered", [])

    # Find delivery days for selected vendor
    delivery = None
    for v in final_state.get("vendors", []):
        if v["id"] == selected:
            delivery = v.get("delivery_days")

    # All rejected vendors
    rejected = {
        h["action"]["vendor_id"]
        for h in history
        if h["action"].get("type", "").upper() == "REJECT_VENDOR"
    }

    # ── Check 1: Accepted a deal
    check_accepted = outcome == "accepted"

    # ── Check 2: Avoided trap vendors (partial credit)
    traps_avoided = TRAP_VENDOR_IDS - {selected}
    traps_rejected_explicitly = TRAP_VENDOR_IDS & rejected
    if selected not in TRAP_VENDOR_IDS:
        trap_score = 1.0
    elif len(traps_rejected_explicitly) == 1:
        trap_score = 0.5  # caught one trap
    else:
        trap_score = 0.0
    check_traps = trap_score

    # ── Check 3: Budget after dynamic events
    check_budget = (final_p is not None) and (final_p <= budget)

    # ── Check 4: Deadline after dynamic events
    check_deadline = (delivery is not None) and (delivery <= deadline)

    # ── Check 5: Chose a genuinely safe vendor
    check_safe = selected in SAFE_VENDOR_IDS

    raw_score = (
        (1.0 * check_accepted) +
        (1.0 * check_traps) +
        (1.0 * check_budget) +
        (1.0 * check_deadline) +
        (1.0 * check_safe)
    )
    score = round(raw_score / 5.0, 2)

    return {
        "task":   "task3_hard",
        "score":  score,
        "reward_range": "0.0–1.0",
        "checks": {
            "accepted_a_deal":     check_accepted,
            "avoided_trap_vendors": check_traps,
            "within_budget":       check_budget,
            "meets_deadline":      check_deadline,
            "chose_safe_vendor":   check_safe
        },
        "selected_vendor":  selected,
        "final_price":      final_p,
        "events_fired":     [e["event_id"] for e in events],
        "budget_at_close":  budget,
        "deadline_at_close": deadline,
        "passed":           score >= 0.60   # 3/5 checks minimum
    }