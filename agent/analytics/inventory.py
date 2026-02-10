import pandas as pd
from agent.core.context import DataContext

# ------------------------------------------------------
# INVENTORY ANALYTICS
# ------------------------------------------------------

def stockouts_by_product(ctx: DataContext):
    """Count how many days each product had a stockout."""
    df = ctx.inventory.copy()
    stockouts = df[df["stockout_flag"] == "Yes"]
    return (
        stockouts.groupby("product")["date"]
        .nunique()
        .reset_index()
        .rename(columns={"date": "stockout_days"})
    )


def avg_closing_stock(ctx: DataContext):
    """Average closing stock per product."""
    df = ctx.inventory.copy()
    return (
        df.groupby("product")["closing_stock"]
        .mean()
        .reset_index()
        .rename(columns={"closing_stock": "avg_closing_stock"})
    )

