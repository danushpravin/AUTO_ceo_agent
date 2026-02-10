# ------------------------------------------------------
# RECOMMENDATION LAYER — FLAG & SIGNAL DRIVEN
# ------------------------------------------------------

def generate_recommendations(
        flags: list,
        growth_signal: dict | None = None
) -> list:
    """
    Converts interpretation flags + growth signals into 
    executive-safe decision levers. 
    """

    recs = []

    for f in flags:
        t = f["type"]

        # --- MARKETING EFFICIENCY ---
        if t == "LOW_ROAS":
            recs.append({
                "trigger_flag": t,
                "scope": "channel",
                "entity": f.get("channel"),
                "recommendation": (
                    f"Reduce or pause spend on {f.get('channel')} until ROAS improves."
                ),
                "expected_impact": "Stops inefficient capital burn.",
                "risk_tradeoff": "Short-term revenue decline possible.",
                "confidence": "HIGH",
            })

        if t == "NEGATIVE_OR_LOW_NET_MARGIN":
            recs.append({
                "trigger_flag": t,
                "scope": "channel",
                "entity": f.get("channel"),
                "recommendation": (
                    f"Audit CAC, pricing, and product mix for {f.get('channel')}."
                ),
                "expected_impact": "Eliminates value-destructive growth.",
                "risk_tradeoff": "Channel scale may reduce temporarily.",
                "confidence": "HIGH",
            })
        
        if t == "SPEND_SPIKE_WEAK_RETURN":
            recs.append({
                "trigger_flag": t,
                "scope": "channel",
                "entity": f.get("channel"),
                "recommendation": (
                    f"Investigate recent spend increase on {f.get('channel')} for attribution leakage."
                ),
                "expected_impact": "Prevents inefficient scaling.",
                "risk_tradeoff": "Delayed growth if spike was experimental.",
                "confidence": "MEDIUM",
            })
        
        # --- PRODUCT PORTFOLIO ---
        if t == "PRODUCT_REVENUE_CONCENTRATION":
            recs.append({
                "trigger_flag": t,
                "scope": "portfolio",
                "entity": None,
                "recommendation": (
                    "Reduce dependency on top products via SKU expansion or demand diversification."
                ),
                "expected_impact": "Improves revenue resilience.",
                "risk_tradeoff": "New products may dilute margins initially.",
                "confidence": "MEDIUM",
            })
        
        if t == "FAKE_GROWTH_PRODUCT":
            recs.append({
                "trigger_flag": t,
                "scope": "product",
                "entity": f.get("product"),
                "recommendation": (
                    f"Reasses pricing or marketing support for {f.get('product')}"
                ),
                "expected_impact": "Prevents profit-negative growth.",
                "risk_tradeoff": "Revenue contraction possible.",
                "confidence": "HIGH",
            })
        
        # --- Inventory ---
        if t == "FREQUENT_STOCKOUTS":
            recs.append({
                "trigger_flag": t,
                "scope": f.get("product"),
                "recommendation": (
                    f"Increase safety stock or reorder frequency for {f.get('product')}."
                ),
                "expected_impact": "Recovers lost revenue.",
                "risk_tradeoff": "Higher inventory holding costs.",
                "confidence": "HIGH",
            })

        if t == "STOCKOUT_REVENUE_IMPACT":
            recs.append({
                "trigger_flag": t,
                "scope": "product",
                "entity": f.get("product"),
                "recommendation": (
                    f"Prioritize supply allocation to {f.get('product')} during demand peaks."
                ),
                "expected_impact": "Reduces supply-constrained losses.",
                "risk_tradeoff": "Lower priority SKUs may suffer.",
                "confidence": "HIGH",
            })

        if t == "LOW_STOCK_PRESSURE":
            recs.append({
                "trigger_flag": t,
                "scope": "product",
                "entity": f.get("product"),
                "recommendation": (
                    f"Closely monitor demand volatility for {f.get('product')}."
                ),
                "expected_impact": "Prevents future stockouts.",
                "risk_tradeoff": "Forecast errors possible.",
                "confidence": "MEDIUM",
            })
        
        # --- CHANNEL DEPENDENCY ---
        if t in ["CHANNEL_REVENUE_CONCENTRATION", "SINGLE_CHANNEL_DEPENDENCY", "PROFIT_CONCENTRATION"]:
            recs.append({
                "trigger_flag": t,
                "scope": "company",
                "entity": None,
                "recommendation": (
                    "Diversify revenue sources across additional channels."
                ),
                "expected_impact": "Reduces single-point-of-failure risk.",
                "risk_tradeoff": "New channels may be inefficient initially.",
                "confidence": "MEDIUM",
            })
        
        if t == "ROAS_ILLUSIONS":
            recs.append({
                "trigger_flag": t,
                "scope": "channel",
                "entity": f.get("channel"),
                "recommendation": (
                    f"Validate true incremental lift from {f.get('channel')} spend."
                ),
                "expected_impact": "Prevents false confidence from blended ROAS.",
                "risk_tradeoff": "Measurement complexity increases.",
                "confidence": "MEDIUM",
            })
        
        # --- GROWTH QUALITY SIGNAL OVERLAY ---
        if growth_signal:
            signal = growth_signal.get("signal")

            if signal == "NEGATIVE":
                recs.append({
                    "trigger_flag": "GROWTH_QUALITY_NEGATIVE",
                    "scope": "company",
                    "entity": None,
                    "recommendation": (
                        "Avoid aggressive scaling until unit economics stabilize."
                    ),
                    "expected_impact": "Prevents compounding losses.",
                    "risk_tradeoff": "Growth slowdown.",
                    "confidence": growth_signal.get("confidence", "MEDIUM"), 
                })
        
    return recs
