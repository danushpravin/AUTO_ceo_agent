# RECOMMENDATION LAYER - Flag and Signal driven

## Purpose
Transforms diagnostic flags and growth signals into clear, executive-safe actions.

## What it does
Converts analytical findings into concrete business decisions with:
- explicit trigger
- action
- expected impact
- risk trade-off

## Why this exists
Most analytics stop at insight.
This layer closes the loop by turning insight into decisions.

---

## Inputs

### flags
List of structured risk signals produced by interpretation layers.

Each flag represents a verified business issue (e.g. inefficient marketing, supply risk, revenue concentration).

### growth_signal 
Company-level growth quality signal used to modulate aggresiveness of recommendations.

---

## Outputs

List of recommendation objects, each containing:

- **trigger_flag** - Which business risk caused the action
- **scope** - Channel / product / portfolio / company
- **entity** - Specific object affected (if applicable)
- **recommendation** - Executable business action
- **expected_impact** - Strategic benefit
- **risk_tradeoff** - Known downside
- **confidence** - Reliability of the action

---

## Business Logic

### 1. Marketing Efficiency Actions
Triggered when paid growth destroys value.

Examples:
- Pause or reduce inefficent spend.
- Audit acquisition cost and pricing.
- Investigate attribution leakage.

Goal: **Stop capital burn before scaling.**

---

### 2. Product Portfolio Actions
Triggered when revenue is fragile or fake.

Examples:
- Reduce dependency on top SKUs.
- Reassess unprofitable products.
- Diversify demand sources.

Goal: **Improve long-term revenue resilience.**

---

### 3. Inventory Actions
Triggered when supply constrains revenue.

Examples:
- Increase safety stock.
- Prioritize high-impact SKUs.
- Monitor low-stock volatility.

Goal: **Recover revenue lost to operations.**

---

### 4. Channel Dependency Actions
Triggered when business relies on too few channels.

Examples:
- Expand to new channels.
- Reduce single-point-of-failure risk.
- Validate true incremental performance.

Goal: **Reduce systemic business risk.**

---

### 5. Growth Quality Overlay
Triggered when overall growth is unhealthy.

Example:
- Delay aggresive scaling until unit economics stabilize.

Goal: **Prevent compounding losses.**

---

## Design Principles

### Deterministic
No machine learning. Same inputs always produce same actions.

### Explainable
Every recommendation maps directly to a specefic business risk.

### Executive-safe
Actions are phrased in operational and strategic language.

### Risk-aware
Every action includes an explicit downside.

---

## Strategic Role in System

This layer acts as the **decision interface** between analytics and leadership.

Interpretation answers:
> *What is wrong?*

Recommendation answers:
> *What should we do about it?*

This is the final step that turns data into business control.