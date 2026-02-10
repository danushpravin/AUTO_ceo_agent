import pandas as pd
from agent.core.context import DataContext

# ------------------------------------------------------
# EXECUTIVE PULSE
# ------------------------------------------------------

def _latest_date(ctx: DataContext):
    if ctx.daily.empty:
        return None
    #ctx.daily["date"] is datetime64 already
    return ctx.daily["date"].max()

def revenue_recent_performance(
        ctx: DataContext,
        n: int = 7
):
    """
    Executive primitive:
    - Returns recent daily revenue series
    - Computes baseline average (excluding today)
    - Computes today's deviation vs baseline

    Agent can choose n = 7, 14, 30, etc.
    """

    if ctx.daily.empty:
        return None
    
    latest = _latest_date(ctx)
    start = latest - pd.Timedelta(days=n)

    window = (
        ctx.daily[
            (ctx.daily["date"] > start) &
            (ctx.daily["date"] <= latest)
        ]
        .sort_values("date")
        .copy()
    )

    if len(window) < 2:
        return None
    
    today_revenue = float(window.iloc[-1]["revenue"])
    baseline_avg = float(window.iloc[:-1]["revenue"].mean())

    delta_pct = None
    if baseline_avg > 0:
        delta_pct = (today_revenue - baseline_avg) / baseline_avg * 100

    return { 
        "window_days": n,
        "daily_series": window[["date", "revenue", "units"]],
        "baseline_avg": baseline_avg,
        "today_revenue": today_revenue,
        "delta_pct": delta_pct,
    }


def daily_delta(ctx: DataContext):
    """
    Convenience wrapper: today vs yesterday
    """
    result = revenue_recent_performance(ctx, n=2)
    if result is None:
        return None

    return {
        "date": result["daily_series"].iloc[-1]["date"].date().isoformat(),
        "revenue_today": result["today_revenue"],
        "revenue_yesterday": float(result["daily_series"].iloc[-2]["revenue"]),
        "delta_pct": result["delta_pct"],
    }

