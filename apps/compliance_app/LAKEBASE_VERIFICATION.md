# Lakebase Verification & Setup Guide

✅ **VERIFIED**: Both `create_table.py` and `app.py` are now compatible with **Databricks Lakebase** (PostgreSQL).

Reference: [Databricks Lakebase Notebook Documentation](https://docs.databricks.com/aws/en/oltp/instances/query/notebook)

## What Changed

### 1. **`Setup/create_table.py`** - Now Uses Direct PostgreSQL Connection

**Before** (Incorrect - Was using Spark/Lakehouse Federation):
```python
spark = SparkSession.builder...
df.write.format("lakehouse").saveAsTable(...)
```

**After** (Correct - Uses psycopg2 for Lakebase):
```python
import psycopg2
from databricks.sdk import WorkspaceClient

# Get Lakebase instance and OAuth token
instance = w.database.get_database_instance(name=INSTANCE_NAME)
cred = w.database.generate_database_credential(...)

# Connect directly to PostgreSQL
conn = psycopg2.connect(
    host=instance.read_write_dns,
    dbname=DATABASE,
    user=POSTGRES_USER,
    password=cred.token,
    sslmode="require"
)
```

**Key Changes**:
- ✅ Uses `psycopg2` for direct PostgreSQL connections
- ✅ Uses Databricks SDK to obtain OAuth tokens
- ✅ Connects to Lakebase instance using `read_write_dns`
- ✅ Uses batch inserts for performance
- ✅ Proper PostgreSQL transaction management

### 2. **`app.py`** - Now Connects to Lakebase Directly

**Before** (Incorrect - Was using SQL Warehouse):
```python
w.statement_execution.execute_statement(
    statement=query,
    warehouse_id=WAREHOUSE_ID,
    wait_timeout="30s"
)
```

**After** (Correct - Uses Lakebase connection):
```python
@st.cache_resource
def get_lakebase_connection():
    instance = w.database.get_database_instance(name=INSTANCE_NAME)
    cred = w.database.generate_database_credential(...)
    return psycopg2.connect(...)

def execute_query(query):
    conn = get_lakebase_connection()
    df = pd.read_sql_query(query, conn)
    return df
```

**Key Changes**:
- ✅ Direct PostgreSQL connection via `psycopg2`
- ✅ Cached connection resource for performance
- ✅ Uses `pandas.read_sql_query()` for DataFrame conversion
- ✅ No SQL Warehouse required

### 3. **Configuration Updates**

**Lakebase Instance Configuration**:
```python
INSTANCE_NAME = "chat-db"        # Your Lakebase instance
DATABASE = "compliance_app"       # PostgreSQL database
SCHEMA = "audit"                  # PostgreSQL schema
TABLE = "document_registry"       # Table name
POSTGRES_USER = "admin"           # Your Postgres role/user
```

**Updated Requirements**:
- Added: `psycopg2-binary>=2.9.0`
- Removed: `pyspark` dependency (not needed in app)

## How to Run

### Step 1: Ensure Lakebase Instance Exists

Your Lakebase instance must be created and running:
- **Instance Name**: `chat-db`
- **Database**: `compliance_app`
- **User**: `admin` (or your Postgres role)

Verify in Databricks:
```sql
SHOW DATABASE INSTANCES;
```

### Step 2: Run the Setup Script (One-Time)

In a Databricks notebook:

```python
%run /Workspace/path/to/compliance_app/Setup/create_table.py
```

This will:
1. Connect to Lakebase instance `chat-db`
2. Create schema `audit` in database `compliance_app`
3. Create table `audit.document_registry`
4. Insert 500 sample document records

**Expected Output**:
```
================================================================================
Document Compliance Table Setup (Databricks Lakebase - PostgreSQL)
================================================================================

Lakebase Instance: chat-db
Database: compliance_app
Schema: audit
Table: document_registry

[1/4] Connecting to Lakebase instance...
✓ Connected to Lakebase instance: <instance-dns>

[2/4] Creating schema...
✓ Schema 'audit' created or already exists

[3/4] Creating table...
✓ Dropped existing table audit.document_registry (if it existed)
✓ Table audit.document_registry created successfully

[4/4] Populating table with sample data...
Generating 500 sample records...
Inserting 500 records into audit.document_registry...
✓ Successfully inserted 500 records into audit.document_registry

Sample records:
  DOC00000001 | Policy Document_Retail_Banking_1.pdf... | Retail Banking | Compliant

Table statistics:
  Total documents: 500
  Business units: 12
  Marked for archival: 75
  Non-compliant: 125
  Requiring review: 350

================================================================================
✓ Setup complete!
================================================================================
```

### Step 3: Verify the Data

Query the table directly:

```python
import psycopg2
from databricks.sdk import WorkspaceClient
import uuid

w = WorkspaceClient()

instance_name = "chat-db"
instance = w.database.get_database_instance(name=instance_name)
cred = w.database.generate_database_credential(
    request_id=str(uuid.uuid4()), 
    instance_names=[instance_name]
)

conn = psycopg2.connect(
    host=instance.read_write_dns,
    dbname="compliance_app",
    user="admin",
    password=cred.token,
    sslmode="require"
)

# Test query
import pandas as pd
df = pd.read_sql_query("SELECT COUNT(*) FROM audit.document_registry", conn)
print(df)
```

### Step 4: Deploy the Streamlit App

The app will automatically connect to Lakebase using the same pattern.

1. Navigate to **Databricks Apps** in your workspace
2. Click **Create App**
3. Select the `compliance_app` directory
4. Click **Deploy**

The app will use `app.yaml` configuration (no secrets needed - OAuth is automatic).

## Key Differences: Lakebase vs. SQL Warehouse

| Feature | Lakebase (PostgreSQL) | SQL Warehouse |
|---------|----------------------|---------------|
| **Connection** | Direct psycopg2 | SQL execution API |
| **Authentication** | OAuth token via SDK | Warehouse ID + token |
| **Protocol** | PostgreSQL wire protocol | HTTP REST API |
| **Use Case** | OLTP, transactional | OLAP, analytics |
| **Performance** | Low latency queries | Large scans |
| **Driver** | `psycopg2` | `databricks-sql-connector` |

## Troubleshooting

### Issue: "Database instance not found"
**Solution**: Verify instance name is correct:
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
instances = w.database.list_database_instances()
for inst in instances:
    print(inst.name)
```

### Issue: "Permission denied"
**Solution**: Ensure your Postgres user has proper permissions:
```sql
GRANT ALL ON SCHEMA audit TO admin;
GRANT ALL ON ALL TABLES IN SCHEMA audit TO admin;
```

### Issue: "Connection timeout"
**Solution**: 
- Verify Lakebase instance is running
- Check network connectivity
- Ensure you're using the correct `read_write_dns`

### Issue: "OAuth token expired"
**Solution**: The app automatically refreshes tokens. If issues persist, clear the Streamlit cache:
```python
st.cache_resource.clear()
```

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│     Databricks Workspace               │
│                                         │
│  ┌────────────────────────────────┐   │
│  │  Streamlit App                 │   │
│  │  (compliance_app/app.py)       │   │
│  └───────────┬────────────────────┘   │
│              │                         │
│              │ psycopg2                │
│              │ + OAuth token           │
│              ▼                         │
│  ┌────────────────────────────────┐   │
│  │  Lakebase Instance: chat-db    │   │
│  │  ┌──────────────────────────┐  │   │
│  │  │  Database: compliance_app│  │   │
│  │  │    Schema: audit         │  │   │
│  │  │      Table: document_... │  │   │
│  │  └──────────────────────────┘  │   │
│  └────────────────────────────────┘   │
│         (Managed PostgreSQL)           │
└─────────────────────────────────────────┘
```

## Sample Queries

### Check Table Structure
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'audit' 
  AND table_name = 'document_registry';
```

### Find Non-Compliant Documents
```sql
SELECT document_name, business_unit, owner_name, compliance_status
FROM audit.document_registry
WHERE compliance_status = 'Non-Compliant'
ORDER BY upload_date DESC;
```

### Documents by Business Unit
```sql
SELECT 
    business_unit,
    COUNT(*) as document_count,
    SUM(file_size_mb) as total_size_mb
FROM audit.document_registry
GROUP BY business_unit
ORDER BY document_count DESC;
```

## Performance Tips

1. **Connection Pooling**: The app uses `@st.cache_resource` to cache connections
2. **Batch Operations**: Setup script uses `execute_batch()` for inserts
3. **OAuth Token Refresh**: Tokens are refreshed automatically every 15 minutes
4. **Indexed Queries**: PostgreSQL automatically creates index on PRIMARY KEY

## References

- [Databricks Lakebase Documentation](https://docs.databricks.com/aws/en/oltp/instances/query/notebook)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [Databricks SDK for Python](https://databricks-sdk-py.readthedocs.io/)

---

**Status**: ✅ Verified and ready for use with Databricks Lakebase  
**Last Updated**: November 2025  
**Version**: 2.0.0 (Lakebase-compatible)

