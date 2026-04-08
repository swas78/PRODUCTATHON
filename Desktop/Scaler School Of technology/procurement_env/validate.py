"""
validate.py — Pre-submission Validator
=======================================
Run this before submitting to catch issues early.
Checks all 5 items from the hackathon pre-submission checklist.

Usage:
  python validate.py
"""

import sys
import json
import importlib

PASS = "[PASS]"
FAIL = "[FAIL]"
results = []


def check(name, fn):
    try:
        ok, msg = fn()
        status = PASS if ok else FAIL
        print(f"{status} {name}: {msg}")
        results.append(ok)
    except Exception as e:
        print(f"{FAIL} {name}: Exception — {e}")
        results.append(False)


# ── 1. Import env ─────────────────────────────────────────────────────────────
def test_import():
    mod = importlib.import_module("env")
    assert hasattr(mod, "ProcurementEnv")
    return True, "ProcurementEnv importable"

check("Import env", test_import)


# ── 2. reset() returns a dict with required keys ──────────────────────────────
def test_reset():
    from env import ProcurementEnv
    env = ProcurementEnv(task_level="easy")
    s = env.reset()
    required = ["budget", "deadline_days", "requirements",
                "vendors", "current_round", "max_rounds", "done"]
    missing = [k for k in required if k not in s]
    if missing:
        return False, f"Missing keys: {missing}"
    return True, "reset() returns all required keys"

check("reset() keys", test_reset)


# ── 3. step() returns required fields ─────────────────────────────────────────
def test_step():
    from env import ProcurementEnv
    env = ProcurementEnv(task_level="easy")
    env.reset()
    action = {"type": "ACCEPT_DEAL", "vendor_id": env._state["vendors"][0]["id"]}
    result = env.step(action)
    for key in ["state", "reward", "done", "info"]:
        assert key in result, f"Missing key: {key}"
    r = result["reward"]
    assert 0.0 <= r <= 1.0, f"Reward out of range: {r}"
    return True, f"step() OK, reward={r}"

check("step() output", test_step)


# ── 4. All 3 task graders return score in 0.0–1.0 ────────────────────────────
def test_graders():
    from env import ProcurementEnv
    from tasks.task1_easy   import grade_task1
    from tasks.task2_medium import grade_task2
    from tasks.task3_hard   import grade_task3

    for level, grade_fn in [("easy", grade_task1),
                              ("medium", grade_task2),
                              ("hard", grade_task3)]:
        env  = ProcurementEnv(task_level=level)
        obs  = env.reset()
        done = False
        steps = []
        while not done:
            # dummy agent: always accept first vendor immediately
            action = {"type": "ACCEPT_DEAL",
                      "vendor_id": obs["vendors"][0]["id"]}
            result = env.step(action)
            obs, done = result["state"], result["done"]
            steps.append({"action": action, "result": result})

        grade = grade_fn(obs, steps)
        s = grade["score"]
        assert 0.0 <= s <= 1.0, f"{level} score out of range: {s}"
        assert "checks" in grade
        assert "passed" in grade

    return True, "All 3 graders return valid 0.0–1.0 scores"

check("Graders 0.0–1.0", test_graders)


# ── 5. openenv.yaml is valid YAML with required keys ─────────────────────────
def test_yaml():
    import yaml
    with open("openenv.yaml") as f:
        cfg = yaml.safe_load(f)
    required = ["name", "version", "tasks", "observation_space",
                "action_space", "reward", "grader", "infra", "inference"]
    missing = [k for k in required if k not in cfg]
    if missing:
        return False, f"Missing YAML keys: {missing}"
    tasks = cfg.get("tasks", [])
    assert len(tasks) >= 3, "Need at least 3 tasks"
    return True, f"openenv.yaml valid, {len(tasks)} tasks defined"

check("openenv.yaml", test_yaml)


# ── 6. inference.py exists and has main() ────────────────────────────────────
def test_inference():
    import ast, os
    assert os.path.exists("inference.py"), "inference.py not found"
    with open("inference.py") as f:
        tree = ast.parse(f.read())
    fns = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "main" in fns, "main() not found in inference.py"
    return True, "inference.py exists with main()"

check("inference.py", test_inference)


# ── SUMMARY ───────────────────────────────────────────────────────────────────
print()
passed = sum(results)
total  = len(results)
print(f"Result: {passed}/{total} checks passed")

if passed == total:
    print("Ready to submit!")
    sys.exit(0)
else:
    print("Fix the above issues before submitting.")
    sys.exit(1)