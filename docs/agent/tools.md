# 'tools.py' Documentation

## File Purpose
'tools.py' acts as the **centralized execution layer** for AUTO. It exposes all analytic, interpretation, and recommendation functions as "tools" that the agent can call. Each tool wraps internal functions from 'analytics/', 'reasoning/', and 'decisions/', ensuring consistent access to the preloaded 'DataContext'.

This is **the only file the agent runtime interacts with directly** for operations. It abstracts the internal function calls and provides a clean API.

---

## Responsibilities 
- Wrap all analytic, interperation (reasoning) and decision functions as callable tools.
- Provide a single point to access all computations.
- Automatically load the 'DataContext' once at startup.
- Aggregate signals and flags for the recommendation engine.

---

## Data Loading
- 'CTX = load_context()' loads all CSV data and enrichments once.
- Every tool uses this same 'CTX' object, ensuring consistency and avoiding repeated computations.

---

## Tool Categories

### 1. Executive Tools
High-level, company-wide metrics:
- 'tool_daily_delta()' -> daily change metrics.
- 'tool_revenue_recent_performance(n=7)' -> last 'n' days' revenue.
- 'tool_top_products(n=3)' -> top 'n' products by revenue.
- 'tool_top_regions(n=3)' -> top 'n' regions by revenue.
- 'tool_true_profit_by_channel()' -> profit by marketing channel.

### 2. Analytics Tools
Core numeric analytics:
- 'tool_sales_by_product()' -> sales grouped by product.
- 'tool_sales_by region()' -> sales grouped by region.
- 'tool_sales_by_channel()' -> sales grouped by channel.
- 'tool_revenue_by_month()' -> revenue aggregated monthly.
- 'tool_profit_by_product()' -> profit per product.
- 'tool_cost_components_by_product()' -> breakdown of cost components per product.

### 3. Inventory Tools
Supply chain and stock metrics:
- 'tool_inventory_stockouts()' -> stockout counts bt product.
- 'tool_inventory_avg_stock()' -> average closing stock per product.

### 4. Marketing Tools
Performance and efficiency metrics:
- 'tool_marketing_roas()' -> ROAS per marketing channel.
- 'tool_marketing_spend_trend()' -> spend trends over time.

### 5. Interpretation Tools
Higher-level reasoninh and signal extraction:
- 'tool_interpret_growth_quality()' -> evaluate growth signal vs profit.
- 'tool_marketing_efficiency(lookback_days=30)' -> evaluates efficiency of marketing spend.
- 'tool_product_portfolio_health()' -> flags concentraition risks in products.
- 'tool_inventory_health_vs_revenue(lookback_days=30)' -> inventory impact on revenue.
- 'tool_channel_dependency_risk()' -> flags concentration risks in marketing channels.

### 6. Recommendation Tool
- 'tool_generate_recommendations()' -> aggregates all flags from interpretation tools + growth signal.
- Provides the **central executive recommendation primitive** for AUTO.
- Logic:
  1. Collect flags from 'marketing_efficiency', 'product_portfolio_health', 'inventory_health_vs_revenue', and 'channel_dependency_risk'.
  2. Compute growth signal via 'interpret_growth_quality'.
  3. Feed flags + growth signal into 'generate_recommendations'.

---

## Design Decisions
- All functions are **stateless wrt the agent**, using the preloaded 'CTX'.
- Wrappers return **Python dicts or list-of-dicts**, which are ready for the agent to consume.
- Tools are seperated by concern: executive, analytics, inventory, marketing, interpretation, recommendation.
- Preloading 'DataContext' avoids repeated CSV reads or heavy computations.

---

## What this file does NOT do
- Does not perform direct reasoning or executive decision-making itself.
- Does not read CSVs directly - relies on 'core/context.py'.
- Does not interact with external systems or the LLM.
- Purely a **tool wrapper and execution layer**.