"""
inference.py — Baseline Agent for Procurement Negotiation Environment
======================================================================
Runs all 3 tasks using an LLM agent via OpenAI-compatible client.
Emits structured [START] / [STEP] / [END] stdout logs as required.

Usage:
  python inference.py

Env vars required:
  API_BASE_URL   e.g. https://api.openai.com/v1
  MODEL_NAME     e.g. gpt-4o or claude-sonnet-4-6
  HF_TOKEN       your Hugging Face / API key
"""

import os
import sys
import json
import time

from openai import OpenAI
from env import ProcurementEnv
from tasks.task1_easy   import grade_task1
from tasks.task2_medium import grade_task2
from tasks.task3_hard   import grade_task3

# ── CONFIG ────────────────────────────────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN",     "")

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

TASK_CONFIGS = [
    {"level": "easy",   "seed": 1, "grade_fn": grade_task1},
    {"level": "medium", "seed": 2, "grade_fn": grade_task2},
    {"level": "hard",   "seed": 3, "grade_fn": grade_task3},
]

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert AI procurement manager. Your job is to analyse vendor contracts,
negotiate the best deal, and select the optimal vendor under uncertainty.

RULES:
1. Read each vendor's contract_text carefully. Clauses like component substitution,
   refurbished units, or liability caps are RED FLAGS — penalise that vendor.
2. Always try to negotiate (COUNTER_OFFER) at least once before accepting.
3. Never accept a deal that exceeds the budget.
4. Never accept a deal that cannot meet the deadline.
5. Prefer vendors with transparent, buyer-friendly contract terms.

ACTIONS you can return (pick exactly one per turn):
  {"type": "COUNTER_OFFER",  "vendor_id": "X", "new_price": 195}
  {"type": "ACCEPT_DEAL",    "vendor_id": "X"}
  {"type": "REJECT_VENDOR",  "vendor_id": "X"}
  {"type": "SELECT_VENDOR",  "vendor_id": "X"}

Return ONLY valid JSON. No explanation outside the JSON.

After each ACCEPT_DEAL also add an "explanation" field summarising your reasoning:
  {"type": "ACCEPT_DEAL", "vendor_id": "X", "explanation": "..."}
"""


# ── AGENT FUNCTION ─────────────────────────────────────────────────────────────
def llm_agent(state: dict) -> dict:
    """Call the LLM with current state, return parsed action."""
    user_msg = (
        "Current procurement state:\n"
        + json.dumps(state, indent=2)
        + "\n\nChoose your next action. Return valid JSON only."
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=512,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg}
        ]
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if model wraps in ```json
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: safe default action
        return {"type": "ACCEPT_DEAL", "vendor_id": state["vendors"][0]["id"],
                "explanation": "JSON parse failed — fallback action."}


# ── MAIN RUNNER ───────────────────────────────────────────────────────────────
def main():
    all_results = []

    for cfg in TASK_CONFIGS:
        level    = cfg["level"]
        seed     = cfg["seed"]
        grade_fn = cfg["grade_fn"]

        env  = ProcurementEnv(task_level=level, seed=seed)
        obs  = env.reset()
        done = False
        steps_log = []
        step_num  = 0

        # ── [START] log ───────────────────────────────────────────────────────
        print(json.dumps({
            "event":      "START",
            "task":       f"task_{level}",
            "task_level": level,
            "budget":     obs["budget"],
            "deadline":   obs["deadline_days"],
            "vendors":    [v["id"] for v in obs["vendors"]]
        }))
        sys.stdout.flush()

        t_start = time.time()

        while not done:
            step_num += 1
            action = llm_agent(obs)
            result = env.step(action)

            obs    = result["state"]
            reward = result["reward"]
            done   = result["done"]
            info   = result["info"]

            step_entry = {
                "step":   step_num,
                "action": action,
                "reward": reward,
                "done":   done,
                "info":   info
            }
            steps_log.append(step_entry)

            # ── [STEP] log ────────────────────────────────────────────────────
            print(json.dumps({
                "event":  "STEP",
                "task":   f"task_{level}",
                "step":   step_num,
                "action": action.get("type"),
                "vendor": action.get("vendor_id"),
                "reward": reward,
                "done":   done
            }))
            sys.stdout.flush()

        # ── Grade ─────────────────────────────────────────────────────────────
        grade = grade_fn(obs, steps_log)
        elapsed = round(time.time() - t_start, 2)

        # ── [END] log ─────────────────────────────────────────────────────────
        print(json.dumps({
            "event":            "END",
            "task":             f"task_{level}",
            "score":            grade["score"],
            "passed":           grade["passed"],
            "selected_vendor":  grade.get("selected_vendor"),
            "final_price":      grade.get("final_price"),
            "checks":           grade["checks"],
            "elapsed_seconds":  elapsed
        }))
        sys.stdout.flush()

        all_results.append(grade)

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    avg_score = round(sum(r["score"] for r in all_results) / len(all_results), 4)
    all_passed = all(r["passed"] for r in all_results)

    print(json.dumps({
        "event":       "SUMMARY",
        "tasks_run":   len(all_results),
        "avg_score":   avg_score,
        "all_passed":  all_passed,
        "results":     [
            {"task": r["task"], "score": r["score"], "passed": r["passed"]}
            for r in all_results
        ]
    }))
    sys.stdout.flush()

    # Exit non-zero if any task failed
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()