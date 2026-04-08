"""
Procurement & Contract Negotiation Environment
OpenEnv-compatible RL environment

Fixes applied:
  - 5 vendors instead of 2 (forces real trade-off reasoning)
  - Rich multi-clause contract text (real LLM parsing challenge)
  - Grader checks verifiable outcomes, not just reward floats
  - Hidden contract clause traps that override numeric data
  - Dynamic events that change mid-episode
  - Negotiation memory across rounds
  - Structured [START]/[STEP]/[END] logging for evaluation
"""

import json
import random
import copy
from typing import Optional


# ── VENDOR CATALOGUE ──────────────────────────────────────────────────────────
# Each vendor has: public fields (agent can see) + hidden fields (grader only)
# true_risk is NEVER sent to the agent — it must be inferred from contract text

VENDOR_CATALOGUE = [
    {
        "id": "A",
        "name": "QuickSupply Co.",
        "price_per_unit": 160,
        "delivery_days": 12,
        "warranty_months": 6,
        "flexibility": 0.10,   # will drop at most 10% on price
        "true_risk": 0.85,     # HIDDEN — agent must infer from contract
        "contract_text": """
VENDOR AGREEMENT — QuickSupply Co.

CLAUSE 2.1 (Pricing): Unit price fixed at quoted rate. No volume discount applies.

CLAUSE 4.2 (Delivery): In the event delivery exceeds the agreed schedule, vendor 
shall incur a penalty of 20% of invoice value per week of delay, capped at 60%. 
Vendor disclaims liability for delays caused by logistics partners.

CLAUSE 7.1 (Warranty): Warranty coverage is limited to manufacturing defects only. 
Physical damage, improper use, or third-party modifications void this warranty. 
Coverage period is 6 months from delivery date.

CLAUSE 9.3 (Component Substitution): Vendor reserves the right to substitute 
equivalent or comparable components without prior buyer notification if supply 
chain disruptions occur. Substituted components carry no additional warranty.

CLAUSE 11.1 (Dispute Resolution): All disputes shall be resolved via binding 
arbitration in vendor's home jurisdiction. Buyer waives right to class action.
        """.strip()
    },
    {
        "id": "B",
        "name": "ReliaTech Ltd.",
        "price_per_unit": 220,
        "delivery_days": 5,
        "warranty_months": 24,
        "flexibility": 0.70,
        "true_risk": 0.12,
        "contract_text": """
VENDOR AGREEMENT — ReliaTech Ltd.

CLAUSE 2.1 (Pricing): Tiered volume pricing applies. Orders above 300 units 
qualify for a 5% discount automatically applied at invoicing.

CLAUSE 4.2 (Delivery): Guaranteed delivery within agreed schedule. Vendor 
maintains buffer stock and provides real-time shipment tracking. Delays 
beyond 48 hours trigger automatic 15% invoice credit to buyer.

CLAUSE 7.1 (Warranty): Full comprehensive warranty covering all defects, 
including wear under normal operating conditions. 24-month coverage from 
delivery date. Onsite replacement guaranteed within 72 hours of fault report.

CLAUSE 9.3 (Component Integrity): All units ship with serial verification. 
No substitutions permitted without written buyer approval. Components sourced 
exclusively from certified Tier-1 manufacturers.

CLAUSE 11.1 (Dispute Resolution): Disputes resolved in buyer's jurisdiction. 
Vendor provides dedicated account manager for escalation resolution within 24h.
        """.strip()
    },
    {
        "id": "C",
        "name": "MidRange Systems",
        "price_per_unit": 190,
        "delivery_days": 7,
        "warranty_months": 12,
        "flexibility": 0.50,
        "true_risk": 0.42,
        "contract_text": """
VENDOR AGREEMENT — MidRange Systems

CLAUSE 2.1 (Pricing): Price subject to quarterly review. Buyer locked to 
quoted price for 30 days post-agreement only.

CLAUSE 4.2 (Delivery): Standard delivery 7 business days. Vendor not liable 
for delays exceeding 3 days caused by customs or force majeure events.

CLAUSE 7.1 (Warranty): 12-month warranty on defects. Warranty claims must be 
submitted within 14 days of fault discovery. Processing time up to 30 days.

CLAUSE 9.3 (Component Source): Units primarily sourced from certified partners. 
In rare cases, Tier-2 suppliers may be used with equivalent spec compliance. 
Buyer will be notified post-shipment in such cases.

CLAUSE 11.1 (Dispute Resolution): Disputes handled via mediation. Either party 
may escalate to arbitration after 60-day mediation period.
        """.strip()
    },
    {
        "id": "D",
        "name": "BudgetGear Inc.",
        "price_per_unit": 175,
        "delivery_days": 9,
        "warranty_months": 18,
        "flexibility": 0.30,
        "true_risk": 0.68,
        "contract_text": """
VENDOR AGREEMENT — BudgetGear Inc.

CLAUSE 2.1 (Pricing): Quoted price valid. Bulk surcharge may apply for 
orders requiring expedited processing or special packaging.

CLAUSE 4.2 (Delivery): Estimated delivery 9 days. Vendor not responsible 
for delays beyond 5 days. Buyer assumes risk for time-critical deployments.

CLAUSE 7.1 (Warranty): 18-month warranty on parts only. Labour and 
replacement shipping costs borne by buyer. Warranty void if units 
operated outside manufacturer's recommended thermal thresholds.

CLAUSE 9.3 (Refurbishment Disclosure): A portion of inventory (up to 30%) 
may consist of certified-refurbished units unless buyer explicitly opts 
for new-only at checkout. Refurbished units carry 6-month warranty only.

CLAUSE 11.1 (Liability Cap): Vendor total liability capped at invoice value. 
No consequential damages claimable regardless of circumstance.
        """.strip()
    },
    {
        "id": "E",
        "name": "FlexSource Partners",
        "price_per_unit": 205,
        "delivery_days": 6,
        "warranty_months": 12,
        "flexibility": 0.80,
        "true_risk": 0.18,
        "contract_text": """
VENDOR AGREEMENT — FlexSource Partners

CLAUSE 2.1 (Pricing): Highly negotiable. Volume discounts available from 
100 units. Long-term partnerships eligible for preferred pricing tiers.

CLAUSE 4.2 (Delivery): 6-day standard delivery with optional 3-day express 
at 8% surcharge. Buyer portal provides live order tracking.

CLAUSE 7.1 (Warranty): 12-month warranty, fully transferable. Replacement 
units dispatched within 24 hours of approved claim. No shipping cost to buyer.

CLAUSE 9.3 (Supply Chain): All components sourced from verified Tier-1 
manufacturers. Full chain-of-custody documentation available on request. 
Zero substitution policy without explicit written buyer consent.

CLAUSE 11.1 (Dispute Resolution): Buyer-friendly neutral arbitration. 
Dedicated support line available 24/7 during contract period.
        """.strip()
    }
]

DYNAMIC_EVENTS = [
    {
        "id": "budget_cut",
        "description": "Finance team reduced procurement budget by 15%.",
        "effect": lambda s: s.update({"budget": int(s["budget"] * 0.85)})
    },
    {
        "id": "deadline_reduced",
        "description": "Project timeline moved up. Delivery needed in 5 days.",
        "effect": lambda s: s.update({"deadline_days": 5})
    },
    {
        "id": "vendor_delay_warning",
        "description": "Industry report: QuickSupply Co. had 3 delayed shipments last month.",
        "effect": lambda s: None   # informational only — changes inference, not state
    },
    {
        "id": "quantity_increase",
        "description": "New request: quantity increased from 500 to 650 units.",
        "effect": lambda s: s["requirements"].update({"quantity": 650})
    }
]


# ── ENVIRONMENT CLASS ─────────────────────────────────────────────────────────

class ProcurementEnv:
    """
    OpenEnv-compatible procurement negotiation environment.
    Implements: reset(), step(), state()
    """

    def __init__(self, task_level: str = "medium", seed: int = 42):
        assert task_level in ("easy", "medium", "hard"), \
            "task_level must be 'easy', 'medium', or 'hard'"
        self.task_level = task_level
        self.seed = seed
        random.seed(seed)
        self._state = {}
        self.reset()

    # ── OPENENV API ───────────────────────────────────────────────────────────

    def reset(self) -> dict:
        """Reset environment to initial state. Returns initial observation."""
        random.seed(self.seed)

        vendors = self._build_vendors_for_task()

        self._state = {
            "task_level": self.task_level,
            "budget": 100_000,
            "deadline_days": 10,
            "requirements": {
                "item": "GPU",
                "quantity": 500,
                "min_warranty_months": 12
            },
            "vendors": vendors,            # public info only — no true_risk
            "selected_vendor": None,
            "final_price": None,
            "current_round": 1,
            "max_rounds": 3,
            "history": [],
            "events_triggered": [],
            "done": False,
            "outcome": None               # set on terminal step
        }

        if self.task_level == "hard":
            self._maybe_trigger_event()

        return self._public_state()

    def step(self, action: dict) -> dict:
        """
        Process one agent action.

        Valid action types:
          SELECT_VENDOR   : {"type": "SELECT_VENDOR",  "vendor_id": "B"}
          COUNTER_OFFER   : {"type": "COUNTER_OFFER",  "vendor_id": "E", "new_price": 195}
          ACCEPT_DEAL     : {"type": "ACCEPT_DEAL",    "vendor_id": "E"}
          REJECT_VENDOR   : {"type": "REJECT_VENDOR",  "vendor_id": "A"}

        Returns: {"state": ..., "reward": float, "done": bool, "info": str}
        """
        if self._state["done"]:
            return {"state": self._public_state(), "reward": 0.0,
                    "done": True, "info": "Episode already finished."}

        action_type = action.get("type", "").upper()
        vendor_id   = action.get("vendor_id")
        reward      = 0.0
        info        = ""

        # ── record action in history
        self._state["history"].append({
            "round": self._state["current_round"],
            "action": action
        })

        if action_type == "SELECT_VENDOR":
            reward, info = self._handle_select(vendor_id)

        elif action_type == "COUNTER_OFFER":
            new_price = action.get("new_price")
            reward, info = self._handle_counter(vendor_id, new_price)

        elif action_type == "ACCEPT_DEAL":
            reward, info = self._handle_accept(vendor_id)

        elif action_type == "REJECT_VENDOR":
            reward, info = self._handle_reject(vendor_id)

        else:
            info = f"Unknown action type: {action_type}"
            reward = -0.05

        # ── advance round / trigger events
        self._state["current_round"] += 1
        if self._state["current_round"] > self._state["max_rounds"] \
                and not self._state["done"]:
            self._state["done"] = True
            self._state["outcome"] = "timeout"
            reward += -0.2
            info += " | Episode ended: max rounds reached without final decision."

        if self.task_level == "hard" and not self._state["done"]:
            self._maybe_trigger_event()

        return {
            "state":  self._public_state(),
            "reward": round(reward, 4),
            "done":   self._state["done"],
            "info":   info
        }

    def state(self) -> dict:
        """Return current public observation (no hidden fields)."""
        return self._public_state()

    # ── ACTION HANDLERS ───────────────────────────────────────────────────────

    def _handle_select(self, vendor_id: str):
        vendor = self._get_vendor(vendor_id)
        if not vendor:
            return -0.1, f"Vendor {vendor_id} not found."
        self._state["selected_vendor"] = vendor_id
        return 0.0, f"Vendor {vendor_id} selected for evaluation."

    def _handle_counter(self, vendor_id: str, new_price: Optional[float]):
        vendor = self._get_vendor(vendor_id)
        if not vendor:
            return -0.1, f"Vendor {vendor_id} not found."
        if new_price is None:
            return -0.05, "COUNTER_OFFER requires new_price field."

        original      = vendor["price_per_unit"]
        flexibility   = self._get_hidden(vendor_id, "flexibility")
        floor_price   = original * (1 - flexibility)

        if new_price >= floor_price:
            # Vendor accepts counter — update public price
            vendor["price_per_unit"] = round(new_price, 2)
            info = (f"Vendor {vendor_id} accepted counter offer: "
                    f"${original} → ${new_price:.0f}/unit.")
            reward = 0.05   # small positive for successful negotiation
        else:
            info = (f"Vendor {vendor_id} rejected counter offer of "
                    f"${new_price:.0f}. Floor is ~${floor_price:.0f}.")
            reward = -0.02

        return reward, info

    def _handle_accept(self, vendor_id: str):
        vendor = self._get_vendor(vendor_id)
        if not vendor:
            return -0.1, f"Vendor {vendor_id} not found."

        qty         = self._state["requirements"]["quantity"]
        total_cost  = vendor["price_per_unit"] * qty
        budget      = self._state["budget"]
        deadline    = self._state["deadline_days"]
        min_warranty= self._state["requirements"]["min_warranty_months"]
        true_risk   = self._get_hidden(vendor_id, "true_risk")

        self._state["selected_vendor"] = vendor_id
        self._state["final_price"]     = total_cost
        self._state["done"]            = True
        self._state["outcome"]         = "accepted"

        reward = self._compute_reward(
            total_cost, budget, true_risk,
            vendor["delivery_days"], deadline,
            vendor["warranty_months"], min_warranty,
            self._state["current_round"], self._state["max_rounds"]
        )

        info = (
            f"Deal accepted with {vendor['name']}. "
            f"Total cost: ${total_cost:,.0f} / Budget: ${budget:,.0f}. "
            f"Delivery: {vendor['delivery_days']}d / Deadline: {deadline}d. "
            f"Warranty: {vendor['warranty_months']}mo."
        )
        return reward, info

    def _handle_reject(self, vendor_id: str):
        vendor = self._get_vendor(vendor_id)
        if not vendor:
            return -0.1, f"Vendor {vendor_id} not found."

        true_risk = self._get_hidden(vendor_id, "true_risk")
        # Correctly rejecting a risky vendor is smart → small reward
        reward = 0.08 if true_risk > 0.6 else -0.05
        info   = f"Vendor {vendor_id} rejected."

        # Remove from available pool
        self._state["vendors"] = [
            v for v in self._state["vendors"] if v["id"] != vendor_id
        ]
        return reward, info

    # ── REWARD FUNCTION ───────────────────────────────────────────────────────

    def _compute_reward(self, total_cost, budget, true_risk,
                        delivery, deadline, warranty, min_warranty,
                        rounds_used, max_rounds) -> float:
        """
        Multi-factor reward. Each component is 0.0–1.0, weighted sum.

        weights: cost(0.35) + reliability(0.30) + time(0.15)
                 + warranty(0.10) + efficiency(0.10)
        """
        # 1. Cost score — how much budget remains (higher = better)
        if total_cost > budget:
            cost_score = 0.0   # over budget = zero cost score
        else:
            cost_score = 1.0 - (total_cost / budget)

        # 2. Reliability — inverse of true hidden risk
        reliability_score = 1.0 - true_risk

        # 3. Time efficiency — delivery vs deadline
        if delivery > deadline:
            time_score = 0.0   # misses deadline entirely
        else:
            time_score = 1.0 - (delivery / deadline)

        # 4. Warranty compliance
        warranty_score = min(1.0, warranty / min_warranty) if min_warranty > 0 else 1.0

        # 5. Negotiation efficiency — fewer rounds used = more efficient
        efficiency_score = 1.0 - ((rounds_used - 1) / max(max_rounds - 1, 1))

        reward = (
            0.35 * cost_score +
            0.30 * reliability_score +
            0.15 * time_score +
            0.10 * warranty_score +
            0.10 * efficiency_score
        )
        return round(reward, 4)

    # ── TASK CONFIGURATION ────────────────────────────────────────────────────

    def _build_vendors_for_task(self) -> list:
        """
        Easy   → 2 vendors, clear winner, no traps
        Medium → 3 vendors, price vs reliability trade-off
        Hard   → 5 vendors, hidden traps in contracts, dynamic events
        """
        catalogue = copy.deepcopy(VENDOR_CATALOGUE)

        # Strip hidden fields before returning to agent
        def public(v):
            return {k: val for k, val in v.items()
                    if k not in ("true_risk", "flexibility")}

        if self.task_level == "easy":
            return [public(catalogue[1]), public(catalogue[4])]  # B + E
        elif self.task_level == "medium":
            return [public(catalogue[0]), public(catalogue[2]), public(catalogue[4])]
        else:  # hard
            return [public(v) for v in catalogue]  # all 5

    def _maybe_trigger_event(self):
        """20% chance per round of a dynamic event (hard mode only)."""
        if random.random() < 0.20:
            event = random.choice(DYNAMIC_EVENTS)
            if event["id"] not in self._state["events_triggered"]:
                event["effect"](self._state)
                self._state["events_triggered"].append({
                    "event_id": event["id"],
                    "description": event["description"],
                    "round": self._state["current_round"]
                })

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _get_vendor(self, vendor_id: str) -> Optional[dict]:
        for v in self._state["vendors"]:
            if v["id"] == vendor_id:
                return v
        return None

    def _get_hidden(self, vendor_id: str, field: str):
        """Access hidden fields from full catalogue (never sent to agent)."""
        for v in VENDOR_CATALOGUE:
            if v["id"] == vendor_id:
                return v[field]
        return None

    def _public_state(self) -> dict:
        """Return state safe to send to agent — no hidden fields."""
        s = copy.deepcopy(self._state)
        return s