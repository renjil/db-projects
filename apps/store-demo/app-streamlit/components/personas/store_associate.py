"""
Store Associate persona views for 7-Eleven Store Intelligence Platform.
Simplified, view-only access to Dashboard, Inventory, and Genie.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from utils.db import get_db
from utils.theme import COLORS
from utils.components import (
    page_header, section_header, metric_row, alert_card, quick_question_buttons,
    target_metric_row, display_genie_results
)
from utils.charts import area_chart, horizontal_bar_chart
from utils.genie import ask_genie


def render_store_associate_content(tab: str, store: Dict[str, Any]):
    """
    Render content for store associate based on selected tab.

    Args:
        tab: Selected tab name
        store: Current store dictionary
    """
    if tab == "Dashboard":
        render_dashboard(store)
    elif tab == "Inventory":
        render_inventory(store)
    elif tab == "Ask Genie":
        render_genie(store)


def render_dashboard(store: Dict[str, Any]):
    """Render simplified dashboard for store associate."""
    db = get_db()

    # Page header
    page_header(
        f"{store['store_name']}",
        f"Store Code: {store['store_code']} | {store.get('city', '')}, {store.get('state', '')}"
    )

    # KPIs section
    section_header("TODAY'S SNAPSHOT", "")

    try:
        kpis_list = db.get_store_kpis(store["store_id"])
        daily_data = db.get_daily_summary(store["store_id"], days=7)

        if not kpis_list:
            st.info("No KPI data available for this store.")
            return

        kpis = kpis_list[0]

        # Extract values with fallbacks
        today_sales = float(kpis.get("today_sales") or kpis.get("yesterday_sales") or 0)
        today_gp = float(kpis.get("today_gp") or kpis.get("yesterday_gp") or 0)
        gp_margin = float(kpis.get("today_gp_margin_pct") or kpis.get("l28d_avg_gp_margin_pct") or 0)
        vs_cluster = float(kpis.get("today_vs_cluster_pct") or kpis.get("l28d_avg_vs_cluster_pct") or 0)

        # Get target values
        sales_target = float(kpis.get("today_sales_target") or today_sales)
        gp_target = float(kpis.get("today_gp_target") or today_gp)
        margin_target = float(kpis.get("gp_margin_target") or gp_margin)

        # Render target metrics
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
        return

    st.markdown("---")

    # Two-column layout for trend chart and alerts
    col1, col2 = st.columns([3, 2])

    with col1:
        section_header("7-DAY SALES TREND", "")
        try:
            if daily_data:
                df = pd.DataFrame(daily_data)
                df["summary_date"] = pd.to_datetime(df["summary_date"])
                df["total_sales"] = pd.to_numeric(df["total_sales"], errors="coerce").fillna(0)
                df = df.sort_values("summary_date")

                fig = area_chart(
                    df, x="summary_date", y="total_sales",
                    title="", height=250, color=COLORS["green"]
                )
                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Sales ($)",
                    yaxis_tickformat="$,.0f"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No trend data available.")
        except Exception as e:
            st.error(f"Failed to load trend: {e}")

    with col2:
        section_header("ACTIVE ALERTS", "")
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
                        key=f"assoc_alert_{i}"
                    )
                if len(alerts) > 3:
                    st.caption(f"+{len(alerts) - 3} more alerts")
        except Exception as e:
            st.error(f"Failed to load alerts: {e}")


def render_inventory(store: Dict[str, Any]):
    """Render simplified inventory view for store associate (view-only)."""
    db = get_db()

    page_header(
        "Inventory Status",
        f"{store['store_name']} - View Only"
    )

    # KPI Summary
    try:
        summary_list = db.get_inventory_summary(store["store_id"])

        if summary_list:
            summary = summary_list[0]

            oos_count = int(summary.get("oos_tailored_count") or 0)
            projected_oos = int(summary.get("projected_oos_3d_count") or 0)
            total_items = int(summary.get("total_tailored_items") or 0)

            metrics = [
                {
                    "label": "Out of Stock",
                    "value": str(oos_count),
                    "delta": "Items need attention" if oos_count > 0 else "All stocked",
                    "delta_color": "inverse" if oos_count > 0 else "normal",
                    "icon": ""
                },
                {
                    "label": "Projected OOS (7 days)",
                    "value": str(projected_oos),
                    "delta": "Reorder soon" if projected_oos > 0 else "Good",
                    "delta_color": "inverse" if projected_oos > 5 else "normal",
                    "icon": ""
                },
                {
                    "label": "Total Items",
                    "value": str(total_items),
                    "icon": ""
                }
            ]

            metric_row(metrics)

    except Exception as e:
        st.error(f"Failed to load inventory summary: {e}")

    st.markdown("---")

    # Out of stock items
    section_header("OUT OF STOCK ITEMS", "")

    try:
        inventory = db.get_inventory_health(store["store_id"])

        if not inventory:
            st.info("No inventory data available.")
            return

        df = pd.DataFrame(inventory)

        # Convert types
        for col in ["soh_qty", "days_until_oos"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        if "is_out_of_stock" in df.columns:
            # Handle string booleans properly (database may return "true"/"false" as strings)
            df["is_out_of_stock"] = df["is_out_of_stock"].astype(str).str.lower() == "true"
        else:
            df["is_out_of_stock"] = False

        if "days_until_oos" not in df.columns:
            df["days_until_oos"] = 999

        # Show OOS items
        oos_df = df[df["is_out_of_stock"] == True]

        if oos_df.empty:
            st.success("No out-of-stock items!")
        else:
            display_df = oos_df[["article_name", "category_name"]].head(10).copy()
            display_df.columns = ["Article", "Category"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            if len(oos_df) > 10:
                st.caption(f"Showing 10 of {len(oos_df)} OOS items")

        st.markdown("---")

        # Projected OOS
        section_header("RUNNING LOW (OOS in 7 days)", "")

        proj_df = df[(df["days_until_oos"] <= 7) & (df["days_until_oos"] > 0) & (df["is_out_of_stock"] == False)]

        if proj_df.empty:
            st.success("No items projected to go OOS soon!")
        else:
            display_df = proj_df[["article_name", "category_name", "soh_qty"]].head(10).copy()
            display_df.columns = ["Article", "Category", "SOH"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Failed to load inventory: {e}")

    # Note for associates
    st.info("Contact your Store Manager to place reorders.")


def render_genie(store: Dict[str, Any]):
    """Render Genie chat for store associate."""
    db = get_db()

    page_header(
        "Ask Genie",
        f"AI Assistant for {store['store_name']}"
    )

    # Initialize chat state
    if "genie_messages" not in st.session_state:
        st.session_state.genie_messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    # Quick questions (simplified for associates)
    st.markdown("**Quick Questions:**")

    quick_questions = [
        "What's out of stock?",
        "Top selling items today",
        "Show active alerts",
        "How are we doing vs cluster?"
    ]

    selected_question = quick_question_buttons(quick_questions, columns=2)

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

    # Chat input
    prompt = st.chat_input("Ask about your store...")

    if st.session_state.pending_question:
        prompt = st.session_state.pending_question
        st.session_state.pending_question = None

    if prompt:
        st.session_state.genie_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_genie(prompt, store["store_id"])
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

    # Clear chat
    if st.session_state.genie_messages:
        if st.button("Clear Chat", key="clear_assoc_chat"):
            st.session_state.genie_messages = []
            st.rerun()
