# Procurement & Contract Negotiation Environment

An OpenEnv-compatible RL environment where an AI agent acts as a procurement
manager — reading multi-clause vendor contracts, inferring hidden risks,
negotiating prices, adapting to dynamic market events, and selecting the
optimal vendor under uncertainty.

---

## Observation Space

| Field | Type | Description |
|---|---|---|
| `budget` | int | Procurement budget in USD |
| `deadline_days` | int | Days until delivery required |
| `requirements` | dict | Item, quantity, min warranty |
| `vendors` | list | Public vendor data + full contract text |
| `current_round` | int | Current negotiation round |
| `max_rounds` | int | Maximum rounds allowed |
| `history` | list | All past actions |
| `events_triggered` | list | Dynamic events fired this episode |
| `done` | bool | Episode complete flag |

## Action Space

```json
{"type": "SELECT_VENDOR",  "vendor_id": "B"}
{"type": "COUNTER_OFFER",  "vendor_id": "E", "new_price": 195}
{"type": "ACCEPT_DEAL",    "vendor_id": "E", "explanation": "..."}
{"type": "REJECT_VENDOR",  "vendor_id": "A"}
```

## Tasks

| Task | Level | Vendors | Key Challenge |
|---|---|---|---|
| task1_easy | Easy | 2 | Identify clear best vendor |
| task2_medium | Medium | 3 | Infer hidden risk, negotiate |
| task3_hard | Hard | 5 | Contract traps + dynamic events |

## Reward Function

```
reward = 0.35 * cost_score
       + 0.30 * reliability_score
       + 0.15 * time_efficiency
       + 0.10 * warranty_score
       + 0.10 * negotiation_efficiency
```

All components normalised to 0.0–1.0. Final reward in range [0.0, 1.0].

## Setup

```bash
pip install -r requirements.txt

export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your_key_here"

# Validate before submitting
python validate.py

# Run baseline agent
python inference.py
```

## Docker

```bash
docker build -t procurement-env .
docker run -e API_BASE_URL=... -e MODEL_NAME=... -e HF_TOKEN=... procurement-env
```

## Log Format

All stdout logs follow the required [START]/[STEP]/[END] JSON format:

```json
{"event": "START", "task": "task_hard", "budget": 100000, ...}
{"event": "STEP",  "task": "task_hard", "step": 1, "action": "COUNTER_OFFER", ...}
{"event": "END",   "task": "task_hard", "score": 0.82, "passed": true, ...}
{"event": "SUMMARY", "avg_score": 0.79, "all_passed": true}
```