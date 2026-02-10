# Analytics Documentation

## Sales Analytics ('sales.py')

### Purpose
This module contains **pure sales-related analytical functions**.
It performs aggregation and ranking on sales data and returns structured outputs for further reasoning or reporting.

- No business logic
- No decision-making
- No side effects
Only **data aggregation**

---

### Dependencies
- 'pandas' for grouping and aggregation
- 'DataContext' for accessing in-memory sales data

---

### Data Source
All functions operate on:

- 'ctx.sales'

Required columns:
- 'date'
- 'revenue'
- 'region'
- 'product'
- 'channel'

---

## Functions

### 'revenue_by_month(ctx: DataContext)'

**Description**
Aggregates total revenue by calendar month.

**Logic**
- Creates a month column from 'date'
- Groups by month
- Sumns revenue

**Returns**
- DataFrame with:
  - 'month'
  - 'revenue'

**Why it exits**
- Enables time-based revenue trend analysis.

---

### 'sales_by_region(ctx: DataContext)'

**Description**
COmputes total revenue per region.

**Logic**
- Groups sales by 'region'
- Sums revenue

**Returns**
- DataFrame with:
  - 'region'
  - 'revenue'

**Why it exists**
- Identifies geographically strong and weak markets.

---

### 'sales_by_product(ctx: DataContext)'

**Description**
Computes total revenue per product.

**Logic**
- Groups sales by 'product'
- Sums revenue

**Returns**
- DataFrame with:
  - 'product'
  - 'revenue'

**Why it exists**
- Highlights top and underperforming products.

---

### 'sales_by_channel(ctx: DataContext)'

**Description**
Computes total revenue per sales channel.

**Logic**
- Groups sales by 'channel'
- Sums revenue

**Returns**
- DataFrame with:
  - 'channel'
  - 'revenue'

**Why it exists**
- Measures channel-level contributions to revenue.

---

### 'top_regions(ctx: DataContext, n=3)'

**Description**
Returns the top 'n' regions by revenue.

**Logic**
- Uses 'sales_by_region'
- Sorts by revenue (descending)
- Selects top 'n'

**Returns**
- DataFrame of top-performing regions

**Why it exists**
- Provides reusable ranking logic without duplication.

---

### 'top_products(ctx: DataContext, n=3)'

**Description**
Returns the top 'n' products by revenue.

**Logic**
- Uses 'sales_by_product'
- Sorts by revenue (descending)
- Selects top 'n'

**Returns**
- DataFrame of top-performing products

**Why it exits**
- Enables consistent product ranking across the system.

---

### Design Principles
- Stateless functions
- Read-only access to data
- Composable and reusable
- Safe for agent-driven execution

## Marketing Analytics ('marketing.py')

### Purpose
This module contains **pure marketing performance analytics**.
It focuses on **spend efficiency and revenue attribution** across marketing channels.

- No decision-making
- No thresholds or judgement
- No side effects
Only **metric computation**

---

### Data Source
All fucntions operate on:

- 'ctx.marketing'

Required columns:
- 'date'
- 'channel'
- 'spend'
- 'revenue'

---

## Functions

### 'roas_by_channel(ctx: DataContext)'

**Description**
Computes the **average Return on Ad Spend (ROAS)** for each marketing channel.

ROAS is a core efficiency metric used downstream to detect:
- Inefficient spend
- Channels driving fake or low-quality growth
- Disproportionate revenue contribution

**Logic**
- Creates a copy of the marketing dataset
- Computes ROAS per row as:
  - 'revenue / spend'
- Replaces zero spend values to avoid division errors
- Groups by 'channel'
- Computes **mean ROAS** per channel

**Returns**
- Pandas Series with:
  - index: 'channel'
  - values: average ROAS

**Why it exists**
- Seperates raw efficiency measurement from interpretation logic.
- Enables consistent efficiency signals across the system.

---

### 'spend_over_time(ctx: DataContext)'

**Description**
Aggregates total marketing spend over time on a **monthly basis**.

Used to analyze:
- Spend acceleration or contraction
- Correlation between spend and revenue trends
- Burn rate behavior

**Logic**
- Creates a copy of the marketing dataset
- Extracts month from 'date'
- Converts month to string for safe downstream usage
- Groups by month
- Sums spend

**Returns**
- Pandas Series with:
  - index: 'month'
  - values: total spend

**Why it exists**
- Provides time-series spend visibility without embedding assumptions.
- Supports later efficiency and risk interpretation.

---

### Design Notes
- Functions return **raw metrics only**, not conclusions.
- Period-to-string conversion avoids serializarion and agent issues.
- Outputs are intentionally simple to remain composable.

## Inventory Analytics ('inventory.py')

### Purpose
This module contains **pure inventory and supply-chain analytics**.
It exposes metrics related to **stock availability and inventory stability**.

- No forecasting
- No decision logic
- No corrective actions
Only **inventory signal extraction**

---

### Dependencies
- 'pandas' for filtering and aggregation
- 'DataContext' for accessing in-memory inventory data

---

### Data Source
All functions operate on:

- 'ctx.inventory'

Required columns:
- 'date'
- 'product'
- 'closing_stock'
- 'stockout_flag'

---

## Functions

### 'stockouts_by_product(ctx: DataContext)'

**Description**
Counts the number of **distinct days** each product experienced a stockout.
This metric captures **supply fragility**, not volume lost.

**Logic**
- Creates a copy of inventory data
- Filters rows where 'stockout_flag' == "Yes"
- Groups by 'product'
- Counts unique stockout dates
- Renames output column to 'stockout_days'

**Returns**
- DataFrame with:
  - 'product'
  - 'stockout_days'

**Why it exists**
- Quantifies operational risk without estimating lost revenue.
- Feeds downstream inventory-health and risk interpretation.

---

### 'avg_closing_stock(ctx: DataContext)'

**Description**
Computes the **average closing stock level** per product.

Used to assess:
- Inventory buffer adequacy
- Overstocking vs understocking risk

**Logic**
- Creates a copy of inventory data
- Groups by 'product'
- Computes mean of 'closing_stock'
- Renames output column to 'avg_closing_stock'

**Returns**
- DataFrame with:
  - 'product'
  - 'avg_closing_stock'

**Why it exists**
- Provides a stable inventory baseline.
- Enables comparison against demand and stock frequency.

---

### Design Notes
- Stockout analysis is **event-based**, not quantity-based.
- No assumptions are made about demand recovery or lost sales.
- Functions remain fully composable with sales and revenue analytics.

## Profit and Unit Economics Analytics ('profit.py')

### Purpose 
This module contains **pure profitability and unit economics analytics**.
It focuses on extracting **true financial performance signals** by combining revenue with cost structures.

- No forecasting
- No growth assumptions
- No business decisions
Only **profit computation**

---

### Data Source
All functions operate on:

- 'ctx.sales_enriched'
- 'ctx.marketing'
- 'ctx.unit'

Required columns:

**'ctx.sales_enriched'**
- 'product'
- 'region'
- 'channel'
- 'revenue'
- 'units_sold'
- 'unit_cost'

**'ctx.marketing'**
- 'channel'
- 'spend'

**'ctx.unit'**
- 'product'
- 'selling_price'
- 'cogs'
- 'packaging_cost'
- 'logistics_cost'

---

## Functions

### 'profit_by_product(ctx: DataContext)'

**Description**
Computes **true product-level profit**, excluding marketing spend.
Represents core **unit economics**, not growth economics.

**Logic**
- Groups sales by 'product'
- Aggregates:
  - Total revenue
  - Total units sold
  - Total product cost
- Computes:
  - 'profit = revenue - total_cost'
  - 'profit_margin_pct = profit / revenue * 100'

**Returns**
- DataFrame with:
  - 'product'
  - 'revenue'
  - 'units'
  - 'total_cost'
  - 'profit'
  - 'profit_margin_pct'

**Why it exists**
- Seperates popular products from **profitable products**.
- Exposes loss-making SKUs hidden behind revenue.

---

### 'true_profit_by_channel(ctx: DataContext)'

**Description**
Computes **net profit by marketing channel**, including:
- Product costs
- Marketing spend

This represents **real business profit**, not contribution margin.

**Logic**
- Computes product cost per channel:
  - 'unit_cost * units_sold'
- Aggregates:
  - Revenue by channel
  - Product cost by channel
  - Marketing spend by channel
- Merges all three
- Computes:
  - 'net_proft = revenue - product_cost - spend'
  - 'profit_margin_pct'

**Returns**
- DataFrame with:
 - 'channel'
 - 'revenue'
 - 'product_cost'
 - 'spend'
 - 'net_profit'
 - 'profit_margin_pct'

**Why it exists**
- Detects channels that look efficient but **destroys profit**.
- Prevents scaling unprofitable acquisition loops.

---

### 'true_profit_by_region(ctx: DataContext)'

**Description**
Computes **net profit by region**, excluding marketing spend.
Focuses on operational and geographic efficiency.

**Logic**
- Groups by 'region'
- Aggregates revenue and total product cost
- Computes:
  - 'net_profit'
  - 'profit_margin_pct'

**Returns**
- DataFrame with:
  - 'region'
  - 'revenue'
  - 'total_cost'
  - 'net_profit'
  - 'profit_margin_pct'

**Why it exists**
- Surfaces regions that generate revenue but no margin.
- Highlights cost-to-serve problems.

---

### 'loss_making_products(ctx: DataContext)'

**Description**
Identifies **products with negative profit**, ranked by revenue.

These are the most dangerous SKUs:
High volume, negative economics.

**Logic**
- Calls 'profit_by_product'
- Filters rows where 'profit < 0'
- Sorts by revenue descending

**Returns**
- DataFrame of only loss-making products

**Why it exists**
- Forces visbility on silent financial leaks.
- Enables hard prodcut portfolio decisions.

---

### 'cost_components_by_product(ctx: DataContext)

**Description**
Returns **raw cost breakdown per product**.
No aggregation. No interpretation.

**Returns**
- DataFrame with:
  - 'product'
  - 'selling_price'
  - 'cogs'
  - 'packaging_cost'
  - 'logistics_cost'

**Why it exists**
- Explains *why* products are unprofitable.
- Feeds downstream cost diagnostics.

---

### Design Notes
- All profit calculations are deterministic
- No estimates or heuristics
- Margins are derived, never assumed
- Marketing is inlcuded only where explicitly stated.

---

## Executive Pulse Analytics ('executive_pulse.py')

### Purpose
This module contains **executive-level daily metrics**.
It provides **baseline comparisons and recent trends** for revenue and operational performance.

- No decisions made
- No thresholds applied
- Only recent and delta metrics

---

### Data Source
All functions operate on:

- 'ctx.daily'

Required columns:
- 'date'
- 'revenue'
- 'units'

---

## Functions

### '_latest_date(ctx: DataContext)'

**Description**
Internal helper to find the most recent date in 'ctx.daily'.

**Returns**
- Latest datetime, or None if dataset is empty

---

### 'revenue_recent_performance(ctx: DataContext, n=7)'

**Description**
Computes **recent revenue series** and **today vs baseline delta**.

**Logic**
- Finds latest date
- Creates n-day window ending on latest date
- Computes baseline average excluding today
- Computes delta percentage for today vs baseline

**Returns**
- Dictionary with:
  - 'window_days'
  - 'daily_series' (date, revenue, units)
  - 'baseline_avg'
  - 'today_revenue'
  - 'delta_pct'

**Why it exists**
- Provides executive-level snapshot of revenue trend
- Agent-safe, stateless primitve for decision support.

---

### 'daily_delta(ctx: DataContext)'

**Description**
Convenience wrapper for **today vs yesterday revenue delta**.

**Logic**
- Calls 'revenue_recent_performance' with n=2
- Extracts yesterday and today revenue
- Computes delta percentage

**Returns**
- Dictionary with:
  - 'date'
  - 'revenue_today'
  - 'revenue_yesterday'
  - 'delta_pct'

**Why it exists**
- Quick, executive-friendly daily signal
- Simplifies downstream alerting or reporting

---

### Design Notes
- Stateless, read-only metrics
- Handles empty datasets gracefully
- Designed for **agent-driven executive monitoring**

---