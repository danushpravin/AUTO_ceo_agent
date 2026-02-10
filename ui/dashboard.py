import streamlit as st
import pandas as pd
from pathlib import Path
from copy import deepcopy
from world.world_factory import simulate_next_day_ui
from ui.config_io import load_config, save_config
from ui.scenarios import recession_week, viral_spike, marketing_death_spiral


def panel_help(text):
    st.markdown(
        f"<div style='text-align:right; color:#999;' title='{text}'>ⓘ</div>",
        unsafe_allow_html=True
    )



def render_dashboard(company_id):
    if company_id.startswith("sandbox_"):
        display_name = company_id[len("sandbox_"):]
    else:
        display_name = company_id

    st.markdown(f"## Company: {display_name}")
    config = load_config(company_id)
    if config.get("description"):
        st.caption(config["description"])

    DATA_DIR = Path("data/companies") / company_id

    sales = pd.read_csv(DATA_DIR / "sales.csv", parse_dates=["date"])
    marketing = pd.read_csv(DATA_DIR / "marketing.csv", parse_dates=["date"])
    inventory = pd.read_csv(DATA_DIR / "inventory.csv", parse_dates=["date"])
    econ = pd.read_csv(DATA_DIR / "unit_economics.csv")

    # ---------- Helpers ----------
    daily_rev = sales.groupby("date")["revenue"].sum()
    daily_units = sales.groupby("date")["units_sold"].sum()
    daily_cac = sales.groupby("date")["CAC"].mean()

    def trend_delta(series):
        last_7 = series.tail(7).mean()
        prev_7 = series.tail(14).head(7).mean()
        if pd.isna(prev_7) or prev_7 == 0:
            return None
        return (last_7 - prev_7) / prev_7 * 100
    


    # ---------- KPIs ----------
    last_7_revenue = daily_rev.tail(7).sum()
    last_7_units = daily_units.tail(7).sum()
    last_7_cac = daily_cac.tail(7).mean()

    stockouts = (
        inventory[inventory["stockout_flag"] == "Yes"]
        .groupby("date")
        .size()
        .shape[0]
    )

    rev_delta = trend_delta(daily_rev)
    unit_delta = trend_delta(daily_units)
    cac_delta = trend_delta(daily_cac)


    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Revenue (Last 7 Days)",
        f"₹{last_7_revenue:,.0f}",
        f"{rev_delta:+.1f}%" if rev_delta is not None else None,
        border=True
    )
    k2.metric(
        "Units Sold (Last 7 Days)",
        f"{last_7_units:,}",
        f"{unit_delta:+.1f}%" if unit_delta is not None else None,
        border=True
    )
    k3.metric(
        "Avg CAC (Last 7 Days)",
        f"₹{last_7_cac:.2f}",
        delta=None,  # hide Streamlit delta
        border=True
    )
    k4.metric(
        "Stockout Days (All Time)",
        stockouts,
        border=True
    )

    st.divider()

    # ---------- Revenue Trend ----------
    with st.container(border=True):
        t1, t2 = st.columns([0.95, 0.05])
        with t1:
            st.subheader("Revenue Trend")
        with t2:
            panel_help("Daily revenue aggregated across all products.")
        st.line_chart(daily_rev)

    # ---------- Units Trend ----------
    with st.container(border=True):
        t1, t2 = st.columns([0.95, 0.05])
        with t1:
            st.subheader("Units Sold Trend")
        with t2:
            panel_help("Daily units sold across all products.")
        st.line_chart(daily_units)

    # ---------- CAC Trend ----------
    with st.container(border=True):
        t1, t2 = st.columns([0.95, 0.05])
        with t1:
            st.subheader("CAC Trend")
        with t2:
            panel_help("Average customer acquisition cost per day.")
        st.line_chart(daily_cac)

    # ---------- Marketing Performance ----------
    with st.container(border=True):
        t1, t2 = st.columns([0.95,0.05])
        with t1:
            st.subheader("Marketing Spend vs Revenue")
        with t2:
            panel_help("Total marketing spend and revenue by channel.")
        channel_perf = marketing.groupby("channel")[["spend","revenue"]].sum()
        st.bar_chart(channel_perf)

    # ---------- Inventory ----------
    with st.container(border=True):
        t1, t2 = st.columns([0.95, 0.05])
        with t1:
            st.subheader("Inventory Status")
        with t2:
            panel_help("Current stock levels and lost demand.")
        latest_stock = (
            inventory.sort_values("date")
            .groupby("product")
            .tail(1)[["product","closing_stock","lost_demand"]]
        )
        st.dataframe(latest_stock, use_container_width=True)

    # ---------- Unit Economics ----------
    with st.container(border=True):
        t1, t2 = st.columns([0.95, 0.05])
        with t1:
            st.subheader("Unit Economics")
        with t2:
            panel_help("Costs and margins per product.")
        st.dataframe(econ, use_container_width=True)

    st.divider()

    # ---------- Simulation Controls ----------
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Simulate Next Day"):
            simulate_next_day_ui(company_id, {})
            st.success("Simulated next day.")
            st.rerun()

    with col2:
        if st.button("Simulate Next Week"):
            for _ in range(7):
                simulate_next_day_ui(company_id, {})
            st.success("Simulated next week.")
            st.rerun()

    # ---------- Shock Injectors ----------
    t1, t2 = st.columns([0.95, 0.05])
    with t1:
        st.subheader("Shock Injectors")
    with t2:
        panel_help("Inject external scenarios.")

    c1, c2, c3 = st.columns(3)

    def run_scenario(scenario_fn):
        original = load_config(company_id)
        mutated = deepcopy(original)
        scenario_fn(mutated)
        save_config(company_id, mutated)
        for _ in range(7):
            simulate_next_day_ui(company_id, {})
        save_config(company_id, original)
        st.rerun()

    with c1:
        if st.button("Recession Week"):
            run_scenario(recession_week)

    with c2:
        if st.button("Viral Demand Spike"):
            run_scenario(viral_spike)

    with c3:
        if st.button("Marketing Death Spiral"):
            run_scenario(marketing_death_spiral)
