# Loan Explorer

A Databricks App for searching, viewing, and managing loan applications with contract document downloads.

## Features

- 🔍 **Search** - Find loans by Application ID or Applicant Name
- 📋 **View Details** - Click on any loan to see full application details in a modal
- 📄 **Download Contracts** - Download loan contract PDFs from Unity Catalog volumes
- 💵 **Payment Summary** - View monthly payment, total payment, and interest calculations

---

## Prerequisites

Before deploying the app, ensure the data infrastructure is set up:

1. Follow the instructions in [`setup/README.md`](setup/README.md) to:
   - Create the `loan_applications` table
   - Create the `loan_contracts` volume
   - Upload sample contract PDFs

---

## Deployment Steps

### Step 1: Clone Repository to Workspace

1. Navigate to your Databricks workspace
2. Go to **Workspace** in the sidebar
3. Choose or create a folder for your apps (e.g., `/Workspace/Users/<your-email>/apps/`)
4. Click **⋮** → **Create**
5. Select **Git Folder** and enter the repo URL
6. Clone the repository
7. The code for the Loan explorer app can be found in `apps/loan-explorer`

Alternatively, use the Databricks CLI:
```bash
databricks repos create --url <repo-url> --path /Workspace/Users/<your-email>/apps/loan-explorer
```

---

### Step 2: Create the App

1. Navigate to **Apps** in the Databricks sidebar
2. Click **Create App**
3. Enter app details:
   - **Name**: `loan-explorer`
   - **Description**: Loan application search and management

---

### Step 3: Add Resources

In the app configuration, add the following resources:

#### SQL Warehouse
1. Click **+ Add resource**
2. Select **SQL Warehouse**
3. Choose your SQL warehouse (or select "Serverless" for auto-provisioning)
4. Set **Permission**: `CAN_USE`
5. Set **Resource key**: `sql-warehouse`

#### Volume (Loan Documents)
1. Click **+ Add resource**
2. Select **Volume**
3. Enter the volume path: `/Volumes/<catalog>/<schema>/loan_contracts`
   - Example: `/Volumes/renjiharold_demo/loan_explorer/loan_contracts`
4. Set **Permission**: `READ VOLUME`
5. Set **Resource key**: `loan-docs`

---

### Step 4: Configure Environment Variables

Ensure the following environment variables are configured:

| Variable | Source |
|----------|--------|
| `DATABRICKS_WAREHOUSE_ID` | `valueFrom: sql-warehouse` |
| `LOAN_DOCS_VOLUME` | `valueFrom: loan-docs` |

These should match what's in your `app.yaml`:
```yaml
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql-warehouse
  - name: LOAN_DOCS_VOLUME
    valueFrom: loan-docs
```

---

### Step 5: Grant Permissions to App Service Principal

After creating the app, grant the app's service principal access to the loan data:

1. Find your app's service principal name (shown in the app details page)
2. Either do this via the UI in the Catalog Explorer or run the following SQL commands in a Databricks SQL notebook:

```sql
-- Grant access to catalog and schema
GRANT USE CATALOG ON CATALOG <catalog> TO `<app-service-principal>`;
GRANT USE SCHEMA ON SCHEMA <catalog>.<schema> TO `<app-service-principal>`;

-- Grant SELECT on the loan_applications table
GRANT SELECT ON TABLE <catalog>.<schema>.loan_applications TO `<app-service-principal>`;

```

---

### Step 6: Deploy the App

1. In the app configuration, go to **Deploy**
2. Select **Workspace folder**
3. Browse to the cloned repository location:
   - Example: `/Workspace/Users/<your-email>/apps/loan-explorer`
4. Click **Deploy**
5. Wait for the deployment to complete. Status will be shown as **Running**
6. Access the app from the URL displayed on screen

---

## Project Structure

```
loan-explorer/
├── app.py              # Main Streamlit application
├── app.yaml            # App configuration (command, env variables)
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── setup/
    ├── README.md           # Data setup instructions
    ├── setup_loan_table.sql    # SQL script for table creation
    └── docs/               # Sample contract PDFs
```

---

## Configuration

### app.yaml

```yaml
command: ["streamlit", "run", "app.py"]

env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql-warehouse
  - name: LOAN_DOCS_VOLUME
    valueFrom: loan-docs
```

### requirements.txt

```
streamlit
databricks-sql-connector
databricks-sdk
```

---

## Permissions Required

The app service principal needs:

| Permission | Resource |
|------------|----------|
| `USE CATALOG` | Catalog containing loan data |
| `USE SCHEMA` | Schema containing loan table and volume |
| `SELECT` | `loan_applications` table |
| `READ VOLUME` | `loan_contracts` volume |
| `CAN_USE` | SQL Warehouse |

---

## Troubleshooting

### App fails to start
- Check that all environment variables are configured correctly
- Verify the SQL warehouse is running

### No loan data displayed
- Verify the table `loan_applications` exists and has data
- Check catalog/schema names match in the app queries

### Contract download not working
- Verify the volume path in `LOAN_DOCS_VOLUME` is correct
- Check that PDF files are uploaded with correct naming: `<application_id>_contract.pdf`
- Ensure the app has `READ VOLUME` permission on the volume

