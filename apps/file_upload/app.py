"""
File Upload to Unity Catalog Volumes

A Databricks application that provides a user-friendly interface for uploading
files directly to Unity Catalog Volumes.

Features:
- Upload any file type to Unity Catalog Volumes
- Three-level namespace validation (catalog.schema.volume)
- Secure service principal authentication
- Real-time upload feedback
- File overwrite support
"""

import io
import os
from datetime import datetime
import streamlit as st
from databricks.sdk import WorkspaceClient

# Page configuration
st.set_page_config(
    page_title="File Upload to Unity Catalog",
    page_icon="📤",
    layout="centered"
)

# Initialize Databricks client with environment variables (secure)
try:
    w = WorkspaceClient(
        host=os.getenv("DATABRICKS_HOST", "https://your-workspace.cloud.databricks.com"),
        client_id=os.getenv("SP_CLIENT_ID"),
        client_secret=os.getenv("SP_CLIENT_SECRET")
    )
except Exception as e:
    st.error(f"Failed to initialize Databricks client: {str(e)}")
    st.info("Please ensure SP_CLIENT_ID and SP_CLIENT_SECRET environment variables are configured.")
    st.stop()

# Header
st.title("📤 File Upload to Unity Catalog")
st.markdown("Upload files directly to Unity Catalog Volumes")

# Helper function to format file size
def format_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

# File uploader
st.subheader("1. Select File")
uploaded_file = st.file_uploader(
    label="Choose a file to upload",
    help="All file types are supported. Maximum size: 200MB",
    label_visibility="collapsed"
)

# Show file details if file is selected
if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("File Name", uploaded_file.name)
    with col2:
        st.metric("File Size", format_file_size(uploaded_file.size))

st.divider()

# Volume path input
st.subheader("2. Specify Destination")
upload_volume_path = st.text_input(
    label="Unity Catalog Volume Path",
    placeholder="catalog.schema.volume_name",
    help="Enter in format: catalog.schema.volume_name (e.g., main.marketing.raw_files)",
    value=""
)

# Optional: Add subdirectory path
use_subdirectory = st.checkbox("Upload to subdirectory", value=False)
subdirectory = ""
if use_subdirectory:
    subdirectory = st.text_input(
        label="Subdirectory path (optional)",
        placeholder="folder/subfolder",
        help="Enter path without leading or trailing slashes"
    )

st.divider()

# Upload button
st.subheader("3. Upload")

if st.button("📤 Upload File", type="primary", use_container_width=True):
    # Validation
    if not uploaded_file:
        st.warning("⚠️ Please select a file to upload")
    elif not upload_volume_path:
        st.warning("⚠️ Please specify a volume path")
    else:
        try:
            with st.spinner("Uploading file..."):
                # Read file content
                file_bytes = uploaded_file.read()
                binary_data = io.BytesIO(file_bytes)
                file_name = uploaded_file.name
                
                # Parse and validate volume path
                parts = upload_volume_path.strip().split(".")
                
                if len(parts) != 3:
                    st.error("❌ Invalid volume path format. Please use: catalog.schema.volume_name")
                else:
                    catalog = parts[0]
                    schema = parts[1]
                    volume_name = parts[2]
                    
                    # Build full file path
                    if use_subdirectory and subdirectory:
                        # Clean subdirectory path
                        subdirectory_clean = subdirectory.strip().strip("/")
                        volume_file_path = f"/Volumes/{catalog}/{schema}/{volume_name}/{subdirectory_clean}/{file_name}"
                    else:
                        volume_file_path = f"/Volumes/{catalog}/{schema}/{volume_name}/{file_name}"
                    
                    # Upload file using Databricks SDK
                    w.files.upload(volume_file_path, binary_data, overwrite=True)
                    
                    # Success message
                    st.success(f"✅ File uploaded successfully!")
                    st.code(volume_file_path, language=None)
                    
                    # Show upload details
                    st.info(f"""
                    **Upload Details:**
                    - File: {file_name}
                    - Size: {format_file_size(uploaded_file.size)}
                    - Destination: {volume_file_path}
                    - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """)
                    
        except Exception as e:
            st.error(f"❌ Error uploading file: {str(e)}")
            
            # Provide helpful error messages
            error_msg = str(e).lower()
            if "permission" in error_msg or "access" in error_msg:
                st.info("""
                **Permission Issue:**
                The service principal may not have write access to this volume.
                
                Grant permissions using:
                ```sql
                GRANT WRITE_VOLUME ON VOLUME {catalog}.{schema}.{volume_name} 
                TO `<service-principal-id>`;
                ```
                """)
            elif "not found" in error_msg or "does not exist" in error_msg:
                st.info(f"""
                **Volume Not Found:**
                The volume `{upload_volume_path}` may not exist.
                
                Create it using:
                ```sql
                CREATE VOLUME IF NOT EXISTS {upload_volume_path};
                ```
                """)

# Sidebar with instructions
with st.sidebar:
    st.header("📖 Instructions")
    
    st.markdown("""
    ### How to Use
    
    1. **Select a file** using the file uploader
    2. **Enter volume path** in format: `catalog.schema.volume`
    3. **Optionally** specify a subdirectory
    4. **Click Upload** to save the file
    
    ### Volume Path Format
    
    Unity Catalog volumes use a three-level namespace:
    - **Catalog**: Top-level container
    - **Schema**: Database/schema name  
    - **Volume**: Volume name
    
    **Example:** `main.marketing.raw_files`
    
    ### Supported Files
    
    All file types are supported:
    - Data: CSV, JSON, Parquet, Avro
    - Documents: PDF, DOCX, TXT
    - Media: PNG, JPG, MP4
    - Code: PY, SQL, YAML
    - Archives: ZIP, TAR, GZ
    
    ### Tips
    
    - Files with the same name will be overwritten
    - Maximum file size: 200MB
    - Use subdirectories to organize files
    - Check permissions if upload fails
    """)
    
    st.divider()
    
    st.markdown("""
    ### Need Help?
    
    - [Unity Catalog Volumes Docs](https://docs.databricks.com/en/volumes/)
    - [Service Principal Setup](https://docs.databricks.com/en/dev-tools/service-principals.html)
    """)

# Footer
st.divider()
st.caption("🔐 Powered by Databricks Unity Catalog | Secure file upload via service principal authentication")

