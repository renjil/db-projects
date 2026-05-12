"""
Persona definitions and configurations for 7-Eleven Store Intelligence Platform.
Defines roles, permissions, and tab configurations for different user types.
"""

from typing import Dict, List, Any, Optional

# Persona definitions with tabs, icons, and permissions
PERSONAS: Dict[str, Dict[str, Any]] = {
    "store_associate": {
        "name": "Store Associate",
        "icon": "👤",
        "image": "assets/store_associate.png",
        "description": "Front-line store staff with view access to their assigned store",
        "tabs": ["Dashboard", "Inventory", "Ask Genie"],
        "tab_icons": ["speedometer2", "box-seam", "chat-dots"],
        "can_select_store": False,  # Assigned store only
        "data_scope": "single_store",  # Only sees their assigned store
        "features": {
            "can_view_sales": True,
            "can_view_inventory": True,
            "can_reorder": False,  # View only
            "can_view_writeoffs": False,
            "can_view_team": False,
            "can_view_analytics": False,
            "can_use_genie": True,
        }
    },
    "store_manager": {
        "name": "Store Manager",
        "icon": "👔",
        "image": "assets/store_manager.png",
        "description": "Store manager with full access to their store's data and operations",
        "tabs": ["Dashboard", "Inventory", "Write-Offs", "Analytics", "Ask Genie"],
        "tab_icons": ["speedometer2", "box-seam", "trash", "graph-up", "chat-dots"],
        "can_select_store": False,  # Assigned store only
        "data_scope": "single_store",
        "features": {
            "can_view_sales": True,
            "can_view_inventory": True,
            "can_reorder": True,
            "can_view_writeoffs": True,
            "can_view_team": True,
            "can_view_analytics": True,
            "can_use_genie": True,
        }
    },
    "regional_manager": {
        "name": "Regional Manager",
        "icon": "🌐",
        "image": "assets/regional_manager.png",
        "description": "Regional manager with access to all stores in their region",
        "tabs": ["Overview", "Store Map", "Store Details", "Analytics", "Ask Genie"],
        "tab_icons": ["grid-3x3-gap", "geo-alt", "shop", "graph-up", "chat-dots"],
        "can_select_store": True,  # Can select any store for drill-down
        "data_scope": "all_stores",  # Sees aggregated data for all stores
        "features": {
            "can_view_sales": True,
            "can_view_inventory": True,
            "can_reorder": True,
            "can_view_writeoffs": True,
            "can_view_team": True,
            "can_view_analytics": True,
            "can_use_genie": True,
            "can_view_all_stores": True,
            "can_compare_stores": True,
        }
    }
}

# Sample user assignments (in production, this would come from auth/SSO)
SAMPLE_USERS: Dict[str, Dict[str, Any]] = {
    "sarah_associate": {
        "name": "Sarah",
        "persona": "store_associate",
        "assigned_store_id": 1,  # Bondi Beach
    },
    "mike_manager": {
        "name": "Mike",
        "persona": "store_manager",
        "assigned_store_id": 1,  # Bondi Beach
    },
    "emma_regional": {
        "name": "Emma",
        "persona": "regional_manager",
        "assigned_store_id": None,  # All stores
        "region": "NSW",
    }
}


def get_persona(persona_key: str) -> Dict[str, Any]:
    """Get persona configuration by key."""
    return PERSONAS.get(persona_key, PERSONAS["store_manager"])


def get_persona_tabs(persona_key: str) -> List[str]:
    """Get available tabs for a persona."""
    persona = get_persona(persona_key)
    return persona.get("tabs", ["Dashboard"])


def get_persona_tab_icons(persona_key: str) -> List[str]:
    """Get tab icons for a persona."""
    persona = get_persona(persona_key)
    return persona.get("tab_icons", ["speedometer2"])


def can_select_store(persona_key: str) -> bool:
    """Check if persona can select different stores."""
    persona = get_persona(persona_key)
    return persona.get("can_select_store", False)


def get_data_scope(persona_key: str) -> str:
    """Get data scope for persona (single_store or all_stores)."""
    persona = get_persona(persona_key)
    return persona.get("data_scope", "single_store")


def has_feature(persona_key: str, feature: str) -> bool:
    """Check if persona has a specific feature enabled."""
    persona = get_persona(persona_key)
    features = persona.get("features", {})
    return features.get(feature, False)


def get_default_store_id(persona_key: str, user_id: Optional[str] = None) -> Optional[int]:
    """
    Get default store ID for a persona/user.

    Args:
        persona_key: The persona type
        user_id: Optional user ID for user-specific assignment

    Returns:
        Store ID or None for regional managers
    """
    # In production, this would look up user's assigned store from auth system
    if user_id and user_id in SAMPLE_USERS:
        return SAMPLE_USERS[user_id].get("assigned_store_id")

    # Default assignments for demo
    defaults = {
        "store_associate": 1,  # First store
        "store_manager": 1,    # First store
        "regional_manager": None,  # No default, show all
    }

    return defaults.get(persona_key)


def get_persona_display_info(persona_key: str) -> Dict[str, str]:
    """
    Get display information for a persona.

    Returns:
        Dictionary with name, icon, image, and description
    """
    persona = get_persona(persona_key)
    return {
        "name": persona.get("name", "Unknown"),
        "icon": persona.get("icon", "👤"),
        "image": persona.get("image", ""),
        "description": persona.get("description", ""),
    }


def validate_persona_access(persona_key: str, tab: str) -> bool:
    """
    Validate if a persona has access to a specific tab.

    Args:
        persona_key: The persona type
        tab: The tab name to check

    Returns:
        True if persona has access, False otherwise
    """
    tabs = get_persona_tabs(persona_key)
    return tab in tabs


def get_all_persona_keys() -> List[str]:
    """Get all available persona keys."""
    return list(PERSONAS.keys())


def get_persona_for_store_context(persona_key: str, store_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get persona info with store context for display.

    Args:
        persona_key: The persona type
        store_id: Optional store ID for context

    Returns:
        Dictionary with persona info and store context
    """
    persona = get_persona(persona_key)

    return {
        **persona,
        "store_id": store_id,
        "shows_all_stores": persona.get("data_scope") == "all_stores" and store_id is None,
    }
