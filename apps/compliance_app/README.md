# Document Compliance Management System

A comprehensive Databricks application for tracking and managing documents uploaded by various business units in a bank. This application demonstrates how to use Databricks lakehouse tables to build a real-world compliance and document management system.

## Features

### 📊 Overview Dashboard
- **Key Metrics**: Total documents, business units, storage usage, compliance status
- **Visualizations**: 
  - Documents by business unit
  - Compliance status distribution
  - Classification level breakdown
  - Upload trends over time

### 📄 Document Registry
- Full document listing with search functionality
- Detailed document attributes including:
  - Document metadata (name, type, owner)
  - Upload and modification dates
  - File size and storage location
  - Classification and compliance status
  - Retention and archival information
- Export functionality to CSV

### 📈 Advanced Analytics
- Document type distribution analysis
- Retention period statistics
- Owner/contributor metrics
- Business unit performance tracking

### ⚠️ Compliance Alerts
- Non-compliant documents requiring attention
- Reviews due in the next 30 days
- Documents pending archival
- Action items dashboard

## Table Schema

The application uses a PostgreSQL table accessed via Databricks Lakehouse Federation:
- **Full Path**: `` `chat-db`.`compliance_app`.`audit`.`document_registry` ``
- **Storage**: PostgreSQL database
- **Access Method**: Lakehouse Federation

### Key Attributes:
- **Document Info**: ID, name, type, size
- **Ownership**: Owner name, email, business unit
- **Dates**: Upload date, last modified, review dates, archival date
- **Compliance**: Status, classification, retention period
- **Tracking**: Archival marking, review requirements, encryption status

## Setup Instructions

### 1. Create the Table and Populate Data

Run the one-time setup script located in the `Setup` folder. See `Setup/README.md` for detailed instructions.

**Quick Start:**

In a Databricks notebook:
```python
%run /path/to/compliance_app/Setup/create_table.py
```

This will:
- Create the schema `main.banking_compliance`
- Create the table `document_registry`
- Populate with 500 sample documents

For more setup options and troubleshooting, see the [Setup README](Setup/README.md).

### 2. Configure the Application

Update the following in `app.py`:

```python
WAREHOUSE_ID = "your-sql-warehouse-id"  # Your SQL warehouse ID

# These should already be configured correctly:
LAKEHOUSE_INSTANCE = "chat-db"
DATABASE = "compliance_app"
SCHEMA = "audit"
TABLE = "document_registry"
```

Ensure your Lakehouse Federation connection `chat-db` is configured in Databricks and accessible from your app.

### 3. Set Up Secrets

Create secrets in Databricks for secure credential management:

```bash
databricks secrets create-scope banking-demo
databricks secrets put-secret banking-demo databricks-host --string-value "your-workspace-url"
databricks secrets put-secret banking-demo warehouse-id --string-value "your-warehouse-id"
```

### 4. Deploy the App

From the Databricks workspace:

1. Navigate to **Apps**
2. Click **Create App**
3. Select this directory (`compliance_app`)
4. The app will use the `app.yaml` configuration
5. Click **Deploy**

## Use Cases for Banks

### Regulatory Compliance
- Track all documents required for regulatory reporting
- Ensure proper retention periods are maintained
- Monitor document classification levels
- Generate audit reports

### Document Lifecycle Management
- Track upload dates and ownership
- Schedule and monitor document reviews
- Automate archival workflows
- Manage storage costs

### Risk Management
- Identify non-compliant documents
- Monitor sensitive document access
- Track encryption status
- Ensure proper document classification

### Business Unit Accountability
- Monitor document ownership by department
- Track contribution metrics
- Identify compliance gaps by unit
- Enable cross-department visibility

## Sample Queries

### Find Non-Compliant Documents
```sql
SELECT document_name, business_unit, owner_name, compliance_status
FROM `chat-db`.`compliance_app`.`audit`.`document_registry`
WHERE compliance_status = 'Non-Compliant'
ORDER BY upload_date DESC;
```

### Documents Due for Review
```sql
SELECT document_name, reviewer_name, next_review_date
FROM `chat-db`.`compliance_app`.`audit`.`document_registry`
WHERE review_required = true
  AND next_review_date <= current_date() + INTERVAL 30 DAYS
ORDER BY next_review_date;
```

### Storage by Business Unit
```sql
SELECT 
    business_unit,
    COUNT(*) as document_count,
    SUM(file_size_mb) / 1024 as storage_gb
FROM `chat-db`.`compliance_app`.`audit`.`document_registry`
GROUP BY business_unit
ORDER BY storage_gb DESC;
```

## Technology Stack

- **Databricks Lakehouse Federation**: Access PostgreSQL data through Databricks
- **PostgreSQL**: Reliable relational database for document metadata
- **Streamlit**: Interactive web interface
- **Plotly**: Interactive visualizations
- **Databricks SDK**: SQL execution and workspace integration
- **PySpark**: Data processing and table operations

## Benefits of Using Databricks Lakehouse Federation

1. **Single Source of Truth**: All document metadata in governed PostgreSQL database
2. **Unified Access**: Query PostgreSQL alongside other data sources in Databricks
3. **Scalability**: Leverage PostgreSQL's proven reliability and scale
4. **Security**: Fine-grained access control through both Databricks and PostgreSQL
5. **ACID Compliance**: PostgreSQL transactions ensure data consistency
6. **Real-time Updates**: Direct access to operational PostgreSQL database
7. **Cost-Effective**: Use existing PostgreSQL infrastructure
8. **Integration**: Seamlessly combine with Spark workloads and other data sources
9. **No Data Duplication**: Query data directly without ETL processes

## Future Enhancements

- **Document Upload**: Direct file upload to Unity Catalog volumes
- **Automated Workflows**: Trigger archival and review notifications
- **ML Integration**: Automated document classification
- **Advanced Search**: Full-text search within documents
- **Version Control**: Track document versions and changes
- **Access Logs**: Monitor who accessed which documents
- **Approval Workflows**: Multi-level document approval process

## Support

For questions or issues, contact your Databricks administrator or compliance team.

---

**Last Updated**: November 2025
**Version**: 1.0.0

