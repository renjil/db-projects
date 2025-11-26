# Lakehouse Federation Setup Guide

Quick reference for setting up the PostgreSQL-backed compliance app with Databricks Lakehouse Federation.

## Configuration Summary

| Component | Value |
|-----------|-------|
| **Lakehouse Instance** | `chat-db` |
| **Database** | `compliance_app` |
| **Schema** | `audit` |
| **Table** | `document_registry` |
| **Full Table Path** | `` `chat-db`.`compliance_app`.`audit`.`document_registry` `` |

## Step-by-Step Setup

### 1. Configure Lakehouse Federation Connection (One-Time)

In your Databricks workspace:

1. Navigate to **Catalog** → **Add** → **Add a connection**
2. Select **PostgreSQL** as the connection type
3. Configure with these details:
   - **Connection Name**: `chat-db`
   - **Host**: `your-postgres-host.example.com`
   - **Port**: `5432` (or your custom port)
   - **Database**: `compliance_app`
   - **Username**: Your PostgreSQL username
   - **Password**: Your PostgreSQL password
4. Click **Test Connection** to verify
5. Click **Create** to save the connection

### 2. Run the Setup Script (One-Time)

In a Databricks notebook:

```python
%run /Workspace/path/to/compliance_app/Setup/create_table.py
```

This will:
- Create the schema `audit` in PostgreSQL database `compliance_app`
- Create the `document_registry` table with proper schema
- Populate with 500 sample document records

### 3. Verify the Setup

```sql
-- Check connection
SHOW TABLES IN `chat-db`.`compliance_app`.`audit`;

-- Verify data
SELECT COUNT(*) as total_docs 
FROM `chat-db`.`compliance_app`.`audit`.`document_registry`;

-- Sample query
SELECT document_name, business_unit, compliance_status 
FROM `chat-db`.`compliance_app`.`audit`.`document_registry` 
LIMIT 10;
```

### 4. Deploy the Streamlit App

1. Ensure `WAREHOUSE_ID` is set in `app.py`
2. The table configuration is already set:
   ```python
   LAKEHOUSE_INSTANCE = "chat-db"
   DATABASE = "compliance_app"
   SCHEMA = "audit"
   TABLE = "document_registry"
   ```
3. Deploy through Databricks Apps UI

## Key Features

### What This Setup Provides

✅ **PostgreSQL Backend**: Data stored in reliable PostgreSQL database  
✅ **Databricks Integration**: Query via SQL warehouse like any other table  
✅ **No ETL Required**: Direct access to operational data  
✅ **ACID Transactions**: Full PostgreSQL transaction support  
✅ **Unified Governance**: Manage access through Databricks  
✅ **Scalability**: Leverage both PostgreSQL and Spark capabilities  

### Table Schema

The `document_registry` table includes:

- **Document Metadata**: ID, name, type, size
- **Ownership**: Owner name, email, business unit
- **Compliance**: Status, classification, retention period
- **Review Tracking**: Reviewer, review dates
- **Archival**: Archival flags and scheduled dates
- **Security**: Encryption status, storage location

## Common Operations

### Query the Table

```sql
SELECT * FROM `chat-db`.`compliance_app`.`audit`.`document_registry`
WHERE business_unit = 'Risk Management'
  AND compliance_status = 'Non-Compliant';
```

### Check Connection Status

```sql
DESCRIBE CONNECTION `chat-db`;
```

### View Table Schema

```sql
DESCRIBE TABLE `chat-db`.`compliance_app`.`audit`.`document_registry`;
```

## Troubleshooting

### Connection Issues

**Problem**: "Connection 'chat-db' not found"
- **Solution**: Verify the Lakehouse Federation connection is created in Databricks Catalog

**Problem**: "Could not connect to PostgreSQL"
- **Solution**: Check network connectivity, firewall rules, and PostgreSQL credentials

### Permission Issues

**Problem**: "Permission denied to create table"
- **Solution**: Ensure PostgreSQL user has CREATE privileges on the database

**Problem**: "Cannot access table"
- **Solution**: Verify Databricks user has permissions to use the Lakehouse connection

### Data Issues

**Problem**: "No data returned"
- **Solution**: Run the setup script again to populate data

**Problem**: "Query timeout"
- **Solution**: Ensure SQL warehouse is running and PostgreSQL is responding

## Architecture Benefits

```
┌─────────────────────────────────────────────────┐
│         Databricks Workspace                    │
│                                                 │
│  ┌────────────────┐      ┌─────────────────┐  │
│  │  Streamlit App │─────▶│  SQL Warehouse  │  │
│  └────────────────┘      └─────────┬───────┘  │
│                                     │          │
└─────────────────────────────────────┼──────────┘
                                      │
                          Lakehouse   │
                          Federation  │
                                      ▼
                          ┌──────────────────┐
                          │   PostgreSQL     │
                          │   chat-db        │
                          │                  │
                          │   compliance_app │
                          │   └── audit      │
                          │       └── docs   │
                          └──────────────────┘
```

**Benefits**:
- **Single Query Interface**: Use Databricks SQL for all data
- **No Duplication**: Data stays in PostgreSQL
- **Real-time**: Always queries live data
- **Unified Security**: Manage access through Databricks
- **Hybrid Analytics**: Combine with other data sources

## Maintenance

### Re-populate Data

To refresh with new sample data:
```python
%run /Workspace/path/to/compliance_app/Setup/create_table.py
```
⚠️ **Warning**: This drops and recreates the table, deleting all existing data

### Update Connection

To modify PostgreSQL credentials:
1. Go to Catalog → Connections
2. Click on `chat-db`
3. Click **Edit**
4. Update credentials
5. Test and save

### Monitor Performance

```sql
-- Check query performance
SELECT * FROM `chat-db`.`compliance_app`.`audit`.`document_registry`
WHERE upload_date >= CURRENT_DATE - INTERVAL 30 DAYS;

-- Analyze table statistics (if supported)
ANALYZE TABLE `chat-db`.`compliance_app`.`audit`.`document_registry`;
```

## Support Resources

- **Databricks Lakehouse Federation Docs**: [Documentation Link]
- **PostgreSQL Connection Guide**: See Databricks documentation
- **Setup README**: See `Setup/README.md` for detailed instructions
- **Main README**: See `README.md` for application features

---

**Last Updated**: November 2025  
**Version**: 1.0.0 (PostgreSQL via Lakehouse Federation)

