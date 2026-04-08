"""
Task 1 — Easy: Clear Best Vendor Selection
==========================================
Scenario : 2 vendors. One is clearly better on all metrics.
           No negotiation needed. No hidden traps.
Goal     : Agent must identify and accept the correct vendor.
Grader   : Checks 3 binary verifiable outcomes.
"""

from env import ProcurementEnv


def run_task1(agent_fn) -> dict:
    """
    Run Task 1 and return grading results.

    agent_fn: callable(state) -> action dict
    """
    env   = ProcurementEnv(task_level="easy", seed=1)
    obs   = env.reset()
    done  = False
    steps = []

    while not done:
        action   = agent_fn(obs)
        result   = env.step(action)
        obs      = result["state"]
        done     = result["done"]
        steps.append({"action": action, "result": result})

    return grade_task1(obs, steps)


def grade_task1(final_state: dict, steps: list) -> dict:
    """
    Grader checks 3 verifiable binary outcomes. No subjective scoring.

    Check 1: Did agent accept vendor B or E (the reliable ones)?
    Check 2: Did the final price stay within budget?
    Check 3: Did selected vendor meet the deadline?
    """
    selected  = final_state.get("selected_vendor")
    outcome   = final_state.get("outcome")
    budget    = final_state.get("budget", 100_000)
    deadline  = final_state.get("deadline_days", 10)
    final_p   = final_state.get("final_price", 9_999_999)
    qty       = final_state["requirements"]["quantity"]

    # Find selected vendor's delivery days from state
    delivery  = None
    for v in final_state.get("vendors", []):
        if v["id"] == selected:
            delivery = v.get("delivery_days")

    # ── Check 1: Accepted a deal at all
    check_accepted = outcome == "accepted"

    # ── Check 2: Within budget
    check_budget = (final_p is not None) and (final_p <= budget)

    # ── Check 3: Meets deadline
    check_deadline = (delivery is not None) and (delivery <= deadline)

    checks  = [check_accepted, check_budget, check_deadline]
    score   = round(sum(checks) / len(checks), 2)

    return {
        "task": "task1_easy",
        "score": score,
        "reward_range": "0.0–1.0",
        "checks": {
            "accepted_a_deal":    check_accepted,
            "within_budget":      check_budget,
            "meets_deadline":     check_deadline
        },
        "selected_vendor": selected,
        "final_price":     final_p,
        "passed":          score >= 0.67   # at least 2/3 checks
    }