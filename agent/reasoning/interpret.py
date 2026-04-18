import pandas as pd
from agent.core.context import DataContext
from agent.analytics.executive import _latest_date
from agent.analytics.profit import *
 
# ============================================================
# THRESHOLD CONSTANTS
# Domain knowledge and reasoning behind these values lives in
# agent/rag/knowledge/*.md — retrieved by the LLM at runtime.
# These constants are the single source of truth for computation.
# ============================================================
 
# --- Growth Quality ---
GROWTH_LOSS_REVENUE_SHARE_CAUTION = 0.15   # 15% loss revenue share → CAUTION
GROWTH_LOSS_REVENUE_SHARE_NEGATIVE = 0.30  # 30% loss revenue share → NEGATIVE
 
# --- Marketing Efficiency ---
MARKETING_MIN_ROAS = 2.0                   # Minimum viable ROAS
MARKETING_MIN_NET_MARGIN_PCT = 0.0         # Net profit margin floor (%)
MARKETING_SPEND_SPIKE_PCT = 25.0           # Spend increase that triggers spike check (%)
 
# --- Product Portfolio ---
PORTFOLIO_MIN_HEALTHY_MARGIN_PCT = 20.0    # Margin threshold for STAR / CASH_COW
PORTFOLIO_HIGH_REVENUE_SHARE_PCT = 30.0    # Revenue share threshold for concentration risk
PORTFOLIO_ZOMBIE_REVENUE_SHARE_PCT = 5.0   # Below this → ZOMBIE candidate
 
# --- Inventory ---
INVENTORY_STOCKOUT_DAYS_THRESHOLD = 3      # Stockout days in window before flagging
INVENTORY_REVENUE_DROP_THRESHOLD_PCT = 15.0  # Revenue drop % on stockout days
INVENTORY_LOW_STOCK_UNITS = 5.0            # Closing stock at or below → low stock pressure
 
# --- Channel Dependency ---
CHANNEL_MAX_REVENUE_SHARE_PCT = 50.0       # Single channel revenue concentration ceiling
CHANNEL_MAX_PROFIT_SHARE_PCT = 70.0        # Single channel profit concentration ceiling
CHANNEL_MIN_HEALTHY_MARGIN_PCT = 5.0       # Minimum net margin for a channel to be "healthy"
 
 
# ------------------------------------------------------
# INTERPRETATION LAYER — Growth Quality
# ------------------------------------------------------
 
def interpret_growth_quality(
        recent_perf: dict,
        profit_by_product_df: pd.DataFrame
):
    """
    Interprets whether recent revenue growth is healthy or fake.
    Deterministic, rule-based, explainable.
    Thresholds from: agent/rag/knowledge/growth_quality.md
    """
 
    if recent_perf is None or profit_by_product_df.empty:
        return {
            "signal": "NEUTRAL",
            "reason": "Insufficient data to assess growth quality.",
            "evidence": {},
            "confidence": "LOW"
        }
 
    revenue_delta = recent_perf.get("delta_pct")
 
    total_profit = profit_by_product_df["profit"].sum()
    loss_products = profit_by_product_df[
        profit_by_product_df["profit"] < 0
    ]
 
    total_revenue = profit_by_product_df["revenue"].sum()
    loss_revenue_share = (
        loss_products["revenue"].sum() / total_revenue
        if total_revenue > 0 else 0
    )
 
    if revenue_delta is not None and revenue_delta > 0:
 
        if total_profit <= 0:
            return {
                "signal": "NEGATIVE",
                "reason": "Revenue increased but overall profit is negative.",
                "evidence": {
                    "revenue_delta_pct": revenue_delta,
                    "total_profit": total_profit,
                },
                "confidence": "HIGH"
            }
 
        if loss_revenue_share > GROWTH_LOSS_REVENUE_SHARE_NEGATIVE:
            return {
                "signal": "NEGATIVE",
                "reason": "Revenue growth is driven by loss-making products.",
                "evidence": {
                    "revenue_delta_pct": revenue_delta,
                    "loss_revenue_share": round(loss_revenue_share, 2),
                    "loss_products": loss_products["product"].tolist(),
                    "threshold_used": GROWTH_LOSS_REVENUE_SHARE_NEGATIVE,
                },
                "confidence": "HIGH"
            }
 
        if loss_revenue_share > GROWTH_LOSS_REVENUE_SHARE_CAUTION:
            return {
                "signal": "CAUTION",
                "reason": "Revenue growth present but loss-making products have meaningful revenue share.",
                "evidence": {
                    "revenue_delta_pct": revenue_delta,
                    "loss_revenue_share": round(loss_revenue_share, 2),
                    "loss_products": loss_products["product"].tolist(),
                    "threshold_used": GROWTH_LOSS_REVENUE_SHARE_CAUTION,
                },
                "confidence": "MEDIUM"
            }
 
        return {
            "signal": "POSITIVE",
            "reason": "Revenue growth is supported by profitable products.",
            "evidence": {
                "revenue_delta_pct": revenue_delta,
                "total_profit": total_profit,
                "loss_revenue_share": round(loss_revenue_share, 2),
            },
            "confidence": "HIGH"
        }
 
    return {
        "signal": "NEUTRAL",
        "reason": "No meaningful revenue growth detected.",
        "evidence": {
            "revenue_delta_pct": revenue_delta
        },
        "confidence": "MEDIUM"
    }
 
 
# ------------------------------------------------------
# INTERPRETATION LAYER — Marketing Efficiency
# ------------------------------------------------------
 
def _date_window(df: pd.DataFrame, date_col: str, end: pd.Timestamp, days: int) -> pd.DataFrame:
    """Inclusive window: (end-days, end)."""
    start = end - pd.Timedelta(days=days)
    return df[(df[date_col] > start) & (df[date_col] <= end)].copy()
 
 
def marketing_efficiency(ctx: DataContext, lookback_days: int = 30):
    """
    Deterministic interpretation primitive.
    Evaluates paid channels on ROAS, CAC, and net profit contribution.
    Thresholds from: agent/rag/knowledge/marketing_efficiency.md
 
    Returns:
    {
        "as_of": "YYYY-MM-DD",
        "window_days": int,
        "channel_table": DataFrame,
        "flags": [...],
        "interpretation": [...]
    }
    """
    latest = _latest_date(ctx)
 
    m = _date_window(ctx.marketing, "date", latest, lookback_days)
    s = _date_window(ctx.sales_enriched, "date", latest, lookback_days)
 
    if m.empty:
        return {
            "as_of": latest.date().isoformat(),
            "window_days": lookback_days,
            "channel_table": pd.DataFrame(),
            "flags": [{"type": "NO_MARKETING_DATA", "severity": "high"}],
            "interpretation": ["No marketing data available in the selected window."]
        }
 
    # --- Core marketing rollup ---
    roll = (
        m.groupby("channel", as_index=False)
        .agg(
            spend=("spend", "sum"),
            mkt_revenue=("revenue", "sum"),
            conversions=("conversions", "sum"),
            clicks=("clicks", "sum"),
            impressions=("impressions", "sum"),
        )
    )
    roll["roas"] = roll["mkt_revenue"] / roll["spend"].replace(0, pd.NA)
    roll["cac"] = roll["spend"] / roll["conversions"].replace(0, pd.NA)
 
    if s.empty:
        return {
            "as_of": latest.date().isoformat(),
            "window_days": lookback_days,
            "channel_table": roll.sort_values("spend", ascending=False),
            "flags": [{"type": "NO_SALES_DATA_WINDOW", "severity": "high"}],
            "interpretation": ["Marketing window has data, but no sales rows exist in the same window."],
        }
 
    sales_roll = (
        s.groupby("channel", as_index=False)
        .agg(
            sales_revenue=("revenue", "sum"),
            units=("units_sold", "sum"),
            product_cost=("unit_cost", lambda x: (x * s.loc[x.index, "units_sold"]).sum()),
        )
    )
 
    channel_table = roll.merge(sales_roll, on="channel", how="left")
 
    channel_table["net_profit"] = (
        channel_table["sales_revenue"].fillna(0)
        - channel_table["product_cost"].fillna(0)
        - channel_table["spend"].fillna(0)
    )
    channel_table["net_profit_margin_pct"] = (
        channel_table["net_profit"] / channel_table["sales_revenue"].replace(0, pd.NA) * 100
    )
 
    # --- Spend trend: last half vs first half ---
    half = max(2, lookback_days // 2)
    first = _date_window(ctx.marketing, "date", latest - pd.Timedelta(days=half), half)
    last = _date_window(ctx.marketing, "date", latest, half)
 
    def _sum_by_channel(df, col):
        if df.empty:
            return pd.DataFrame(columns=["channel", col])
        return df.groupby("channel", as_index=False)[col].sum()
 
    spend_first = _sum_by_channel(first, "spend").rename(columns={"spend": "spend_first"})
    spend_last = _sum_by_channel(last, "spend").rename(columns={"spend": "spend_last"})
    rev_first = _sum_by_channel(first, "revenue").rename(columns={"revenue": "rev_first"})
    rev_last = _sum_by_channel(last, "revenue").rename(columns={"revenue": "rev_last"})
 
    trend = (
        spend_first
        .merge(spend_last, on="channel", how="outer")
        .merge(rev_first, on="channel", how="outer")
        .merge(rev_last, on="channel", how="outer")
        .fillna(0)
    )
    trend["spend_change_pct"] = (
        (trend["spend_last"] - trend["spend_first"])
        / trend["spend_first"].replace(0, pd.NA) * 100
    )
    trend["rev_change_pct"] = (
        (trend["rev_last"] - trend["rev_first"])
        / trend["rev_first"].replace(0, pd.NA) * 100
    )
 
    channel_table = channel_table.merge(
        trend[["channel", "spend_change_pct", "rev_change_pct"]],
        on="channel", how="left"
    )
 
    # --- Flags + interpretations ---
    flags = []
    interpretation = []
 
    for _, r in channel_table.iterrows():
        ch = r["channel"]
        roas = r.get("roas")
        npm = r.get("net_profit_margin_pct")
        spend_chg = r.get("spend_change_pct")
 
        if pd.notna(roas) and roas < MARKETING_MIN_ROAS:
            flags.append({
                "type": "LOW_ROAS",
                "channel": ch,
                "severity": "medium",
                "value": float(roas),
                "threshold": MARKETING_MIN_ROAS,
            })
            interpretation.append(
                f"{ch}: ROAS below minimum viable threshold "
                f"({float(roas):.2f} < {MARKETING_MIN_ROAS})."
            )
 
        if pd.notna(npm) and npm < MARKETING_MIN_NET_MARGIN_PCT:
            flags.append({
                "type": "NEGATIVE_OR_LOW_NET_MARGIN",
                "channel": ch,
                "severity": "high",
                "value": float(npm),
                "threshold": MARKETING_MIN_NET_MARGIN_PCT,
            })
            interpretation.append(
                f"{ch}: Net profit margin below floor "
                f"({float(npm):.2f}% < {MARKETING_MIN_NET_MARGIN_PCT}%). "
                "Spend and product mix are not generating net profit."
            )
 
        if pd.notna(spend_chg) and spend_chg >= MARKETING_SPEND_SPIKE_PCT:
            rev_chg = r.get("rev_change_pct")
            if pd.isna(rev_chg) or rev_chg < spend_chg:
                flags.append({
                    "type": "SPEND_SPIKE_WEAK_RETURN",
                    "channel": ch,
                    "severity": "medium",
                    "spend_change_pct": float(spend_chg),
                    "rev_change_pct": (None if pd.isna(rev_chg) else float(rev_chg)),
                    "threshold": MARKETING_SPEND_SPIKE_PCT,
                })
                interpretation.append(
                    f"{ch}: Spend jumped ~{float(spend_chg):.1f}% "
                    "but revenue did not follow. Potential diminishing returns or targeting fatigue."
                )
 
    if not flags:
        interpretation.append(
            "No major marketing efficiency red flags detected in this window."
        )
 
    return {
        "as_of": latest.date().isoformat(),
        "window_days": lookback_days,
        "channel_table": channel_table.sort_values("spend", ascending=False),
        "flags": flags,
        "interpretation": interpretation,
        "thresholds_used": {
            "min_roas": MARKETING_MIN_ROAS,
            "min_net_margin_pct": MARKETING_MIN_NET_MARGIN_PCT,
            "spend_spike_pct": MARKETING_SPEND_SPIKE_PCT,
        }
    }
 
 
# ------------------------------------------------------
# INTERPRETATION LAYER — Product Portfolio Health
# ------------------------------------------------------
 
def product_portfolio_health(ctx: DataContext):
    """
    Evaluates product-level economic health and portfolio risk.
    Thresholds from: agent/rag/knowledge/product_portfolio.md
    """
 
    latest = _latest_date(ctx)
    if latest is None:
        return None
 
    df = profit_by_product(ctx).copy()
 
    total_revenue = df["revenue"].sum()
    if total_revenue <= 0:
        return None
 
    df["revenue_share_pct"] = df["revenue"] / total_revenue * 100
 
    def classify(row):
        high_rev = row["revenue_share_pct"] >= PORTFOLIO_HIGH_REVENUE_SHARE_PCT
        good_margin = row["profit_margin_pct"] >= PORTFOLIO_MIN_HEALTHY_MARGIN_PCT
        negative_margin = row["profit_margin_pct"] < 0
        zombie = (
            row["revenue_share_pct"] < PORTFOLIO_ZOMBIE_REVENUE_SHARE_PCT
            and not good_margin
        )
 
        if high_rev and good_margin:
            return "STAR"
        if not high_rev and good_margin:
            return "CASH_COW"
        if high_rev and negative_margin:
            return "FAKE_GROWTH"
        if zombie:
            return "ZOMBIE"
        return "EXPERIMENTAL"
 
    df["category"] = df.apply(classify, axis=1)
 
    flags = []
    interpretation = []
 
    # Revenue concentration
    dominant = df[df["revenue_share_pct"] >= PORTFOLIO_HIGH_REVENUE_SHARE_PCT]
    for _, r in dominant.iterrows():
        severity = "high" if r["revenue_share_pct"] >= 50.0 else "medium"
        flags.append({
            "type": "PRODUCT_REVENUE_CONCENTRATION",
            "product": r["product"],
            "revenue_share_pct": float(r["revenue_share_pct"]),
            "severity": severity,
            "threshold": PORTFOLIO_HIGH_REVENUE_SHARE_PCT,
        })
        interpretation.append(
            f"{r['product']} contributes {r['revenue_share_pct']:.1f}% of total revenue. "
            "Portfolio may be overly dependent on this product."
        )
 
    # Fake growth products
    fake = df[df["category"] == "FAKE_GROWTH"]
    for _, r in fake.iterrows():
        flags.append({
            "type": "FAKE_GROWTH_PRODUCT",
            "product": r["product"],
            "profit_margin_pct": float(r["profit_margin_pct"]),
            "revenue_share_pct": float(r["revenue_share_pct"]),
            "severity": "high",
            "threshold_margin": PORTFOLIO_MIN_HEALTHY_MARGIN_PCT,
        })
        interpretation.append(
            f"{r['product']} has high revenue share ({r['revenue_share_pct']:.1f}%) "
            "but negative margins. Growth here is destroying value."
        )
 
    # Zombie drag
    zombies = df[df["category"] == "ZOMBIE"]
    if len(zombies) >= 2:
        flags.append({
            "type": "ZOMBIE_PRODUCT_DRAG",
            "products": zombies["product"].tolist(),
            "count": len(zombies),
            "severity": "medium",
        })
        interpretation.append(
            f"{len(zombies)} zombie products detected with low revenue share and sub-threshold margins. "
            "These consume operational bandwidth without meaningful contribution."
        )
 
    if not flags:
        interpretation.append(
            "Product portfolio shows no major structural health risks under current thresholds."
        )
 
    return {
        "as_of": latest.date().isoformat(),
        "product_table": df.sort_values("revenue", ascending=False),
        "flags": flags,
        "interpretation": interpretation,
        "thresholds_used": {
            "min_healthy_margin_pct": PORTFOLIO_MIN_HEALTHY_MARGIN_PCT,
            "high_revenue_share_pct": PORTFOLIO_HIGH_REVENUE_SHARE_PCT,
            "zombie_revenue_share_pct": PORTFOLIO_ZOMBIE_REVENUE_SHARE_PCT,
        }
    }
 
 
# ------------------------------------------------------
# INTERPRETATION LAYER — Inventory Health vs Revenue
# ------------------------------------------------------
 
def inventory_health_vs_revenue(ctx: DataContext, lookback_days: int = 30):
    """
    Links stock availability (stockouts / low-stock pressure) to revenue outcomes.
    Thresholds from: agent/rag/knowledge/inventory_management.md
 
    Returns:
    {
        "as_of": "YYYY-MM-DD",
        "window_days": int,
        "product_table": DataFrame,
        "flags": [...],
        "interpretation": [...]
    }
    """
 
    latest = _latest_date(ctx)
    if latest is None:
        return None
 
    inv = _date_window(ctx.inventory, "date", latest, lookback_days)
    sales = _date_window(ctx.sales, "date", latest, lookback_days)
 
    if inv.empty:
        return {
            "as_of": latest.date().isoformat(),
            "window_days": lookback_days,
            "product_table": pd.DataFrame(),
            "flags": [{"type": "NO_INVENTORY_DATA", "severity": "high"}],
            "interpretation": ["No inventory data available in the selected window."],
        }
 
    sales_day = (
        sales.groupby(["date", "product"], as_index=False)
        .agg(revenue=("revenue", "sum"), units_sold=("units_sold", "sum"))
    )
 
    inv_day = inv[[
        "date", "product", "lost_demand", "stockout_flag", "closing_stock", "units_dispatched"
    ]].copy()
    inv_day["lost_demand"] = inv_day.get("lost_demand", 0).fillna(0).astype(float)
    inv_day["is_stockout"] = inv_day["stockout_flag"].astype(str).str.lower().isin(["yes", "true", "1"])
    inv_day["is_low_stock"] = inv_day["closing_stock"].fillna(0) <= INVENTORY_LOW_STOCK_UNITS
 
    merged = inv_day.merge(sales_day, on=["date", "product"], how="left")
    merged["revenue"] = merged["revenue"].fillna(0.0)
    merged["units_sold"] = merged["units_sold"].fillna(0.0)
 
    merged["realized_price"] = (
        merged.groupby("product")["revenue"].transform("sum") /
        merged.groupby("product")["units_sold"].transform("sum")
    )
    merged["realized_price"] = merged["realized_price"].fillna(0.0)
 
    merged["lost_revenue_estimate"] = 0.0
    mask = merged["is_stockout"] & (merged["lost_demand"] > 0)
    merged.loc[mask, "lost_revenue_estimate"] = (
        merged.loc[mask, "lost_demand"] * merged.loc[mask, "realized_price"]
    )
 
    def _avg_revenue(df, mask):
        sub = df[mask]
        if sub.empty:
            return pd.NA
        return float(sub["revenue"].mean())
 
    rows = []
    for product, g in merged.groupby("product"):
        stockout_days = int(g["is_stockout"].sum())
        low_stock_days = int(g["is_low_stock"].sum())
        total_days = int(g["date"].nunique())
        avg_rev_stockout = _avg_revenue(g, g["is_stockout"])
        avg_rev_normal = _avg_revenue(g, ~g["is_stockout"])
        lost_units = int(g.loc[g["is_stockout"], "lost_demand"].sum())
        lost_revenue = float(g.loc[g["is_stockout"], "lost_revenue_estimate"].sum())
 
        impact_pct = pd.NA
        if pd.notna(avg_rev_normal) and avg_rev_normal > 0 and pd.notna(avg_rev_stockout):
            impact_pct = (avg_rev_normal - avg_rev_stockout) / avg_rev_normal * 100.0
 
        rows.append({
            "product": product,
            "days_observed": total_days,
            "stockout_days": stockout_days,
            "low_stock_days": low_stock_days,
            "avg_daily_revenue_non_stockout": avg_rev_normal,
            "avg_daily_revenue_stockout": avg_rev_stockout,
            "revenue_drop_pct_on_stockout": impact_pct,
            "lost_units_estimated": lost_units,
            "lost_revenue_estimated": lost_revenue,
        })
 
    product_table = pd.DataFrame(rows).sort_values(
        ["stockout_days", "revenue_drop_pct_on_stockout"], ascending=False
    )
 
    # Scale stockout threshold proportionally to window
    scaled_stockout_threshold = max(
        INVENTORY_STOCKOUT_DAYS_THRESHOLD,
        round(INVENTORY_STOCKOUT_DAYS_THRESHOLD * (lookback_days / 30))
    )
 
    flags = []
    interpretation = []
 
    for _, r in product_table.iterrows():
        p = r["product"]
        so_days = int(r["stockout_days"])
        drop = r["revenue_drop_pct_on_stockout"]
 
        if so_days >= scaled_stockout_threshold:
            flags.append({
                "type": "FREQUENT_STOCKOUTS",
                "product": p,
                "severity": "high",
                "stockout_days": so_days,
                "threshold_days": scaled_stockout_threshold,
            })
            interpretation.append(
                f"{p}: Stocked out on {so_days} days in the last {lookback_days} days "
                f"(threshold: {scaled_stockout_threshold} days)."
            )
 
        if pd.notna(drop) and drop >= INVENTORY_REVENUE_DROP_THRESHOLD_PCT:
            flags.append({
                "type": "STOCKOUT_REVENUE_IMPACT",
                "product": p,
                "severity": "high",
                "revenue_drop_pct_on_stockout": float(drop),
                "threshold_pct": INVENTORY_REVENUE_DROP_THRESHOLD_PCT,
            })
            interpretation.append(
                f"{p}: Avg daily revenue is ~{float(drop):.1f}% lower on stockout days vs normal days. "
                "Likely revenue loss from supply constraint."
            )
 
        if int(r["low_stock_days"]) >= scaled_stockout_threshold and so_days < scaled_stockout_threshold:
            flags.append({
                "type": "LOW_STOCK_PRESSURE",
                "product": p,
                "severity": "medium",
                "low_stock_days": int(r["low_stock_days"]),
                "low_stock_threshold_units": INVENTORY_LOW_STOCK_UNITS,
            })
            interpretation.append(
                f"{p}: {int(r['low_stock_days'])} days with closing stock at or below "
                f"{INVENTORY_LOW_STOCK_UNITS} units. Risk of future stockouts if demand spikes."
            )
 
    if not flags:
        interpretation.append(
            "No major inventory-driven revenue risks detected under current thresholds."
        )
 
    return {
        "as_of": latest.date().isoformat(),
        "window_days": lookback_days,
        "product_table": product_table,
        "flags": flags,
        "interpretation": interpretation,
        "thresholds_used": {
            "stockout_days_threshold": scaled_stockout_threshold,
            "revenue_drop_threshold_pct": INVENTORY_REVENUE_DROP_THRESHOLD_PCT,
            "low_stock_units": INVENTORY_LOW_STOCK_UNITS,
        }
    }
 
 
# ------------------------------------------------------
# INTERPRETATION LAYER — Channel Dependency Risk
# ------------------------------------------------------
 
def channel_dependency_risk(ctx: DataContext):
    """
    Evaluates business risk from over-dependence on specific channels.
    Thresholds from: agent/rag/knowledge/channel_dependency.md
    """
 
    latest = _latest_date(ctx)
    if latest is None:
        return None
 
    df = true_profit_by_channel(ctx).copy()
    if df.empty:
        return None
 
    total_revenue = df["revenue"].sum()
    total_profit = df["net_profit"].sum()
 
    df["revenue_share_pct"] = df["revenue"] / total_revenue * 100 if total_revenue > 0 else 0
    df["profit_share_pct"] = df["net_profit"] / total_profit * 100 if total_profit > 0 else 0
 
    flags = []
    interpretation = []
 
    # Revenue concentration
    for _, r in df.iterrows():
        if r["revenue_share_pct"] >= CHANNEL_MAX_REVENUE_SHARE_PCT:
            severity = "high" if r["revenue_share_pct"] >= 70.0 else "medium"
            flags.append({
                "type": "CHANNEL_REVENUE_CONCENTRATION",
                "channel": r["channel"],
                "severity": severity,
                "revenue_share_pct": float(r["revenue_share_pct"]),
                "threshold": CHANNEL_MAX_REVENUE_SHARE_PCT,
            })
            interpretation.append(
                f"{r['channel']} contributes {r['revenue_share_pct']:.1f}% of total revenue. "
                "Business may be overly dependent on this channel."
            )
 
    # Profit concentration
    for _, r in df.iterrows():
        if r["profit_share_pct"] >= CHANNEL_MAX_PROFIT_SHARE_PCT:
            flags.append({
                "type": "PROFIT_CONCENTRATION",
                "channel": r["channel"],
                "severity": "high",
                "profit_share_pct": float(r["profit_share_pct"]),
                "threshold": CHANNEL_MAX_PROFIT_SHARE_PCT,
            })
            interpretation.append(
                f"{r['channel']} contributes {r['profit_share_pct']:.1f}% of total profit. "
                "Profitability is fragile if this channel degrades."
            )
 
    # ROAS illusion: positive revenue, negative net margin
    illusion = df[(df["profit_margin_pct"] < 0) & (df["revenue"] > 0)]
    for _, r in illusion.iterrows():
        flags.append({
            "type": "ROAS_ILLUSION",
            "channel": r["channel"],
            "severity": "high",
            "profit_margin_pct": float(r["profit_margin_pct"]),
        })
        interpretation.append(
            f"{r['channel']} generates revenue but has negative net margin. "
            "This channel appears efficient but is destroying value."
        )
 
    # Single healthy channel
    healthy = df[df["profit_margin_pct"] >= CHANNEL_MIN_HEALTHY_MARGIN_PCT]
    if len(healthy) <= 1:
        flags.append({
            "type": "SINGLE_CHANNEL_DEPENDENCY",
            "severity": "high",
            "healthy_channels": healthy["channel"].tolist(),
            "threshold_margin_pct": CHANNEL_MIN_HEALTHY_MARGIN_PCT,
        })
        interpretation.append(
            f"Only {len(healthy)} channel(s) meet the minimum healthy margin threshold "
            f"({CHANNEL_MIN_HEALTHY_MARGIN_PCT}%). "
            "Business has insufficient channel diversification."
        )
 
    if not flags:
        interpretation.append(
            "No major channel dependency risks detected under current thresholds."
        )
 
    return {
        "as_of": latest.date().isoformat(),
        "channel_table": df.sort_values("revenue", ascending=False),
        "flags": flags,
        "interpretation": interpretation,
        "thresholds_used": {
            "max_revenue_share_pct": CHANNEL_MAX_REVENUE_SHARE_PCT,
            "max_profit_share_pct": CHANNEL_MAX_PROFIT_SHARE_PCT,
            "min_healthy_margin_pct": CHANNEL_MIN_HEALTHY_MARGIN_PCT,
        }
    }
 