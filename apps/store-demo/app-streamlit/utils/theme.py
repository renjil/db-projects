"""
7-Eleven Theme Configuration
Centralized colors, fonts, and CSS for the Store Intelligence Platform.
"""

# 7-Eleven Brand Colors
COLORS = {
    "green": "#007A53",          # Primary - 7-Eleven Green
    "green_light": "#00A86B",    # Lighter green for hover states
    "green_dark": "#005A3C",     # Darker green for text
    "orange": "#F7941D",         # Secondary - 7-Eleven Orange
    "orange_light": "#FFB347",   # Lighter orange
    "red": "#C8102E",            # Alert/Accent - 7-Eleven Red
    "red_light": "#E63946",      # Lighter red for warnings
    "bg_light": "#F8F9FA",       # Light background
    "bg_secondary": "#F0F2F5",   # Secondary background
    "bg_card": "#FFFFFF",        # Card background
    "text_dark": "#1A1A1A",      # Primary text
    "text_primary": "#1A1A1A",   # Primary text (alias)
    "text_muted": "#6C757D",     # Secondary text
    "border": "#E9ECEF",         # Border color
    "success": "#28A745",        # Success state
    "warning": "#FFC107",        # Warning state
}

# Severity colors for alerts
SEVERITY_COLORS = {
    "HIGH": COLORS["red"],
    "MEDIUM": COLORS["orange"],
    "LOW": COLORS["green"],
}

# Performance status colors
PERFORMANCE_COLORS = {
    "above": COLORS["green"],
    "at": COLORS["orange"],
    "below": COLORS["red"],
}

# Plotly chart theme
PLOTLY_TEMPLATE = {
    "layout": {
        "colorway": [
            COLORS["green"],
            COLORS["orange"],
            COLORS["red"],
            "#4A90D9",
            "#9B59B6",
            "#3498DB",
            "#1ABC9C",
            "#F39C12",
        ],
        "font": {"family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif"},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
        "hoverlabel": {
            "bgcolor": "white",
            "font_size": 13,
            "font_family": "Inter, sans-serif"
        }
    }
}


def get_css() -> str:
    """Return the main CSS stylesheet for the app."""
    return f"""
    <style>
        /* Import Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Global styles */
        .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Header styling */
        .main-header {{
            font-size: 2rem;
            font-weight: 700;
            color: {COLORS['green']};
            margin-bottom: 0.5rem;
        }}

        .sub-header {{
            font-size: 0.9rem;
            color: {COLORS['text_muted']};
            margin-bottom: 1.5rem;
        }}

        /* Section headers */
        .section-header {{
            font-size: 1.1rem;
            font-weight: 600;
            color: {COLORS['text_dark']};
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid {COLORS['green']};
        }}

        /* Metric card styling */
        .metric-card {{
            background: {COLORS['bg_card']};
            border-radius: 12px;
            padding: 1.25rem;
            border: 1px solid {COLORS['border']};
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            transition: box-shadow 0.2s ease;
            min-height: 140px;
            display: flex;
            flex-direction: column;
        }}

        .metric-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .metric-icon {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        .metric-label {{
            font-size: 0.8rem;
            color: {COLORS['text_muted']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
        }}

        .metric-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {COLORS['text_dark']};
            line-height: 1.2;
        }}

        .metric-delta {{
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }}

        .metric-delta-positive {{
            color: {COLORS['green']};
        }}

        .metric-delta-negative {{
            color: {COLORS['red']};
        }}

        .metric-delta-neutral {{
            color: {COLORS['text_muted']};
        }}

        /* Sparkline container */
        .sparkline-container {{
            margin-top: 0.5rem;
            height: 30px;
        }}

        /* Alert card styling */
        .alert-card {{
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }}

        .alert-high {{
            background: #FFF5F5;
            border-left: 4px solid {COLORS['red']};
        }}

        .alert-medium {{
            background: #FFF8E6;
            border-left: 4px solid {COLORS['orange']};
        }}

        .alert-low {{
            background: #F0FFF4;
            border-left: 4px solid {COLORS['green']};
        }}

        .alert-icon {{
            font-size: 1.25rem;
        }}

        .alert-content {{
            flex: 1;
        }}

        .alert-title {{
            font-weight: 600;
            color: {COLORS['text_dark']};
            margin-bottom: 0.25rem;
        }}

        .alert-message {{
            font-size: 0.9rem;
            color: {COLORS['text_muted']};
        }}

        /* Quick question buttons */
        .question-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
            margin: 1rem 0;
        }}

        .question-btn {{
            background: {COLORS['bg_light']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 0.75rem 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: left;
            font-size: 0.9rem;
            color: {COLORS['text_dark']};
        }}

        .question-btn:hover {{
            background: {COLORS['green']};
            color: white;
            border-color: {COLORS['green']};
        }}

        /* Data table styling */
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}

        .styled-table th {{
            background: {COLORS['bg_light']};
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
            color: {COLORS['text_dark']};
            border-bottom: 2px solid {COLORS['border']};
        }}

        .styled-table td {{
            padding: 0.75rem;
            border-bottom: 1px solid {COLORS['border']};
        }}

        .styled-table tr:hover {{
            background: {COLORS['bg_light']};
        }}

        /* Status badges */
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .badge-success {{
            background: #D4EDDA;
            color: #155724;
        }}

        .badge-warning {{
            background: #FFF3CD;
            color: #856404;
        }}

        .badge-danger {{
            background: #F8D7DA;
            color: #721C24;
        }}

        /* Progress bar */
        .progress-container {{
            background: {COLORS['bg_light']};
            border-radius: 4px;
            height: 8px;
            overflow: hidden;
        }}

        .progress-bar {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }}

        /* Streamlit overrides */
        [data-testid="stMetricValue"] {{
            font-size: 1.5rem;
            font-weight: 600;
        }}

        [data-testid="stMetricDelta"] svg[fill="#09ab3b"] {{
            fill: {COLORS['green']} !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
        }}

        .stTabs [data-baseweb="tab"] {{
            padding: 0.75rem 1rem;
            font-weight: 500;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {COLORS['green']} !important;
            color: white !important;
        }}

        /* Option menu full width styling */
        .nav-menu-container {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        div[data-testid="stVerticalBlock"] > div:has(nav) {{
            width: 100% !important;
        }}

        nav ul {{
            width: 100% !important;
            display: flex !important;
        }}

        nav ul li {{
            flex: 1 !important;
        }}

        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['green_dark']} 0%, {COLORS['green']} 100%);
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: white;
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: white !important;
        }}

        [data-testid="stSidebar"] .stSelectbox label {{
            color: rgba(255,255,255,0.9) !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }}

        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background-color: rgba(255,255,255,0.15) !important;
            border-color: rgba(255,255,255,0.3) !important;
            color: white !important;
        }}

        [data-testid="stSidebar"] .stSelectbox > div > div:hover {{
            border-color: rgba(255,255,255,0.5) !important;
        }}

        [data-testid="stSidebar"] .stSelectbox svg {{
            fill: white !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.2) !important;
        }}

        [data-testid="stSidebar"] .stExpander {{
            background-color: rgba(255,255,255,0.1) !important;
            border-color: rgba(255,255,255,0.2) !important;
        }}

        [data-testid="stSidebar"] .stExpander summary {{
            color: white !important;
        }}

        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: rgba(255,255,255,0.7) !important;
        }}

        /* Chat styling */
        .chat-container {{
            background: {COLORS['bg_card']};
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid {COLORS['border']};
        }}

        /* Hide default Streamlit elements but keep sidebar toggle */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* Ensure sidebar collapse/expand button is always visible */
        [data-testid="collapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
        }}
    </style>
    """


def get_sidebar_css() -> str:
    """Return additional CSS for sidebar with white text."""
    return f"""
    <style>
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['green_dark']} 0%, {COLORS['green']} 100%);
        }}

        [data-testid="stSidebar"] * {{
            color: white !important;
        }}

        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background-color: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,0.3);
        }}

        [data-testid="stSidebar"] .stSelectbox > div > div:hover {{
            border-color: rgba(255,255,255,0.5);
        }}
    </style>
    """
