# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks Secrets Setup for File Upload App
# MAGIC
# MAGIC This notebook creates the necessary secrets for the File Upload application.
# MAGIC
# MAGIC ## Prerequisites
# MAGIC - Admin access to create secret scopes
# MAGIC - Service Principal credentials (Client ID and Secret)
# MAGIC
# MAGIC ## Secrets to Create
# MAGIC 1. `databricks-host` - Your Databricks workspace URL
# MAGIC 2. `sp-client-id` - Service Principal Client ID
# MAGIC 3. `sp-client-secret` - Service Principal Client Secret

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration
# MAGIC
# MAGIC Update these values for your environment:

# COMMAND ----------

# Configuration
SECRET_SCOPE = "rh-demo"
DATABRICKS_HOST = "https://e2-demo-field-eng.cloud.databricks.com"

# Service Principal Credentials
# Option 1: Set these directly (not recommended for production)
SP_CLIENT_ID = "your-client-id-here"
SP_CLIENT_SECRET = "your-client-secret-here"

# Option 2: Use dbutils.widgets for interactive input (recommended)
# Uncomment these lines to use widgets:
# dbutils.widgets.text("client_id", "", "Service Principal Client ID")
# dbutils.widgets.text("client_secret", "", "Service Principal Client Secret")
# SP_CLIENT_ID = dbutils.widgets.get("client_id")
# SP_CLIENT_SECRET = dbutils.widgets.get("client_secret")

print("Configuration loaded")
print(f"Secret Scope: {SECRET_SCOPE}")
print(f"Databricks Host: {DATABRICKS_HOST}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Create Secret Scope
# MAGIC
# MAGIC Create the secret scope if it doesn't already exist.

# COMMAND ----------

try:
    # Check if scope exists
    existing_scopes = [scope.name for scope in spark.sql("SHOW SECRETS SCOPES").collect()]
    
    if SECRET_SCOPE in existing_scopes:
        print(f"✓ Secret scope '{SECRET_SCOPE}' already exists")
    else:
        # Create scope using Databricks CLI command
        print(f"Creating secret scope '{SECRET_SCOPE}'...")
        # Note: This requires workspace admin permissions
        dbutils.secrets.createScope(SECRET_SCOPE)
        print(f"✓ Created secret scope '{SECRET_SCOPE}'")
except Exception as e:
    print(f"Note: {e}")
    print("\nAlternative: Create scope using Databricks CLI:")
    print(f"  databricks secrets create-scope {SECRET_SCOPE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Set Databricks Host Secret
# MAGIC
# MAGIC Store the Databricks workspace URL.

# COMMAND ----------

# Using Databricks CLI to set secret
# Note: In notebook, you'll need to use CLI commands or REST API

print("Setting databricks-host secret...")
print(f"Value: {DATABRICKS_HOST}")
print("\nRun this command in your terminal:")
print(f"databricks secrets put-secret {SECRET_SCOPE} databricks-host --string-value \"{DATABRICKS_HOST}\"")
print("\nOr use this Python code (requires databricks-sdk):")
print(f"""
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
# Note: Secret creation via SDK requires appropriate permissions
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Set Service Principal Client ID
# MAGIC
# MAGIC Store the Service Principal Client ID.

# COMMAND ----------

print("Setting sp-client-id secret...")
print(f"Value: {SP_CLIENT_ID}")
print("\nRun this command in your terminal:")
print(f"databricks secrets put-secret {SECRET_SCOPE} sp-client-id --string-value \"{SP_CLIENT_ID}\"")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Set Service Principal Client Secret
# MAGIC
# MAGIC Store the Service Principal Client Secret (most sensitive).

# COMMAND ----------

print("Setting sp-client-secret secret...")
print("Value: [HIDDEN]")
print("\nRun this command in your terminal:")
print(f"databricks secrets put-secret {SECRET_SCOPE} sp-client-secret")
print("(You'll be prompted to enter the secret value)")
print("\nOr with value inline:")
print(f"echo \"YOUR_SECRET\" | databricks secrets put-secret {SECRET_SCOPE} sp-client-secret")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Alternative: Using Databricks REST API
# MAGIC
# MAGIC If you prefer to use REST API directly:

# COMMAND ----------

import requests
import base64

# Get workspace URL and token from notebook context
workspace_url = spark.conf.get("spark.databricks.workspaceUrl")
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

def create_secret_via_api(scope, key, value):
    """Create or update a secret using Databricks REST API"""
    url = f"https://{workspace_url}/api/2.0/secrets/put"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "scope": scope,
        "key": key,
        "string_value": value
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print(f"✓ Secret '{key}' created/updated successfully")
        return True
    else:
        print(f"✗ Failed to create secret '{key}': {response.text}")
        return False

# Uncomment to use:
# create_secret_via_api(SECRET_SCOPE, "databricks-host", DATABRICKS_HOST)
# create_secret_via_api(SECRET_SCOPE, "sp-client-id", SP_CLIENT_ID)
# create_secret_via_api(SECRET_SCOPE, "sp-client-secret", SP_CLIENT_SECRET)

print("REST API functions defined. Uncomment the calls above to use.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verification
# MAGIC
# MAGIC Verify that all secrets have been created.

# COMMAND ----------

# List secrets in the scope
print(f"Secrets in scope '{SECRET_SCOPE}':")
print("\nRun this command to list secrets:")
print(f"databricks secrets list --scope {SECRET_SCOPE}")

print("\n" + "="*80)
print("Expected secrets:")
print("  - databricks-host")
print("  - sp-client-id")
print("  - sp-client-secret")
print("="*80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Testing Secret Access
# MAGIC
# MAGIC Test that you can access the secrets (values will be redacted in output).

# COMMAND ----------

try:
    # Read secrets (values are redacted in output)
    host = dbutils.secrets.get(scope=SECRET_SCOPE, key="databricks-host")
    client_id = dbutils.secrets.get(scope=SECRET_SCOPE, key="sp-client-id")
    client_secret = dbutils.secrets.get(scope=SECRET_SCOPE, key="sp-client-secret")
    
    print("✓ All secrets are accessible")
    print(f"  databricks-host: [REDACTED - {len(host)} characters]")
    print(f"  sp-client-id: [REDACTED - {len(client_id)} characters]")
    print(f"  sp-client-secret: [REDACTED - {len(client_secret)} characters]")
    
except Exception as e:
    print(f"✗ Error accessing secrets: {e}")
    print("\nMake sure secrets are created first using the CLI commands above.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ### What You Need to Do:
# MAGIC
# MAGIC 1. **Create Secret Scope** (one-time):
# MAGIC    ```bash
# MAGIC    databricks secrets create-scope rh-demo
# MAGIC    ```
# MAGIC
# MAGIC 2. **Set Databricks Host**:
# MAGIC    ```bash
# MAGIC    databricks secrets put-secret rh-demo databricks-host \
# MAGIC      --string-value "https://e2-demo-field-eng.cloud.databricks.com"
# MAGIC    ```
# MAGIC
# MAGIC 3. **Set Service Principal Client ID**:
# MAGIC    ```bash
# MAGIC    databricks secrets put-secret rh-demo sp-client-id \
# MAGIC      --string-value "your-client-id"
# MAGIC    ```
# MAGIC
# MAGIC 4. **Set Service Principal Client Secret**:
# MAGIC    ```bash
# MAGIC    databricks secrets put-secret rh-demo sp-client-secret
# MAGIC    # You'll be prompted to enter the secret
# MAGIC    ```
# MAGIC
# MAGIC 5. **Verify**:
# MAGIC    ```bash
# MAGIC    databricks secrets list --scope rh-demo
# MAGIC    ```
# MAGIC
# MAGIC ### Next Steps:
# MAGIC - Deploy the File Upload app
# MAGIC - The app will automatically read secrets from the scope
# MAGIC - Test the app to ensure it can authenticate
# MAGIC
# MAGIC ### Security Notes:
# MAGIC - Never print or display secret values
# MAGIC - Rotate secrets regularly
# MAGIC - Use separate scopes for different environments
# MAGIC - Grant minimal permissions to service principals

