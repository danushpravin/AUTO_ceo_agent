import pandas as pd
from agent.core.context import DataContext

# ------------------------------------------------------
# MARKETING ANALYTICS
# ------------------------------------------------------

def roas_by_channel(ctx: DataContext):
    """
    Average ROAS per marketing channel.
    Used to detect inefficient spend and fake growth.
    """
    df = ctx.marketing.copy()
    df["ROAS"] = df["revenue"] / df["spend"].replace(0,pd.NA)
    return (
        df.groupby("channel")["ROAS"]
        .mean()
    )


def spend_over_time(ctx: DataContext):
    # ❗ FIX: Convert Period → string
    df = ctx.marketing.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return (
        df.groupby("month")["spend"]
        .sum()
    )


