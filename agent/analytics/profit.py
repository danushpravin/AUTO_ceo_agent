import pandas as pd
from agent.core.context import DataContext

# ------------------------------------------------------
# PROFIT / UNIT ECONOMICS ANALYTICS
# ------------------------------------------------------

def profit_by_product(ctx: DataContext):
    """
    True profit by product (excluding marketing spend)
    """
    df = ctx.sales_enriched.copy()

    agg = (
        df.groupby("product", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            units=("units_sold", "sum"),
            total_cost=("unit_cost", lambda x: (x*df.loc[x.index, "units_sold"]).sum())
        )
    )

    agg["profit"] = agg["revenue"]-agg["total_cost"]
    agg["profit_margin_pct"] = agg["profit"]/agg["revenue"]*100

    return agg

def true_profit_by_channel(ctx: DataContext):
    """
    Net profit by marketing channel:
    revenue - product costs - marketing spend
    """
    df = ctx.sales_enriched.copy()
    #Product costs per channel
    cost_by_channel = (
    df.assign(cost=df["unit_cost"] * df["units_sold"])
      .groupby("channel", as_index=False)["cost"]
      .sum()
      .rename(columns={"cost": "product_cost"})
    )


    revenue_by_channel = (
        df.groupby("channel", as_index=False)["revenue"].sum()
    )

    spend_by_channel = (
        ctx.marketing.groupby("channel", as_index=False)["spend"].sum()
    )

    merged = (
        revenue_by_channel
        .merge(cost_by_channel, on="channel", how="left")
        .merge(spend_by_channel, on="channel", how="left")
        .fillna(0)
    )
    
    merged["net_profit"] = (
        merged["revenue"]
        - merged["product_cost"]
        - merged["spend"]
    )

    merged["profit_margin_pct"] = merged["net_profit"]/merged["revenue"] * 100

    return merged

def true_profit_by_region(ctx: DataContext):
    """
    Net profit by region (excluding marketing spend)
    """
    df = ctx.sales_enriched.copy()

    agg = (
        df.groupby("region", as_index=False)
        .agg(
            revenue = ("revenue", "sum"),
            total_cost = ("unit_cost", lambda x: (x * df.loc[x.index, "units_sold"]).sum())
        )
    )

    agg["net_profit"] = agg["revenue"] - agg["total_cost"]
    agg["profit_margin_pct"] = agg["net_profit"]/agg["revenue"] * 100

    return agg

def loss_making_products(ctx: DataContext):
    """
    Products with high revenue but negative profit.
    """

    profit_df = profit_by_product(ctx)
    return profit_df[profit_df["profit"]<0].sort_values("revenue", ascending=False)

def cost_components_by_product(ctx: DataContext):
    return ctx.unit[[
        "product",
        "selling_price",
        "cogs",
        "packaging_cost",
        "logistics_cost"
    ]]

