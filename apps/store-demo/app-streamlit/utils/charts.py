"""
Plotly Chart Helpers for 7-Eleven Store Intelligence Platform.
Reusable chart components with consistent styling.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List, Dict, Any, Union
from utils.theme import COLORS, PLOTLY_TEMPLATE


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply 7-Eleven theme to a Plotly figure."""
    fig.update_layout(
        font=dict(family="Inter, -apple-system, sans-serif"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=40, b=40),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Inter, sans-serif"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig


def trend_line_chart(
    df: pd.DataFrame,
    x: str,
    y: Union[str, List[str]],
    title: str = "",
    y_title: str = "",
    height: int = 300,
    show_area: bool = False,
    comparison_line: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """
    Create a trend line chart.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name(s) for y-axis
        title: Chart title
        y_title: Y-axis title
        height: Chart height in pixels
        show_area: Fill area under line
        comparison_line: Optional dict with 'y' column and 'name' for comparison

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Handle single or multiple y columns
    y_cols = [y] if isinstance(y, str) else y
    colors = [COLORS["green"], COLORS["orange"], COLORS["red"], "#4A90D9"]

    for i, col in enumerate(y_cols):
        fill_mode = "tozeroy" if show_area and i == 0 else None
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            mode="lines",
            name=col.replace("_", " ").title(),
            line=dict(color=colors[i % len(colors)], width=2),
            fill=fill_mode,
            fillcolor=f"rgba{tuple(list(bytes.fromhex(colors[i % len(colors)][1:])) + [0.1])}" if fill_mode else None
        ))

    # Add comparison line if provided
    if comparison_line and comparison_line.get("y") in df.columns:
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[comparison_line["y"]],
            mode="lines",
            name=comparison_line.get("name", "Comparison"),
            line=dict(color=COLORS["text_muted"], width=2, dash="dash")
        ))

    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title=y_title,
        height=height,
        showlegend=len(y_cols) > 1 or comparison_line is not None
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"])

    return apply_theme(fig)


def area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    height: int = 300,
    color: str = None
) -> go.Figure:
    """Create an area chart."""
    color = color or COLORS["green"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode="lines",
        fill="tozeroy",
        line=dict(color=color, width=2),
        fillcolor=f"rgba{tuple(list(bytes.fromhex(color[1:])) + [0.15])}"
    ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=False
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"])

    return apply_theme(fig)


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    height: int = 300,
    horizontal: bool = False,
    color: Optional[str] = None,
    color_by: Optional[str] = None,
    show_values: bool = True
) -> go.Figure:
    """
    Create a bar chart.

    Args:
        df: DataFrame with data
        x: Column name for x/category axis
        y: Column name for y/value axis
        title: Chart title
        height: Chart height
        horizontal: If True, create horizontal bars
        color: Static color for all bars
        color_by: Column to determine bar colors
        show_values: Show values on bars

    Returns:
        Plotly figure
    """
    color = color or COLORS["green"]

    if horizontal:
        fig = go.Figure(go.Bar(
            x=df[y],
            y=df[x],
            orientation="h",
            marker_color=color,
            text=df[y].apply(lambda v: f"${v:,.0f}" if isinstance(v, (int, float)) else str(v)) if show_values else None,
            textposition="outside"
        ))
    else:
        colors = None
        if color_by and color_by in df.columns:
            colors = df[color_by].apply(
                lambda v: COLORS["green"] if v >= 0 else COLORS["red"]
            ).tolist()

        fig = go.Figure(go.Bar(
            x=df[x],
            y=df[y],
            marker_color=colors if colors else color,
            text=df[y].apply(lambda v: f"{v:,.0f}" if isinstance(v, (int, float)) else str(v)) if show_values else None,
            textposition="outside"
        ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=False
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"])

    return apply_theme(fig)


def horizontal_bar_chart(
    df: pd.DataFrame,
    category: str,
    value: str,
    title: str = "",
    height: int = 300,
    color: str = None,
    format_values: str = "${:,.0f}"
) -> go.Figure:
    """Create a horizontal bar chart, typically for rankings."""
    color = color or COLORS["green"]

    # Ensure value column is numeric
    df = df.copy()
    df[value] = pd.to_numeric(df[value], errors="coerce").fillna(0)

    # Sort by value
    df_sorted = df.sort_values(value, ascending=True)

    fig = go.Figure(go.Bar(
        x=df_sorted[value],
        y=df_sorted[category],
        orientation="h",
        marker_color=color,
        text=df_sorted[value].apply(lambda v: format_values.format(v)),
        textposition="outside"
    ))

    fig.update_layout(
        title=title,
        height=max(height, len(df_sorted) * 30),
        showlegend=False,
        yaxis=dict(automargin=True)
    )

    fig.update_xaxes(showgrid=True, gridcolor=COLORS["border"])
    fig.update_yaxes(showgrid=False)

    return apply_theme(fig)


def pie_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str = "",
    height: int = 300,
    hole: float = 0.4
) -> go.Figure:
    """
    Create a donut/pie chart.

    Args:
        df: DataFrame with data
        names: Column for slice names
        values: Column for slice values
        title: Chart title
        height: Chart height
        hole: Size of donut hole (0 for pie, 0.4 for donut)

    Returns:
        Plotly figure
    """
    colors = [
        COLORS["green"],
        COLORS["orange"],
        COLORS["red"],
        "#4A90D9",
        "#9B59B6",
        "#3498DB",
        "#1ABC9C",
        "#F39C12",
    ]

    fig = go.Figure(go.Pie(
        labels=df[names],
        values=df[values],
        hole=hole,
        marker=dict(colors=colors[:len(df)]),
        textinfo="percent+label",
        textposition="outside"
    ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return apply_theme(fig)


def gauge_chart(
    value: float,
    max_value: float = 100,
    title: str = "",
    height: int = 250,
    thresholds: Optional[Dict[str, float]] = None
) -> go.Figure:
    """
    Create a gauge chart for KPI attainment.

    Args:
        value: Current value
        max_value: Maximum value
        title: Chart title
        height: Chart height
        thresholds: Dict with 'warning' and 'danger' percentages

    Returns:
        Plotly figure
    """
    thresholds = thresholds or {"warning": 80, "danger": 60}

    # Determine color based on thresholds
    percentage = (value / max_value * 100) if max_value > 0 else 0
    if percentage >= thresholds["warning"]:
        bar_color = COLORS["green"]
    elif percentage >= thresholds["danger"]:
        bar_color = COLORS["orange"]
    else:
        bar_color = COLORS["red"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        title={"text": title, "font": {"size": 14}},
        number={"suffix": "%", "font": {"size": 28}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": bar_color},
            "bgcolor": COLORS["bg_light"],
            "steps": [
                {"range": [0, thresholds["danger"]], "color": "#FFF5F5"},
                {"range": [thresholds["danger"], thresholds["warning"]], "color": "#FFF8E6"},
                {"range": [thresholds["warning"], 100], "color": "#F0FFF4"}
            ],
            "threshold": {
                "line": {"color": COLORS["text_dark"], "width": 2},
                "thickness": 0.75,
                "value": 100
            }
        }
    ))

    fig.update_layout(height=height)
    return apply_theme(fig)


def comparison_bar_chart(
    df: pd.DataFrame,
    category: str,
    actual: str,
    target: str,
    title: str = "",
    height: int = 300
) -> go.Figure:
    """
    Create a grouped bar chart comparing actual vs target.

    Args:
        df: DataFrame with data
        category: Column for categories
        actual: Column for actual values
        target: Column for target values
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df[category],
        y=df[actual],
        name="Actual",
        marker_color=COLORS["green"]
    ))

    fig.add_trace(go.Bar(
        x=df[category],
        y=df[target],
        name="Target",
        marker_color=COLORS["orange"]
    ))

    fig.update_layout(
        title=title,
        height=height,
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"])

    return apply_theme(fig)


def yoy_growth_chart(
    df: pd.DataFrame,
    category: str,
    growth: str,
    title: str = "YoY Growth",
    height: int = 300
) -> go.Figure:
    """
    Create a bar chart showing YoY growth with positive/negative coloring.

    Args:
        df: DataFrame with data
        category: Column for categories
        growth: Column for growth percentages
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    df_sorted = df.sort_values(growth, ascending=False)

    colors = df_sorted[growth].apply(
        lambda v: COLORS["green"] if v >= 0 else COLORS["red"]
    ).tolist()

    fig = go.Figure(go.Bar(
        x=df_sorted[category],
        y=df_sorted[growth],
        marker_color=colors,
        text=df_sorted[growth].apply(lambda v: f"{v:+.1f}%"),
        textposition="outside"
    ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=False
    )

    # Add zero line
    fig.add_hline(y=0, line_dash="solid", line_color=COLORS["text_muted"])

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"])

    return apply_theme(fig)


def multi_line_chart(
    df: pd.DataFrame,
    x: str,
    y_columns: List[str],
    names: Optional[List[str]] = None,
    title: str = "",
    height: int = 300,
    show_legend: bool = True
) -> go.Figure:
    """
    Create a multi-line chart for comparing multiple metrics.

    Args:
        df: DataFrame with data
        x: Column for x-axis
        y_columns: List of columns to plot
        names: Display names for each line
        title: Chart title
        height: Chart height
        show_legend: Show legend

    Returns:
        Plotly figure
    """
    colors = [COLORS["green"], COLORS["orange"], COLORS["red"], "#4A90D9", "#9B59B6"]
    names = names or y_columns

    fig = go.Figure()

    for i, (col, name) in enumerate(zip(y_columns, names)):
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            mode="lines+markers",
            name=name,
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=6)
        ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=show_legend
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"])

    return apply_theme(fig)


def inventory_status_chart(
    oos_count: int,
    projected_oos: int,
    dead_stock: int,
    healthy: int,
    title: str = "Inventory Status",
    height: int = 250
) -> go.Figure:
    """Create a stacked bar or status chart for inventory health."""
    categories = ["Out of Stock", "Projected OOS", "Dead Stock", "Healthy"]
    values = [oos_count, projected_oos, dead_stock, healthy]
    colors = [COLORS["red"], COLORS["orange"], COLORS["text_muted"], COLORS["green"]]

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation="h",
        marker_color=colors,
        text=values,
        textposition="outside"
    ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=False
    )

    fig.update_xaxes(showgrid=True, gridcolor=COLORS["border"])
    fig.update_yaxes(showgrid=False)

    return apply_theme(fig)
