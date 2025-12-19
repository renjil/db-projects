# Loan Explorer - Setup Guide

This guide walks you through setting up the data infrastructure required for the Loan Explorer app.

## Prerequisites

- Access to a Databricks workspace
- Permissions to create/use catalogs, schemas, tables, and volumes
- Databricks SQL warehouse access

---

## Step 1: Configure Catalog

### Option A: Use an Existing Catalog
If you have an existing catalog, update the catalog name in `setup_loan_table.sql`:

```sql
-- Replace 'renjiharold_demo' with your catalog name
CREATE SCHEMA IF NOT EXISTS <your_catalog>.loan_explorer;
```

### Option B: Create a New Catalog
If you need to create a new catalog, run the following in a Databricks SQL notebook:

```sql
CREATE CATALOG IF NOT EXISTS <your_catalog_name>;
```

Then update `setup_loan_table.sql` to use your new catalog name.

---

## Step 2: Configure Schema

### Option A: Use an Existing Schema
If you want to use a different schema name, update all references in `setup_loan_table.sql`:

```sql
-- Replace 'loan_explorer' with your schema name
CREATE SCHEMA IF NOT EXISTS <catalog>.<your_schema>;
CREATE TABLE IF NOT EXISTS <catalog>.<your_schema>.loan_applications (...);
INSERT INTO <catalog>.<your_schema>.loan_applications VALUES (...);
```

### Option B: Use Default Schema
The script uses `loan_explorer` as the default schema. No changes needed if this works for you.

---

## Step 3: Run the Setup Script

1. Open a Databricks SQL notebook or SQL editor
2. Copy and paste the contents of `setup_loan_table.sql`
3. Run the script to:
   - Create the schema (if it doesn't exist)
   - Create the `loan_applications` table
   - Insert 10 sample loan records

```sql
-- Verify the data was inserted
SELECT * FROM <catalog>.<schema>.loan_applications;
```

---

## Step 4: Create the Managed Volume

Create a managed volume to store loan contract PDFs. This can be done via the UI, or using SQL as shown below.

```sql
CREATE VOLUME IF NOT EXISTS <catalog>.<schema>.loan_contracts
COMMENT 'Volume for storing loan contract PDF documents';
```

**Example with default values:**
```sql
CREATE VOLUME IF NOT EXISTS renjiharold_demo.loan_explorer.loan_contracts
COMMENT 'Volume for storing loan contract PDF documents';
```

Verify the volume was created:
```sql
DESCRIBE VOLUME <catalog>.<schema>.loan_contracts;
```

---

## Step 5: Upload Contract Documents

1. Download the PDF files from the `setup/docs/` folder to your local filesystem.
2. Navigate to **Catalog** in the Databricks sidebar
2. Browse to your catalog → schema → **loan_contracts** volume
3. Click **Upload** button
4. Select the PDF files from where you downloaded it in Step 1.
5. Upload all contract documents

### Expected File Naming Convention
Contract files should be named as:
```
<application_id>_contract.pdf
```

**Examples:**
- `LOAN-2024-001_contract.pdf`
- `LOAN-2024-002_contract.pdf`
- `LOAN-2024-005_contract.pdf`
- etc.

---



