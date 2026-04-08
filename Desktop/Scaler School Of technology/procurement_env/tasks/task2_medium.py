"""
Task 2 — Medium: Price vs Reliability Trade-off
================================================
Scenario : 3 vendors. Cheapest has hidden risk in contract.
           Agent must read contract text, infer risk, negotiate.
Goal     : Avoid high-risk vendors. Negotiate price down. Stay in budget.
Grader   : 4 verifiable outcome checks.
"""

from env import ProcurementEnv, VENDOR_CATALOGUE


# Vendors with true_risk > 0.6 are "risky" — agent must infer from contract
RISKY_VENDOR_IDS = {
    v["id"] for v in VENDOR_CATALOGUE if v["true_risk"] > 0.60
}


def run_task2(agent_fn) -> dict:
    env  = ProcurementEnv(task_level="medium", seed=2)
    obs  = env.reset()
    done = False
    steps = []

    while not done:
        action = agent_fn(obs)
        result = env.step(action)
        obs    = result["state"]
        done   = result["done"]
        steps.append({"action": action, "result": result})

    return grade_task2(obs, steps)


def grade_task2(final_state: dict, steps: list) -> dict:
    """
    Check 1: Accepted a deal (didn't time out)
    Check 2: Did NOT accept a risky vendor (true_risk > 0.6)
    Check 3: Final price within budget
    Check 4: At least one COUNTER_OFFER was attempted (used negotiation)
    """
    selected = final_state.get("selected_vendor")
    outcome  = final_state.get("outcome")
    budget   = final_state.get("budget", 100_000)
    final_p  = final_state.get("final_price", 9_999_999)
    history  = final_state.get("history", [])

    # ── Check 1
    check_accepted = outcome == "accepted"

    # ── Check 2: Avoided risky vendors
    check_avoided_risk = selected not in RISKY_VENDOR_IDS

    # ── Check 3: Budget compliance
    check_budget = (final_p is not None) and (final_p <= budget)

    # ── Check 4: Used negotiation at least once
    counter_offers = [
        h for h in history
        if h["action"].get("type", "").upper() == "COUNTER_OFFER"
    ]
    check_negotiated = len(counter_offers) >= 1

    checks = [check_accepted, check_avoided_risk,
              check_budget, check_negotiated]
    score  = round(sum(checks) / len(checks), 2)

    return {
        "task":    "task2_medium",
        "score":   score,
        "reward_range": "0.0–1.0",
        "checks": {
            "accepted_a_deal":       check_accepted,
            "avoided_risky_vendor":  check_avoided_risk,
            "within_budget":         check_budget,
            "used_negotiation":      check_negotiated
        },
        "selected_vendor":   selected,
        "final_price":       final_p,
        "counter_offers":    len(counter_offers),
        "passed":            score >= 0.75   # at least 3/4 checks
    }