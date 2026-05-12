"""
Store Manager persona views for 7-Eleven Store Intelligence Platform.
Full access to Dashboard, Inventory, Write-Offs, Analytics, and Genie.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

from utils.db import get_db
from utils.theme import COLORS
from utils.components import (
    page_header, section_header, metric_row, alert_card,
    quick_question_buttons, progress_bar, target_metric_row,
    display_genie_results, sentiment_score_card, sentiment_breakdown_chart,
    feedback_themes_display
)
from utils.charts import (
    area_chart, pie_chart, horizontal_bar_chart,
    yoy_growth_chart, gauge_chart, multi_line_chart
)
from utils.genie import ask_genie


def render_store_manager_content(tab: str, store: Dict[str, Any]):
    """
    Render content for store manager based on selected tab.

    Args:
        tab: Selected tab name
        store: Current store dictionary
    """
    if tab == "Dashboard":
        render_dashboard(store)
    elif tab == "Inventory":
        render_inventory(store)
    elif tab == "Write-Offs":
        render_writeoffs(store)
    elif tab == "Analytics":
        render_analytics(store)
    elif tab == "Ask Genie":
        render_genie(store)


def render_dashboard(store: Dict[str, Any]):
    """Render full dashboard for store manager."""
    db = get_db()

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
            st.info("No KPI data available.")
            return

        kpis = kpis_list[0]

        today_sales = float(kpis.get("today_sales") or kpis.get("yesterday_sales") or 0)
        today_gp = float(kpis.get("today_gp") or kpis.get("yesterday_gp") or 0)
        gp_margin = float(kpis.get("today_gp_margin_pct") or kpis.get("l28d_avg_gp_margin_pct") or 0)
        vs_cluster = float(kpis.get("today_vs_cluster_pct") or kpis.get("l28d_avg_vs_cluster_pct") or 0)

        # Get target values
        sales_target = float(kpis.get("today_sales_target") or today_sales)
        gp_target = float(kpis.get("today_gp_target") or today_gp)
        margin_target = float(kpis.get("gp_margin_target") or gp_margin)

        # Use target metric cards for main KPIs
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
                "target": 0,  # Target is to be at or above cluster (0%)
                "format_type": "number",
                "inverse": False
            }
        ]

        target_metric_row(target_metrics)

    except Exception as e:
        st.error(f"Failed to load KPIs: {e}")
        return

    # Customer Sentiment Summary (compact view)
    st.markdown("---")
    section_header("CUSTOMER SENTIMENT", "")
    try:
        sentiment_data = db.get_store_sentiment(store["store_id"])
        if sentiment_data:
            sentiment = sentiment_data[0]
            col1, col2, col3 = st.columns(3)
            with col1:
                rating = float(sentiment.get("overall_rating") or 0)
                stars = "★" * int(rating) + "☆" * (5 - int(rating))
                st.metric("Customer Rating", f"{rating:.1f}/5.0", stars)
            with col2:
                score = int(sentiment.get("sentiment_score") or 0)
                # Color code based on score
                if score >= 70:
                    score_delta = "Good"
                elif score >= 50:
                    score_delta = "Fair"
                else:
                    score_delta = "Needs Attention"
                st.metric("Sentiment Score", f"{score}/100", score_delta)
            with col3:
                trend = sentiment.get("trend_direction") or "stable"
                trend_icons = {"improving": "↑ Improving", "stable": "→ Stable", "declining": "↓ Declining"}
                trend_display = trend_icons.get(trend, "→ Stable")
                st.metric("Trend", trend.capitalize(), trend_display.split()[0])
        else:
            st.caption("No sentiment data available")
    except Exception:
        pass  # Silently fail - sentiment is supplementary info

    st.markdown("---")

    # Two-column layout
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
                fig.update_layout(xaxis_title="", yaxis_title="Sales ($)", yaxis_tickformat="$,.0f")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load trend: {e}")

    with col2:
        section_header("ACTIVE ALERTS", "")
        try:
            alerts = db.get_alerts(store["store_id"])
            if not alerts:
                st.success("No active alerts!")
            else:
                high_count = len([a for a in alerts if a.get("alert_severity") == "HIGH"])
                medium_count = len([a for a in alerts if a.get("alert_severity") == "MEDIUM"])
                st.caption(f"{high_count} High | {medium_count} Medium | {len(alerts) - high_count - medium_count} Low")

                for i, alert in enumerate(alerts[:4]):
                    alert_card(
                        title=alert.get("alert_title", "Alert"),
                        message=alert.get("alert_message", ""),
                        severity=alert.get("alert_severity", "LOW"),
                        key=f"mgr_alert_{i}"
                    )
        except Exception as e:
            st.error(f"Failed to load alerts: {e}")

    st.markdown("---")

    # Quick Actions
    section_header("QUICK ACTIONS", "")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("View Reorders", use_container_width=True):
            st.session_state.current_tab = "Inventory"
            st.rerun()

    with col2:
        if st.button("Check Write-Offs", use_container_width=True):
            st.session_state.current_tab = "Write-Offs"
            st.rerun()

    with col3:
        if st.button("View Analytics", use_container_width=True):
            st.session_state.current_tab = "Analytics"
            st.rerun()

    with col4:
        if st.button("Ask Genie", use_container_width=True):
            st.session_state.current_tab = "Ask Genie"
            st.rerun()


def render_inventory(store: Dict[str, Any]):
    """Render full inventory management for store manager."""
    db = get_db()

    page_header("Inventory Health", f"{store['store_name']} ({store['store_code']})")

    # KPI Summary
    try:
        summary_list = db.get_inventory_summary(store["store_id"])

        if summary_list:
            summary = summary_list[0]

            oos_count = int(summary.get("oos_tailored_count") or 0)
            projected_oos = int(summary.get("projected_oos_3d_count") or 0)
            dead_stock_count = int(summary.get("dead_stock_count") or 0)
            dead_stock_value = float(summary.get("dead_stock_value") or 0)

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
                    "label": "Dead Stock",
                    "value": str(dead_stock_count),
                    "delta": f"${dead_stock_value:,.0f} value",
                    "delta_color": "inverse" if dead_stock_count > 10 else "normal",
                    "icon": ""
                }
            ]

            metric_row(metrics)

    except Exception as e:
        st.error(f"Failed to load inventory summary: {e}")

    st.markdown("---")

    # Filters
    col1, col2 = st.columns([2, 2])
    with col1:
        show_filter = st.selectbox(
            "Show",
            ["All Items", "Out of Stock", "Projected OOS", "Dead Stock", "Needs Reorder"],
            key="mgr_inv_filter"
        )

    # Load inventory
    try:
        inventory = db.get_inventory_health(store["store_id"])
        if not inventory:
            st.info("No inventory data available.")
            return

        df = pd.DataFrame(inventory)

        for col in ["soh_qty", "soh_value", "days_until_oos", "suggested_reorder_qty"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        for col in ["is_out_of_stock", "is_dead_stock"]:
            if col in df.columns:
                # Handle string booleans properly (database may return "true"/"false" as strings)
                df[col] = df[col].astype(str).str.lower() == "true"

        # Apply filter
        if show_filter == "Out of Stock":
            df = df[df["is_out_of_stock"] == True]
        elif show_filter == "Projected OOS":
            df = df[(df["days_until_oos"] <= 7) & (df["days_until_oos"] > 0) & (df["is_out_of_stock"] == False)]
        elif show_filter == "Dead Stock":
            df = df[df["is_dead_stock"] == True]
        elif show_filter == "Needs Reorder":
            df = df[df["suggested_reorder_qty"] > 0]

        # Show inventory tabs
        tab1, tab2, tab3 = st.tabs(["Items List", "By Category", "Dead Stock"])

        with tab1:
            if df.empty:
                st.info("No items match filter.")
            else:
                display_cols = ["article_name", "category_name", "soh_qty", "days_until_oos", "suggested_reorder_qty"]
                available_cols = [c for c in display_cols if c in df.columns]
                display_df = df[available_cols].head(50).copy()
                # Ensure numeric columns are properly typed
                for col in ["soh_qty", "days_until_oos", "suggested_reorder_qty"]:
                    if col in display_df.columns:
                        display_df[col] = pd.to_numeric(display_df[col], errors="coerce").fillna(0)
                display_df.columns = ["Article", "Category", "SOH", "Days to OOS", "Reorder Qty"][:len(available_cols)]

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Days to OOS": st.column_config.NumberColumn(format="%.1f")
                    }
                )

        with tab2:
            category_data = db.get_inventory_by_category(store["store_id"])
            if category_data:
                cat_df = pd.DataFrame(category_data)
                fig = horizontal_bar_chart(
                    cat_df.head(10),
                    category="category_name",
                    value="total_items",
                    title="Items by Category",
                    height=300,
                    color=COLORS["green"]
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            dead_stock = db.get_dead_stock(store["store_id"], limit=20)
            if dead_stock:
                dead_df = pd.DataFrame(dead_stock)
                # Convert numeric columns
                for col in ["soh_qty", "soh_value"]:
                    if col in dead_df.columns:
                        dead_df[col] = pd.to_numeric(dead_df[col], errors="coerce").fillna(0)
                display_df = dead_df[["article_name", "category_name", "soh_qty", "soh_value"]].copy()
                display_df.columns = ["Article", "Category", "SOH", "Value ($)"]
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Value ($)": st.column_config.NumberColumn(format="$%.2f")
                    }
                )
            else:
                st.success("No dead stock!")

    except Exception as e:
        st.error(f"Failed to load inventory: {e}")


def render_writeoffs(store: Dict[str, Any]):
    """Render write-off analysis for store manager."""
    db = get_db()

    page_header("Write-Off Analysis", f"{store['store_name']} ({store['store_code']})")

    # Date filter
    col1, col2 = st.columns([2, 4])
    with col1:
        period = st.selectbox(
            "Period",
            ["Last 7 Days", "Last 14 Days", "Last 28 Days"],
            key="mgr_wo_period"
        )

    days = {"Last 7 Days": 7, "Last 14 Days": 14, "Last 28 Days": 28}[period]

    st.markdown("---")

    # KPIs
    try:
        trends_list = db.get_writeoff_trends(store["store_id"])

        if trends_list:
            trends = trends_list[0]

            today_value = float(trends.get("today_writeoff_value") or 0)
            l7d_value = float(trends.get("l7d_writeoff_value") or 0)
            vs_cluster = float(trends.get("l7d_vs_cluster_pct") or 0)
            anomaly_count = int(trends.get("l7d_anomaly_count") or 0)

            metrics = [
                {"label": "Today", "value": f"${today_value:,.0f}", "icon": ""},
                {
                    "label": "7-Day Total",
                    "value": f"${l7d_value:,.0f}",
                    "icon": ""
                },
                {
                    "label": "vs Cluster",
                    "value": f"{vs_cluster:+.1f}%",
                    "delta": "Above Cluster" if vs_cluster > 0 else "Below Cluster" if vs_cluster < 0 else "At Cluster",
                    "delta_color": "inverse" if vs_cluster > 10 else "normal",
                    "icon": ""
                },
                {
                    "label": "Anomalies",
                    "value": str(anomaly_count),
                    "delta": "Need review" if anomaly_count > 0 else "None",
                    "delta_color": "inverse" if anomaly_count > 0 else "normal",
                    "icon": ""
                }
            ]

            metric_row(metrics)

    except Exception as e:
        st.error(f"Failed to load trends: {e}")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns([3, 2])

    with col1:
        section_header("WRITE-OFF TREND", "")
        try:
            daily_data = db.get_writeoff_daily(store["store_id"], days=days)
            if daily_data:
                df = pd.DataFrame(daily_data)
                df["writeoff_date"] = pd.to_datetime(df["writeoff_date"])
                df["total_value"] = pd.to_numeric(df["total_value"], errors="coerce").fillna(0)
                df = df.sort_values("writeoff_date")

                fig = area_chart(
                    df, x="writeoff_date", y="total_value",
                    title="", height=250, color=COLORS["orange"]
                )
                fig.update_layout(xaxis_title="", yaxis_title="Value ($)", yaxis_tickformat="$,.0f")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load trend: {e}")

    with col2:
        section_header("BY CATEGORY", "")
        try:
            category_data = db.get_writeoff_by_category(store["store_id"], days=days)
            if category_data:
                cat_df = pd.DataFrame(category_data)
                cat_df["total_value"] = pd.to_numeric(cat_df["total_value"], errors="coerce").fillna(0)
                fig = pie_chart(
                    cat_df.head(6), names="category_name", values="total_value",
                    title="", height=250, hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load categories: {e}")

    st.markdown("---")

    # Detail table
    section_header("WRITE-OFF DETAILS", "")
    try:
        detail = db.get_writeoff_detail(store["store_id"], days=days)
        if detail:
            detail_df = pd.DataFrame(detail)
            display_cols = ["writeoff_date", "article_name", "category_name", "quantity", "value"]
            available_cols = [c for c in display_cols if c in detail_df.columns]
            display_df = detail_df[available_cols].head(30).copy()
            display_df.columns = ["Date", "Article", "Category", "Qty", "Value ($)"][:len(available_cols)]
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Value ($)": st.column_config.NumberColumn(format="$%.2f")
                }
            )
        else:
            st.info("No write-off data for this period.")
    except Exception as e:
        st.error(f"Failed to load details: {e}")


def render_analytics(store: Dict[str, Any]):
    """Render analytics dashboard for store manager."""
    db = get_db()

    page_header("Performance Analytics", f"{store['store_name']} ({store['store_code']})")

    # Period selector
    col1, col2 = st.columns([2, 4])
    with col1:
        period = st.selectbox(
            "Period",
            ["Last 7 Days", "Last 14 Days", "Last 28 Days"],
            key="mgr_analytics_period"
        )

    days = {"Last 7 Days": 7, "Last 14 Days": 14, "Last 28 Days": 28}[period]

    st.markdown("---")

    # KPIs
    try:
        kpis_list = db.get_store_kpis(store["store_id"])
        if kpis_list:
            kpis = kpis_list[0]

            l7d_sales = float(kpis.get("l7d_total_sales") or 0)
            l28d_sales = float(kpis.get("l28d_total_sales") or 0)
            vs_budget = float(kpis.get("l7d_vs_budget_pct") or 0)
            vs_ly = float(kpis.get("l7d_vs_ly_pct") or 0)

            metrics = [
                {"label": "7-Day Sales", "value": f"${l7d_sales:,.0f}", "icon": ""},
                {"label": "28-Day Sales", "value": f"${l28d_sales:,.0f}", "icon": ""},
                {
                    "label": "vs Budget",
                    "value": f"{vs_budget:+.1f}%",
                    "delta_color": "normal" if vs_budget >= 0 else "inverse",
                    "icon": ""
                },
                {
                    "label": "vs Last Year",
                    "value": f"{vs_ly:+.1f}%",
                    "delta_color": "normal" if vs_ly >= 0 else "inverse",
                    "icon": ""
                }
            ]

            metric_row(metrics)

    except Exception as e:
        st.error(f"Failed to load KPIs: {e}")

    st.markdown("---")

    # Sales trend
    section_header("SALES TREND", "")
    try:
        daily_data = db.get_daily_summary(store["store_id"], days=days)
        if daily_data:
            df = pd.DataFrame(daily_data)
            df["summary_date"] = pd.to_datetime(df["summary_date"])
            df["total_sales"] = pd.to_numeric(df["total_sales"], errors="coerce").fillna(0)
            df = df.sort_values("summary_date")

            fig = area_chart(
                df, x="summary_date", y="total_sales",
                title="", height=300, color=COLORS["green"]
            )
            fig.update_layout(xaxis_title="", yaxis_title="Sales ($)", yaxis_tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load trend: {e}")

    st.markdown("---")

    # Category performance
    col1, col2 = st.columns(2)

    with col1:
        section_header("CATEGORY SALES", "")
        try:
            category_data = db.get_category_performance(store["store_id"])
            if not category_data:
                category_data = db.get_category_summary(store["store_id"])

            if category_data:
                cat_df = pd.DataFrame(category_data)
                if "total_sales" in cat_df.columns:
                    cat_df["total_sales"] = pd.to_numeric(cat_df["total_sales"], errors="coerce").fillna(0)
                    fig = pie_chart(
                        cat_df.head(8), names="category_name", values="total_sales",
                        title="", height=300, hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load categories: {e}")

    with col2:
        section_header("TOP PRODUCTS", "")
        try:
            products = db.get_top_products(store["store_id"], limit=8)
            if products:
                prod_df = pd.DataFrame(products)
                value_col = "apsd" if "apsd" in prod_df.columns else "total_sales"
                prod_df[value_col] = pd.to_numeric(prod_df[value_col], errors="coerce").fillna(0)

                fig = horizontal_bar_chart(
                    prod_df, category="article_name", value=value_col,
                    title="", height=300, color=COLORS["green"],
                    format_values="${:.2f}" if value_col == "apsd" else "${:,.0f}"
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load products: {e}")

    # Customer Sentiment Section (AI-powered insights from unstructured data)
    st.markdown("---")
    section_header("CUSTOMER SENTIMENT", "")
    st.caption("AI-powered insights from Google/Yelp reviews and customer surveys")

    try:
        sentiment_data = db.get_store_sentiment(store["store_id"])
        if sentiment_data:
            sentiment = sentiment_data[0]

            # Display sentiment metrics
            sentiment_score_card(
                rating=float(sentiment.get("overall_rating") or 0),
                sentiment_score=int(sentiment.get("sentiment_score") or 0),
                review_count=int(sentiment.get("review_count") or 0),
                trend=sentiment.get("trend_direction") or "stable"
            )

            # Breakdown chart
            st.markdown("**Review Sentiment Breakdown**")
            sentiment_breakdown_chart(
                positive_pct=float(sentiment.get("positive_pct") or 0),
                neutral_pct=float(sentiment.get("neutral_pct") or 0),
                negative_pct=float(sentiment.get("negative_pct") or 0)
            )

            # Feedback themes
            st.markdown("**Customer Feedback Themes**")
            feedback_themes_display(
                positive_themes=sentiment.get("top_positive_themes") or "",
                negative_themes=sentiment.get("top_negative_themes") or ""
            )
        else:
            st.info("No customer sentiment data available for this store.")

    except Exception as e:
        st.error(f"Failed to load sentiment data: {e}")

    # Link to full dashboard
    st.markdown("---")
    dashboard_id = "01f13c890186129189b53eaf8e910cb7"
    base_url = "https://e2-demo-field-eng.cloud.databricks.com"
    st.link_button(
        "View Full AI/BI Dashboard in Databricks",
        f"{base_url}/sql/dashboardsv3/{dashboard_id}",
        use_container_width=False
    )


def render_genie(store: Dict[str, Any]):
    """Render Genie chat for store manager."""
    page_header("Ask Genie", f"AI Assistant for {store['store_name']}")

    db = get_db()

    if "genie_messages" not in st.session_state:
        st.session_state.genie_messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    st.markdown("**Popular Questions:**")

    quick_questions = [
        "What should I reorder today?",
        "Show me dead stock report",
        "What were yesterday's write-offs?",
        "Show me top selling items",
        "How many pies should I cook?",
        "Am I tracking vs budget?"
    ]

    selected_question = quick_question_buttons(quick_questions, columns=3)

    if selected_question:
        st.session_state.pending_question = selected_question

    st.markdown("---")

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

    prompt = st.chat_input("Ask about your store performance...")

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

    if st.session_state.genie_messages:
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.genie_messages = []
                st.rerun()
