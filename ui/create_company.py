import streamlit as st
import json
import random
from openai import OpenAI
from world.world_factory import create_company
from world.generate_world import flat_demand_profile

client = OpenAI()


# -------------------------------------------------------
# LLM DEMAND PROFILE GENERATOR
# -------------------------------------------------------

DEMAND_PROFILE_SYSTEM = """
You are a business simulation expert. Given a company description and product list,
generate a realistic DEMAND_PROFILE for each product.

Return ONLY valid JSON — no explanation, no markdown, no code fences.

The JSON must follow this exact structure:
{
  "Product Name": {
    "seasonality": [12 floats, one per month Jan-Dec, representing demand multiplier],
    "trend": {
      "type": "growth" | "decay" | "stable",
      "start": float,
      "peak_month": int (1-12),
      "end": float
    },
    "events": [
      {
        "name": "string",
        "date": "MM-DD",
        "duration_days": int,
        "multiplier": float
      }
    ]
  }
}

Rules:
- seasonality values should be realistic for the product category and region (India)
- trend reflects product lifecycle: new products grow, mature products are stable, declining products decay
- events should be relevant to the product category (e.g. Diwali for gifting, Valentine's for beauty, New Year for fitness)
- multipliers should be realistic: seasonality 0.6-1.5, events 1.2-2.5
- trend start and end should be between 0.5 and 1.2
- include 2-4 relevant events per product
- all 12 seasonality values must be present
"""


def generate_demand_profile_llm(description: str, products: list) -> dict:
    prompt = f"""
Company description: {description}
Products: {', '.join(products)}

Generate a DEMAND_PROFILE for each product based on the business context above.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": DEMAND_PROFILE_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.4,
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        profile = json.loads(raw)

        result = {}
        for p in products:
            if p in profile and _valid_profile(profile[p]):
                result[p] = profile[p]
            else:
                result[p] = flat_demand_profile()

        return result

    except Exception:
        return {p: flat_demand_profile() for p in products}


def _valid_profile(profile: dict) -> bool:
    try:
        assert isinstance(profile.get("seasonality"), list)
        assert len(profile["seasonality"]) == 12
        assert all(isinstance(v, (int, float)) for v in profile["seasonality"])
        assert isinstance(profile.get("trend"), dict)
        assert profile["trend"].get("type") in ("growth", "decay", "stable")
        assert isinstance(profile.get("events"), list)
        return True
    except (AssertionError, TypeError):
        return False


# -------------------------------------------------------
# STEP 1 — BASIC DETAILS
# -------------------------------------------------------

def render_step1():
    st.markdown("### Create New Company")
    st.markdown("#### Step 1 of 2 — Basic Details")

    company_id = st.text_input("Company ID", st.session_state.get("s1_company_id", "MyBrand"))
    description = st.text_input(
        "One-line description",
        st.session_state.get("s1_description", ""),
        placeholder="e.g. D2C skincare brand selling serums and creams via Instagram ads in India"
    )
    products = st.text_area(
        "Products (comma separated)",
        st.session_state.get("s1_products", "Product A, Product B"),
    )
    regions = st.text_area(
        "Regions (comma separated)",
        st.session_state.get("s1_regions", "North, South, East, West"),
    )
    channels = st.text_area(
        "Marketing Channels (comma separated)",
        st.session_state.get("s1_channels", "Instagram, Google, Influencers"),
    )
    base_demand_input = st.text_area(
        "Base Daily Demand (comma separated, same order as products)",
        st.session_state.get("s1_base_demand", "50, 50"),
        help="Expected units sold per day per product."
    )
    selling_price_input = st.text_area(
        "Selling Price (comma separated, same order as products)",
        st.session_state.get("s1_selling_price", "999, 999"),
    )
    region_weights_input = st.text_area(
        "Region Weights (comma separated, must sum to 1)",
        st.session_state.get("s1_region_weights", "0.25, 0.25, 0.25, 0.25"),
    )
    channel_weights_input = st.text_area(
        "Channel Weights (comma separated, must sum to 1)",
        st.session_state.get("s1_channel_weights", "0.5, 0.3, 0.2"),
    )
    starting_stock = st.number_input(
        "Starting stock per product",
        min_value=30, max_value=150,
        value=st.session_state.get("s1_starting_stock", 80),
    )

    # Validation
    products_list = [p.strip() for p in products.split(",") if p.strip()]
    regions_list = [r.strip() for r in regions.split(",") if r.strip()]
    channels_list = [c.strip() for c in channels.split(",") if c.strip()]
    selling_prices = [x.strip() for x in selling_price_input.split(",") if x.strip()]
    base_demand = [x.strip() for x in base_demand_input.split(",") if x.strip()]
    region_weights = [x.strip() for x in region_weights_input.split(",") if x.strip()]
    channel_weights = [x.strip() for x in channel_weights_input.split(",") if x.strip()]

    errors = []
    if len(selling_prices) != len(products_list):
        errors.append("Selling prices must match number of products.")
    if len(base_demand) != len(products_list):
        errors.append("Base demand must match number of products.")
    if len(region_weights) != len(regions_list):
        errors.append("Region weights must match number of regions.")
    if len(channel_weights) != len(channels_list):
        errors.append("Channel weights must match number of channels.")

    for e in errors:
        st.error(f"❌ {e}")

    if st.button("Next →", disabled=bool(errors)):
        st.session_state.s1_company_id = company_id
        st.session_state.s1_description = description
        st.session_state.s1_products = products
        st.session_state.s1_regions = regions
        st.session_state.s1_channels = channels
        st.session_state.s1_base_demand = base_demand_input
        st.session_state.s1_selling_price = selling_price_input
        st.session_state.s1_region_weights = region_weights_input
        st.session_state.s1_channel_weights = channel_weights_input
        st.session_state.s1_starting_stock = starting_stock
        st.session_state.s1_products_list = products_list
        st.session_state.s1_regions_list = regions_list
        st.session_state.s1_channels_list = channels_list
        st.session_state.s1_selling_prices_f = [float(x) for x in selling_prices]
        st.session_state.s1_base_demand_f = [float(x) for x in base_demand]
        st.session_state.s1_region_weights_f = [float(x) for x in region_weights]
        st.session_state.s1_channel_weights_f = [float(x) for x in channel_weights]

        # Clear previously generated demand profile when basic details change
        st.session_state.pop("s2_demand_profile", None)

        st.session_state.create_step = 2
        st.rerun()


# -------------------------------------------------------
# STEP 2 — ADVANCED SETTINGS + DEMAND PROFILE
# -------------------------------------------------------

def render_step2():
    st.markdown("### Create New Company")
    st.markdown("#### Step 2 of 2 — Advanced Settings")

    company_id = st.session_state.s1_company_id
    description = st.session_state.s1_description
    products_list = st.session_state.s1_products_list
    regions_list = st.session_state.s1_regions_list
    channels_list = st.session_state.s1_channels_list
    selling_prices_f = st.session_state.s1_selling_prices_f
    base_demand_f = st.session_state.s1_base_demand_f
    region_weights_f = st.session_state.s1_region_weights_f
    channel_weights_f = st.session_state.s1_channel_weights_f
    starting_stock = st.session_state.s1_starting_stock

    with st.container(border=True):
        st.caption(
            f"**Company:** {company_id}  |  "
            f"**Products:** {', '.join(products_list)}  |  "
            f"**Channels:** {', '.join(channels_list)}"
        )
        if st.button("← Back"):
            st.session_state.create_step = 1
            st.rerun()

    # Unit Economics
    st.markdown("##### Unit Economics")
    default_unit_econ = {}
    for i, p in enumerate(products_list):
        price = selling_prices_f[i]
        default_unit_econ[p] = {
            "cogs": int(price * 0.48),
            "packaging_cost": int(price * 0.06),
            "logistics_cost": int(price * 0.08),
        }
    unit_econ_json = st.text_area(
        "Unit Economics (JSON)",
        json.dumps(default_unit_econ, indent=2),
        help="cogs ~48%, packaging ~6%, logistics ~8% of selling price."
    )

    # Production Range
    st.markdown("##### Production Range")
    default_production_range = {}
    for i, p in enumerate(products_list):
        demand = base_demand_f[i]
        mean = demand * random.uniform(0.85, 1.05)
        default_production_range[p] = [int(mean * 0.9), int(mean * 1.1)]
    production_range_json = st.text_area(
        "Production Range (JSON)",
        json.dumps(default_production_range, indent=2),
        help="Min and max units produced per product per day."
    )

    # Channel Behavior
    st.markdown("##### Channel Behavior")
    good = random.choice(channels_list)
    remaining = [c for c in channels_list if c != good]
    bad = random.choice(remaining) if remaining else good
    default_channel_behavior = {}
    for c in channels_list:
        if c == good:
            default_channel_behavior[c] = {"ctr": [0.03, 0.06], "cvr": [0.12, 0.25], "cpc": [0.3, 0.8]}
        elif c == bad:
            default_channel_behavior[c] = {"ctr": [0.005, 0.015], "cvr": [0.01, 0.05], "cpc": [1.5, 3.0]}
        else:
            default_channel_behavior[c] = {"ctr": [0.01, 0.03], "cvr": [0.05, 0.15], "cpc": [0.6, 1.5]}
    channel_behavior_json = st.text_area(
        "Channel Behavior (JSON)",
        json.dumps(default_channel_behavior, indent=2),
        help="CTR, CVR, CPC per channel. spend_inefficiency auto-generated if omitted."
    )

    demand_noise_input = st.text_input("Demand Noise (min, max)", "0.8, 1.2")

    # Demand Profile
    st.markdown("---")
    st.markdown("##### Demand Profile")
    st.caption(
        "Seasonality, growth trend, and event spikes per product. "
        "Click **Generate** to auto-infer from your company description — edit if needed."
    )

    col_gen, _ = st.columns([0.4, 0.6])
    with col_gen:
        if st.button("✨ Generate Demand Profile", type="primary"):
            with st.spinner("Inferring demand patterns..."):
                generated = generate_demand_profile_llm(
                    description or company_id,
                    products_list
                )
                st.session_state.s2_demand_profile = json.dumps(generated, indent=2)
            st.success("Generated — review below.")

    if "s2_demand_profile" not in st.session_state:
        st.session_state.s2_demand_profile = json.dumps(
            {p: flat_demand_profile() for p in products_list}, indent=2
        )

    st.session_state["demand_profile_editor"] = st.session_state.s2_demand_profile

    demand_profile_json = st.text_area(
        "Demand Profile (JSON)",
        height=400,
        key="demand_profile_editor"
    )

    # Create Company
    st.markdown("---")
    if st.button("🚀 Create Company", type="primary"):
        try:
            unit_econ = json.loads(unit_econ_json)
        except Exception:
            unit_econ = {p: {"cogs": 60, "packaging_cost": 5, "logistics_cost": 10} for p in products_list}

        for i, p in enumerate(products_list):
            unit_econ.setdefault(p, {"cogs": 60, "packaging_cost": 5, "logistics_cost": 10})
            unit_econ[p]["selling_price"] = selling_prices_f[i]

        try:
            production_range = json.loads(production_range_json)
        except Exception:
            production_range = {p: [20, 60] for p in products_list}

        try:
            channel_behavior = json.loads(channel_behavior_json)
        except Exception:
            channel_behavior = {c: {"ctr": [0.01, 0.03], "cvr": [0.05, 0.15], "cpc": [0.5, 2.0]} for c in channels_list}

        try:
            demand_noise = [float(x.strip()) for x in demand_noise_input.split(",")]
        except Exception:
            demand_noise = [0.8, 1.2]

        try:
            demand_profile = json.loads(demand_profile_json)
        except Exception:
            demand_profile = {p: flat_demand_profile() for p in products_list}

        form = {
            "description": description,
            "products": products_list,
            "regions": regions_list,
            "channels": channels_list,
            "unit_econ": unit_econ,
            "base_demand": {p: base_demand_f[i] for i, p in enumerate(products_list)},
            "region_weights": {r: region_weights_f[i] for i, r in enumerate(regions_list)},
            "channel_weights": {c: channel_weights_f[i] for i, c in enumerate(channels_list)},
            "channel_behavior": channel_behavior,
            "starting_stock": starting_stock,
            "production_range": production_range,
            "demand_noise": demand_noise,
            "demand_profile": demand_profile,
        }

        sandbox_id = f"sandbox_{company_id}"
        with st.spinner(f"Generating one year of data for {company_id}..."):
            create_company(sandbox_id, form)

        st.session_state.company_created = True
        st.session_state.company_id = sandbox_id

        for key in list(st.session_state.keys()):
            if key.startswith("s1_") or key.startswith("s2_"):
                del st.session_state[key]
        st.session_state.create_step = 1

        st.success(f"✅ Company '{company_id}' created.")
        st.rerun()


# -------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------

def render_create_company():
    if st.session_state.get("company_created", False):
        return

    if "create_step" not in st.session_state:
        st.session_state.create_step = 1

    if st.session_state.create_step == 1:
        render_step1()
    else:
        render_step2()