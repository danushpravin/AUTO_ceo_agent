# ------------------------------------------------------
# RECOMMENDATION LAYER — CONTEXT ASSEMBLER
# ------------------------------------------------------
#
# Design principle:
#   This layer does NOT generate recommendation text.
#   It assembles a structured, prioritised context payload
#   from interpretation flags and growth signals.
#
#   The LLM (in agent.py) receives this payload alongside
#   RAG-retrieved knowledge and generates reasoned,
#   context-sensitive recommendations from both.
#
#   Separating assembly (deterministic) from reasoning
#   (LLM + RAG) keeps this layer traceable and testable.
# ------------------------------------------------------

# Priority order for flag types — higher index = higher urgency
FLAG_PRIORITY = {
    # Critical: value destruction in progress
    "FAKE_GROWTH_PRODUCT": 10,
    "ROAS_ILLUSION": 10,
    "NEGATIVE_OR_LOW_NET_MARGIN": 9,
    "PROFIT_CONCENTRATION": 9,
    "GROWTH_QUALITY_NEGATIVE": 9,

    # High: revenue or supply at immediate risk
    "FREQUENT_STOCKOUTS": 8,
    "STOCKOUT_REVENUE_IMPACT": 8,
    "SINGLE_CHANNEL_DEPENDENCY": 8,

    # Medium: structural fragility building
    "CHANNEL_REVENUE_CONCENTRATION": 6,
    "PRODUCT_REVENUE_CONCENTRATION": 6,
    "LOW_ROAS": 6,
    "SPEND_SPIKE_WEAK_RETURN": 5,
    "ZOMBIE_PRODUCT_DRAG": 4,

    # Forward-looking warnings
    "LOW_STOCK_PRESSURE": 3,
}

# Human-readable scope labels for the LLM
FLAG_SCOPE = {
    "FAKE_GROWTH_PRODUCT": "product",
    "ROAS_ILLUSION": "channel",
    "NEGATIVE_OR_LOW_NET_MARGIN": "channel",
    "PROFIT_CONCENTRATION": "channel",
    "GROWTH_QUALITY_NEGATIVE": "company",
    "FREQUENT_STOCKOUTS": "product",
    "STOCKOUT_REVENUE_IMPACT": "product",
    "SINGLE_CHANNEL_DEPENDENCY": "company",
    "CHANNEL_REVENUE_CONCENTRATION": "channel",
    "PRODUCT_REVENUE_CONCENTRATION": "portfolio",
    "LOW_ROAS": "channel",
    "SPEND_SPIKE_WEAK_RETURN": "channel",
    "ZOMBIE_PRODUCT_DRAG": "portfolio",
    "LOW_STOCK_PRESSURE": "product",
}

# What the LLM should focus on per flag type — 
# seeds the reasoning direction without prescribing the output
FLAG_REASONING_SEED = {
    "FAKE_GROWTH_PRODUCT": "product is generating revenue at a loss — revenue scale is making the loss worse",
    "ROAS_ILLUSION": "channel appears efficient on marketing metrics but destroys net value after product costs",
    "NEGATIVE_OR_LOW_NET_MARGIN": "channel spend plus product cost exceeds revenue — not a creative problem, an economics problem",
    "PROFIT_CONCENTRATION": "single channel controls most profit — any degradation collapses the entire profit pool",
    "GROWTH_QUALITY_NEGATIVE": "top-line growth is not translating to bottom-line value — scaling now compounds losses",
    "FREQUENT_STOCKOUTS": "supply is the binding constraint on revenue — not demand, not marketing",
    "STOCKOUT_REVENUE_IMPACT": "stockouts are measurably suppressing daily revenue — this is a quantified loss event",
    "SINGLE_CHANNEL_DEPENDENCY": "business has no profitable fallback if the primary channel degrades",
    "CHANNEL_REVENUE_CONCENTRATION": "revenue resilience is low — channel disruption creates immediate top-line impact",
    "PRODUCT_REVENUE_CONCENTRATION": "portfolio resilience is low — single product failure creates immediate top-line impact",
    "LOW_ROAS": "marketing spend is not generating sufficient revenue return to be profitable after costs",
    "SPEND_SPIKE_WEAK_RETURN": "incremental spend is not generating proportional incremental revenue — efficiency is deteriorating",
    "ZOMBIE_PRODUCT_DRAG": "low-contribution products are consuming operational and inventory bandwidth without return",
    "LOW_STOCK_PRESSURE": "inventory buffer is thin — demand volatility or supply delay will cause stockout",
}


def generate_recommendations(
        flags: list,
        growth_signal: dict | None = None
) -> dict:
    """
    Assembles a structured recommendation context from interpretation flags
    and growth signal. Returns a prioritised payload for LLM reasoning.

    The LLM uses this payload + RAG knowledge to generate
    specific, traceable, context-sensitive recommendations.

    Returns:
    {
        "recommendation_context": [
            {
                "priority": int,
                "flag_type": str,
                "scope": str,
                "entity": str | None,
                "reasoning_seed": str,
                "evidence": dict,
                "severity": str,
            },
            ...
        ],
        "growth_signal": dict | None,
        "summary": {
            "total_flags": int,
            "critical_flags": int,
            "affected_scopes": list,
            "dominant_risk_area": str | None,
        }
    }
    """

    context_items = []
    seen_growth_signal = False

    for f in flags:
        t = f.get("type")
        if not t:
            continue

        priority = FLAG_PRIORITY.get(t, 2)
        scope = FLAG_SCOPE.get(t, "company")
        reasoning_seed = FLAG_REASONING_SEED.get(t, "")

        # Extract entity (product / channel) if present
        entity = f.get("channel") or f.get("product") or f.get("products") or None

        # Pull all numeric evidence from the flag for LLM context
        evidence = {
            k: v for k, v in f.items()
            if k not in ("type", "severity") and v is not None
        }

        context_items.append({
            "priority": priority,
            "flag_type": t,
            "scope": scope,
            "entity": entity,
            "reasoning_seed": reasoning_seed,
            "evidence": evidence,
            "severity": f.get("severity", "medium"),
        })

    # Growth signal as a standalone context item (only once)
    if growth_signal and growth_signal.get("signal") in ("NEGATIVE", "CAUTION"):
        if not seen_growth_signal:
            priority = FLAG_PRIORITY.get("GROWTH_QUALITY_NEGATIVE", 9)
            context_items.append({
                "priority": priority,
                "flag_type": "GROWTH_QUALITY_NEGATIVE",
                "scope": "company",
                "entity": None,
                "reasoning_seed": FLAG_REASONING_SEED["GROWTH_QUALITY_NEGATIVE"],
                "evidence": growth_signal.get("evidence", {}),
                "severity": "high" if growth_signal.get("signal") == "NEGATIVE" else "medium",
            })
            seen_growth_signal = True

    # Sort by priority descending — LLM addresses highest urgency first
    context_items.sort(key=lambda x: x["priority"], reverse=True)

    # --- Summary block ---
    critical_flags = [i for i in context_items if i["priority"] >= 8]
    affected_scopes = list(dict.fromkeys(i["scope"] for i in context_items))  # ordered, deduped

    # Dominant risk area = scope with most high-priority flags
    scope_counts = {}
    for item in context_items:
        if item["priority"] >= 6:
            scope_counts[item["scope"]] = scope_counts.get(item["scope"], 0) + 1
    dominant_risk_area = max(scope_counts, key=scope_counts.get) if scope_counts else None

    return {
        "recommendation_context": context_items,
        "growth_signal": growth_signal,
        "summary": {
            "total_flags": len(context_items),
            "critical_flags": len(critical_flags),
            "affected_scopes": affected_scopes,
            "dominant_risk_area": dominant_risk_area,
        }
    }