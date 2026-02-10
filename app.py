import streamlit as st
from ui.create_company import render_create_company
from ui.dashboard import render_dashboard
from ui.auto_panel import render_auto_panel
from pathlib import Path
import shutil

DATA_ROOT = Path("data/companies")

def cleanup_sandbox():
    for d in DATA_ROOT.iterdir():
        if d.is_dir() and d.name.startswith("sandbox_"):
            shutil.rmtree(d)



def get_existing_companies():
    if not DATA_ROOT.exists():
        return []
    return [d.name for d in DATA_ROOT.iterdir() if d.is_dir()]

st.set_page_config(
    page_title="AUTO — Executive Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "company_id" not in st.session_state:
    st.session_state.company_id = None


if st.session_state.company_id is None:
    cleanup_sandbox()

if "show_help" not in st.session_state:
    st.session_state.show_help = False

# ---------- ENTRY ----------
if st.session_state.company_id is None:

    st.markdown("## AUTO — Autonomous Executive Intelligence")
    st.markdown(
        "Talk to a living company. Stress-test reality. "
        "Watch KPIs and trends update in real-time, "
        "and get explanations from your executive analyst, AUTO."
    )

    # Optional: add a little description for demo / create
    st.markdown("---")
    st.markdown(
        "**Explore Demo:** Step into a pre-built D2C company with a few products and marketing channels. "
        "See how sales, marketing, inventory, and unit economics interact in real time. "
        "Interact with AUTO to understand what's happening, run shocks, and get executive insights.\n\n"
        "**Create My Own Company:** Start from scratch and configure your own products, marketing, and sales channels. "
        "This company exists only for this session and will be erased when you reload or leave the app. "
        "Watch AUTO provide real-time guidance and analytics."
    )

    mode = st.radio(
        "How would you like to start?",
        ["Explore demo company (recommended)", "Create my own company"]
    )

    companies = get_existing_companies()

    if mode == "Explore demo company (recommended)":
        if not companies:
            st.warning("No demo companies found.")
        else:
            selected = st.selectbox(
                "Choose a demo company",
                companies
            )
            if st.button("Enter Demo"):
                st.session_state.company_id = selected
                st.session_state.show_tutorial = None
                st.rerun()
    else:
        render_create_company()

    st.stop()




# ---------- TOP-RIGHT INSTRUCTIONS EXPANDER ----------
col_main, col_right = st.columns([0.01, 10])

with col_right:
    with st.expander("Instructions", expanded=st.session_state.show_help):
        st.session_state.show_help = True
        st.markdown("## Dashboard Guide")
        st.markdown("""
### What you're seeing
This is a live business simulation.  
Every number reflects a real underlying system.

---

### KPIs (top panels)
Executive-level health metrics:
- Revenue
- Units
- CAC
- Stockouts

They update when reality changes.

---

### AUTO (left sidebar)
Your executive analyst.

Ask things like:
- Why is profit down?
- What’s the biggest risk?
- Which product should I double down on?

AUTO interprets the **current state only**.

---

### Shock Injectors
Stress-test the company:
- Demand shocks
- Supply shocks
- Marketing Inefficiency

Reality updates instantly.

Then ask AUTO what happened.

---

### Reset AUTO
AUTO is deterministic.

Reset when:
- You inject shocks
- You simulate a new week or day
- You want a clean executive read

Reset forces a fresh interpretation.
""")
# ---------- APP ----------
render_dashboard(st.session_state.company_id)

with st.sidebar:
    render_auto_panel(st.session_state.company_id)




