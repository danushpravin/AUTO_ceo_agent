# Inventory Management — Thresholds and Interpretation Framework

## What Inventory Health vs Revenue Measures

Inventory health analysis connects supply availability to revenue outcomes. A stockout is not merely an operational inconvenience — it is a direct revenue loss event. The purpose of this analysis is to quantify how often products run out of stock, how severely stockouts suppress revenue on those days, and whether low-stock pressure is building toward future stockout risk even when full stockouts have not yet occurred.

## Stockout Frequency Threshold

A product that stocks out on 3 or more days within a 30-day window has a recurring supply problem, not an isolated incident. Three or more stockout days in 30 suggests that reorder points are set too low, lead times are underestimated, or demand forecasting is systematically inaccurate. At this frequency, stockouts are a structural supply failure, not bad luck.

Threshold: 3 or more stockout days in a 30-day window triggers a FREQUENT_STOCKOUTS flag at high severity. 1 to 2 stockout days in 30 is a warning signal worth monitoring. Zero stockout days is the operational target. Scale this proportionally for longer windows — for 60-day analysis, the threshold scales to 6 days; for 90-day analysis, 9 days.

## Revenue Impact of Stockouts

The most important stockout metric is not frequency — it is revenue impact. A product that stocks out on 5 days but generates almost no revenue on those days has low business impact. A product that stocks out on 3 days but shows 40% lower average daily revenue on stockout days versus normal days is a critical revenue leak. The revenue drop percentage on stockout days is the primary economic severity indicator.

Threshold: Average daily revenue drop of 15% or more on stockout days versus non-stockout days triggers a STOCKOUT_REVENUE_IMPACT flag at high severity. A 15% revenue drop means that every stockout day costs the business 15% of that product's normal daily contribution. Across multiple products and multiple stockout days, this compounds into material lost revenue that is invisible in monthly aggregates.

## Low Stock Pressure Warning

Low-stock pressure is a leading indicator of future stockouts. When closing stock levels fall to 5 units or fewer (for typical SKUs) across multiple days, the product is operating with nearly no buffer. A demand spike, delayed shipment, or forecast miss will immediately cause a full stockout. This is the pre-failure signal.

Threshold: 3 or more days with closing stock at or below 5 units, in the absence of frequent full stockouts, triggers a LOW_STOCK_PRESSURE flag at medium severity. This is a forward-looking risk flag, not a historical loss flag. The business has not yet lost revenue — but the conditions for loss are present.

## Lost Revenue Estimation

When a stockout occurs and lost demand data is available (units of demand that could not be fulfilled), lost revenue can be estimated by multiplying lost units by the product's average realized price. This estimate is conservative — it does not account for customers who did not attempt to purchase because they knew the product was unavailable (demand suppression effect). Actual lost revenue is likely higher than the estimate.

## Inventory Fragility vs Revenue Scale

High-revenue products with frequent stockouts represent the most critical inventory failures. A stockout in a product contributing 40% of portfolio revenue has 10 times the impact of a stockout in a product contributing 4% of revenue. Inventory health flags should always be interpreted in the context of the product's revenue share from the portfolio health analysis. A stockout flag on a STAR or FAKE_GROWTH product is a critical priority. A stockout flag on a ZOMBIE product is low priority.

## Interpreting No Inventory Flags

No inventory flags means all products maintained stock above the low-stock threshold for the analysis window, and no product showed meaningful revenue suppression from supply constraints. This is the operational baseline. It does not mean inventory is optimised — holding costs, overstock risk, and working capital efficiency are separate questions not covered by this analysis.