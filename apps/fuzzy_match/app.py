"""
AI Fuzzy Match — Databricks AI-powered entity similarity matching.

Upload two datasets, select a column from each, and run ai_similarity()
to find matching entities across datasets.
"""

import io
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

# ── Configuration ─────────────────────────────────────────────────────────────

CATALOG = "renjiharold_demo"
SCHEMA = "sanctions_screening"
VOLUME = "uploads"
VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

assert os.getenv("DATABRICKS_WAREHOUSE_ID"), "DATABRICKS_WAREHOUSE_ID must be set in app.yaml."

cfg = Config()
w = WorkspaceClient()

# ── Page setup ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Fuzzy Match",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ── Header ─────────────────────────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b4965 55%, #5fa8d3 100%);
        padding: 2.5rem 3rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 30px rgba(13, 27, 42, 0.2);
        position: relative;
        overflow: hidden;
    }
    .main-header::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(95,168,211,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 0.4rem;
        letter-spacing: -0.02em;
    }
    .main-header .subtitle {
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        margin: 0;
    }
    .main-header .powered {
        color: rgba(255,255,255,0.45);
        font-size: 0.78rem;
        margin-top: 0.6rem;
    }

    /* ── Section titles ─────────────────────────────────────── */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1b4965;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── Metric cards ───────────────────────────────────────── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 0.75rem;
        border-radius: 10px;
        border: 1px solid #bae6fd;
    }

    /* ── Pair info banner ───────────────────────────────────── */
    .pair-info {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        font-size: 0.95rem;
        color: #1b4965;
        margin-bottom: 1rem;
    }

    /* ── Download button ────────────────────────────────────── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #166534 0%, #22c55e 100%);
        color: white;
        border: none;
        font-weight: 700;
        border-radius: 10px;
        padding: 0.8rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #14532d 0%, #166534 100%);
        transform: translateY(-1px);
    }

    /* ── Scrollbar ──────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 3px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

    /* ── Hide Streamlit chrome ──────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    """
<div class="main-header">
    <h1>🔗 AI Fuzzy Match</h1>
    <p class="subtitle">AI-powered entity similarity matching across datasets</p>
    <p class="powered">Powered by Databricks AI Functions · ai_similarity()</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Helper functions ──────────────────────────────────────────────────────────


@st.cache_resource
def get_connection():
    return sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{cfg.warehouse_id}",
        credentials_provider=lambda: cfg.authenticate,
    )


def read_uploaded_file(uploaded_file):
    """Parse an uploaded file to a DataFrame. Returns None on failure."""
    if uploaded_file is None:
        return None
    ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
    if ext not in ALLOWED_EXTENSIONS:
        st.error(
            f"**Unsupported file type** `.{ext}`\n\n"
            "Please upload a **CSV** (`.csv`) or **Excel** (`.xlsx`, `.xls`) file."
        )
        return None
    try:
        return pd.read_csv(uploaded_file) if ext == "csv" else pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"**Could not read file:** {exc}")
        return None


def upload_to_volume(df: pd.DataFrame, filename: str) -> str:
    """Write DataFrame as CSV to the Unity Catalog volume and return the path."""
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    path = f"{VOLUME_PATH}/{filename}"
    w.files.upload(path, buf, overwrite=True)
    return path


def sanitize_col(name: str) -> str:
    """Strip backticks from column names to prevent SQL injection."""
    return name.replace("`", "")


def run_similarity_query(path1: str, col1: str, path2: str, col2: str) -> pd.DataFrame:
    """Execute the ai_similarity cross-join query and return results."""
    col1, col2 = sanitize_col(col1), sanitize_col(col2)
    query = f"""
    WITH source AS (
        SELECT DISTINCT TRIM(CAST(`{col1}` AS STRING)) AS source_value
        FROM read_files('{path1}', format => 'csv', header => 'true')
        WHERE `{col1}` IS NOT NULL
          AND TRIM(CAST(`{col1}` AS STRING)) != ''
    ),
    target AS (
        SELECT DISTINCT TRIM(CAST(`{col2}` AS STRING)) AS target_value
        FROM read_files('{path2}', format => 'csv', header => 'true')
        WHERE `{col2}` IS NOT NULL
          AND TRIM(CAST(`{col2}` AS STRING)) != ''
    )
    SELECT
        source_value,
        target_value,
        ai_similarity(source_value, target_value) AS similarity_score
    FROM source CROSS JOIN target
    ORDER BY similarity_score DESC
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    cols = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    df = pd.DataFrame(rows, columns=cols)
    df["similarity_score"] = pd.to_numeric(df["similarity_score"], errors="coerce")
    return df


# ── Session state ─────────────────────────────────────────────────────────────

if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "result_col1" not in st.session_state:
    st.session_state.result_col1 = None
if "result_col2" not in st.session_state:
    st.session_state.result_col2 = None

# ── File upload ───────────────────────────────────────────────────────────────

left, right = st.columns(2, gap="large")

with left:
    st.markdown(
        '<div class="section-title">📄 Source Dataset</div>',
        unsafe_allow_html=True,
    )
    file1 = st.file_uploader(
        "Upload source file",
        type=list(ALLOWED_EXTENSIONS),
        key="file1",
        help="CSV or Excel file containing the source entities (e.g. portfolio holdings)",
    )
    df1 = read_uploaded_file(file1)
    col1_name = None
    if df1 is not None:
        col1_name = st.selectbox(
            "Select column to match",
            df1.columns.tolist(),
            key="sel_col1",
        )
        n_unique = df1[col1_name].dropna().nunique()
        st.caption(f"{len(df1):,} rows · {n_unique:,} unique values in **{col1_name}**")
        with st.expander("Preview data", expanded=True):
            st.dataframe(df1.head(8), use_container_width=True, hide_index=True)

with right:
    st.markdown(
        '<div class="section-title">📄 Target Dataset</div>',
        unsafe_allow_html=True,
    )
    file2 = st.file_uploader(
        "Upload target file",
        type=list(ALLOWED_EXTENSIONS),
        key="file2",
        help="CSV or Excel file containing the target entities to match against (e.g. sanctions list)",
    )
    df2 = read_uploaded_file(file2)
    col2_name = None
    if df2 is not None:
        col2_name = st.selectbox(
            "Select column to match",
            df2.columns.tolist(),
            key="sel_col2",
        )
        n_unique = df2[col2_name].dropna().nunique()
        st.caption(f"{len(df2):,} rows · {n_unique:,} unique values in **{col2_name}**")
        with st.expander("Preview data", expanded=True):
            st.dataframe(df2.head(8), use_container_width=True, hide_index=True)

# ── Matching controls ─────────────────────────────────────────────────────────

st.divider()

if df1 is not None and df2 is not None and col1_name and col2_name:
    u1 = df1[col1_name].dropna().nunique()
    u2 = df2[col2_name].dropna().nunique()
    total_pairs = u1 * u2

    st.markdown(
        f'<div class="pair-info">'
        f"<strong>{u1:,}</strong> unique source values × "
        f"<strong>{u2:,}</strong> unique target values = "
        f"<strong>{total_pairs:,}</strong> pairs to evaluate"
        f"</div>",
        unsafe_allow_html=True,
    )

    if total_pairs > 10_000:
        st.warning(
            "Large number of pairs detected. "
            "The query may take several minutes. Consider reducing the dataset size."
        )

ctrl_left, ctrl_right = st.columns([2, 3])

with ctrl_right:
    threshold = st.slider(
        "Minimum similarity threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
        help="Filter results to only show pairs at or above this similarity score.",
    )

with ctrl_left:
    run_disabled = df1 is None or df2 is None
    run_clicked = st.button(
        "🚀 Run AI Similarity Matching",
        type="primary",
        use_container_width=True,
        disabled=run_disabled,
    )

# ── Execute matching ──────────────────────────────────────────────────────────

if run_clicked:
    if df1 is None or df2 is None:
        st.error("Please upload both files before running.")
    elif not col1_name or not col2_name:
        st.error("Please select a column from each dataset.")
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with st.spinner("Uploading files to Unity Catalog volume…"):
                p1 = upload_to_volume(df1, f"source_{ts}.csv")
                p2 = upload_to_volume(df2, f"target_{ts}.csv")

            with st.spinner(
                "Running AI similarity matching — this may take several minutes for large datasets…"
            ):
                results_df = run_similarity_query(p1, col1_name, p2, col2_name)

            st.session_state.results_df = results_df
            st.session_state.result_col1 = col1_name
            st.session_state.result_col2 = col2_name

        except Exception as exc:
            st.error(f"**Matching failed:** {exc}")
            error_msg = str(exc).lower()
            if "volume" in error_msg or "not found" in error_msg:
                st.info(
                    f"The volume `{CATALOG}.{SCHEMA}.{VOLUME}` may not exist. "
                    f"Create it with:\n```sql\n"
                    f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME};\n```"
                )

# ── Results ───────────────────────────────────────────────────────────────────

if st.session_state.results_df is not None:
    results_df = st.session_state.results_df.copy()
    c1 = st.session_state.result_col1
    c2 = st.session_state.result_col2

    if threshold > 0:
        results_df = results_df[results_df["similarity_score"] >= threshold]

    display_df = results_df.rename(
        columns={
            "source_value": f"Source ({c1})",
            "target_value": f"Target ({c2})",
            "similarity_score": "Similarity Score",
        }
    )

    st.divider()
    st.markdown(
        '<div class="section-title">📊 Matching Results</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Pairs", f"{len(display_df):,}")
    with m2:
        high = len(results_df[results_df["similarity_score"] >= 0.7])
        st.metric("High Similarity (≥ 0.7)", f"{high:,}")
    with m3:
        avg = results_df["similarity_score"].mean() if len(results_df) > 0 else 0
        st.metric("Average Score", f"{avg:.3f}")
    with m4:
        mx = results_df["similarity_score"].max() if len(results_df) > 0 else 0
        st.metric("Highest Score", f"{mx:.3f}")

    if len(results_df) > 0:
        fig = px.histogram(
            results_df,
            x="similarity_score",
            nbins=20,
            labels={"similarity_score": "Similarity Score", "count": "Pair Count"},
            color_discrete_sequence=["#1b4965"],
        )
        fig.update_layout(
            bargap=0.05,
            title_font_size=14,
            xaxis_title="Similarity Score",
            yaxis_title="Number of Pairs",
            height=300,
            margin=dict(t=30, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "Similarity Score": st.column_config.ProgressColumn(
                "Similarity Score",
                format="%.3f",
                min_value=0,
                max_value=1,
            ),
        },
    )

    csv_data = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_data,
        file_name=f"fuzzy_match_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("ℹ️ About")
    st.markdown(
        """
    **AI Fuzzy Match** uses Databricks
    [`ai_similarity()`](https://docs.databricks.com/en/sql/language-manual/functions/ai_similarity.html)
    to compare entities across two datasets.

    ### How it works

    1. Upload two files (CSV or Excel)
    2. Select the column to compare from each
    3. Click **Run** — the app uploads data to a
       Unity Catalog volume and runs a cross-join
       with `ai_similarity()` on a SQL Warehouse
    4. Review results and download

    ### Tips

    - Keep datasets small (< 200 unique values each)
      for faster results
    - Use the threshold slider to focus on
      high-confidence matches
    - Results are sorted by similarity score
      (highest first)

    ### Use cases

    - Sanctions screening
    - Customer deduplication
    - Product catalog matching
    - Vendor name normalization
    """
    )

    st.divider()
    st.caption(f"Volume: `{CATALOG}.{SCHEMA}.{VOLUME}`")

# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    f"🔐 Data stored in Unity Catalog volume `{CATALOG}.{SCHEMA}.{VOLUME}` · "
    "Powered by Databricks AI Functions"
)
