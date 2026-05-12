"""
Regional Manager persona views for 7-Eleven Store Intelligence Platform.
Overview of all stores, store map, drill-down capability, and analytics.
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from typing import Dict, Any, List, Optional

from utils.db import get_db
from utils.theme import COLORS
from utils.components import (
    page_header, section_header, metric_row, alert_card, quick_question_buttons,
    target_metric_row, display_genie_results, sentiment_comparison_table
)
from utils.charts import (
    area_chart, pie_chart, horizontal_bar_chart, gauge_chart
)
from utils.genie import ask_genie


def render_regional_manager_content(
    tab: str,
    stores: List[Dict[str, Any]],
    selected_store: Optional[Dict[str, Any]] = None
):
    """
    Render content for regional manager based on selected tab.

    Args:
        tab: Selected tab name
        stores: List of all stores
        selected_store: Optional selected store for drill-down
    """
    if tab == "Overview":
        render_overview(stores)
    elif tab == "Store Map":
        render_store_map(stores)
    elif tab == "Store Details":
        render_store_details(stores, selected_store)
    elif tab == "Analytics":
        render_analytics(stores, selected_store)
    elif tab == "Ask Genie":
        render_genie(stores, selected_store)


def get_performance_status(vs_cluster: float) -> tuple:
    """Get performance status and color based on vs_cluster percentage."""
    if vs_cluster >= 5:
        return "Above Cluster", COLORS["green"]
    elif vs_cluster >= -5:
        return "At Cluster", COLORS["orange"]
    else:
        return "Below Cluster", COLORS["red"]


def render_overview(stores: List[Dict[str, Any]]):
    """Render regional overview with aggregated KPIs."""
    db = get_db()

    page_header(
        "Regional Overview",
        f"All {len(stores)} Stores"
    )

    # Get KPIs for all stores
    try:
        all_kpis = db.get_store_kpis()  # No store_id = all stores

        if not all_kpis:
            st.info("No KPI data available.")
            return

        kpis_df = pd.DataFrame(all_kpis)

        # Ensure numeric columns
        numeric_cols = ["today_sales", "yesterday_sales", "today_gp", "yesterday_gp",
                       "l7d_total_sales", "l28d_total_sales", "today_vs_cluster_pct",
                       "l28d_avg_vs_cluster_pct", "today_sales_target", "today_gp_target",
                       "gp_margin_target"]
        for col in numeric_cols:
            if col in kpis_df.columns:
                kpis_df[col] = pd.to_numeric(kpis_df[col], errors="coerce").fillna(0)

        # Calculate aggregates
        total_today_sales = kpis_df["today_sales"].sum() if "today_sales" in kpis_df.columns else 0
        if total_today_sales == 0:
            total_today_sales = kpis_df["yesterday_sales"].sum() if "yesterday_sales" in kpis_df.columns else 0

        total_today_gp = kpis_df["today_gp"].sum() if "today_gp" in kpis_df.columns else 0
        if total_today_gp == 0:
            total_today_gp = kpis_df["yesterday_gp"].sum() if "yesterday_gp" in kpis_df.columns else 0

        total_l7d = kpis_df["l7d_total_sales"].sum() if "l7d_total_sales" in kpis_df.columns else 0

        # Calculate targets (sum of all store targets)
        total_sales_target = kpis_df["today_sales_target"].sum() if "today_sales_target" in kpis_df.columns else total_today_sales
        total_gp_target = kpis_df["today_gp_target"].sum() if "today_gp_target" in kpis_df.columns else total_today_gp

        # Calculate vs_cluster from today or L28D average
        vs_cluster_col = "today_vs_cluster_pct" if "today_vs_cluster_pct" in kpis_df.columns else "l28d_avg_vs_cluster_pct"
        avg_vs_cluster = kpis_df[vs_cluster_col].mean() if vs_cluster_col in kpis_df.columns else 0

        # Count stores by performance
        above_count = len(kpis_df[kpis_df[vs_cluster_col] >= 5]) if vs_cluster_col in kpis_df.columns else 0
        at_count = len(kpis_df[(kpis_df[vs_cluster_col] >= -5) & (kpis_df[vs_cluster_col] < 5)]) if vs_cluster_col in kpis_df.columns else 0
        below_count = len(kpis_df[kpis_df[vs_cluster_col] < -5]) if vs_cluster_col in kpis_df.columns else 0

        section_header("REGIONAL PERFORMANCE", "")

        target_metrics = [
            {
                "label": "Total Sales Today",
                "value": f"${total_today_sales:,.0f}",
                "actual": total_today_sales,
                "target": total_sales_target,
                "format_type": "currency",
                "inverse": False
            },
            {
                "label": "Total GP Today",
                "value": f"${total_today_gp:,.0f}",
                "actual": total_today_gp,
                "target": total_gp_target,
                "format_type": "currency",
                "inverse": False
            },
            {
                "label": "7-Day Sales",
                "value": f"${total_l7d:,.0f}",
                "actual": total_l7d,
                "target": total_l7d,  # No weekly target available
                "format_type": "currency",
                "show_badge": False
            },
            {
                "label": "Avg vs Cluster",
                "value": f"{avg_vs_cluster:+.1f}%",
                "actual": avg_vs_cluster,
                "target": 0,
                "format_type": "number",
                "inverse": False
            }
        ]

        target_metric_row(target_metrics)

        # Regional Sentiment Summary (compact view)
        st.markdown("---")
        section_header("CUSTOMER SENTIMENT", "")
        try:
            sentiment_data = db.get_all_store_sentiments()
            if sentiment_data:
                # Calculate regional averages
                scores = [float(s.get("sentiment_score") or 0) for s in sentiment_data if s.get("sentiment_score")]
                avg_score = sum(scores) / len(scores) if scores else 0
                declining_count = len([s for s in sentiment_data if s.get("trend_direction") == "declining"])

                col1, col2 = st.columns(2)
                with col1:
                    if avg_score >= 70:
                        score_delta = "Good"
                    elif avg_score >= 50:
                        score_delta = "Fair"
                    else:
                        score_delta = "Needs Attention"
                    st.metric("Avg Sentiment Score", f"{avg_score:.0f}/100", score_delta)
                with col2:
                    attention_delta = "Needs Review" if declining_count > 0 else "All Stable"
                    st.metric("Stores with Declining Sentiment", str(declining_count), attention_delta)
            else:
                st.caption("No sentiment data available")
        except Exception:
            pass  # Silently fail - sentiment is supplementary info

        st.markdown("---")

        # Performance breakdown
        section_header("STORE PERFORMANCE BREAKDOWN", "")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style="background: rgba(0, 122, 83, 0.1); border: 2px solid {COLORS['green']};
                 border-radius: 12px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {COLORS['green']};">{above_count}</div>
                <div style="color: {COLORS['text_muted']};">Above Cluster</div>
                <div style="font-size: 0.8rem; color: {COLORS['text_muted']};">(+5% or more)</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background: rgba(247, 148, 29, 0.1); border: 2px solid {COLORS['orange']};
                 border-radius: 12px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {COLORS['orange']};">{at_count}</div>
                <div style="color: {COLORS['text_muted']};">At Cluster</div>
                <div style="font-size: 0.8rem; color: {COLORS['text_muted']};">(-5% to +5%)</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background: rgba(200, 16, 46, 0.1); border: 2px solid {COLORS['red']};
                 border-radius: 12px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {COLORS['red']};">{below_count}</div>
                <div style="color: {COLORS['text_muted']};">Below Cluster</div>
                <div style="font-size: 0.8rem; color: {COLORS['text_muted']};">(-5% or less)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Top and Bottom performers
        col1, col2 = st.columns(2)

        with col1:
            section_header("TOP 5 PERFORMERS", "")
            kpis_df["vs_cluster_display"] = kpis_df.get(vs_cluster_col, 0)
            top_5 = kpis_df.nlargest(5, vs_cluster_col)[["store_id", "vs_cluster_display"]].copy()

            # Merge with store names
            store_dict = {s["store_id"]: s["store_name"] for s in stores}
            top_5["store_name"] = top_5["store_id"].map(store_dict)

            for _, row in top_5.iterrows():
                pct = row["vs_cluster_display"]
                status, color = get_performance_status(pct)
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid {COLORS['border']};">
                    <span>{row['store_name']}</span>
                    <span style="color: {color}; font-weight: 600;">{pct:+.1f}%</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            section_header("BOTTOM 5 PERFORMERS", "")
            bottom_5 = kpis_df.nsmallest(5, vs_cluster_col)[["store_id", "vs_cluster_display"]].copy()
            bottom_5["store_name"] = bottom_5["store_id"].map(store_dict)

            for _, row in bottom_5.iterrows():
                pct = row["vs_cluster_display"]
                status, color = get_performance_status(pct)
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid {COLORS['border']};">
                    <span>{row['store_name']}</span>
                    <span style="color: {color}; font-weight: 600;">{pct:+.1f}%</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Active alerts across all stores
        section_header("REGIONAL ALERTS", "")
        try:
            all_alerts = db.get_alerts()  # All stores
            if not all_alerts:
                st.success("No active alerts across all stores!")
            else:
                high_alerts = [a for a in all_alerts if a.get("alert_severity") == "HIGH"]
                st.warning(f"{len(high_alerts)} HIGH priority alerts | {len(all_alerts)} total alerts")

                for i, alert in enumerate(high_alerts[:5]):
                    store_name = store_dict.get(alert.get("store_id"), "Unknown Store")
                    alert_card(
                        title=f"{store_name}: {alert.get('alert_title', 'Alert')}",
                        message=alert.get("alert_message", ""),
                        severity=alert.get("alert_severity", "LOW"),
                        key=f"regional_alert_{i}"
                    )

        except Exception as e:
            st.error(f"Failed to load alerts: {e}")

    except Exception as e:
        st.error(f"Failed to load regional overview: {e}")


def render_store_map(stores: List[Dict[str, Any]]):
    """Render store map with performance indicators."""
    db = get_db()

    page_header("Store Map", "Click a store to see details")

    # Legend
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    with col1:
        st.markdown(f'<span style="color: {COLORS["green"]};">**Above Cluster** (+5%+)</span>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<span style="color: {COLORS["orange"]};">**At Cluster** (+/-5%)</span>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span style="color: {COLORS["red"]};">**Below Cluster** (-5%+)</span>', unsafe_allow_html=True)

    try:
        # Get KPIs for all stores
        all_kpis = db.get_store_kpis()
        kpis_dict = {k["store_id"]: k for k in all_kpis} if all_kpis else {}

        # Merge stores with KPIs
        stores_with_kpis = []
        for store in stores:
            kpi = kpis_dict.get(store["store_id"], {})
            store_data = {**store}
            store_data["vs_cluster"] = float(kpi.get("today_vs_cluster_pct") or kpi.get("l28d_avg_vs_cluster_pct") or 0)
            store_data["today_sales"] = float(kpi.get("today_sales") or kpi.get("yesterday_sales") or 0)
            store_data["performance_status"], store_data["color"] = get_performance_status(store_data["vs_cluster"])
            stores_with_kpis.append(store_data)

        # Create map
        valid_coords = []
        for s in stores_with_kpis:
            lat = s.get("latitude")
            lon = s.get("longitude")
            if lat and lon:
                try:
                    valid_coords.append((float(lat), float(lon)))
                except (ValueError, TypeError):
                    continue

        if valid_coords:
            center_lat = sum(c[0] for c in valid_coords) / len(valid_coords)
            center_lon = sum(c[1] for c in valid_coords) / len(valid_coords)
        else:
            center_lat, center_lon = -28.0, 135.0

        m = folium.Map(location=[center_lat, center_lon], zoom_start=4, tiles="CartoDB positron")

        for store in stores_with_kpis:
            lat = store.get("latitude")
            lon = store.get("longitude")

            if lat is None or lon is None:
                continue

            try:
                lat, lon = float(lat), float(lon)
            except (ValueError, TypeError):
                continue

            vs_cluster = store["vs_cluster"]
            today_sales = store["today_sales"]
            status = store["performance_status"]
            color = store["color"]

            popup_html = f"""
            <div style="font-family: Inter, sans-serif; min-width: 220px; padding: 5px;">
                <h4 style="margin: 0 0 8px 0; color: {COLORS['green']}; font-size: 14px;">
                    {store['store_name']}
                </h4>
                <p style="margin: 0 0 10px 0; color: #666; font-size: 12px;">
                    {store.get('city', '')}, {store.get('state', '')}
                </p>
                <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 4px 0;"><b>Today's Sales:</b></td>
                        <td style="padding: 4px 0; text-align: right;">${today_sales:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0;"><b>vs Cluster:</b></td>
                        <td style="padding: 4px 0; text-align: right; color: {color}; font-weight: 600;">
                            {vs_cluster:+.1f}%
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0;"><b>Status:</b></td>
                        <td style="padding: 4px 0; text-align: right;">
                            <span style="background: {color}; color: white; padding: 2px 8px;
                                  border-radius: 10px; font-size: 11px;">{status}</span>
                        </td>
                    </tr>
                </table>
            </div>
            """

            folium.CircleMarker(
                location=[lat, lon],
                radius=12,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=store['store_name']
            ).add_to(m)

        map_data = st_folium(m, width=None, height=500, returned_objects=["last_object_clicked"])

        if map_data and map_data.get("last_object_clicked"):
            clicked = map_data["last_object_clicked"]
            st.info(f"Clicked location: {clicked.get('lat'):.4f}, {clicked.get('lng'):.4f}")
            st.caption("Use 'Store Details' tab to drill down into a specific store")

        st.caption(f"Showing {len(stores_with_kpis)} stores")

    except Exception as e:
        st.error(f"Failed to load map: {e}")


def render_store_details(stores: List[Dict[str, Any]], selected_store: Optional[Dict[str, Any]]):
    """Render store drill-down details."""
    db = get_db()

    page_header("Store Details", "Select a store to view detailed performance")

    # Store selector
    store_options = {s["store_name"]: s for s in stores}
    store_names = list(store_options.keys())

    current_idx = 0
    if selected_store:
        current_name = selected_store.get("store_name")
        if current_name in store_names:
            current_idx = store_names.index(current_name)

    selected_name = st.selectbox(
        "Select Store",
        store_names,
        index=current_idx,
        key="regional_store_selector"
    )

    store = store_options[selected_name]

    # Update session state if different
    if selected_name != (selected_store.get("store_name") if selected_store else None):
        st.session_state.selected_store_for_drilldown = store

    st.markdown("---")

    # Show store details (similar to store manager dashboard)
    section_header(f"{store['store_name']} - Performance Summary", "")

    try:
        kpis_list = db.get_store_kpis(store["store_id"])

        if kpis_list:
            kpis = kpis_list[0]

            today_sales = float(kpis.get("today_sales") or kpis.get("yesterday_sales") or 0)
            today_gp = float(kpis.get("today_gp") or kpis.get("yesterday_gp") or 0)
            gp_margin = float(kpis.get("today_gp_margin_pct") or kpis.get("l28d_avg_gp_margin_pct") or 0)
            vs_cluster = float(kpis.get("today_vs_cluster_pct") or kpis.get("l28d_avg_vs_cluster_pct") or 0)

            # Get target values
            sales_target = float(kpis.get("today_sales_target") or today_sales)
            gp_target = float(kpis.get("today_gp_target") or today_gp)
            margin_target = float(kpis.get("gp_margin_target") or gp_margin)

            target_metrics = [
                {
                    "label": "Today's Sales",
                    "value": f"${today_sales:,.0f}",
                    "actual": today_sales,
                    "target": sales_target,
                    "format_type": "currency",
                    "inverse": False
                },
                {
                    "label": "Gross Profit",
                    "value": f"${today_gp:,.0f}",
                    "actual": today_gp,
                    "target": gp_target,
                    "format_type": "currency",
                    "inverse": False
                },
                {
                    "label": "GP Margin",
                    "value": f"{gp_margin:.1f}%",
                    "actual": gp_margin,
                    "target": margin_target,
                    "format_type": "percent",
                    "inverse": False
                },
                {
                    "label": "vs Cluster",
                    "value": f"{vs_cluster:+.1f}%",
                    "actual": vs_cluster,
                    "target": 0,
                    "format_type": "number",
                    "inverse": False
                }
            ]

            target_metric_row(target_metrics)

    except Exception as e:
        st.error(f"Failed to load KPIs: {e}")

    st.markdown("---")

    # Sales trend
    col1, col2 = st.columns([3, 2])

    with col1:
        section_header("7-DAY SALES TREND", "")
        try:
            daily_data = db.get_daily_summary(store["store_id"], days=7)
            if daily_data:
                df = pd.DataFrame(daily_data)
                df["summary_date"] = pd.to_datetime(df["summary_date"])
                df["total_sales"] = pd.to_numeric(df["total_sales"], errors="coerce").fillna(0)
                df = df.sort_values("summary_date")

                fig = area_chart(
                    df, x="summary_date", y="total_sales",
                    title="", height=250, color=COLORS["green"]
                )
                fig.update_layout(xaxis_title="", yaxis_title="Sales ($)", yaxis_tickformat="$,.0f")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load trend: {e}")

    with col2:
        section_header("STORE ALERTS", "")
        try:
            alerts = db.get_alerts(store["store_id"])
            if not alerts:
                st.success("No active alerts!")
            else:
                for i, alert in enumerate(alerts[:3]):
                    alert_card(
                        title=alert.get("alert_title", "Alert"),
                        message=alert.get("alert_message", ""),
                        severity=alert.get("alert_severity", "LOW"),
                        key=f"detail_alert_{i}"
                    )
        except Exception as e:
            st.error(f"Failed to load alerts: {e}")

    st.markdown("---")

    # Quick inventory and writeoff summary
    col1, col2 = st.columns(2)

    with col1:
        section_header("INVENTORY STATUS", "")
        try:
            summary = db.get_inventory_summary(store["store_id"])
            if summary:
                s = summary[0]
                oos = int(s.get("oos_tailored_count") or 0)
                proj_oos = int(s.get("projected_oos_3d_count") or 0)
                dead = int(s.get("dead_stock_count") or 0)

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("OOS Items", oos)
                with col_b:
                    st.metric("Proj. OOS", proj_oos)
                with col_c:
                    st.metric("Dead Stock", dead)
        except Exception as e:
            st.error(f"Failed to load inventory: {e}")

    with col2:
        section_header("WRITE-OFF STATUS", "")
        try:
            trends = db.get_writeoff_trends(store["store_id"])
            if trends:
                t = trends[0]
                today_wo = float(t.get("today_writeoff_value") or 0)
                l7d_wo = float(t.get("l7d_writeoff_value") or 0)
                anomalies = int(t.get("l7d_anomaly_count") or 0)

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Today", f"${today_wo:,.0f}")
                with col_b:
                    st.metric("7-Day", f"${l7d_wo:,.0f}")
                with col_c:
                    st.metric("Anomalies", anomalies)
        except Exception as e:
            st.error(f"Failed to load write-offs: {e}")


def render_analytics(stores: List[Dict[str, Any]], selected_store: Optional[Dict[str, Any]]):
    """Render regional analytics with comparison capability."""
    db = get_db()

    page_header("Regional Analytics", "Compare performance across stores")

    try:
        all_kpis = db.get_store_kpis()
        if not all_kpis:
            st.info("No data available.")
            return

        kpis_df = pd.DataFrame(all_kpis)

        # Merge with store names
        store_dict = {s["store_id"]: s["store_name"] for s in stores}
        kpis_df["store_name"] = kpis_df["store_id"].map(store_dict)

        # Ensure numeric
        for col in ["l7d_total_sales", "today_vs_cluster_pct", "l28d_avg_vs_cluster_pct"]:
            if col in kpis_df.columns:
                kpis_df[col] = pd.to_numeric(kpis_df[col], errors="coerce").fillna(0)

        # Store sales comparison
        section_header("SALES COMPARISON (7-Day)", "")

        if "l7d_total_sales" in kpis_df.columns:
            fig = horizontal_bar_chart(
                kpis_df.nlargest(15, "l7d_total_sales"),
                category="store_name",
                value="l7d_total_sales",
                title="",
                height=400,
                color=COLORS["green"],
                format_values="${:,.0f}"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Performance distribution
        section_header("PERFORMANCE vs CLUSTER DISTRIBUTION", "")

        vs_cluster_col = "today_vs_cluster_pct" if "today_vs_cluster_pct" in kpis_df.columns else "l28d_avg_vs_cluster_pct"

        if vs_cluster_col in kpis_df.columns:
            fig = horizontal_bar_chart(
                kpis_df.sort_values(vs_cluster_col, ascending=True),
                category="store_name",
                value=vs_cluster_col,
                title="",
                height=500,
                color=COLORS["green"],
                format_values="{:+.1f}%"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Store ranking table
        section_header("STORE RANKING", "")

        display_cols = ["store_name", "l7d_total_sales", vs_cluster_col]
        available_cols = [c for c in display_cols if c in kpis_df.columns]
        display_df = kpis_df[available_cols].sort_values(vs_cluster_col, ascending=False).copy()
        display_df.columns = ["Store", "7-Day Sales", "vs Cluster (%)"][:len(available_cols)]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "7-Day Sales": st.column_config.NumberColumn(format="$%.0f"),
                "vs Cluster (%)": st.column_config.NumberColumn(format="%.1f%%")
            }
        )

        # Customer Sentiment Comparison Section
        st.markdown("---")
        section_header("CUSTOMER SENTIMENT COMPARISON", "")
        st.caption("AI-powered insights from customer reviews across all stores")

        try:
            sentiment_data = db.get_all_store_sentiments()
            if sentiment_data:
                # Display comparison table
                sentiment_comparison_table(sentiment_data)

                # Highlight stores needing attention
                declining_stores = [s for s in sentiment_data if s.get("trend_direction") == "declining"]
                if declining_stores:
                    st.warning(f"{len(declining_stores)} store(s) with declining customer sentiment:")
                    for store_sent in declining_stores[:3]:
                        st.markdown(f"- **{store_sent.get('store_name')}**: {store_sent.get('top_negative_themes', 'N/A')}")
            else:
                st.info("No customer sentiment data available.")
        except Exception as e:
            st.error(f"Failed to load sentiment data: {e}")

    except Exception as e:
        st.error(f"Failed to load analytics: {e}")


def render_genie(stores: List[Dict[str, Any]], selected_store: Optional[Dict[str, Any]]):
    """Render Genie chat for regional manager."""
    db = get_db()

    # Determine context - regional or specific store
    context_store = selected_store or (stores[0] if stores else None)
    context_label = context_store["store_name"] if context_store else "All Stores"

    page_header("Ask Genie", f"AI Assistant - Context: {context_label}")

    # Context selector
    st.markdown("**Chat Context:**")
    col1, col2 = st.columns([2, 4])
    with col1:
        context_options = ["All Stores"] + [s["store_name"] for s in stores]
        context_idx = 0
        if context_store:
            store_name = context_store["store_name"]
            if store_name in context_options:
                context_idx = context_options.index(store_name)

        selected_context = st.selectbox(
            "Select context",
            context_options,
            index=context_idx,
            key="genie_context"
        )

        # Get store_id for context
        if selected_context == "All Stores":
            genie_store_id = None
        else:
            genie_store = next((s for s in stores if s["store_name"] == selected_context), None)
            genie_store_id = genie_store["store_id"] if genie_store else None

    st.markdown("---")

    # Initialize chat state
    if "genie_messages" not in st.session_state:
        st.session_state.genie_messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    # Quick questions for regional
    st.markdown("**Quick Questions:**")

    quick_questions = [
        "Which stores are below cluster?",
        "What's the total regional sales?",
        "Show me stores with high write-offs",
        "Which stores have OOS issues?",
        "Top performing stores this week",
        "Stores needing attention"
    ]

    selected_question = quick_question_buttons(quick_questions, columns=3)

    if selected_question:
        st.session_state.pending_question = selected_question

    st.markdown("---")

    # Chat interface
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.genie_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                # Show data visualization if available
                if message.get("data") is not None and len(message["data"]) > 0:
                    display_genie_results(message["data"])
                if message.get("sql"):
                    with st.expander("View SQL Query"):
                        st.code(message["sql"], language="sql")

    prompt = st.chat_input("Ask about regional performance...")

    if st.session_state.pending_question:
        prompt = st.session_state.pending_question
        st.session_state.pending_question = None

    if prompt:
        st.session_state.genie_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_genie(prompt, genie_store_id)
                query_results = None

                if response["answer"]:
                    st.write(response["answer"])

                    # Execute SQL and visualize results
                    if response.get("sql"):
                        try:
                            query_results = db.execute_query(response["sql"])
                            if query_results and len(query_results) > 0:
                                display_genie_results(query_results)
                        except Exception as e:
                            st.caption(f"Could not execute query: {e}")

                        with st.expander("View SQL Query"):
                            st.code(response["sql"], language="sql")

        st.session_state.genie_messages.append({
            "role": "assistant",
            "content": response["answer"],
            "sql": response.get("sql"),
            "data": query_results
        })

        st.rerun()

    if st.session_state.genie_messages:
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.genie_messages = []
                st.rerun()
