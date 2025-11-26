# Setup Instructions

This folder contains the one-time setup script to create and populate the PostgreSQL lakehouse table with sample data.

## Prerequisites

- Access to a Databricks workspace
- Lakehouse Federation connection configured for PostgreSQL (connection name: `chat-db`)
- Permissions to create schemas and tables in the PostgreSQL database
- PySpark environment (available in Databricks notebooks or jobs)
- PostgreSQL database instance accessible from Databricks

## Running the Setup

### Option 1: Databricks Notebook

1. Upload `create_table.py` to your Databricks workspace or import it into a notebook
2. Run the script:
   ```python
   %run /path/to/Setup/create_table.py
   ```

### Option 2: Databricks Jobs

1. Create a new Databricks job
2. Add a Python task pointing to `create_table.py`
3. Run the job

### Option 3: Command Line (with Databricks CLI)

```bash
databricks jobs create --json '{
  "name": "Setup Compliance Table",
  "tasks": [{
    "task_key": "setup_compliance_table",
    "python_file": "dbfs:/path/to/create_table.py",
    "new_cluster": {
      "spark_version": "13.3.x-scala2.12",
      "node_type_id": "i3.xlarge",
      "num_workers": 2
    }
  }]
}'
```

## What the Setup Does

The `create_table.py` script performs the following operations:

1. **Creates Schema**: Creates `main.banking_compliance` schema if it doesn't exist
2. **Creates Table**: Creates the `document_registry` table with full schema definition
3. **Populates Data**: Inserts 500 sample documents with realistic banking data including:
   - Document metadata (names, types, sizes)
   - Ownership information (names, emails, business units)
   - Compliance tracking (status, classifications, retention)
   - Review and archival information

## Table Details

- **Lakehouse Instance**: `chat-db`
- **Database**: `compliance_app`
- **Schema**: `audit`
- **Table**: `document_registry`
- **Full Name**: `` `chat-db`.`compliance_app`.`audit`.`document_registry` ``
- **Sample Records**: 500 documents
- **Storage**: PostgreSQL database (via Lakehouse Federation)

## Customization

You can customize the setup by modifying these variables in `create_table.py`:

```python
LAKEHOUSE_INSTANCE = "chat-db"      # Your Lakehouse Federation connection name
DATABASE = "compliance_app"          # Your PostgreSQL database name
SCHEMA = "audit"                     # Your PostgreSQL schema name
TABLE = "document_registry"          # Your table name
num_records = 500                    # Change number of sample records
```

## Lakehouse Federation Setup

Before running the setup script, ensure you have configured a Lakehouse Federation connection in Databricks:

1. Go to **Catalog** in Databricks workspace
2. Click **Add** > **Add a connection**
3. Select **PostgreSQL**
4. Configure connection with:
   - **Connection Name**: `chat-db`
   - **Host**: Your PostgreSQL host
   - **Port**: 5432 (or your custom port)
   - **Database**: `compliance_app`
   - **Username/Password**: Your PostgreSQL credentials
5. Test the connection and save

## Verification

After running the setup, verify the table was created successfully:

```sql
-- Check table exists
DESCRIBE TABLE `chat-db`.`compliance_app`.`audit`.`document_registry`;

-- View sample data
SELECT * FROM `chat-db`.`compliance_app`.`audit`.`document_registry` LIMIT 10;

-- Check record count
SELECT COUNT(*) FROM `chat-db`.`compliance_app`.`audit`.`document_registry`;
```

## Re-running Setup

The script drops and recreates the table, so re-running will:
- Drop the existing table (if it exists)
- Create a fresh table
- Populate with new sample data
- **Warning**: This will DELETE all existing data in the table

## Next Steps

After successful setup:
1. Verify the table exists: `` `chat-db`.`compliance_app`.`audit`.`document_registry` ``
2. Update `WAREHOUSE_ID` in `../app.py` (if not already set)
3. Ensure Lakehouse Federation connection is available to the app
4. Deploy the Streamlit app
5. Access the compliance dashboard

## Troubleshooting

**Connection Errors:**
- Verify Lakehouse Federation connection `chat-db` is configured
- Test the connection in Databricks UI
- Ensure PostgreSQL database is accessible from Databricks

**Permission Errors:**
- Ensure you have CREATE permissions on the PostgreSQL database
- Verify schema creation permissions in PostgreSQL
- Check PostgreSQL user has necessary privileges

**Schema Not Found:**
- Verify PostgreSQL database `compliance_app` exists
- Check that the connection name matches `chat-db`
- Ensure you have access to create schemas

**Data Not Appearing:**
- Confirm the script completed successfully
- Check for error messages in the output
- Verify table exists: `SELECT * FROM \`chat-db\`.\`compliance_app\`.\`audit\`.\`document_registry\` LIMIT 1`
- Check PostgreSQL logs for any issues

**Lakehouse Federation Issues:**
- Ensure Databricks runtime supports Lakehouse Federation
- Verify network connectivity between Databricks and PostgreSQL
- Check firewall rules allow connections from Databricks

---

**Note**: This setup only needs to be run once. The data will persist in the PostgreSQL database and can be queried by the app through Lakehouse Federation indefinitely.

