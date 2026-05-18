"""
7-Eleven Store Intelligence Platform - Streamlit App
Main entry point with persona-based views and horizontal navigation.
"""

import streamlit as st
from typing import Optional, Dict, Any

from utils.db import get_db
from utils.theme import get_css, COLORS
from utils.personas import (
    PERSONAS, get_persona_tabs, get_persona_tab_icons,
    can_select_store, get_persona_display_info, get_default_store_id
)
from utils.navigation import (
    horizontal_tabs, sidebar_persona_selector,
    render_store_info_card, render_store_selector_sidebar
)
from components.personas.store_associate import render_store_associate_content
from components.personas.store_manager import render_store_manager_content
from components.personas.regional_manager import render_regional_manager_content


# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="7-Eleven Store Intelligence",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/7-eleven_logo.svg/200px-7-eleven_logo.svg.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_css(), unsafe_allow_html=True)


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "persona": "store_manager",  # Default persona
        "selected_store": None,
        "assigned_store_id": None,  # For store-level personas
        "selected_store_for_drilldown": None,  # For regional drill-down
        "stores_loaded": False,
        "stores_list": [],
        "current_tab": None,  # Will be set based on persona
        "genie_messages": [],
        "pending_question": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_stores():
    """Load stores into session state."""
    if not st.session_state.stores_loaded:
        try:
            db = get_db()
            stores = db.get_stores()
            st.session_state.stores_list = stores if stores else []
            st.session_state.stores_loaded = True

            # Set default store if not selected
            if stores and not st.session_state.selected_store:
                st.session_state.selected_store = stores[0]
                st.session_state.assigned_store_id = stores[0]["store_id"]
        except Exception as e:
            st.session_state.stores_loaded = True  # Prevent retry loop
            st.session_state.stores_list = []
            st.session_state.load_error = str(e)


def render_sidebar():
    """Render the sidebar with persona selector and store info."""
    with st.sidebar:
        # Logo and title
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("assets/logo.png", width=100)
        st.markdown("""
        <div style="text-align: center; margin-top: -10px; margin-bottom: 15px;">
            <div style="font-size: 1.1rem; font-weight: 600; color: white; letter-spacing: 0.5px;">
                Store Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr style='border-color: rgba(255,255,255,0.2); margin: 0 0 15px 0;'>", unsafe_allow_html=True)

        # Persona selector
        st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 5px;'>Select Role:</p>", unsafe_allow_html=True)
        new_persona = sidebar_persona_selector(PERSONAS, st.session_state.persona)

        # Handle persona change
        if new_persona != st.session_state.persona:
            st.session_state.persona = new_persona
            st.session_state.current_tab = None  # Reset tab
            st.rerun()

        # Get persona info
        persona_info = get_persona_display_info(st.session_state.persona)

        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            font-size: 0.85rem;
            color: rgba(255,255,255,0.8);
        ">
            {persona_info['description']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color: rgba(255,255,255,0.2); margin: 15px 0;'>", unsafe_allow_html=True)

        # Store selector (conditional based on persona)
        stores = st.session_state.stores_list

        if st.session_state.persona == "regional_manager":
            # Regional manager can select store for drill-down
            st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 5px;'>Store Drill-down (Optional):</p>", unsafe_allow_html=True)

            if stores:
                store_options = ["All Stores"] + [s["store_name"] for s in stores]

                current_idx = 0
                if st.session_state.selected_store_for_drilldown:
                    name = st.session_state.selected_store_for_drilldown.get("store_name")
                    if name in store_options:
                        current_idx = store_options.index(name)

                selected_name = st.selectbox(
                    "Select Store",
                    store_options,
                    index=current_idx,
                    key="sidebar_store_selector"
                )

                if selected_name == "All Stores":
                    st.session_state.selected_store_for_drilldown = None
                else:
                    store = next((s for s in stores if s["store_name"] == selected_name), None)
                    if store:
                        st.session_state.selected_store_for_drilldown = store
                        render_store_info_card(store)

        else:
            # Store Associate and Store Manager - assigned store only
            st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 5px;'>Your Assigned Store:</p>", unsafe_allow_html=True)

            if st.session_state.selected_store:
                store = st.session_state.selected_store
                st.markdown(f"<p style='color: white; font-size: 1.1rem; font-weight: 600; margin: 0;'>{store['store_name']}</p>", unsafe_allow_html=True)
                render_store_info_card(store)

                # Allow changing store for demo purposes
                with st.expander("Change Store (Demo)"):
                    if stores:
                        store_options = {s["store_name"]: s for s in stores}
                        store_names = list(store_options.keys())

                        current_idx = 0
                        current_name = store.get("store_name")
                        if current_name in store_names:
                            current_idx = store_names.index(current_name)

                        new_store_name = st.selectbox(
                            "Select",
                            store_names,
                            index=current_idx,
                            key="demo_store_selector"
                        )

                        if new_store_name and store_options[new_store_name] != st.session_state.selected_store:
                            st.session_state.selected_store = store_options[new_store_name]
                            st.session_state.assigned_store_id = store_options[new_store_name]["store_id"]
                            st.rerun()

        st.markdown("<hr style='border-color: rgba(255,255,255,0.2); margin: 15px 0;'>", unsafe_allow_html=True)

        # Footer
        st.markdown("<p style='color: rgba(255,255,255,0.7); font-size: 0.8rem; text-align: center;'>Powered by Databricks</p>", unsafe_allow_html=True)


def render_header():
    """Render the main header with banner and user context."""
    import base64

    persona_info = get_persona_display_info(st.session_state.persona)

    # Build context string
    if st.session_state.persona == "regional_manager":
        if st.session_state.selected_store_for_drilldown:
            store_context = st.session_state.selected_store_for_drilldown['store_name']
        else:
            store_context = "All Stores"
    else:
        store_context = st.session_state.selected_store['store_name'] if st.session_state.selected_store else ""

    # Load persona image as base64
    persona_image_b64 = ""
    if persona_info.get("image"):
        try:
            with open(persona_info["image"], "rb") as img_file:
                persona_image_b64 = base64.b64encode(img_file.read()).decode()
        except FileNotFoundError:
            pass

    # Build persona display (image or fallback to icon)
    if persona_image_b64:
        persona_display = f'<img src="data:image/png;base64,{persona_image_b64}" style="width: 60px; height: 60px; border-radius: 50%; border: 2px solid white; object-fit: cover;">'
    else:
        persona_display = f'<div style="font-size: 2rem;">{persona_info.get("icon", "👤")}</div>'

    # Render banner
    st.markdown(f"""<div style="background: linear-gradient(135deg, {COLORS['green']} 0%, {COLORS['green_dark']} 100%); border-radius: 12px; padding: 20px 30px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
<div>
<div style="font-size: 1.6rem; font-weight: 700; color: white; margin-bottom: 5px;">7-Eleven Store Intelligence</div>
<div style="font-size: 0.95rem; color: rgba(255,255,255,0.85);">{store_context}</div>
</div>
<div style="display: flex; align-items: center; gap: 15px;">
<div style="text-align: right;">
<div style="font-size: 1.1rem; font-weight: 600; color: white;">{persona_info['name']}</div>
</div>
{persona_display}
</div>
</div>""", unsafe_allow_html=True)


def render_navigation():
    """Render horizontal tab navigation."""
    tabs = get_persona_tabs(st.session_state.persona)
    icons = get_persona_tab_icons(st.session_state.persona)

    # Get default tab index
    default_index = 0
    if st.session_state.current_tab and st.session_state.current_tab in tabs:
        default_index = tabs.index(st.session_state.current_tab)

    selected_tab = horizontal_tabs(
        tabs=tabs,
        icons=icons,
        default_index=default_index,
        key=f"nav_{st.session_state.persona}"
    )

    # Update current tab
    st.session_state.current_tab = selected_tab

    return selected_tab


def render_content(tab: str):
    """Render content based on persona and selected tab."""
    persona = st.session_state.persona

    # If get_stores() failed during load_stores(), show the actual exception so
    # operators can diagnose. Without this, every failure mode (permission
    # denied, missing column, network error, etc.) looks identical to "no data".
    load_error = st.session_state.get("load_error")
    if load_error:
        st.error(
            f"Could not load stores from the warehouse. The underlying error was:\n\n"
            f"```\n{load_error}\n```\n\n"
            "Check your `DATABRICKS_CATALOG` / `DATABRICKS_SCHEMA` / "
            "`DATABRICKS_WAREHOUSE_ID` in `app-streamlit/app.yaml`, the app "
            "service principal's permissions on the warehouse and schema, and "
            "that `setup_all` ran cleanly."
        )

    if persona == "store_associate":
        store = st.session_state.selected_store
        if store:
            render_store_associate_content(tab, store)
        else:
            st.warning("No store assigned. Please contact your manager.")

    elif persona == "store_manager":
        store = st.session_state.selected_store
        if store:
            render_store_manager_content(tab, store)
        else:
            st.warning("No store assigned. Please contact your regional manager.")

    elif persona == "regional_manager":
        stores = st.session_state.stores_list
        selected_store = st.session_state.selected_store_for_drilldown
        render_regional_manager_content(tab, stores, selected_store)


def main():
    """Main application entry point."""
    # Initialize
    init_session_state()
    load_stores()

    # Render sidebar
    render_sidebar()

    # Render header banner
    render_header()

    # Render navigation
    selected_tab = render_navigation()

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Render content
    render_content(selected_tab)


# Run the app
if __name__ == "__main__":
    main()
else:
    main()
