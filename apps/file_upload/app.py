import io
import os
import streamlit as st
from databricks.sdk import WorkspaceClient

SP_CLIENT_ID = os.getenv("SP_CLIENT_ID")
SP_CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")

w = WorkspaceClient(
    host="https://e2-demo-field-eng.cloud.databricks.com",
    client_id="43d91404-054d-4e45-800a-7dc30da01a9e",
    client_secret="dosea74b304b76a9ba9e95000e4cac8b55fa"
)

st.title("File Upload to Unity Catalog Volume")

uploaded_file = st.file_uploader(label="Select file")

upload_volume_path = st.text_input(
    label="Specify a three-level Unity Catalog volume name (catalog.schema.volume_name)",
    placeholder="main.marketing.raw_files",
)

if st.button("Save changes"):
    if uploaded_file and upload_volume_path:
        try:
            file_bytes = uploaded_file.read()
            binary_data = io.BytesIO(file_bytes)
            file_name = uploaded_file.name

            parts = upload_volume_path.strip().split(".")
            
            if len(parts) != 3:
                st.error("Please provide a valid three-level volume path")
            else:
                catalog = parts[0]
                schema = parts[1]
                volume_name = parts[2]

                volume_file_path = f"/Volumes/{catalog}/{schema}/{volume_name}/{file_name}"
                
                # Upload using custom service principal
                w.files.upload(volume_file_path, binary_data, overwrite=True)
                
                st.success(f"File uploaded successfully to {volume_file_path}")
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
    else:
        st.warning("Please select a file and specify a volume path")