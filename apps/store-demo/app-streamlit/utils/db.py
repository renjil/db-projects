"""
Database client for Databricks SQL queries.
Streamlit version with caching support.
"""

import os
import streamlit as st
from typing import Any, Dict, List, Optional
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState


class DatabaseClient:
    """Client for executing SQL queries against Databricks."""

    def __init__(self):
        # Initialize WorkspaceClient - in Databricks Apps this uses service principal auth
        self.client = WorkspaceClient()

        # Required environment variables - no defaults
        self.warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        self.catalog = os.getenv("DATABRICKS_CATALOG")
        self.schema = os.getenv("DATABRICKS_SCHEMA")

        # Validate required config
        if not all([self.warehouse_id, self.catalog, self.schema]):
            missing = []
            if not self.warehouse_id: missing.append("DATABRICKS_WAREHOUSE_ID")
            if not self.catalog: missing.append("DATABRICKS_CATALOG")
            if not self.schema: missing.append("DATABRICKS_SCHEMA")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as list of dicts."""
        # Replace catalog/schema placeholders
        sql = sql.replace("${catalog}", self.catalog).replace("${schema}", self.schema)

        response = self.client.statement_execution.execute_statement(
            warehouse_id=self.warehouse_id,
            statement=sql,
            wait_timeout="30s"
        )

        if response.status.state == StatementState.FAILED:
            raise Exception(f"Query failed: {response.status.error}")

        if response.status.state != StatementState.SUCCEEDED:
            raise Exception(f"Query did not complete: {response.status.state}")

        if not response.manifest or not response.result:
            return []

        columns = [col.name for col in response.manifest.schema.columns]
        rows = []

        if response.result.data_array:
            for row in response.result.data_array:
                rows.append(dict(zip(columns, row)))

        return rows

    def get_stores(self) -> List[Dict[str, Any]]:
        """Get all accessible stores."""
        try:
            result = self.execute_query("""
                SELECT
                    store_id,
                    store_code,
                    store_name,
                    address,
                    city,
                    state,
                    postcode,
                    cluster_id,
                    territory,
                    format_type,
                    latitude,
                    longitude
                FROM ${catalog}.${schema}.silver_stores
                WHERE is_active = TRUE
                ORDER BY store_name
            """)
            return result
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"get_stores failed: {str(e)}")

    def get_store_kpis(self, store_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get store KPI summary."""
        where_clause = f"WHERE store_id = {store_id}" if store_id else ""
        return self.execute_query(f"""
            SELECT *
            FROM ${{catalog}}.${{schema}}.gold_store_kpi_override
            {where_clause}
        """)

    def get_daily_summary(self, store_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily store summary for the last N days."""
        return self.execute_query(f"""
            SELECT *
            FROM ${{catalog}}.${{schema}}.gold_daily_store_summary
            WHERE store_id = {store_id}
              AND summary_date >= CURRENT_DATE() - {days}
            ORDER BY summary_date DESC
        """)

    def get_category_performance(self, store_id: int) -> List[Dict[str, Any]]:
        """Get category performance for a store."""
        # Use gold_product_performance aggregation (gold_category_performance has schema issues)
        return self.execute_query(f"""
            SELECT
                category_name,
                SUM(total_sales) as total_sales,
                SUM(total_gp) as total_gp,
                AVG(gp_margin_pct) as avg_gp_margin
            FROM ${{catalog}}.${{schema}}.gold_product_performance
            WHERE store_id = {store_id}
            GROUP BY category_name
            ORDER BY total_sales DESC
        """)

    def get_inventory_health(self, store_id: int) -> List[Dict[str, Any]]:
        """Get inventory health for a store."""
        return self.execute_query(f"""
            SELECT *
            FROM ${{catalog}}.${{schema}}.gold_inventory_health
            WHERE store_id = {store_id}
              AND is_tailored_in = TRUE
            ORDER BY days_until_oos NULLS LAST
        """)

    def get_inventory_summary(self, store_id: int) -> List[Dict[str, Any]]:
        """Get inventory summary for a store."""
        return self.execute_query(f"""
            SELECT *
            FROM ${{catalog}}.${{schema}}.gold_inventory_summary
            WHERE store_id = {store_id}
        """)

    def get_dead_stock(self, store_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get dead stock items for a store."""
        return self.execute_query(f"""
            SELECT *
            FROM ${{catalog}}.${{schema}}.gold_dead_stock
            WHERE store_id = {store_id}
            ORDER BY soh_value DESC
            LIMIT {limit}
        """)

    def get_writeoff_summary(self, store_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get write-off summary for a store."""
        return self.execute_query(f"""
            SELECT *
            FROM ${{catalog}}.${{schema}}.gold_writeoff_summary
            WHERE store_id = {store_id}
              AND writeoff_date >= CURRENT_DATE() - {days}
            ORDER BY writeoff_date DESC
        """)

    def get_writeoff_detail(self, store_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get write-off details for a store."""
        return self.execute_query(f"""
            SELECT *
            FROM ${{catalog}}.${{schema}}.gold_writeoff_detail
            WHERE store_id = {store_id}
              AND writeoff_date >= CURRENT_DATE() - {days}
            ORDER BY writeoff_date DESC, writeoff_hour DESC
        """)

    def get_writeoff_trends(self, store_id: int) -> List[Dict[str, Any]]:
        """Get write-off trends for a store."""
        return self.execute_query(f"""
            SELECT *
            FROM ${{catalog}}.${{schema}}.gold_writeoff_trends
            WHERE store_id = {store_id}
        """)

    def get_alerts(self, store_id: Optional[int] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get alerts for a store."""
        conditions = ["expires_at >= CURRENT_DATE()"]
        if store_id:
            conditions.append(f"store_id = {store_id}")
        if severity:
            conditions.append(f"alert_severity = '{severity}'")

        where_clause = " AND ".join(conditions)

        return self.execute_query(f"""
            SELECT
                alert_id, store_id, store_code, alert_date, alert_time,
                alert_type, alert_severity, alert_title, alert_message,
                article_id, article_name, category_name, metric_value,
                threshold_value, action_recommended, is_acknowledged,
                created_at, expires_at
            FROM ${{catalog}}.${{schema}}.gold_store_alerts
            WHERE {where_clause}
            ORDER BY
                CASE alert_severity
                    WHEN 'HIGH' THEN 1
                    WHEN 'MEDIUM' THEN 2
                    ELSE 3
                END,
                alert_date DESC
        """)

    def get_top_products(self, store_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top products by APSD (Average Per Store Day) for a store."""
        return self.execute_query(f"""
            SELECT
                article_id,
                article_name,
                category_name,
                total_sales,
                total_qty,
                total_gp,
                gp_margin_pct,
                apsd
            FROM ${{catalog}}.${{schema}}.gold_product_performance
            WHERE store_id = {store_id}
            ORDER BY apsd DESC
            LIMIT {limit}
        """)

    def get_category_summary(self, store_id: int) -> List[Dict[str, Any]]:
        """Get category summary with sales and GP for a store."""
        return self.execute_query(f"""
            SELECT
                category_name,
                SUM(total_sales) as total_sales,
                SUM(total_gp) as total_gp,
                AVG(gp_margin_pct) as avg_gp_margin,
                SUM(total_qty) as total_qty
            FROM ${{catalog}}.${{schema}}.gold_product_performance
            WHERE store_id = {store_id}
            GROUP BY category_name
            ORDER BY total_sales DESC
        """)

    def get_budget_tracking(self, store_id: int) -> List[Dict[str, Any]]:
        """Get budget tracking data for a store."""
        return self.execute_query(f"""
            SELECT
                period_type,
                actual_sales,
                budget_sales,
                actual_vs_budget_pct,
                ly_sales,
                actual_vs_ly_pct
            FROM ${{catalog}}.${{schema}}.gold_budget_tracking
            WHERE store_id = {store_id}
        """)

    def get_writeoff_by_category(self, store_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get write-off totals by category."""
        return self.execute_query(f"""
            SELECT
                category_name,
                SUM(total_value) as total_value,
                SUM(total_qty) as total_qty,
                COUNT(*) as record_count
            FROM ${{catalog}}.${{schema}}.gold_writeoff_summary
            WHERE store_id = {store_id}
              AND writeoff_date >= CURRENT_DATE() - {days}
            GROUP BY category_name
            ORDER BY total_value DESC
        """)

    def get_writeoff_daily(self, store_id: int, days: int = 14) -> List[Dict[str, Any]]:
        """Get daily write-off totals for trend chart."""
        return self.execute_query(f"""
            SELECT
                writeoff_date,
                SUM(total_value) as total_value,
                SUM(total_qty) as total_qty,
                AVG(vs_cluster_value_pct) as avg_vs_cluster_pct
            FROM ${{catalog}}.${{schema}}.gold_writeoff_summary
            WHERE store_id = {store_id}
              AND writeoff_date >= CURRENT_DATE() - {days}
            GROUP BY writeoff_date
            ORDER BY writeoff_date
        """)

    def get_inventory_by_category(self, store_id: int) -> List[Dict[str, Any]]:
        """Get inventory status by category."""
        return self.execute_query(f"""
            SELECT
                category_name,
                COUNT(*) as total_items,
                SUM(CASE WHEN is_out_of_stock THEN 1 ELSE 0 END) as oos_count,
                SUM(CASE WHEN days_until_oos <= 3 AND NOT is_out_of_stock THEN 1 ELSE 0 END) as projected_oos_count,
                SUM(CASE WHEN is_dead_stock THEN 1 ELSE 0 END) as dead_stock_count,
                SUM(soh_value) as total_soh_value
            FROM ${{catalog}}.${{schema}}.gold_inventory_health
            WHERE store_id = {store_id}
              AND is_tailored_in = TRUE
            GROUP BY category_name
            ORDER BY total_items DESC
        """)

    def get_store_sentiment(self, store_id: int) -> List[Dict[str, Any]]:
        """Get customer sentiment data for a store."""
        return self.execute_query(f"""
            SELECT
                store_id,
                store_code,
                store_name,
                overall_rating,
                sentiment_score,
                review_count,
                positive_pct,
                neutral_pct,
                negative_pct,
                top_positive_themes,
                top_negative_themes,
                trend_direction,
                nps_score,
                last_updated
            FROM ${{catalog}}.${{schema}}.gold_store_sentiment
            WHERE store_id = {store_id}
        """)

    def get_all_store_sentiments(self) -> List[Dict[str, Any]]:
        """Get customer sentiment data for all stores (regional view)."""
        return self.execute_query("""
            SELECT
                store_id,
                store_code,
                store_name,
                overall_rating,
                sentiment_score,
                review_count,
                positive_pct,
                neutral_pct,
                negative_pct,
                top_positive_themes,
                top_negative_themes,
                trend_direction,
                nps_score,
                last_updated
            FROM ${catalog}.${schema}.gold_store_sentiment
            ORDER BY sentiment_score DESC
        """)


# Singleton instance with Streamlit caching
@st.cache_resource
def get_db() -> DatabaseClient:
    """Get cached database client instance."""
    return DatabaseClient()
