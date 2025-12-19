import streamlit as st
from databricks import sql
import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

# Ensure environment variable is set correctly
assert os.getenv('DATABRICKS_WAREHOUSE_ID'), "DATABRICKS_WAREHOUSE_ID must be set in app.yaml."
assert os.getenv('LOAN_DOCS_VOLUME'), "LOAN_DOCS_VOLUME must be set in app.yaml."

# Databricks config
cfg = Config()

# Workspace client for file operations
w = WorkspaceClient()

# Page configuration
st.set_page_config(
    page_title="Loan Explorer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern banking aesthetic
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-blue: #1e3a8a;
        --secondary-blue: #3b82f6;
        --accent-green: #10b981;
        --accent-yellow: #f59e0b;
        --accent-red: #ef4444;
        --bg-light: #f8fafc;
        --bg-card: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Header styling - matching reference */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Search bar styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .status-approved {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .status-pending {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-rejected {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .status-under-review {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    /* Loan card styling */
    .loan-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        height: 100%;
    }
    
    .loan-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .loan-card-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-wrap: wrap;
    }
    
    .loan-card-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .loan-id {
        font-size: 1rem;
        font-weight: 700;
        color: #1e3a8a;
    }
    
    .loan-name {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .loan-amount {
        font-size: 1.1rem;
        font-weight: 700;
        color: #10b981;
    }
    
    .loan-info {
        display: flex;
        gap: 1.5rem;
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid #f1f5f9;
        flex-wrap: wrap;
    }
    
    .loan-info-item {
        font-size: 0.8rem;
    }
    
    .loan-info-label {
        color: #64748b;
        font-weight: 500;
    }
    
    .loan-info-value {
        color: #1e293b;
        font-weight: 600;
        margin-left: 0.25rem;
    }
    
    /* Side button styling */
    .side-button-col {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    
    .side-button-col .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    
    .side-button-col .stButton > button:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e3a8a 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Card row wrapper */
    .card-row {
        margin-bottom: 0.75rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        padding: 0.75rem;
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    
    .metric-value {
        font-size: 1.1rem;
        color: #1e3a8a;
        font-weight: 700;
    }
    
    /* General button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        width: 100%;
        font-size: 1rem;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #64748b;
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Results count */
    .results-count {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 1rem;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_loan' not in st.session_state:
    st.session_state.selected_loan = None
if 'search_value' not in st.session_state:
    st.session_state.search_value = ""

# Database connection function
@st.cache_resource
def get_connection():
    return sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{cfg.warehouse_id}",
        credentials_provider=lambda: cfg.authenticate
    )

def search_loans(search_term):
    """Search for loans by application ID or applicant name"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if search_term:
        query = """
            SELECT application_id, applicant_name, loan_type, loan_amount, status, application_date,
                   interest_rate, loan_term_months
            FROM renjiharold_demo.loan_explorer.loan_applications
            WHERE LOWER(application_id) LIKE LOWER(?) OR LOWER(applicant_name) LIKE LOWER(?)
            ORDER BY application_date DESC
        """
        search_pattern = f"%{search_term}%"
        cursor.execute(query, (search_pattern, search_pattern))
    else:
        query = """
            SELECT application_id, applicant_name, loan_type, loan_amount, status, application_date,
                   interest_rate, loan_term_months
            FROM renjiharold_demo.loan_explorer.loan_applications
            ORDER BY application_date DESC
            LIMIT 50
        """
        cursor.execute(query)
    
    results = cursor.fetchall()
    cursor.close()
    return results

def get_loan_details(application_id):
    """Get full details for a specific loan"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT *
        FROM renjiharold_demo.loan_explorer.loan_applications
        WHERE application_id = ?
    """
    cursor.execute(query, (application_id,))
    result = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    
    if result:
        return dict(zip(columns, result))
    return None

def download_contract_pdf(application_id):
    """Download PDF contract from Unity Catalog volume using Databricks SDK.
    
    Returns tuple of (file_bytes, file_name) if successful, (None, None) otherwise.
    Reference: https://apps-cookbook.dev/docs/streamlit/volumes/volumes_download
    """
    pdf_dir = os.getenv('LOAN_DOCS_VOLUME')
    pdf_file = f"{application_id}_contract.pdf"
    pdf_path = f"{pdf_dir}/{pdf_file}"
    
    try:
        # Use Databricks SDK to download file from volume
        response = w.files.download(pdf_path)
        file_bytes = response.contents.read()
        return file_bytes, pdf_file
    except Exception as e:
        # File doesn't exist or other error
        return None, str(e)

def get_status_badge(status):
    """Generate HTML for status badge"""
    status_lower = status.lower().replace(' ', '-')
    status_class = f"status-{status_lower}"
    return f'<span class="status-badge {status_class}">{status}</span>'

def format_currency(amount):
    """Format number as currency"""
    return f"${amount:,.2f}"

def calculate_monthly_payment(principal, annual_rate, months):
    """Calculate monthly loan payment"""
    if annual_rate > 0:
        monthly_rate = annual_rate / 100 / 12
        payment = principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        payment = principal / months
    return payment

# Modal dialog for loan details
@st.dialog("Loan Application Details", width="large")
def show_loan_details(application_id):
    """Display loan details in a modal dialog"""
    loan = get_loan_details(application_id)
    
    if not loan:
        st.error("Loan not found")
        return
    
    # Header with loan ID and status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {loan['application_id']}")
        st.markdown(f"**{loan['applicant_name']}**")
    with col2:
        st.markdown(get_status_badge(loan['status']), unsafe_allow_html=True)
    
    st.divider()
    
    # Borrower Information
    st.markdown("#### 👤 Borrower Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Email**  \n{loan['email']}")
    with col2:
        st.markdown(f"**Phone**  \n{loan['phone']}")
    with col3:
        st.markdown(f"**Employment**  \n{loan['employment_status']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Credit Score**  \n{loan['credit_score']}")
    with col2:
        st.markdown(f"**Annual Income**  \n{format_currency(loan['annual_income'])}")
    with col3:
        st.markdown(f"**Employer**  \n{loan['employer_name'] or 'N/A'}")
    
    st.divider()
    
    # Loan Details
    st.markdown("#### 💰 Loan Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Loan Type**  \n{loan['loan_type']}")
    with col2:
        st.markdown(f"**Loan Amount**  \n{format_currency(loan['loan_amount'])}")
    with col3:
        st.markdown(f"**Interest Rate**  \n{loan['interest_rate']}%")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Loan Term**  \n{loan['loan_term_months']} months")
    with col2:
        st.markdown(f"**Application Date**  \n{loan['application_date']}")
    with col3:
        if loan.get('property_address'):
            st.markdown(f"**Property**  \n{loan['property_address']}")
    
    st.divider()
    
    # Payment Calculator
    st.markdown("#### 💵 Payment Summary")
    monthly_payment = calculate_monthly_payment(
        loan['loan_amount'],
        loan['interest_rate'],
        loan['loan_term_months']
    )
    total_payment = monthly_payment * loan['loan_term_months']
    total_interest = total_payment - loan['loan_amount']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly Payment", format_currency(monthly_payment))
    with col2:
        st.metric("Total Payment", format_currency(total_payment))
    with col3:
        st.metric("Total Interest", format_currency(total_interest))
    
    # Notes
    if loan.get('notes'):
        st.divider()
        st.markdown("#### 📝 Notes")
        st.info(loan['notes'])
    
    # Contract Download
    st.divider()
    pdf_bytes, result = download_contract_pdf(loan['application_id'])
    
    if pdf_bytes:
        st.download_button(
            label="📄 Download Loan Contract",
            data=pdf_bytes,
            file_name=f"{loan['application_id']}_contract.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("📄 Contract PDF not available for this application")

# Header
st.markdown("""
<div class="main-header">
    <h1>🏦 Loan Explorer</h1>
    <p>Search, view, and manage loan applications</p>
</div>
""", unsafe_allow_html=True)

# Search bar with Clear functionality
search_col1, search_col2 = st.columns([5, 1])
with search_col1:
    search_term = st.text_input(
        "Search",
        value=st.session_state.search_value,
        placeholder="🔍 Search by Loan ID or Applicant Name...",
        label_visibility="collapsed",
        key="search_input"
    )
    # Update session state when user types
    if search_term != st.session_state.search_value:
        st.session_state.search_value = search_term

with search_col2:
    if st.button("Clear", use_container_width=True):
        st.session_state.search_value = ""
        st.session_state.selected_loan = None
        st.rerun()

# Use the session state value for searching
active_search = st.session_state.search_value

# Loan List
results = search_loans(active_search)

if results:
    st.markdown(f'<div class="results-count">📋 {len(results)} loan application{"s" if len(results) != 1 else ""} found</div>', unsafe_allow_html=True)
    
    # Display each loan as a card with side button
    for row in results:
        app_id, name, loan_type, amount, status, app_date, interest_rate, loan_term = row
        
        # Use columns: card on left, button on right
        card_col, btn_col = st.columns([12, 1])
        
        with card_col:
            card_html = f"""
            <div class="loan-card">
                <div class="loan-card-header">
                    <div class="loan-card-left">
                        <span class="loan-id">{app_id}</span>
                        <span class="loan-name">• {name}</span>
                    </div>
                    <div class="loan-card-right">
                        {get_status_badge(status)}
                        <span class="loan-amount">{format_currency(amount)}</span>
                    </div>
                </div>
                <div class="loan-info">
                    <div class="loan-info-item">
                        <span class="loan-info-label">Type:</span>
                        <span class="loan-info-value">{loan_type}</span>
                    </div>
                    <div class="loan-info-item">
                        <span class="loan-info-label">Rate:</span>
                        <span class="loan-info-value">{interest_rate}%</span>
                    </div>
                    <div class="loan-info-item">
                        <span class="loan-info-label">Term:</span>
                        <span class="loan-info-value">{loan_term} months</span>
                    </div>
                    <div class="loan-info-item">
                        <span class="loan-info-label">Applied:</span>
                        <span class="loan-info-value">{app_date}</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
        
        with btn_col:
            st.markdown('<div class="side-button-col">', unsafe_allow_html=True)
            if st.button("View", key=f"view_{app_id}", use_container_width=True):
                show_loan_details(app_id)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Add spacing between rows
        st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <h3>No loans found</h3>
        <p>Try adjusting your search criteria</p>
    </div>
    """, unsafe_allow_html=True)
