"""
Navigation components for 7-Eleven Store Intelligence Platform.
Horizontal tab navigation using streamlit-option-menu.
"""

import streamlit as st
from streamlit_option_menu import option_menu
from typing import List, Optional, Dict, Any
from utils.theme import COLORS


def horizontal_tabs(
    tabs: List[str],
    icons: Optional[List[str]] = None,
    default_index: int = 0,
    key: str = "main_nav"
) -> str:
    """
    Create horizontal tab navigation with 7-Eleven branding.

    Args:
        tabs: List of tab names
        icons: Optional list of Bootstrap icons (without 'bi-' prefix)
        default_index: Default selected tab index
        key: Unique key for the navigation component

    Returns:
        Selected tab name
    """
    # Default icons if not provided
    if icons is None:
        default_icons = {
            "Dashboard": "speedometer2",
            "Overview": "grid-3x3-gap",
            "Inventory": "box-seam",
            "Write-Offs": "trash",
            "Team": "people",
            "Analytics": "graph-up",
            "Ask Genie": "chat-dots",
            "Store Map": "geo-alt",
            "Store Details": "shop",
        }
        icons = [default_icons.get(tab, "circle") for tab in tabs]

    # Add CSS to make the nav container full width
    st.markdown("""
    <style>
        div[data-testid="stHorizontalBlock"]:has(> div > div > nav) {
            width: 100% !important;
        }
        nav.nav-menu-container {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=tabs,
        icons=icons,
        default_index=default_index,
        orientation="horizontal",
        key=key,
        styles={
            "container": {
                "padding": "0!important",
                "background-color": COLORS["bg_card"],
                "border-radius": "10px",
                "border": f"2px solid {COLORS['green']}",
                "width": "100%",
                "max-width": "100%",
                "margin": "0",
            },
            "menu-container": {
                "width": "100%",
            },
            "icon": {
                "color": COLORS["text_muted"],
                "font-size": "16px",
            },
            "nav-link": {
                "font-size": "16px",
                "font-weight": "500",
                "text-align": "center",
                "padding": "15px 25px",
                "color": COLORS["text_primary"],
                "background-color": "transparent",
                "border-radius": "0",
                "border-right": f"1px solid {COLORS['border']}",
                "--hover-color": COLORS["bg_secondary"],
                "flex-grow": "1",
            },
            "nav-link-selected": {
                "background-color": COLORS["green"],
                "color": "white",
                "font-weight": "600",
                "border-right": f"1px solid {COLORS['green']}",
            },
        }
    )

    return selected


def sidebar_persona_selector(
    personas: Dict[str, Dict[str, Any]],
    current_persona: str
) -> str:
    """
    Render persona selector in sidebar.

    Args:
        personas: Dictionary of persona configs
        current_persona: Currently selected persona key

    Returns:
        Selected persona key
    """
    persona_options = {v["name"]: k for k, v in personas.items()}
    persona_names = list(persona_options.keys())

    # Get current index
    current_name = personas[current_persona]["name"]
    current_idx = persona_names.index(current_name) if current_name in persona_names else 0

    # Render selector
    selected_name = st.selectbox(
        "",
        persona_names,
        index=current_idx,
        key="persona_selector",
        label_visibility="collapsed"
    )

    return persona_options[selected_name]


def render_user_context(
    persona_name: str,
    persona_icon: str,
    store_name: Optional[str] = None,
    user_name: Optional[str] = None
):
    """
    Render user context in the header area.

    Args:
        persona_name: Display name of current persona
        persona_icon: Emoji icon for persona
        store_name: Optional store name (for store-level personas)
        user_name: Optional user name
    """
    # Create user context display
    context_parts = [f"{persona_icon} {persona_name}"]

    if user_name:
        context_parts.append(f"<span style='color: {COLORS['text_muted']};'>|</span> {user_name}")

    if store_name:
        context_parts.append(f"<span style='color: {COLORS['text_muted']};'>|</span> 🏪 {store_name}")

    context_html = f"""
    <div style="
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 16px;
        display: inline-flex;
        align-items: center;
        gap: 12px;
        font-size: 14px;
        color: {COLORS['text_primary']};
    ">
        {' '.join(context_parts)}
    </div>
    """

    st.markdown(context_html, unsafe_allow_html=True)


def render_store_selector_sidebar(
    stores: List[Dict[str, Any]],
    selected_store: Optional[Dict[str, Any]] = None,
    disabled: bool = False,
    label: str = "📍 Select Store"
) -> Optional[Dict[str, Any]]:
    """
    Render store selector in sidebar.

    Args:
        stores: List of store dictionaries
        selected_store: Currently selected store
        disabled: Whether the selector should be disabled
        label: Label for the selector

    Returns:
        Selected store dictionary or None
    """
    if not stores:
        st.warning("No stores available")
        return None

    store_options = {s["store_name"]: s for s in stores}
    store_names = list(store_options.keys())

    # Get current selection index
    current_idx = 0
    if selected_store:
        current_name = selected_store.get("store_name")
        if current_name in store_names:
            current_idx = store_names.index(current_name)

    selected_name = st.selectbox(
        label,
        store_names,
        index=current_idx,
        disabled=disabled,
        key="store_selector_nav"
    )

    return store_options[selected_name] if selected_name else None


def render_store_info_card(store: Dict[str, Any]):
    """
    Render store information card in sidebar.

    Args:
        store: Store dictionary with store details
    """
    if not store:
        return

    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
    ">
        <div style="font-size: 12px; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 0.5px;">Store Code</div>
        <div style="font-weight: 600; color: white; margin-bottom: 10px; font-size: 1rem;">
            {store.get('store_code', 'N/A')}
        </div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 0.5px;">Location</div>
        <div style="color: white; font-size: 0.95rem;">
            {store.get('city', '')}, {store.get('state', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)
