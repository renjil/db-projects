"""
Compliance Document Management Dashboard
Displays and manages documents uploaded by various business units in the bank.

This app connects to a Databricks Lakebase (PostgreSQL) instance.
Reference: https://docs.databricks.com/aws/en/oltp/instances/query/notebook
"""

import streamlit as st
from databricks.sdk import WorkspaceClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
import uuid

# Initialize Databricks client
w = WorkspaceClient()

# Lakebase Configuration
INSTANCE_NAME = "fe-shared-demo"        # Lakebase instance name
DATABASE = "rh_compliance_app"       # PostgreSQL database name
SCHEMA = "audit"                  # PostgreSQL schema name
TABLE = "document_registry"       # Table name
POSTGRES_USER = "06c27421-2fda-44bc-8891-bd83bb09e08c"  # Update with your Service principal ID for Databricks App
TABLE_FULL_NAME = f"{SCHEMA}.{TABLE}"

# Page configuration
st.set_page_config(
    page_title="Document Compliance Dashboard",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .compliant {
        color: #28a745;
        font-weight: bold;
    }
    .non-compliant {
        color: #dc3545;
        font-weight: bold;
    }
    .pending {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_lakebase_connection():
    """Get a cached connection to the Lakebase PostgreSQL instance"""
    try:
        # Get the Lakebase instance details
        instance = w.database.get_database_instance(name=INSTANCE_NAME)
        
        # Generate OAuth credential for authentication
        cred = w.database.generate_database_credential(
            request_id=str(uuid.uuid4()), 
            instance_names=[INSTANCE_NAME]
        )
        
        # Connect to PostgreSQL using psycopg2
        conn = psycopg2.connect(
            host=instance.read_write_dns,
            dbname=DATABASE,
            user=POSTGRES_USER,
            password=cred.token,
            sslmode="require",
            port=5432
        )
        
        return conn
    except Exception as e:
        st.error(f"Error connecting to Lakebase: {str(e)}")
        return None

def execute_query(query):
    """Execute SQL query against Lakebase and return DataFrame"""
    try:
        conn = get_lakebase_connection()
        if conn is None:
            return pd.DataFrame()
        
        # Execute query and return as DataFrame
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return pd.DataFrame()

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.title("📋 Document Compliance Management System")
    st.caption("Banking Document Registry & Compliance Tracking")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    
    # Date range
    date_option = st.selectbox(
        "Time Period",
        ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"]
    )
    
    date_filters = {
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "Last 6 Months": 180,
        "Last Year": 365,
        "All Time": 10000
    }
    days_back = date_filters[date_option]
    
    # Business unit filter
    business_units_query = f"""
    SELECT DISTINCT business_unit 
    FROM {TABLE_FULL_NAME} 
    ORDER BY business_unit
    """
    bu_df = execute_query(business_units_query)
    
    all_business_units = ["All"] + (bu_df['business_unit'].tolist() if not bu_df.empty else [])
    selected_bu = st.multiselect(
        "Business Unit",
        all_business_units,
        default=["All"]
    )
    
    # Compliance status filter
    compliance_status_filter = st.multiselect(
        "Compliance Status",
        ["Compliant", "Non-Compliant", "Pending Review", "Under Investigation"],
        default=["Compliant", "Non-Compliant", "Pending Review", "Under Investigation"]
    )
    
    # Classification filter
    classification_filter = st.multiselect(
        "Classification Level",
        ["Public", "Internal", "Confidential", "Highly Confidential"],
        default=["Confidential", "Highly Confidential"]
    )
    
    # Archival filter
    show_archival_only = st.checkbox("Show only marked for archival", False)
    show_review_required = st.checkbox("Show only review required", False)
    
    st.divider()
    
    # Refresh button
    refresh_data = st.button("🔄 Refresh Data", type="primary", use_container_width=True)

# Build WHERE clause based on filters
where_clauses = [f"upload_date >= CURRENT_DATE - INTERVAL '{days_back} days'"]

if "All" not in selected_bu and selected_bu:
    bu_list = "','".join(selected_bu)
    where_clauses.append(f"business_unit IN ('{bu_list}')")

if compliance_status_filter:
    status_list = "','".join(compliance_status_filter)
    where_clauses.append(f"compliance_status IN ('{status_list}')")

if classification_filter:
    class_list = "','".join(classification_filter)
    where_clauses.append(f"classification IN ('{class_list}')")

if show_archival_only:
    where_clauses.append("marked_for_archival = true")

if show_review_required:
    where_clauses.append("review_required = true")

where_clause = " AND ".join(where_clauses)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📄 Documents", "📈 Analytics", "⚠️ Compliance Alerts"])

with tab1:
    # KPI Metrics
    kpi_query = f"""
    SELECT 
        COUNT(DISTINCT document_id) as total_documents,
        COUNT(DISTINCT business_unit) as active_business_units,
        SUM(file_size_mb) as total_storage_mb,
        COUNT(CASE WHEN marked_for_archival THEN 1 END) as archival_pending,
        COUNT(CASE WHEN compliance_status = 'Non-Compliant' THEN 1 END) as non_compliant,
        COUNT(CASE WHEN review_required AND next_review_date <= CURRENT_DATE + INTERVAL '30 days' THEN 1 END) as reviews_due_soon,
        COUNT(CASE WHEN classification IN ('Confidential', 'Highly Confidential') THEN 1 END) as sensitive_docs
    FROM {TABLE_FULL_NAME}
    WHERE {where_clause}
    """
    
    kpi_df = execute_query(kpi_query)
    
    if not kpi_df.empty:
        st.subheader("📊 Key Metrics")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        with col1:
            st.metric(
                "Total Documents",
                f"{int(kpi_df['total_documents'].iloc[0]):,}"
            )
        
        with col2:
            st.metric(
                "Business Units",
                f"{int(kpi_df['active_business_units'].iloc[0])}"
            )
        
        with col3:
            storage_gb = float(kpi_df['total_storage_mb'].iloc[0]) / 1024
            st.metric(
                "Total Storage",
                f"{storage_gb:.2f} GB"
            )
        
        with col4:
            archival = int(kpi_df['archival_pending'].iloc[0])
            st.metric(
                "Archival Pending",
                f"{archival:,}",
                delta=f"{archival} docs" if archival > 0 else None,
                delta_color="inverse"
            )
        
        with col5:
            non_compliant = int(kpi_df['non_compliant'].iloc[0])
            st.metric(
                "Non-Compliant",
                f"{non_compliant:,}",
                delta=f"⚠️ {non_compliant}" if non_compliant > 0 else "✓",
                delta_color="inverse"
            )
        
        with col6:
            reviews_due = int(kpi_df['reviews_due_soon'].iloc[0])
            st.metric(
                "Reviews Due",
                f"{reviews_due:,}",
                help="Reviews due in next 30 days"
            )
        
        with col7:
            sensitive = int(kpi_df['sensitive_docs'].iloc[0])
            st.metric(
                "Sensitive Docs",
                f"{sensitive:,}",
                help="Confidential & Highly Confidential"
            )
        
        st.divider()
        
        # Charts row 1
        col1, col2 = st.columns(2)
        
        with col1:
            # Documents by business unit
            bu_query = f"""
            SELECT 
                business_unit,
                COUNT(*) as doc_count,
                SUM(file_size_mb) as total_size_mb
            FROM {TABLE_FULL_NAME}
            WHERE {where_clause}
            GROUP BY business_unit
            ORDER BY doc_count DESC
            """
            bu_df = execute_query(bu_query)
            
            if not bu_df.empty:
                st.subheader("📁 Documents by Business Unit")
                fig1 = px.bar(
                    bu_df,
                    x='business_unit',
                    y='doc_count',
                    title='Document Count by Business Unit',
                    labels={'doc_count': 'Number of Documents', 'business_unit': 'Business Unit'},
                    color='doc_count',
                    color_continuous_scale='Blues'
                )
                fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Compliance status distribution
            compliance_query = f"""
            SELECT 
                compliance_status,
                COUNT(*) as count
            FROM {TABLE_FULL_NAME}
            WHERE {where_clause}
            GROUP BY compliance_status
            ORDER BY count DESC
            """
            compliance_df = execute_query(compliance_query)
            
            if not compliance_df.empty:
                st.subheader("✅ Compliance Status Distribution")
                
                colors = {
                    'Compliant': '#28a745',
                    'Non-Compliant': '#dc3545',
                    'Pending Review': '#ffc107',
                    'Under Investigation': '#fd7e14'
                }
                
                fig2 = px.pie(
                    compliance_df,
                    values='count',
                    names='compliance_status',
                    title='Compliance Status',
                    color='compliance_status',
                    color_discrete_map=colors
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        # Charts row 2
        col1, col2 = st.columns(2)
        
        with col1:
            # Documents by classification
            class_query = f"""
            SELECT 
                classification,
                COUNT(*) as count
            FROM {TABLE_FULL_NAME}
            WHERE {where_clause}
            GROUP BY classification
            ORDER BY 
                CASE classification
                    WHEN 'Highly Confidential' THEN 1
                    WHEN 'Confidential' THEN 2
                    WHEN 'Internal' THEN 3
                    WHEN 'Public' THEN 4
                END
            """
            class_df = execute_query(class_query)
            
            if not class_df.empty:
                st.subheader("🔒 Documents by Classification")
                fig3 = px.bar(
                    class_df,
                    x='classification',
                    y='count',
                    title='Classification Distribution',
                    color='classification',
                    color_discrete_map={
                        'Highly Confidential': '#721c24',
                        'Confidential': '#dc3545',
                        'Internal': '#ffc107',
                        'Public': '#28a745'
                    }
                )
                st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Upload trend
            trend_query = f"""
            SELECT 
                DATE_TRUNC('month', upload_date) as month,
                COUNT(*) as doc_count
            FROM {TABLE_FULL_NAME}
            WHERE {where_clause}
            GROUP BY DATE_TRUNC('month', upload_date)
            ORDER BY month DESC
            LIMIT 12
            """
            trend_df = execute_query(trend_query)
            
            if not trend_df.empty:
                st.subheader("📈 Upload Trend (Last 12 Months)")
                fig4 = px.line(
                    trend_df,
                    x='month',
                    y='doc_count',
                    title='Monthly Document Uploads',
                    markers=True
                )
                st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.subheader("📄 Document Registry")
    
    # Search functionality
    search_term = st.text_input("🔍 Search documents", placeholder="Enter document name, owner, or type...")
    
    # Main documents query
    docs_query = f"""
    SELECT 
        document_id,
        document_name,
        document_type,
        business_unit,
        owner_name,
        upload_date,
        file_size_mb,
        classification,
        compliance_status,
        marked_for_archival,
        review_required,
        next_review_date,
        storage_location
    FROM {TABLE_FULL_NAME}
    WHERE {where_clause}
    """
    
    if search_term:
        docs_query += f" AND (LOWER(document_name) LIKE LOWER('%{search_term}%') OR LOWER(owner_name) LIKE LOWER('%{search_term}%') OR LOWER(document_type) LIKE LOWER('%{search_term}%'))"
    
    docs_query += " ORDER BY upload_date DESC LIMIT 1000"
    
    docs_df = execute_query(docs_query)
    
    if not docs_df.empty:
        st.info(f"Showing {len(docs_df)} documents")
        
        # Display dataframe with styling
        st.dataframe(
            docs_df,
            use_container_width=True,
            height=500,
            column_config={
                "document_id": st.column_config.TextColumn("Document ID", width="small"),
                "document_name": st.column_config.TextColumn("Document Name", width="medium"),
                "upload_date": st.column_config.DatetimeColumn("Upload Date", format="YYYY-MM-DD"),
                "file_size_mb": st.column_config.NumberColumn("Size (MB)", format="%.2f"),
                "compliance_status": st.column_config.TextColumn("Status", width="small"),
                "marked_for_archival": st.column_config.CheckboxColumn("Archival"),
                "review_required": st.column_config.CheckboxColumn("Review Required"),
                "next_review_date": st.column_config.DateColumn("Next Review")
            }
        )
        
        # Export functionality
        csv = docs_df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"document_registry_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No documents found matching the criteria")

with tab3:
    st.subheader("📈 Advanced Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Document types distribution
        doc_type_query = f"""
        SELECT 
            document_type,
            COUNT(*) as count,
            AVG(file_size_mb) as avg_size
        FROM {TABLE_FULL_NAME}
        WHERE {where_clause}
        GROUP BY document_type
        ORDER BY count DESC
        LIMIT 10
        """
        doc_type_df = execute_query(doc_type_query)
        
        if not doc_type_df.empty:
            st.markdown("**Document Types**")
            fig = px.bar(
                doc_type_df,
                x='document_type',
                y='count',
                title='Top 10 Document Types',
                color='count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Retention period distribution
        retention_query = f"""
        SELECT 
            retention_period_years,
            COUNT(*) as count
        FROM {TABLE_FULL_NAME}
        WHERE {where_clause}
        GROUP BY retention_period_years
        ORDER BY retention_period_years
        """
        retention_df = execute_query(retention_query)
        
        if not retention_df.empty:
            st.markdown("**Retention Period Distribution**")
            fig = px.bar(
                retention_df,
                x='retention_period_years',
                y='count',
                title='Documents by Retention Period',
                labels={'retention_period_years': 'Years', 'count': 'Number of Documents'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Owner statistics
    st.divider()
    owner_query = f"""
    SELECT 
        owner_name,
        business_unit,
        COUNT(*) as doc_count,
        SUM(file_size_mb) as total_size_mb,
        COUNT(CASE WHEN compliance_status = 'Non-Compliant' THEN 1 END) as non_compliant_count
    FROM {TABLE_FULL_NAME}
    WHERE {where_clause}
    GROUP BY owner_name, business_unit
    ORDER BY doc_count DESC
    LIMIT 20
    """
    owner_df = execute_query(owner_query)
    
    if not owner_df.empty:
        st.markdown("**Top Document Owners**")
        st.dataframe(owner_df, use_container_width=True)

with tab4:
    st.subheader("⚠️ Compliance Alerts & Action Items")
    
    # Critical alerts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚨 Non-Compliant Documents")
        non_compliant_query = f"""
        SELECT 
            document_id,
            document_name,
            business_unit,
            owner_name,
            compliance_status,
            upload_date
        FROM {TABLE_FULL_NAME}
        WHERE compliance_status = 'Non-Compliant'
            AND {where_clause}
        ORDER BY upload_date DESC
        LIMIT 50
        """
        non_compliant_df = execute_query(non_compliant_query)
        
        if not non_compliant_df.empty:
            st.error(f"⚠️ {len(non_compliant_df)} non-compliant documents require immediate attention")
            st.dataframe(non_compliant_df, use_container_width=True, height=300)
        else:
            st.success("✅ No non-compliant documents found")
    
    with col2:
        st.markdown("#### 📅 Reviews Due Soon")
        review_due_query = f"""
        SELECT 
            document_id,
            document_name,
            business_unit,
            reviewer_name,
            next_review_date
        FROM {TABLE_FULL_NAME}
        WHERE review_required = true
            AND next_review_date <= CURRENT_DATE + INTERVAL '30 days'
            AND {where_clause}
        ORDER BY next_review_date ASC
        LIMIT 50
        """
        review_due_df = execute_query(review_due_query)
        
        if not review_due_df.empty:
            st.warning(f"📋 {len(review_due_df)} documents require review in the next 30 days")
            st.dataframe(review_due_df, use_container_width=True, height=300)
        else:
            st.success("✅ No reviews due in the next 30 days")
    
    st.divider()
    
    # Archival pending
    st.markdown("#### 🗄️ Documents Pending Archival")
    archival_query = f"""
    SELECT 
        document_id,
        document_name,
        business_unit,
        owner_name,
        upload_date,
        archival_date,
        file_size_mb
    FROM {TABLE_FULL_NAME}
    WHERE marked_for_archival = true
        AND archival_date <= CURRENT_DATE + INTERVAL '90 days'
        AND {where_clause}
    ORDER BY archival_date ASC
    LIMIT 100
    """
    archival_df = execute_query(archival_query)
    
    if not archival_df.empty:
        st.info(f"📦 {len(archival_df)} documents scheduled for archival in the next 90 days")
        st.dataframe(archival_df, use_container_width=True)
    else:
        st.info("No documents scheduled for archival in the next 90 days")

# Footer
st.divider()
st.caption(f"🔐 Data sourced from: {TABLE_FULL_NAME} (Lakebase) | Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Powered by Databricks Lakebase")

