# Juice Shop Genie Demo

A Databricks Asset Bundle (DABs) that deploys a complete Genie Space demo for a fictional juice shop. Perfect for demonstrating Genie's natural language analytics capabilities.

## What's Included

- **3 Unity Catalog tables** with realistic sample data:
  - `products` - 15 menu items (juices, smoothies, wellness shots)
  - `customers` - 15 loyalty program members (Bronze/Silver/Gold/Platinum tiers)
  - `orders` - 40 transactions across 4 store locations

- **Genie Space** with:
  - 6 sample questions organized by complexity (Low/Medium/High)
  - Pre-written instructions for business definitions and calculations
  - Auto-configured SQL warehouse

## Quick Start

### Prerequisites

1. [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) v0.200+
2. Unity Catalog enabled workspace
3. A SQL Warehouse (serverless recommended)

### Step 1: Configure Authentication

```bash
# Option A: Use an existing profile
export DATABRICKS_CONFIG_PROFILE=your-profile

# Option B: Set environment variables
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
databricks auth login --host $DATABRICKS_HOST
```

### Step 2: Deploy the Bundle

```bash
cd juice-shop-genie

# Validate the bundle
databricks bundle validate

# Deploy to your workspace
databricks bundle deploy

# Run the setup job to create tables and load data
databricks bundle run juice_shop_setup
```

### Step 3: Create the Genie Space

```bash
# Install dependencies (if needed)
pip install databricks-sdk

# Create the Genie space
python scripts/create_genie_space.py

# Or specify a custom catalog:
python scripts/create_genie_space.py --catalog my_catalog --schema juice_shop
```

### Step 4: Add Instructions (Manual Step)

The Genie API doesn't support setting instructions directly. Copy the instructions from `resources/genie_space_config.json` and paste them in the Genie space settings UI.

1. Open the Genie space URL (printed by the script)
2. Click the gear icon (Settings)
3. Paste the instructions into the "Instructions" field
4. Save

## Sample Questions by Complexity

### Low Complexity (Single table, basic aggregations)
1. How many products do we sell?
2. What is the average price of our smoothies?

### Medium Complexity (Joins, GROUP BY)
3. What are the top 3 best-selling products by revenue?
4. Show me total orders by store location and payment method

### High Complexity (Multi-table, business logic)
5. Which Gold and Platinum customers haven't ordered in April 2024?
6. Compare month-over-month revenue growth by product category

## Customization

### Using a Different Catalog

Edit `databricks.yml` or set variables at deploy time:

```bash
databricks bundle deploy -var="catalog=my_catalog" -var="schema=my_schema"
```

### Modifying Sample Data

Edit the SQL files in `src/sql/`:
- `01_create_schema.sql` - Schema creation
- `02_create_tables.sql` - Table definitions
- `03_load_data.sql` - Sample data

### Adding More Instructions

Edit `resources/genie_space_config.json` and update the `instructions` field with additional business rules.

## Project Structure

```
juice-shop-genie/
├── databricks.yml              # DABs bundle configuration
├── README.md                   # This file
├── src/
│   └── sql/
│       ├── 01_create_schema.sql
│       ├── 02_create_tables.sql
│       └── 03_load_data.sql
├── resources/
│   └── genie_space_config.json # Genie space configuration
└── scripts/
    └── create_genie_space.py   # Post-deploy Genie setup
```

## Cleanup

```bash
# Delete the Genie space (via UI or API)
# Then destroy the bundle resources:
databricks bundle destroy

# Drop the schema (optional):
# DROP SCHEMA <catalog>.juice_shop CASCADE;
```

## Troubleshooting

### "Catalog not found"
Ensure you have a Unity Catalog with the expected name. By default, it uses `<username>_demo`. Override with:
```bash
databricks bundle deploy -var="catalog=your_catalog"
```

### "No SQL warehouse found"
Create a SQL warehouse in your workspace, or specify one:
```bash
python scripts/create_genie_space.py --warehouse-id abc123def456
```

### "Permission denied"
Ensure you have:
- CREATE SCHEMA permission on the catalog
- USE CATALOG permission
- Access to a SQL warehouse

## License

MIT - Feel free to use and modify for your demos!
