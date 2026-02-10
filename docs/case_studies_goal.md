🧪 Case Studies You Should Run (Final Set = 3)
✅ Case Study 1 (You already have)
Demand Shock / Revenue Contraction

Purpose: Test growth detection + operational fragility

You’ve already validated:

week-over-week revenue drop

agent correctly flags contraction

no hallucinated causes

Keep this.

🧪 Case Study 2 — Marketing Inefficiency (Profit Leakage)

This is much better than “fake growth” and easier to justify.

🎯 What this tests

Marketing efficiency

CAC vs revenue mismatch

ROAS illusion

Loss-making channels

Recommendation correctness

🔧 Config changes (ONLY)
CHANNEL_BEHAVIOR["Google"]["cpc"] = (30.0, 55.0)
CHANNEL_BEHAVIOR["Influencers"]["cpc"] = (20.0, 40.0)

CHANNEL_W = {
    "Instagram": 0.35,
    "Google": 0.45,
    "Influencers": 0.20,
}


Do NOT change demand.
Let revenue stay stable.

📈 What will naturally happen

Revenue stays flat-ish

Spend increases

CAC rises

Net profit margins go negative

Instagram remains the only healthy channel

🧠 What your agent should say

When you ask:

“Analyze marketing efficiency over the last 30 / 60 days”

Expected outputs:

HIGH severity NEGATIVE_OR_LOW_NET_MARGIN on Google & Influencers

Interpretation like:

“Revenue exists but destroys value”

“Growth is unprofitable”

Recommendation:

Pause or audit these channels

Reassess pricing or product mix

📝 How to document this

Title: Marketing Spend Is Driving Losses, Not Growth
Key Insight: Revenue masks value destruction
Why Agent Matters: Detects profit leakage humans miss

🧪 Case Study 3 — Inventory Failure & Lost Revenue

This one is gold for operations + risk thinking.

🎯 What this tests

Inventory health vs revenue

Stockout detection

Lost demand quantification

Supply chain fragility

🔧 Config changes (ONLY)
PRODUCTION_RANGE = {
    "Nutrain Vanilla": (40, 65),
    "Nutrain Choco Coffee": (30, 55),
    "Nutrain Banana Oats": (25, 40),
}

STARTING_STOCK = 80


Do not touch demand or marketing.

📈 What will happen

Frequent stockouts

Lost demand spikes

Revenue stagnates or drops

Top products go out of stock

Concentration risk worsens

🧠 What your agent should say

When you ask:

“Analyze inventory health vs revenue over the last month”

Expected outputs:

Stockout flags

Revenue loss attribution

Identification of which products hurt most

Interpretation like:

“Revenue decline driven by supply failure, not demand”

“Operational bottleneck limits growth”

📝 How to document this

Title: Growth Is Constrained by Operations, Not Demand
Key Insight: Fixing marketing won’t help if supply fails
Why Agent Matters: Differentiates demand vs execution problems