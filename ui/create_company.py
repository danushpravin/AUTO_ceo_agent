import streamlit as st
import json
import random
from world.world_factory import create_company

def render_create_company():
    if st.session_state.get("company_created", False):
        return
    

    st.markdown("### Create New Company")

    company_id = st.text_input("Company ID", "Nutrain")

    # ---------------- Normal Settings ----------------
    st.markdown("#### Company Identity")
    description = st.text_input(
        "One-line description (optional)",
        placeholder="e.g. D2C skincare brand selling via Instagram ads"
    )
    st.markdown("#### Basic Settings")
    products = st.text_area(
        "Products (comma separated)",
        "Vanilla Shake, Chocolate Shake",
        help="List all products you want to sell."
    )
    regions = st.text_area(
        "Regions (comma separated)",
        "North, South, East, West",
        help="Regions you will sell in."
    )
    channels = st.text_area(
        "Marketing Channels (comma separated)",
        "Instagram, Google, Influencers",
        help="Channels through which you promote products."
    )

    st.markdown("#### Product Details")
    base_demand_input = st.text_area(
        "Base Daily Demand (comma separated for each product, same order as products)",
        "100,80",
        help="Expected number of units sold per day per product."
    )
    selling_price_input = st.text_area(
        "Selling Price (comma separated for each product)",
        "100,100",
        help="Selling price per product."
    )

    region_weights_input = st.text_area(
        "Region Weights (comma separated, same order as regions, must sum to 1)",
        "0.2,0.3,0.4,0.1",
        help="Relative importance or market size for each region."
    )
    channel_weights_input = st.text_area(
        "Channel Weights (comma separated, same order as channels, must sum to 1)",
        "0.5,0.3,0.2",
        help="Relative effectiveness of each marketing channel."
    )

    starting_stock = st.number_input(
        "Starting stock per product",
        min_value=30,
        max_value=150,
        value=100,
        help="Initial inventory per product."
    )

    # -------- Parse lists --------
    products_list = [p.strip() for p in products.split(",") if p.strip()]
    regions_list = [r.strip() for r in regions.split(",") if r.strip()]
    channels_list = [c.strip() for c in channels.split(",") if c.strip()]

    # Selling prices
    selling_prices = [x.strip() for x in selling_price_input.split(",") if x.strip()]
    if len(selling_prices) != len(products_list):
        st.error("❌ Selling prices must match number of products.")
        st.stop()

    # Base demand
    base_demand = [x.strip() for x in base_demand_input.split(",") if x.strip()]
    if len(base_demand) != len(products_list):
        st.error("❌ Base demand must match number of products.")
        st.stop()

    # Region weights
    region_weights = [x.strip() for x in region_weights_input.split(",") if x.strip()]
    if len(region_weights) != len(regions_list):
        st.error("❌ Region weights must match number of regions.")
        st.stop()

    # Channel weights
    channel_weights = [x.strip() for x in channel_weights_input.split(",") if x.strip()]
    if len(channel_weights) != len(channels_list):
        st.error("❌ Channel weights must match number of channels.")
        st.stop()


    # ---------------- Advanced Settings ----------------
    with st.expander("Advanced Settings (optional)"):
        st.markdown("You can fine-tune everything here. Leave blank to use defaults.")

        # selling_prices already exists from UI
        selling_prices = [float(x.strip()) for x in selling_price_input.split(",")]

        default_unit_econ = {}

        for i, p in enumerate(products.split(",")):
            p = p.strip()
            price = selling_prices[i]

            cogs = int(price * 0.48)          # ~50%
            packaging = int(price * 0.06)     # ~6%
            logistics = int(price * 0.08)     # ~8%

            default_unit_econ[p] = {
                "cogs": cogs,
                "packaging_cost": packaging,
                "logistics_cost": logistics
            }

        unit_econ_json = st.text_area(
            "Unit Economics (JSON)",
            json.dumps(default_unit_econ, indent=2),
            help="Auto-derived from selling price (realistic margins)."
        )


        product_list = [p.strip() for p in products.split(",") if p.strip()]

        easy = random.choice(product_list)
        hard = random.choice([p for p in product_list if p != easy])

        default_production_range = {}

        # base_demand_values already exists from UI
        base_demand_values = [float(x.strip()) for x in base_demand_input.split(",")]

        for i, p in enumerate(product_list):
            demand = base_demand_values[i]

            mean = demand * random.uniform(0.85, 1.05)      # capacity slightly under demand
            low = int(mean * 0.9)    # -10%
            high = int(mean * 1.1)   # +10%

            default_production_range[p] = [low, high]

        
        production_range_json = st.text_area(
            "Production Range (JSON)",
            json.dumps(default_production_range, indent=2),
            help="Min and max units produced per product per day."
        )


        channel_list = [c.strip() for c in channels.split(",") if c.strip()]
        good = random.choice(channel_list)
        bad = random.choice([c for c in channel_list if c != good])

        default_channel_behavior = {}

        for c in channel_list:
            if c == good:
                # Hero channel
                default_channel_behavior[c] = {
                    "ctr": [0.03, 0.06],
                    "cvr": [0.12, 0.25],
                    "cpc": [0.3, 0.8]
                }
            elif c == bad:
                # Trash channel
                default_channel_behavior[c] = {
                    "ctr": [0.005, 0.015],
                    "cvr": [0.01, 0.05],
                    "cpc": [1.5, 3.0]
                }
            else:
                # Average channels
                default_channel_behavior[c] = {
                    "ctr": [0.01, 0.03],
                    "cvr": [0.05, 0.15],
                    "cpc": [0.6, 1.5]
                }

        channel_behavior_json = st.text_area(
            "Channel Behavior (JSON)",
            json.dumps(default_channel_behavior, indent=2),
            help="CTR, CVR, CPC for each marketing channel."
        )

        demand_noise_input = st.text_area(
            "Demand Noise (min,max)",
            "0.8,1.2",
            help="Random multiplier for daily demand (e.g., 0.8-1.2)"
        )

    if st.button("Create Company"):
        # ---------------- Parsing Basic Inputs ----------------
        product_list = [p.strip() for p in products.split(",")]
        region_list = [r.strip() for r in regions.split(",")]
        channel_list = [c.strip() for c in channels.split(",")]

        base_demand_values = [float(x.strip()) for x in base_demand_input.split(",")]
        region_weights = [float(x.strip()) for x in region_weights_input.split(",")]
        channel_weights = [float(x.strip()) for x in channel_weights_input.split(",")]
        selling_prices = [float(x.strip()) for x in selling_price_input.split(",")]

        # ---------------- Parsing Advanced Inputs ----------------
        try:
            unit_econ = json.loads(unit_econ_json)
        except:
            unit_econ = {p: {"cogs":60, "packaging_cost":5, "logistics_cost":10} for p in product_list}

        for i, p in enumerate(product_list):
            unit_econ.setdefault(p, {"cogs":60, "packaging_cost":5, "logistics_cost":10})
            unit_econ[p]["selling_price"] = selling_prices[i]

        try:
            production_range = json.loads(production_range_json)
        except:
            production_range = {p: [20,60] for p in product_list}

        try:
            channel_behavior = json.loads(channel_behavior_json)
        except:
            channel_behavior = {c: {"ctr":[0.01,0.03], "cvr":[0.05,0.15], "cpc":[0.5,2.0]} for c in channel_list}

        try:
            demand_noise = [float(x.strip()) for x in demand_noise_input.split(",")]
        except:
            demand_noise = [0.8,1.2]

        # ---------------- Create Config ----------------
        form = {
            "description": description,
            "products": product_list,
            "regions": region_list,
            "channels": channel_list,
            "unit_econ": unit_econ,
            "base_demand": {p: base_demand_values[i] for i,p in enumerate(product_list)},
            "region_weights": {r: region_weights[i] for i,r in enumerate(region_list)},
            "channel_weights": {c: channel_weights[i] for i,c in enumerate(channel_list)},
            "channel_behavior": channel_behavior,
            "starting_stock": starting_stock,
            "production_range": production_range,
            "demand_noise": demand_noise
        }

        sandbox_id = f"sandbox_{company_id}"
        create_company(sandbox_id, form)
        st.session_state.company_created = True
        st.session_state.company_id = sandbox_id
        st.success(f"Company '{company_id}' created.")
        st.rerun()