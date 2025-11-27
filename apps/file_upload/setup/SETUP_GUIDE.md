# Secrets Setup Guide

This folder contains scripts to help you set up Databricks secrets for the File Upload application.

## Prerequisites

1. **Databricks CLI** installed and configured
   ```bash
   pip install databricks-cli
   databricks configure --token
   ```

2. **Service Principal** created with appropriate permissions
   - Get the Client ID and Client Secret
   - Grant WRITE_VOLUME permission on target volumes

3. **Admin Access** to create secret scopes in Databricks

## Option 1: Using Shell Script (Recommended)

The easiest way to set up secrets is using the provided shell script.

### Quick Start

```bash
# Make the script executable
chmod +x setup_secrets.sh

# Run the script
./setup_secrets.sh
```

### What It Does

The script will:
1. ✅ Check if Databricks CLI is installed
2. ✅ Verify CLI is configured
3. ✅ Create secret scope `rh-demo` (if it doesn't exist)
4. ✅ Prompt for Service Principal credentials
5. ✅ Set all required secrets
6. ✅ Verify secrets were created

### Interactive Prompts

```
Enter the Service Principal Client ID:
> 43d91404-054d-4e45-800a-7dc30da01a9e

Enter the Service Principal Client Secret (input hidden):
> ****************************************
```

## Option 2: Using Databricks Notebook

If you prefer to work in a Databricks notebook:

### Steps

1. **Upload the notebook**:
   - Upload `setup_secrets.py` to your Databricks workspace
   - Open it as a Python notebook

2. **Update configuration**:
   - Edit the configuration cell with your values
   - Set `SP_CLIENT_ID` and `SP_CLIENT_SECRET`

3. **Run the notebook**:
   - Execute each cell in order
   - Follow the instructions in markdown cells
   - Copy/paste CLI commands to your terminal

4. **Verify**:
   - Run the verification cell to test secret access

## Option 3: Manual CLI Commands

If you prefer to run commands manually:

### Step 1: Create Secret Scope

```bash
databricks secrets create-scope rh-demo
```

### Step 2: Set Databricks Host

```bash
databricks secrets put-secret rh-demo databricks-host \
  --string-value "https://e2-demo-field-eng.cloud.databricks.com"
```

### Step 3: Set Service Principal Client ID

```bash
databricks secrets put-secret rh-demo sp-client-id \
  --string-value "your-client-id-here"
```

### Step 4: Set Service Principal Client Secret

```bash
# Interactive (recommended - keeps secret out of shell history)
databricks secrets put-secret rh-demo sp-client-secret

# Or inline (be careful with shell history)
echo "your-secret-here" | databricks secrets put-secret rh-demo sp-client-secret
```

### Step 5: Verify

```bash
databricks secrets list --scope rh-demo
```

Expected output:
```
Key name           Last updated
databricks-host    1699564800000
sp-client-id       1699564801000
sp-client-secret   1699564802000
```

## Verification

### Test Secret Access

Run this in a Databricks notebook to verify secrets are accessible:

```python
import os

# Test reading secrets
host = dbutils.secrets.get(scope="rh-demo", key="databricks-host")
client_id = dbutils.secrets.get(scope="rh-demo", key="sp-client-id")
client_secret = dbutils.secrets.get(scope="rh-demo", key="sp-client-secret")

print("✓ All secrets are accessible")
print(f"  Host length: {len(host)} characters")
print(f"  Client ID length: {len(client_id)} characters")
print(f"  Client Secret length: {len(client_secret)} characters")
```

### Test App Configuration

The app should now be able to read these secrets via environment variables configured in `app.yaml`:

```yaml
env:
  - name: DATABRICKS_HOST
    value: "{{secrets/rh-demo/databricks-host}}"
  - name: SP_CLIENT_ID
    value: "{{secrets/rh-demo/sp-client-id}}"
  - name: SP_CLIENT_SECRET
    value: "{{secrets/rh-demo/sp-client-secret}}"
```

## Troubleshooting

### Error: "Secret scope already exists"

**Solution**: The scope already exists. Skip to setting secrets.

### Error: "Permission denied"

**Solution**: You need admin permissions to create secret scopes. Contact your workspace admin.

### Error: "databricks command not found"

**Solution**: Install Databricks CLI:
```bash
pip install databricks-cli
```

### Error: "Authentication failed"

**Solution**: Configure Databricks CLI:
```bash
databricks configure --token
```

You'll need:
- Databricks workspace URL
- Personal access token

### Error: "Cannot read secret"

**Solution**: Ensure:
1. Secret scope exists
2. Secret key is spelled correctly
3. You have permission to read from the scope

## Security Best Practices

### ✅ DO:

- Use secret scopes for all sensitive data
- Rotate service principal secrets regularly
- Use separate scopes for dev/staging/prod
- Grant minimal necessary permissions
- Use interactive prompts for secret input

### ❌ DON'T:

- Print or display secret values
- Store secrets in code or notebooks
- Share service principal credentials
- Use personal credentials for apps
- Commit secrets to version control
- Use the same secrets across environments

## Rotating Secrets

To rotate a secret (recommended every 90 days):

### 1. Generate New Service Principal Secret

In Databricks UI:
1. Go to Settings → Service Principals
2. Find your service principal
3. Click "Generate Secret"
4. Copy the new secret

### 2. Update Secret in Databricks

```bash
# Update the secret
databricks secrets put-secret rh-demo sp-client-secret
# Enter new secret when prompted
```

### 3. Redeploy App (if needed)

If the app is already running, it will pick up the new secret on next restart.

## Managing Multiple Environments

For different environments, use separate secret scopes:

```bash
# Development
databricks secrets create-scope dev-file-upload

# Staging
databricks secrets create-scope staging-file-upload

# Production
databricks secrets create-scope prod-file-upload
```

Update `app.yaml` for each environment:

```yaml
# Development
env:
  - name: SP_CLIENT_SECRET
    value: "{{secrets/dev-file-upload/sp-client-secret}}"
```

## Additional Resources

- [Databricks Secrets Documentation](https://docs.databricks.com/security/secrets/index.html)
- [Databricks CLI Documentation](https://docs.databricks.com/dev-tools/cli/index.html)
- [Service Principals Guide](https://docs.databricks.com/dev-tools/service-principals.html)

## Support

For issues:
1. Check the troubleshooting section
2. Verify CLI is configured correctly
3. Ensure you have necessary permissions
4. Contact your Databricks workspace administrator

---

**Files in This Directory**:
- `setup_secrets.sh` - Automated shell script (recommended)
- `setup_secrets.py` - Databricks notebook version
- `SETUP_GUIDE.md` - This file

**Last Updated**: November 2025

