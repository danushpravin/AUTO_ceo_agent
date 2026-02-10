import pandas as pd
from agent.core.context import DataContext

# ------------------------------------------------------
# SALES ANALYTICS
# ------------------------------------------------------

def revenue_by_month(ctx: DataContext):
    df = ctx.sales.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return (
        df.groupby("month", as_index=False)["revenue"]
          .sum()
    )


def sales_by_region(ctx: DataContext):
    return (
        ctx.sales
        .groupby("region", as_index=False)["revenue"]
        .sum()
    )


def sales_by_product(ctx: DataContext):
    return (
        ctx.sales
        .groupby("product", as_index=False)["revenue"]
        .sum()
    )

def sales_by_channel(ctx: DataContext):
    return (
        ctx.sales
        .groupby("channel", as_index=False)["revenue"]
        .sum()
    )


def top_regions(ctx: DataContext, n=3):
    return (
        sales_by_region(ctx)
        .sort_values("revenue", ascending=False)
        .head(n)
    )


def top_products(ctx: DataContext, n=3):
    return (
        sales_by_product(ctx)
        .sort_values("revenue", ascending=False)
        .head(n)
    )



