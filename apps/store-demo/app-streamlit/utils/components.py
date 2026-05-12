"""
Reusable Styled Components for 7-Eleven Store Intelligence Platform.
"""

import streamlit as st
from typing import Optional, List, Dict, Any, Callable
import pandas as pd
from utils.theme import COLORS, SEVERITY_COLORS


def styled_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",  # "normal", "inverse", or "off"
    icon: str = "",
    sparkline_data: Optional[List[float]] = None,
    help_text: Optional[str] = None
) -> None:
    """
    Render a styled metric card with optional sparkline.

    Args:
        label: The metric label
        value: The metric value (formatted string)
        delta: Optional delta value (e.g., "+5.2%")
        delta_color: "normal" (green=positive), "inverse" (red=positive), "off"
        icon: Emoji or icon to display
        sparkline_data: Optional list of values for sparkline
        help_text: Optional tooltip text
    """
    # Determine delta styling
    delta_class = "metric-delta-neutral"
    if delta and delta_color != "off":
        # Try to determine if positive/negative from the delta string
        is_positive = False
        if delta.startswith("+"):
            is_positive = True
        elif delta.startswith("-"):
            is_positive = False
        else:
            # Try to parse as number, default to neutral if it fails
            try:
                cleaned = delta.replace("%", "").replace("$", "").replace(",", "").strip()
                numeric_val = float(cleaned)
                is_positive = numeric_val > 0
            except (ValueError, TypeError):
                # Non-numeric delta like "Above", "At", "Below" - use delta_color hint
                delta_class = "metric-delta-neutral"
                if delta_color == "normal":
                    # For "normal", assume the caller set it correctly
                    if any(word in delta.lower() for word in ["above", "good", "up"]):
                        delta_class = "metric-delta-positive"
                    elif any(word in delta.lower() for word in ["below", "bad", "down"]):
                        delta_class = "metric-delta-negative"
                elif delta_color == "inverse":
                    if any(word in delta.lower() for word in ["above", "good", "up"]):
                        delta_class = "metric-delta-negative"
                    elif any(word in delta.lower() for word in ["below", "bad", "down"]):
                        delta_class = "metric-delta-positive"
                is_positive = None  # Skip the below logic

        if is_positive is not None:
            if delta_color == "normal":
                delta_class = "metric-delta-positive" if is_positive else "metric-delta-negative"
            else:  # inverse
                delta_class = "metric-delta-negative" if is_positive else "metric-delta-positive"

    # Build sparkline SVG if data provided
    sparkline_svg = ""
    if sparkline_data and len(sparkline_data) > 1:
        sparkline_svg = _generate_sparkline_svg(sparkline_data)

    # Build HTML parts separately to avoid escaping issues
    # Always include delta row for consistent height (use invisible placeholder if no delta)
    if delta:
        delta_part = f'<div class="metric-delta {delta_class}">{delta}</div>'
    else:
        delta_part = '<div class="metric-delta" style="visibility:hidden;">&nbsp;</div>'

    # Always include sparkline row for consistent height
    if sparkline_svg:
        sparkline_part = f'<div style="margin-top:8px;height:25px;">{sparkline_svg}</div>'
    else:
        sparkline_part = '<div style="margin-top:8px;height:25px;"></div>'

    html = f'''<div class="metric-card">
<div class="metric-icon">{icon}</div>
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
{delta_part}
{sparkline_part}
</div>'''
    st.markdown(html, unsafe_allow_html=True)


def _generate_sparkline_svg(data: List[float], width: int = 100, height: int = 25) -> str:
    """Generate an SVG sparkline from data."""
    if not data or len(data) < 2:
        return ""

    min_val = min(data)
    max_val = max(data)
    val_range = max_val - min_val if max_val != min_val else 1

    points = []
    for i, val in enumerate(data):
        x = (i / (len(data) - 1)) * width
        y = height - ((val - min_val) / val_range) * height
        points.append(f"{x:.1f},{y:.1f}")

    points_str = " ".join(points)
    color = COLORS["green"] if data[-1] >= data[0] else COLORS["red"]

    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <polyline
            points="{points_str}"
            fill="none"
            stroke="{color}"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
        />
    </svg>
    """


def metric_row(metrics: List[Dict[str, Any]]) -> None:
    """
    Render a row of metric cards.

    Args:
        metrics: List of metric configs with keys: label, value, delta, icon, sparkline_data
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            styled_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta"),
                delta_color=metric.get("delta_color", "normal"),
                icon=metric.get("icon", ""),
                sparkline_data=metric.get("sparkline_data"),
                help_text=metric.get("help_text")
            )


def alert_card(
    title: str,
    message: str,
    severity: str = "LOW",
    action_label: Optional[str] = None,
    on_click: Optional[Callable] = None,
    key: Optional[str] = None
) -> bool:
    """
    Render a styled alert card.

    Args:
        title: Alert title
        message: Alert message
        severity: "HIGH", "MEDIUM", or "LOW"
        action_label: Optional button label
        on_click: Optional callback function
        key: Unique key for the button

    Returns:
        True if the action button was clicked
    """
    severity_upper = severity.upper()
    alert_class = f"alert-{severity_upper.lower()}"

    icon_map = {"HIGH": "!", "MEDIUM": "!", "LOW": "i"}
    icon = icon_map.get(severity_upper, "i")
    icon_color = SEVERITY_COLORS.get(severity_upper, COLORS["green"])

    col1, col2 = st.columns([5, 1])

    with col1:
        html = f"""
        <div class="alert-card {alert_class}">
            <div class="alert-icon" style="color: {icon_color}; font-weight: bold; width: 24px; height: 24px;
                 border-radius: 50%; border: 2px solid {icon_color}; display: flex; align-items: center;
                 justify-content: center; font-size: 0.9rem;">{icon}</div>
            <div class="alert-content">
                <div class="alert-title">{title}</div>
                <div class="alert-message">{message}</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    clicked = False
    with col2:
        if action_label:
            clicked = st.button(action_label, key=key, use_container_width=True)
            if clicked and on_click:
                on_click()

    return clicked


def alert_list(alerts: List[Dict[str, Any]], max_display: int = 5) -> None:
    """
    Render a list of alert cards.

    Args:
        alerts: List of alert dicts with keys: title, message, severity
        max_display: Maximum number of alerts to display
    """
    if not alerts:
        st.success("No active alerts!")
        return

    for i, alert in enumerate(alerts[:max_display]):
        alert_card(
            title=alert.get("alert_title", alert.get("title", "Alert")),
            message=alert.get("alert_message", alert.get("message", "")),
            severity=alert.get("alert_severity", alert.get("severity", "LOW")),
            action_label="View",
            key=f"alert_{i}"
        )

    if len(alerts) > max_display:
        st.caption(f"Showing {max_display} of {len(alerts)} alerts")


def quick_question_buttons(
    questions: List[str],
    columns: int = 3,
    on_click: Optional[Callable[[str], None]] = None
) -> Optional[str]:
    """
    Render a grid of quick question buttons.

    Args:
        questions: List of questions to display
        columns: Number of columns in the grid
        on_click: Optional callback with selected question

    Returns:
        Selected question or None
    """
    selected = None
    rows = [questions[i:i + columns] for i in range(0, len(questions), columns)]

    for row_idx, row in enumerate(rows):
        cols = st.columns(columns)
        for col_idx, question in enumerate(row):
            with cols[col_idx]:
                if st.button(
                    question,
                    key=f"qq_{row_idx}_{col_idx}",
                    use_container_width=True,
                    type="secondary"
                ):
                    selected = question
                    if on_click:
                        on_click(question)

    return selected


def section_header(title: str, icon: str = "") -> None:
    """Render a styled section header."""
    st.markdown(f'<div class="section-header">{icon} {title}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: Optional[str] = None) -> None:
    """Render a styled page header."""
    st.markdown(f'<p class="main-header">{title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="sub-header">{subtitle}</p>', unsafe_allow_html=True)


def progress_bar(value: float, max_value: float = 100, color: Optional[str] = None) -> None:
    """
    Render a styled progress bar.

    Args:
        value: Current value
        max_value: Maximum value
        color: Optional override color
    """
    percentage = min(100, (value / max_value) * 100) if max_value > 0 else 0

    if color is None:
        if percentage >= 70:
            color = COLORS["green"]
        elif percentage >= 40:
            color = COLORS["orange"]
        else:
            color = COLORS["red"]

    html = f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%; background: {color};"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def styled_dataframe(
    df: pd.DataFrame,
    highlight_column: Optional[str] = None,
    highlight_thresholds: Optional[Dict[str, Any]] = None
) -> None:
    """
    Render a styled dataframe with optional highlighting.

    Args:
        df: DataFrame to display
        highlight_column: Column to apply highlighting to
        highlight_thresholds: Dict with "low", "high" keys for color coding
    """
    if df.empty:
        st.info("No data available.")
        return

    # Apply column formatting
    column_config = {}
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32']:
            if 'pct' in col.lower() or 'margin' in col.lower() or 'rate' in col.lower():
                column_config[col] = st.column_config.NumberColumn(format="%.1f%%")
            elif 'value' in col.lower() or 'sales' in col.lower() or 'cost' in col.lower():
                column_config[col] = st.column_config.NumberColumn(format="$%.2f")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config
    )


def status_badge(text: str, status: str = "success") -> str:
    """
    Return HTML for a status badge.

    Args:
        text: Badge text
        status: "success", "warning", or "danger"

    Returns:
        HTML string for the badge
    """
    return f'<span class="badge badge-{status}">{text}</span>'


def kpi_comparison_card(
    label: str,
    current_value: float,
    comparison_value: float,
    format_str: str = "${:,.0f}",
    comparison_label: str = "vs Last Year"
) -> None:
    """
    Render a KPI card with comparison.

    Args:
        label: KPI label
        current_value: Current period value
        comparison_value: Comparison period value
        format_str: Format string for values
        comparison_label: Label for comparison
    """
    change_pct = ((current_value - comparison_value) / comparison_value * 100) if comparison_value else 0
    delta = f"{change_pct:+.1f}%"
    delta_color = "normal" if change_pct >= 0 else "inverse"

    styled_metric_card(
        label=label,
        value=format_str.format(current_value),
        delta=f"{delta} {comparison_label}",
        delta_color=delta_color
    )


def empty_state(message: str, icon: str = "") -> None:
    """Render an empty state message."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem; color: {COLORS['text_muted']};">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <div style="font-size: 1rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def info_tooltip(text: str) -> str:
    """Return an info icon with tooltip."""
    return f'<span title="{text}" style="cursor: help; color: {COLORS["text_muted"]};">i</span>'


def target_metric_card(
    label: str,
    value: str,
    actual: float,
    target: float,
    format_type: str = "currency",
    show_badge: bool = True,
    inverse: bool = False
) -> None:
    """
    Render a metric card with actuals vs target badge.
    """
    # Calculate percentage of target
    if target > 0:
        pct_of_target = (actual / target) * 100
    else:
        pct_of_target = 100

    # Determine badge color and text
    diff = actual - target
    diff_pct = ((actual - target) / target * 100) if target > 0 else 0

    if inverse:
        if pct_of_target <= 95:
            badge_bg = "#D4EDDA"
            badge_fg = "#155724"
        elif pct_of_target <= 105:
            badge_bg = "#FFF3CD"
            badge_fg = "#856404"
        else:
            badge_bg = "#F8D7DA"
            badge_fg = "#721C24"
    else:
        if pct_of_target >= 100:
            badge_bg = "#D4EDDA"
            badge_fg = "#155724"
        elif pct_of_target >= 90:
            badge_bg = "#FFF3CD"
            badge_fg = "#856404"
        else:
            badge_bg = "#F8D7DA"
            badge_fg = "#721C24"

    # Format badge text
    if format_type == "currency":
        if abs(diff) >= 1000:
            diff_k = diff / 1000
            if diff >= 0:
                badge_text = f"+{diff_k:.1f}K vs target"
            else:
                badge_text = f"{diff_k:.1f}K vs target"
        else:
            if diff >= 0:
                badge_text = f"+${diff:,.0f} vs target"
            else:
                badge_text = f"-${abs(diff):,.0f} vs target"
    elif format_type == "percent":
        badge_text = f"{pct_of_target:.0f}% of target"
    else:
        if diff_pct >= 0:
            badge_text = f"+{diff_pct:.1f}% vs target"
        else:
            badge_text = f"{diff_pct:.1f}% vs target"

    # Use the same card structure as styled_metric_card
    badge_part = ""
    if show_badge:
        badge_part = f'<div class="metric-delta" style="display: inline-block; background: {badge_bg}; color: {badge_fg}; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-top: 0.25rem;">{badge_text}</div>'

    html = f'''<div class="metric-card">
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
{badge_part}
</div>'''
    st.markdown(html, unsafe_allow_html=True)


def target_metric_row(metrics: List[Dict[str, Any]]) -> None:
    """
    Render a row of target metric cards.

    Args:
        metrics: List of metric configs with keys: label, value, actual, target, format_type, inverse
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            target_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                actual=metric.get("actual", 0),
                target=metric.get("target", 0),
                format_type=metric.get("format_type", "currency"),
                show_badge=metric.get("show_badge", True),
                inverse=metric.get("inverse", False)
            )


def display_genie_results(data: list) -> None:
    """
    Display Genie query results as table and/or chart.

    Args:
        data: List of dictionaries from query results
    """
    import plotly.express as px
    import pandas as pd

    if not data:
        return

    df = pd.DataFrame(data)

    # Try to convert columns to numeric where possible
    for col in df.columns:
        try:
            numeric_col = pd.to_numeric(df[col], errors="coerce")
            # Only convert if most values are numeric (not all NaN)
            if numeric_col.notna().sum() > len(df) * 0.5:
                df[col] = numeric_col
        except (ValueError, TypeError):
            pass  # Keep original values

    # Show as table
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Try to create a chart if we have appropriate data
    if len(df) > 1 and len(df.columns) >= 2:
        # Find text/category column and numeric column
        text_cols = df.select_dtypes(include=["object"]).columns.tolist()
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if text_cols and num_cols:
            # Create a bar chart
            x_col = text_cols[0]
            y_col = num_cols[0]

            # Limit to top 10 for readability
            chart_df = df.head(10)

            fig = px.bar(
                chart_df,
                x=x_col,
                y=y_col,
                title="",
                color_discrete_sequence=[COLORS["green"]]
            )
            fig.update_layout(
                xaxis_title="",
                yaxis_title=y_col.replace("_", " ").title(),
                margin=dict(l=20, r=20, t=20, b=20),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)


def sentiment_score_card(
    rating: float,
    sentiment_score: int,
    review_count: int,
    trend: str = "stable"
) -> None:
    """
    Display a sentiment score card with rating stars and trend.

    Args:
        rating: Overall rating (1.0-5.0)
        sentiment_score: Sentiment score (0-100)
        review_count: Number of reviews analyzed
        trend: "improving", "stable", or "declining"
    """
    # Generate star display
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    stars_html = "★" * full_stars
    if half_star:
        stars_html += "☆"
    stars_html += "☆" * empty_stars

    # Trend icon and color
    trend_icons = {
        "improving": ("↑", COLORS["green"]),
        "stable": ("→", COLORS["orange"]),
        "declining": ("↓", COLORS["red"])
    }
    trend_icon, trend_color = trend_icons.get(trend.lower(), ("→", COLORS["orange"]))

    # Sentiment score color
    if sentiment_score >= 70:
        score_color = COLORS["green"]
    elif sentiment_score >= 50:
        score_color = COLORS["orange"]
    else:
        score_color = COLORS["red"]

    html = f'''
    <div style="display: flex; gap: 20px; margin-bottom: 1rem;">
        <div class="metric-card" style="flex: 1;">
            <div class="metric-label">Overall Rating</div>
            <div class="metric-value" style="color: #FFB800;">{rating:.1f}</div>
            <div style="color: #FFB800; font-size: 1.2rem;">{stars_html}</div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.8rem;">{review_count:,} reviews</div>
        </div>
        <div class="metric-card" style="flex: 1;">
            <div class="metric-label">Sentiment Score</div>
            <div class="metric-value" style="color: {score_color};">{sentiment_score}</div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.9rem;">out of 100</div>
        </div>
        <div class="metric-card" style="flex: 1;">
            <div class="metric-label">Trend</div>
            <div class="metric-value" style="color: {trend_color};">{trend_icon}</div>
            <div style="color: {trend_color}; font-size: 0.9rem; text-transform: capitalize;">{trend}</div>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def sentiment_breakdown_chart(
    positive_pct: float,
    neutral_pct: float,
    negative_pct: float
) -> None:
    """
    Display a horizontal breakdown of sentiment percentages.

    Args:
        positive_pct: Percentage of positive reviews
        neutral_pct: Percentage of neutral reviews
        negative_pct: Percentage of negative reviews
    """
    import plotly.graph_objects as go

    fig = go.Figure()

    # Add bars for each sentiment type
    fig.add_trace(go.Bar(
        y=["Reviews"],
        x=[positive_pct],
        name="Positive",
        orientation="h",
        marker_color=COLORS["green"],
        text=f"{positive_pct:.0f}%",
        textposition="inside",
        textfont=dict(color="white", size=12)
    ))

    fig.add_trace(go.Bar(
        y=["Reviews"],
        x=[neutral_pct],
        name="Neutral",
        orientation="h",
        marker_color=COLORS["orange"],
        text=f"{neutral_pct:.0f}%",
        textposition="inside",
        textfont=dict(color="white", size=12)
    ))

    fig.add_trace(go.Bar(
        y=["Reviews"],
        x=[negative_pct],
        name="Negative",
        orientation="h",
        marker_color=COLORS["red"],
        text=f"{negative_pct:.0f}%",
        textposition="inside",
        textfont=dict(color="white", size=12)
    ))

    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[0, 100]
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=80,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)


def feedback_themes_display(
    positive_themes: str,
    negative_themes: str
) -> None:
    """
    Display positive and negative feedback themes in two columns.

    Args:
        positive_themes: Comma-separated positive themes
        negative_themes: Comma-separated negative themes
    """
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'''
        <div style="background: rgba(40, 167, 69, 0.1); border-radius: 8px; padding: 1rem; border-left: 4px solid {COLORS["green"]};">
            <div style="font-weight: 600; color: {COLORS["green"]}; margin-bottom: 0.5rem;">What Customers Love</div>
        ''', unsafe_allow_html=True)

        if positive_themes:
            for theme in positive_themes.split(","):
                theme = theme.strip()
                if theme:
                    st.markdown(f"✓ {theme}")

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
        <div style="background: rgba(220, 53, 69, 0.1); border-radius: 8px; padding: 1rem; border-left: 4px solid {COLORS["red"]};">
            <div style="font-weight: 600; color: {COLORS["red"]}; margin-bottom: 0.5rem;">Areas for Improvement</div>
        ''', unsafe_allow_html=True)

        if negative_themes:
            for theme in negative_themes.split(","):
                theme = theme.strip()
                if theme:
                    st.markdown(f"✗ {theme}")

        st.markdown("</div>", unsafe_allow_html=True)


def sentiment_comparison_table(sentiments: List[Dict[str, Any]]) -> None:
    """
    Display a table comparing sentiment across multiple stores.

    Args:
        sentiments: List of sentiment data dictionaries
    """
    if not sentiments:
        st.info("No sentiment data available.")
        return

    df = pd.DataFrame(sentiments)

    # Select and rename columns for display
    display_cols = {
        "store_name": "Store",
        "overall_rating": "Rating",
        "sentiment_score": "Sentiment",
        "review_count": "Reviews",
        "positive_pct": "Positive %",
        "trend_direction": "Trend",
        "top_negative_themes": "Top Issue"
    }

    # Filter to columns that exist
    available_cols = [c for c in display_cols.keys() if c in df.columns]
    df = df[available_cols].rename(columns={k: display_cols[k] for k in available_cols})

    # Add styling
    def style_sentiment(val):
        try:
            v = float(val)
            if v >= 70:
                return f"color: {COLORS['green']}; font-weight: bold;"
            elif v >= 50:
                return f"color: {COLORS['orange']}; font-weight: bold;"
            else:
                return f"color: {COLORS['red']}; font-weight: bold;"
        except:
            return ""

    def style_trend(val):
        val_lower = str(val).lower()
        if "improv" in val_lower:
            return f"color: {COLORS['green']};"
        elif "declin" in val_lower:
            return f"color: {COLORS['red']};"
        return ""

    st.dataframe(df, use_container_width=True, hide_index=True)
