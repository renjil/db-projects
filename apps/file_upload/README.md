# File Upload to Unity Catalog Volumes

A simple yet powerful Databricks application that enables users to upload files directly to Unity Catalog Volumes through an intuitive web interface.

## Overview

This Streamlit-based app provides a user-friendly way to upload files to Unity Catalog Volumes without requiring command-line access or notebook knowledge. It's designed for business users, data analysts, and anyone who needs to quickly upload files to Databricks storage.

**Perfect for Business Users**: This solution eliminates the need for business users to navigate complex cloud storage consoles (AWS S3, Azure Blob Storage, Google Cloud Storage). Instead of logging into AWS/Azure consoles and manually dropping files into buckets, users can simply use this intuitive web interface to upload their reference data, lookup tables, and other files directly to Unity Catalog Volumes. This makes the data upload process seamless and accessible to non-technical users.

## Features

### Core Functionality
- **📤 File Upload**: Upload any file type through a simple drag-and-drop interface
- **🗂️ Unity Catalog Integration**: Direct upload to Unity Catalog Volumes
- **✅ Path Validation**: Validates three-level namespace format (catalog.schema.volume)
- **♻️ Overwrite Support**: Automatically overwrites existing files with the same name
- **✨ Real-time Feedback**: Success/error messages with file paths
- **🔐 Secure Authentication**: Uses service principal authentication

### User Experience
- Clean, intuitive interface
- Clear instructions and placeholders
- Immediate upload confirmation
- Error handling with helpful messages
- No technical knowledge required

## How It Works

1. **Select a File**: Click "Browse files" or drag-and-drop to select your file
2. **Specify Destination**: Enter the Unity Catalog volume path in format: `catalog.schema.volume_name`
3. **Upload**: Click "Save changes" to upload the file
4. **Confirmation**: See the full path where your file was saved

## Why This Solution?

### Traditional Approach (Complex) ❌
```
Business User needs to upload reference data
    ↓
1. Request AWS/Azure console access (IT ticket, days of waiting)
    ↓
2. Complete cloud security training
    ↓
3. Learn cloud storage concepts (buckets, containers, paths)
    ↓
4. Navigate complex cloud console UI
    ↓
5. Find correct bucket/container (often unclear naming)
    ↓
6. Configure permissions (often requires IT help)
    ↓
7. Upload file (hope you got the path right!)
    ↓
8. Verify file is accessible to data pipelines
```

**Problems**:
- 🚫 Requires cloud console access and training
- 🚫 IT tickets and approval delays
- 🚫 Complex permissions and IAM policies
- 🚫 Risk of uploading to wrong location
- 🚫 No validation or immediate feedback
- 🚫 Difficult for non-technical users

### This App (Simple) ✅
```
Business User needs to upload reference data
    ↓
1. Open Databricks App in browser
    ↓
2. Drag-and-drop file
    ↓
3. Enter volume name (e.g., main.sales.reference_data)
    ↓
4. Click Upload
    ↓
5. Done! File immediately available
```

**Benefits**:
- ✅ No cloud console access needed
- ✅ No special training required
- ✅ Self-service in seconds
- ✅ Automatic path validation
- ✅ Immediate confirmation and feedback
- ✅ Files directly in Unity Catalog (governed and tracked)
- ✅ Works for any business user

### Real-World Impact

**Before**:
- Sales team needs 2-3 days to upload new price list
- Requires IT support ticket
- Training session needed for cloud console
- Risk of uploading to wrong location

**After**:
- Sales team uploads price list in 30 seconds
- Self-service, no IT involvement
- No training needed beyond "drag and drop"
- Automatic validation ensures correct destination

**Time Saved**: From days → seconds  
**User Experience**: From frustration → simplicity  
**IT Burden**: From tickets → zero maintenance

## Use Cases

### Reference Data Management (Primary Use Case)
**Problem**: Business users traditionally need to upload reference data (price lists, product catalogs, customer mappings, etc.) by:
- Logging into AWS Console → S3 buckets
- Navigating Azure Portal → Blob Storage containers
- Managing GCP Console → Cloud Storage buckets
- Understanding cloud storage paths and permissions
- Dealing with complex IAM policies

**Solution**: This app provides a simple, self-service interface where business users can:
- ✅ Upload reference data in seconds via drag-and-drop
- ✅ No cloud console access needed
- ✅ No AWS/Azure/GCP training required
- ✅ Automatic validation and error handling
- ✅ Direct integration with Unity Catalog Volumes
- ✅ Immediate availability for data pipelines and analytics

**Common Reference Data Examples**:
- Product price lists (CSV/Excel)
- Customer mapping tables
- Regional sales territories
- Currency exchange rates
- Holiday calendars
- Vendor information
- Employee hierarchies
- Store location data

### Data Ingestion
- Upload CSV, JSON, or Parquet files for data processing
- Load reference data or lookup tables
- Import configuration files

### Document Management
- Store reports, PDFs, or documentation
- Archive important files
- Share files with data teams

### Machine Learning
- Upload training datasets
- Store model artifacts
- Share feature engineering files

### Collaboration
- Share files between teams
- Provide data to notebooks and jobs
- Centralize file storage

## Example Usage

### Example 1: Upload a CSV File
```
File: sales_data.csv
Volume Path: main.marketing.raw_files
Result: /Volumes/main/marketing/raw_files/sales_data.csv
```

### Example 2: Upload a JSON Config
```
File: config.json
Volume Path: dev.engineering.configs
Result: /Volumes/dev/engineering/configs/config.json
```

### Example 3: Upload a PDF Report
```
File: quarterly_report.pdf
Volume Path: prod.finance.reports
Result: /Volumes/prod/finance/reports/quarterly_report.pdf
```

## Setup Instructions

### Prerequisites

1. **Unity Catalog Volume**: Create a volume if you don't have one
   ```sql
   CREATE VOLUME IF NOT EXISTS catalog.schema.volume_name;
   ```

2. **Service Principal**: Create a service principal with permissions to write to the volume
   - Go to Databricks Settings → Identity and Access → Service Principals
   - Create a new service principal or use an existing one
   - Note the Client ID and generate a Client Secret

3. **Grant Permissions**: Give the service principal write access
   ```sql
   GRANT WRITE_VOLUME ON VOLUME catalog.schema.volume_name TO `<service-principal-id>`;
   ```

### Configuration

1. **Create Secrets**: Store all credentials securely in Databricks secrets
   ```bash
   # Create secret scope
   databricks secrets create-scope rh-demo
   
   # Store Databricks host
   databricks secrets put-secret rh-demo databricks-host \
     --string-value "https://your-workspace.cloud.databricks.com"
   
   # Store service principal credentials
   databricks secrets put-secret rh-demo sp-client-id \
     --string-value "<your-client-id>"
   databricks secrets put-secret rh-demo sp-client-secret \
     --string-value "<your-client-secret>"
   ```

2. **Verify Configuration**: The app is already configured to use environment variables
   
   **app.py** (already configured ✅):
   ```python
   w = WorkspaceClient(
       host=os.getenv("DATABRICKS_HOST"),
       client_id=os.getenv("SP_CLIENT_ID"),
       client_secret=os.getenv("SP_CLIENT_SECRET")
   )
   ```

   **app.yaml** (already configured ✅):
   ```yaml
   env:
     - name: DATABRICKS_HOST
       value: "{{secrets/rh-demo/databricks-host}}"
     - name: SP_CLIENT_ID
       value: "{{secrets/rh-demo/sp-client-id}}"
     - name: SP_CLIENT_SECRET
       value: "{{secrets/rh-demo/sp-client-secret}}"
   ```

3. **Deploy**: Upload to Databricks and deploy the app
   - The app will automatically read credentials from secrets
   - No code changes needed - configuration is complete!

## Technical Details

### Authentication
The app uses **OAuth M2M (machine-to-machine)** authentication via service principal credentials. This ensures secure, programmatic access to Unity Catalog Volumes.

### File Handling
- Files are read into memory as bytes
- Converted to `BytesIO` stream for upload
- Uploaded via Databricks SDK `files.upload()` method
- Original filename is preserved

### Path Structure
Unity Catalog Volumes use a three-level namespace:
```
/Volumes/{catalog}/{schema}/{volume_name}/{file_path}
```

### Supported File Types
All file types are supported:
- Data files: CSV, JSON, Parquet, Avro, ORC
- Documents: PDF, DOCX, TXT, MD
- Media: PNG, JPG, MP4
- Code: PY, SQL, YAML, JSON
- Archives: ZIP, TAR, GZ

### File Size Limits
- Maximum file size depends on Streamlit configuration
- Default: 200 MB per file
- Can be increased via Streamlit settings

## Security Considerations

### Best Practices
✅ **DO:**
- Use service principals (not personal access tokens)
- Store credentials in Databricks secrets
- Grant minimal necessary permissions
- Use separate service principals per app
- Regularly rotate credentials

❌ **DON'T:**
- Hardcode credentials in code
- Share service principal secrets
- Grant overly broad permissions
- Use personal credentials for apps
- Commit secrets to version control

### ✅ Security Configuration

The app uses environment variables for all credentials (properly configured):
```python
w = WorkspaceClient(
    host=os.getenv("DATABRICKS_HOST"),
    client_id=os.getenv("SP_CLIENT_ID"),
    client_secret=os.getenv("SP_CLIENT_SECRET")
)
```

**Environment variables are configured in `app.yaml`:**
```yaml
env:
  - name: DATABRICKS_HOST
    value: "{{secrets/rh-demo/databricks-host}}"
  - name: SP_CLIENT_ID
    value: "{{secrets/rh-demo/sp-client-id}}"
  - name: SP_CLIENT_SECRET
    value: "{{secrets/rh-demo/sp-client-secret}}"
```

**All credentials are securely stored in Databricks secrets!** ✅

## Improvements & Enhancements

### Suggested Improvements
1. **Add File Size Display** - Show uploaded file size
2. **Multiple File Upload** - Allow batch uploads
3. **Progress Bar** - Show upload progress for large files
4. **File Preview** - Preview CSV/JSON before upload
5. **Upload History** - Show recently uploaded files
6. **Folder Creation** - Create subdirectories in volumes
7. **File Listing** - Browse existing files in volumes
8. **File Deletion** - Remove uploaded files
9. **Metadata Tags** - Add custom metadata to uploads

### Potential Features

- **Drag-and-Drop Zone**: Enhanced UI for file selection
- **File Validation**: Check file types, sizes before upload
- **Thumbnail Preview**: For images and PDFs
- **Batch Operations**: Upload multiple files at once
- **Access Logs**: Track who uploaded what and when
- **File Search**: Search uploaded files by name or date
- **Download**: Download files from volumes
- **Share Links**: Generate shareable links to files

## Troubleshooting

### Issue: "Permission Denied"
**Cause**: Service principal doesn't have write permissions  
**Solution**: Grant WRITE_VOLUME permission to the service principal

### Issue: "Volume Not Found"
**Cause**: Volume doesn't exist or path is incorrect  
**Solution**: Verify volume exists and path format is correct

### Issue: "Authentication Failed"
**Cause**: Invalid credentials or expired secret  
**Solution**: Verify service principal credentials and regenerate if needed

### Issue: "File Too Large"
**Cause**: File exceeds size limit  
**Solution**: Increase Streamlit file upload limit or split file

## API Reference

### WorkspaceClient.files.upload()

```python
w.files.upload(
    file_path: str,        # Full path in /Volumes/...
    contents: BytesIO,     # File content as bytes
    overwrite: bool        # True to replace existing file
)
```

### Unity Catalog Volume Path

```
/Volumes/{catalog}/{schema}/{volume}/{path/to/file}
```

- **catalog**: Top-level catalog name
- **schema**: Schema within the catalog
- **volume**: Volume within the schema
- **path/to/file**: Optional subdirectories and filename

## Related Resources

- [Unity Catalog Volumes Documentation](https://docs.databricks.com/en/volumes/index.html)
- [Service Principal Authentication](https://docs.databricks.com/en/dev-tools/service-principals.html)
- [Databricks SDK for Python](https://databricks-sdk-py.readthedocs.io/)
- [Streamlit File Uploader](https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader)

## Version History

- **v1.0**: Initial release with basic file upload functionality
- **Current**: Single file upload to Unity Catalog Volumes

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Databricks Unity Catalog documentation

---

## Disclaimer

This is not an official Databricks solution. Please test and validate before using it in Prod.
For questions or issues, contact your Databricks account team.

**Last Updated**: November 2025  
**License**: Internal Use  
**Maintainer**: Databricks Team

