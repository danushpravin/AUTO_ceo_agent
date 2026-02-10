# Interpretation Documentation

## Interpretation Layer - Growth Quality ('interpret.py')

### Purpose
This component evaluates **whether recent revenue growth is real or artificial**.

It answers the executive question:
> *"Are we growing in a healthy way, or just inflating revenue with loss-making activity?"*

This is one of the **most critical layers** in the agent, because:
- It converts raw metrics into **business meaning**
- It produces **explicit signals** (POSITIVE / NEGATIVE / NEUTRAL)
- It is **fully deterministic and explainable**

No machine learning.
No probabilities.
Only rule-based financial reasoning.

---

### Inputs

#### 'recent_perf' (dict)
Output of:
- 'revenue_recent_performance()'
or
- 'daily_delta()'

#### 'profit_by_product_df' (DataFrame)
Output of:
- 'profit_by_product()'

Required columns:
- 'product'
- 'revenue'
- 'profit'

---

### Function

#### 'interpret_growth_quality(recent_perf, profit_by_product_df)'

---

### Description
Determines whether **recent revenue growth is financially healthy**, based on:

- Direction of revenue change
- Total business profitability
- Share of revenue coming from loss-making products

Returns a structured **business signal** with:
- Clear verdict
- Human-readable reason
- Supporting evidence
- Confidence level

---

### Logic Flow (Step-by-Step)

#### 1. Data Validation Gate

```python
if recent_perf is None or profit_by_product_df.empty:
```
If either:
- No recent revenue data
- No profit data

-> Immediately returns:
   - signal = NEUTRAL
   - confidence = LOW
This prevents false conclusions from partial data.

#### 2. Extract Core Metrics

##### Revenue change
```python
revenue_delta = recent_perf.get("delta_pct")
```

##### Total business profit
```python
total_profit = profit_by_product_df["profit"].sum()
```

##### Loss-making products
```python
loss_products = profit_by_product_df[
    profit_by_product_df["profit"] < 0
]
```

##### Revenue share from loss-makers
```python
loss_revenue_share = (
    loss_products["revenue"].sum()
    / profit_by_product_df["revenue"].sum()
)
```
This is the key economic indicator:
-> *"How much of our revenue is structurally unprofitable?"*

#### 3. Decision Tree

##### Case 1 - Revenue is Growing

```python
if revenue_delta > 0:
```

**1A - Growing but total profit <= 0**

```python
if total_profit <= 0:
```
- Signal: NEGATIVE
- Meaning: Revenue is increasing, but the business is still losing money.

This is classic fake growth.

**1B - Growing but driven by loss-makers**

```python
if loss_revenue_share > 0.3:
```
If more than 30% of revenue comes from unprofitable products:

- Signal: NEGATIVE
- Meaning: Growth is structurally unhealthy.

You are scaling losses.

**1C - Growing and profitable**

If:
 - Revenue is ip
 - Total profit is positive
 - Loss-makers < 30% of revenue

- Signal: POSITIVE
- Meaning: This is real growth backed by healthy unit economics.

##### Case 2 - No meaningful revenue growth

If:
 - Revenue is flat or declining

- Signal: NEUTRAL
- Meaning: No strong growth trend to evaluate.

---

### Output Schema

Every execution returns:
```json
{
    "signal": "POSITIVE | NEGATIVE | NEUTRAL",
    "reason": "Human readable explanation",
    "evidence": {
        "revenue_delta_pct": float,
        "total_profit": float,
        "loss_revenue_share": float,
        "loss_products": [list of products]
    },
    "confidence": "LOW | MEDIUM | HIGH"
}
```
### Why it exists

This function prevents one of the most dangerous executive mistakes:
- *"Confusing revenue growth with business success."*

It ensures the agent:
- Never celebrates growth that destroys value
- Detects loss-driven scaling early
- Forces profitability into every growth conversion

---

### Design Principles

- Fully deterministic
- No heuristics beyond explicit thresholds
- No black-box logic
- Every decision is traceable
- Business-rational, not statiscally optimized

This is not an ML model.
This is financial reasoning encoded as code.

---

## INTERPRETATION LAYER - Marketing Efficiency

### Purpose
This module evaluates **how efficient marketing spend truly is**, not just in terms of ROAS, but in terms of **real business profit and sustainability**.

It answers:
- Are we buying profitable growth?
- Which channels are leaking money?
- Is spend increasing faster than returns?

This layer is:
- Deterministic
- Rule-based
- Fully explainable
- Free of ML or heuristics

Only **signal extraction and interpretation**.

---

### Data Sources

The function operates on:

#### 'ctx.marketing'
Required columns:
- 'date'
- 'channel'
- 'spend'
- 'revenue'
- 'conversions'
- 'clicks'
- 'impressions'

#### 'ctx.sales_enriched'
Required columns:
- 'date'
- 'channel'
- 'revenue'
- 'units_sold'
- 'unit_cost'

---

### Functions

#### '_date_window(df, date_col, end, days)'

**Description**
Utility function that extracts an inclusive rolling window from a dataframe.

**Logic**
- Computes start date = 'end - days'
- Filters rows where:
  - 'date > start'
  - 'date <= end'

**Why it exists**
- Centralizes all time window logic.
- Guarantees consistent lookback behaviour across interpretations.

---

#### 'marketing_efficiency(ctx, lookback_days=30, min_roas=2.0, min_profit_margin_pct=0.0, spend_spike_pct=25.0)'

### Description
Evaluates **true marketing efficiency** by combining:

- Marketing performance (ROAS, CAC)
- Sales reality (unit costs, profit)
- Spend trends over time

This is the **core paid-growth interpretation primitive**.

---

### Output Structure

```python
{
    "as_of": "YYYY-MM-DD",
    "window_days": int,
    "channel_table": DataFrame,
    "flags": [...],
    "interpretation": [...]
}
```
---

### Core Logic Flow

#### 1. Time Window Extraction
- Uses *_latest_date(ctx)* as reference.
- Extracts last lookback_days from:
    - ctx.marketing
    - ctx.sales_enriched

If marketing data is missing:
    - Returns *NO_MARKETING_DATA* flag.

If sales data is missing:
    - Returns *NO_SALES_DATA_WINDOW* flag.
    - Skips profit computation.

#### 2. Marketing Rollup
Aggregates by channel:
 - Total spend
 - Marketing-attributed revenue
 - Conversions
 - Clicks
 - Impressions

Computes:
 - ROAS = revenue / spend
 - CAC = spend / conversions

This captures **platform-side efficiency**.

#### 3. True Profit by Channel

From *sales_enriched*:

Aggregates:
 - Sales revenue
 - Units sold
 - Product cost
  - unit_cost * units_sold (Upgrade: will be made more effcient by reusing analytics primitve)

Then computes:

```python
net_profit = sales_revenue - product_cost - marketing_spend
net_profit_margin_pct = net_profit / sales_revenue
```

This captures **real business economics**, not vanity metrics.

#### 4. Spend vs Return Trend Check

Splits window into halves:
 - First half
 - Last half

Computes per channel:
 - Spend change %
 - Revenue change %

Used to detect:
 - Spend acceleration
 - Diminishing Returns
 - Targeting fatigue

---

### Decision Rules (Flags)

All thresholds are fixed, conservative defaults.
They represent **basic business safety limits**, not optimized values.

The intent is to:
 - Catch problems early
 - Avoid complex tuning
 - Keep signals easy to explain to non-technical users.

#### LOW_ROAS

Triggered if:
```python
roas < min_roas
```

**Default** 
min_roas = 2.0

**Reason**

A ROAS below 2.0 usually means marketing cannot cover:
 - Product cost
 - Operating expenses
 - Overhead

It indicates **inefficient spend** and is a common minimum benchamrk in most businesses.

#### NEGATIVE_OR_LOW_NET_MARGIN

Triggered if:
```python
net_profit_margin_pct < min_profit_margin_pct
```

**Default**
min_profit_margin_pct = 0.0

**Reason**

0% is the economic break-even point. 
Anything below means the business is **losing money per channel**.

This catches cases where revenue looks good, but the company is **structurally unprofitable**.

#### SPEND_SPIKE_WEAK_RETURN

Triggered if:
```python
spend_change_pct >= spend_spike_pct
revenue_change_pct < spend_change_pct
```

**Default**
spend_spike_pct = 25.0

**Reason**

A 25% spend increase is a material budget change.
If revenue does not grow at a similar rate, it signals:
 - Diminishing returns
 - Audience Saturation
 - Poor targeting

It highlights **scaling inefficiently**.

---

### Design Principles

- Uses real profit, not proxy metrics
- No statiscal model
- No learning
- No magic thresholds
- Fully auditable logic

This layer is intentionally:
- Conservative
- Explainable
- Safe for autonomous execution

### Why this layer matters

This module prevents the most common startup failure:
 - Scaling growth that is fundamentally unprofitable

It ensures the agent never confuses:
 - Activity for progress
 - Revenue for health
 - Spend for strategy

Thresholds are designed to be:
 - Simple
 - Conservative
 - Business-readable

This is growth quality, not growth vanity.

---

## INTERPRETATION LAYER - Product Portfolio Health

### Purpose
This module evaluates **product-level economic health and portfolio risk**.

It answers:
 - Which products are actually healthy?
 - Are we dependent on a small number of products?
 - Are high-revenue products secretly destroying value?
 - Which products are dead weight?

This layer translates **raw product performance** into **strategic portfolio insight**.

---

### Data Source

The function operates on the output of:

#### 'profit_by_product(ctx)'

Required columns:
- 'product'
- 'revenue'
- 'profit'
- 'profit_margin_pct'

---

### Functions

#### 'product_portfolio_health(ctx, min_good_margin_pct=20.0, high_revenue_share_pct=30.0)'

---

### Description
Evaluates the **structural health of the product portfolio** by analyzing:

- Revenue concentration
- Profitability by product
- Revenue share vs margin trade-offs

It produces:
- Product classifications
- Risk flags
- Executive-level interpretation

---

### Output Structure

```python
{
    "as_of": "YYYY-MM-DD",
    "product_table": DataFrame,
    "flags": [...],
    "interpretation": [...]
}
```
### Core Logic Flow

#### 1. Data Validation

If:
- No latest date
- Or total revenue <= 0
  Returns *None*

Prevents meaningless portfolio analysis.

#### 2. Revenue Share Computation

```python
df["revenue_share_pct"] = df["revenue"] / total_revenue * 100
```
Key Question:
*"How dependant is the business on each product?"*

#### 3. Product Classification

Each product is assigned to a category based on:
 - Revenue importance
 - Profit margin quality

Classification Rules and Strategic Meaning

- **STAR** :
  Core growth engine. These products fund the business. They have high revenue and strong margins

- **CASH_COW** :
  Profitable but under-scaled. Strong candidates for investment. They have low revenue but strong margins.

- **FAKE_GROWTH** :
  High visibility, negative compounds. Most dangerous category. They have high revenue share but negative margins.

- **ZOMBIE** :
  Consumes attention with no returns. Often shoud be killed. Very low revenue and weak margins.

- **EXPERIMENTAL** :
  Still uncertain. Needs more data before decisions.

---

### Decision Rules (Flags)

All thresholds are intentionally simple and conservative.

#### 1. PRODUCT_REVENUE_CONCENTRATION
Triggered if:
```python
revenue_share_pct >= high_revenue_share_pct
```
**Default**
high_revenue_sahre_pct = 30.0

**Reason**
If a single product contributes over ~30% of revenue, the business has concentration risk.
This makes the company fragile to:
- Markting shifts
- Product failure
- Competition

#### 2. FAKE_GROWTH_PRODUCT
Triggered if:
```python
category == "FAKE_GROWTH"
```
**Reason**
High-revenue products with negative margins:
- Inflate top-line metrics
- Destroy long-term value
- Mask real business health

This is the most critical failure mode in product portfolios.

---

### Why This Layer Matters
This module prevents a common strategic illusion:
- *"Our best-selling products are our best products."*

It forces the agent to reason in terms of:
- Value creation, not popularity
- Portfolio risk, not individual success
- Structural health, not surface metrics

### Design Principles
- Uses real profit and margins
- No statistical modelling
- No learning or optimization
- Fully explainable logic
- Conservative business thresholds

This layer is safe for:
- Executive reporting
- Automated decision systems
- Investor-facing analytics

---

## INTERPRETATION LAYER - Inventory Health vs Revenue

### Purpose
This module evaluates **how inventory availability directly impacts revenue**.

It answers:
- Are stockouts hurting sales?
- Which products are losing revenue due to supply issues?
- Are we runnig dangerously low even if not fully stocked out?
- How much revenue is potentially being lost?

This layer connects **operational reality (inventory)** to **financial outcomes (revenue)**.

---

### Data Sources

The function operates on:

#### 'ctx.inventory'
Required columns:
- 'date'
- 'product'
- 'lost_demand'
- 'stockout_flag'
- 'closing_stock'
- 'units_dispatched'

#### 'ctx.sales'
Required columns:
- 'date'
- 'product'
- 'revenue'
- 'units_sold'

---

### Function

#### 'inventory_health_vs_revenue(ctx, lookback_days=30, stockout_days_threshold=3, revenue_impact_threshold_pct=15.0, low_stock_threshold=5.0)'

---

### Description
Evaluates **inventory-driven revenue risk** by:

- Tracking stockouts and low-stock pressure
- Comparing revenue on stockout days vs normal days
- Estimating lost units and lost revenue
- Flagging products with structural supply constraints

This is an **operational-to-revenue interpretation layer**.

---

### Output Structure

```python
{
    "as_of": "YYYY-MM-DD",
    "window_days": int,
    "product_table": DataFrame,
    "flags": [...],
    "interpretation": [...]
}
```
---

### Core Logic Flow

#### 1. Time Window Extraction
Uses the latest available date and extracts rolling windows from:
- 'ctx.inventory'
- 'ctx.sales'

If inventory data is missing:
- Returns *"NO_INVENTORY_DATA"*

#### 2. Daily Sales Aggregation
Sales data is grouped by:
```python
(date,product)
```
To compute:
- Daily revenue
- Daily units sold

This produces the **revenue outcomes baseline**.

#### 3. Inventory State Normalization
For each product-day:
- is_stockout  
  Normalized from *stockout_flag*

- is_low_stock:
  Triggered if:
  ```python
  closing_stock <= low_stock_threshold
  ```

This created a binary operational state.

#### 4. Merge inventory with sales
```python
merged = inv_day.merge(sales_day, on=["date", "product"])
```
This aligns:
- Supply conditions 
with
- Financial outcomes

#### 5. Realized Price Estimation
```python
realized_price = total_revenue / total_units_sold
```
Used to convert:
- Lost units to Estimated lost revenue.

This avoids needing list prices.

#### 6. Revenue Impact Computation
For each product:
- Average revenue on stockout days
- Average revenue on normal days

Then:
```python
impact_pct = (normal - stockout) / normal * 100
```
This directly measures finaincial damange from stockouts.

---

### Decision Rules (Flags)

All thresholds are intentionally simple and conservative.

#### "FREQUENT_STOCKOUTS"
Triggered if:
```python
stockout_days >= stockout_days_threshold
```

**Default**
stockout_days_threshold = 3

**Reason**
More than a few stockouts in a month usually means:
- Poor demand forecasting
- Broken replenishment logic
- Structural supply bottlenecks

This is an operational failure with revenue impact.

#### STOCKOUT_REVENUE_IMPACT
Triggered if:
revenue_drop_pct_on_stockout >= revenue_impact_threshold_pct

**Default**
revenue_impact_threshold_pct = 15.0

**Reason**
A revenue drop of ~15% or more is large enough to:
- Materially affect monthly performance
- Indicate real unmet demand

This confirms stockouts are actively destroying revenue.

#### LOW_STOCK_PRESSURE
Triggered if:
```python
low_stock_days >= stockout_days_threshold
AND stockout_days < stockout_days_threshold
```

**Default**
stockout_days_threshold = 3

**Reason**
Even without full stockouts, consistently low inventory:
- Reduces buffer for demand spikes
- Creates future risk
- Signals fragile supply planning

This is a leading indicator, not a lagging one.

---

### Why this layer matters

This module prevents a silent killer of growth:
*"We think demand is low, but actually we just had no stock."*

It forces the agent to reason in terms of:
- Lost opportunity 
- Revenue leakage
- Operational bottlenecks

Not just observed sales.

### Design Principles
- No forecasting models
- No assumptions about pricing
- Uses realized business data
- Fully deterministic
- Directly explainable to ops teams

---

## INTERPRETATION LAYER - Channel Dependency Risk

### Purpose
This module evaluates **business risk caused by over-dependence on specefic channels**.

It answers:
- Are we too reliant on one channel for revenue?
- Are we too reliant on one channel for profit?
- Do some channels look good on the surface but destroy value?
- Do we have enough healthy channels to be resilient?

This is a **strategic risk interpretation layer**, not a performance metric.

---

### Data Source

The function operates on:

#### 'true_profit_by_channel(ctx)'
Required columns:
- 'channel'
- 'revenue'
- 'net_profit'
- 'profit_margin_pct'

This table already reflects:
- Real sales revenue
- Product costs
- Marketing spend

So it represents **true channel economics**.

---

### Function

#### 'channel_dependency_risk(ctx, max_revenue_share_pct=50.0m max_profit_share_pct=70.0, min_healthy_margin_pct=5.0)'

---

### Description
Evaluates whether the business is **structurally fragile** due to:

- Revenue concentration
- Profit concentration
- Channels that look active but lose money
- Lack of diversified healthy channels

---

### Output Structure

```python
{
    "as_of": "YYYY-MM-DD",
    "channel_table": DataFrame,
    "flags": [...],
    "interpretation": [...]
}
```
---

### Core Logic Flow

#### 1. Compute Channel Shares
For each channel:
```python
revenue_share_pct = channel_revenue / total_revenue
profit_share_pct = channel_profit / total_profit
```

These are the two key risk dimensions:
 - Revenue dependency
 - Profit dependency

#### 2. Revenue Concentration Check
Flags channels when:
```python
revenue_share_pct >= max_revenue_share_pct
```

This detects:
- Customer acquisition monoculture
- Platform dependency risk
- Single-channel growth exposure

#### 3. Profit Concentration Check
Flags channels where:
```python
profit_share_pct >= max_profit_share_pct
```
This detects:
- Profit fragility
- Business collapse risk if one channel fails
- Hidden single-point-of-failure

#### 4. ROAS Illusion Detection
Identifies channels where:
```python
revenue > 0 and profit_margin_pct < 0
```
These channels:
- Generate activity
- Look productive
- But destroy real value

This catches vanity performance.

#### 5. Healthy Channel Count Check
Evaluates how many channels meet:
```python
profit_margin_pct >= min_healthy_margin_pct
```
If:
```python
len(healthy_channels) <= 1
```
Then:
- Business lacks diversification
- Operational resilience is low
- Any disruption becomes existential

---

### Decision Rules (Flags)
All thresholds are conservative and intentionally simple.

#### "CHANNEL_REVENUE_CONCENTRATION"
Triggered if:
```python
revenue_share_pct >= max_revenue_share_pct
```
**Default**
max_revenue_share_pct = 50.0

**Reason**
If one channel drives more than half of revenue, the business:
- Is exposed to platform risk
- Has weak acquisition diversification
- Can lose growth overnight from external changes

#### "PROFIT_CONCENTRATION"
Triggered if:
```python
profit_share_pct >= max_profit_share_pct
```
**Default**
max_profit_share_pct = 70.0

**Reason**
If one channel generators most profit, the business:
- Appears healthy
- But is financially fragile
- Has no real redundancy

This is a single point of failure risk.

#### "ROAS_ILLUSIONS"
Triggered if:
```python
profit_margin_pct < 0 and revenue > 0
```
**Reason**
These channels:
- Inflate dashboards
- Generate volume
- But destroy shareholder value

This is the most common executive blind spot.

#### "SINGLE_CHANNEL_DEPENDENCY"
Triggered if:
```python
healthy_channel <= 1
```
**Default**
min_healthy_margin_pct = 5.0

**Reason**
A business with only one healthy channel:
- Cannot absorb shocks.
- Cannot experiment safely
- Is one mistake away from collapse

This is a structural risk, not a performance issue.

---

### Why This Layer Matters
Most companies track:
- Growth
- Revenue
- Marketign metrics

Almost none track:
*"How many independent ways do we actually make money?"*

This module forces the agent to reason in terms of:
- Business resilience
- Failure modes
- Structural fragility

---

### Design Principles
- Uses real profit
- No ML
- No forecasts
- No statistical assumptions
- Pure financial logic

This layer encodes:
Risk management as code.