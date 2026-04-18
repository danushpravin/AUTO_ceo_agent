# Product Portfolio Health — Thresholds and Interpretation Framework

## What Product Portfolio Health Measures

A product portfolio is healthy when revenue is distributed across multiple profitable products, no single product creates existential dependency, and no loss-making product is large enough to threaten the overall business. Portfolio health analysis classifies each product by its combination of revenue contribution and profit margin, then surfaces structural risks in the mix.

## Product Classification System

Products are classified into five categories based on their revenue share and profit margin. Understanding these categories is essential to interpreting portfolio health signals correctly.

STAR products have both high revenue share (30% or more of total portfolio revenue) and healthy profit margins (20% or above). These are the core of a healthy business — they drive growth and generate surplus. A business with one or more STAR products is in a strong position, provided it is not exclusively dependent on them.

CASH_COW products have healthy margins (20% or above) but lower revenue share (below 30%). These are reliable, efficient contributors that fund operations without creating concentration risk. A portfolio with multiple cash cows is structurally resilient.

FAKE_GROWTH products have high revenue share (30% or more) but negative profit margins. These are the most dangerous classification. They inflate top-line metrics, attract capital and attention, and destroy value simultaneously. A FAKE_GROWTH product with 40% revenue share means a large portion of the business is running at a loss while appearing healthy. This requires immediate strategic intervention — either repricing, cost restructuring, or discontinuation.

ZOMBIE products have both low revenue share (below 5%) and margins below the healthy threshold. They contribute minimally to revenue and generate little or no profit. They consume inventory capital, SKU management overhead, and operational bandwidth. A portfolio with multiple zombies has an efficiency drag problem.

EXPERIMENTAL products do not fit cleanly into other categories. They may have moderate revenue share and marginal margins, or be new products without enough history to classify definitively.

## Revenue Concentration Threshold

When a single product contributes 30% or more of total portfolio revenue, the business has meaningful concentration risk. If that product faces a supply disruption, pricing pressure, or demand shift, revenue impact is immediate and significant. Above 50% revenue share in a single product, the risk is critical — the business is effectively a single-product business with diversification as an illusion.

Threshold: Revenue share of 30% or above in any single product triggers a PRODUCT_REVENUE_CONCENTRATION flag at medium severity. Above 50%, severity is high. Above 70%, the portfolio has a structural fragility problem that cannot be resolved without new product development or revenue diversification.

## Margin Threshold for Healthy Products

A profit margin of 20% or above indicates a product is generating meaningful surplus after accounting for cost of goods and direct costs. Margins between 10% and 20% are acceptable but indicate limited pricing power or cost efficiency issues. Margins below 10% are fragile — any input cost increase, logistics cost rise, or pricing adjustment can push the product into loss. Negative margins mean the product is loss-making and its revenue contribution is actively harmful to the business.

## Interpreting a Healthy Portfolio

No portfolio flags means that no single product dominates revenue at dangerous concentration levels, no product with significant revenue share has negative margins, and no large zombie cohort exists. This does not mean the portfolio is optimised — there may be growth opportunities in underleveraged cash cow products, or concentration risk approaching but not crossing thresholds.

## Portfolio Risk Compounding

Portfolio risk compounds when multiple weak signals appear simultaneously. A FAKE_GROWTH product combined with high overall revenue concentration in that product, combined with a ZOMBIE tail dragging margins, represents a structurally compromised portfolio even if each flag individually appears manageable. Executive interpretation should always look at the combination of portfolio signals, not each flag in isolation.