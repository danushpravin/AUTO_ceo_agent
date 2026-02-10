import streamlit as st
from agent.agent import run_ceo_agent
from pathlib import Path
import base64

def render_auto_panel(company_id):
    # --- Minimal header with icon ---
    logo_path = "ui/assets/auto_logo.png"
    with open(logo_path, "rb") as f:
        data = f.read()
    logo_base64 = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <img src="data:image/png;base64,{logo_base64}" width="24" />
            <h2 style="margin: 0;">AUTO</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.caption("""
        **Autonomous Executive Intelligence**

        💡 Try asking AUTO things like:  
        - Why is profit down?  
        - What’s our biggest risk?  
        - Which product should I double down on?  

        ⚡ Stress-test the company with **Shock Injectors**: inject a demand, supply, or cost shock, then ask AUTO what happened.  

        🔄 Use the **Reset AUTO** button to get a fresh executive read whenever you inject shocks or simulate a new week.
        """)

    if "auto_messages" not in st.session_state:
        st.session_state.auto_messages = []

    if "auto_initialized_for" not in st.session_state:
        st.session_state.auto_initialized_for = None

    if st.button("Reset AUTO"):
        st.session_state.auto_messages = []
        st.session_state.auto_initialized_for = None
        st.rerun()

    # ---- REAL FIX ----
    if st.session_state.auto_initialized_for != company_id:
        st.session_state.auto_initialized_for = company_id
        st.session_state.auto_messages = []

        with st.spinner("AUTO initializing..."):
            brief = run_ceo_agent(
                [{"role": "user", "content": "Generate today’s executive brief for this company."}],
                company_id
            )

        st.session_state.auto_messages.append({
            "role": "assistant",
            "content": brief
        })

    # Render chat
    for msg in st.session_state.auto_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    auto_query = st.chat_input("Command AUTO")

    if auto_query:
        st.session_state.auto_messages.append({
            "role": "user",
            "content": auto_query
        })

        with st.spinner("Thinking..."):
            response = run_ceo_agent(
                st.session_state.auto_messages,
                company_id
            )

        st.session_state.auto_messages.append({
            "role": "assistant",
            "content": response
        })
        st.rerun()
