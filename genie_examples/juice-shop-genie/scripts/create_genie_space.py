#!/usr/bin/env python3
"""
Create Genie Space for Juice Shop Analytics

This script creates a Genie space after the DABs bundle deploys the tables.
Run this after `databricks bundle deploy` and the setup job completes.

Usage:
    python scripts/create_genie_space.py --catalog <catalog> --schema <schema>

    # Or use defaults (current_user_demo.juice_shop):
    python scripts/create_genie_space.py
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.dashboards import GenieCreateRequestDataSourceConfig
except ImportError:
    print("Error: databricks-sdk not installed. Run: pip install databricks-sdk")
    sys.exit(1)


def load_config(config_path: Path, catalog: str, schema: str) -> dict:
    """Load and interpolate the Genie space configuration."""
    with open(config_path) as f:
        config = json.load(f)

    # Interpolate catalog and schema in table names
    config["tables"] = [
        t.replace("${catalog}", catalog).replace("${schema}", schema)
        for t in config["tables"]
    ]

    return config


def create_genie_space(catalog: str, schema: str, warehouse_id: str = None) -> str:
    """Create the Genie space and return its ID."""

    # Initialize client (uses DATABRICKS_HOST and authentication from environment)
    w = WorkspaceClient()

    # Load configuration
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "resources" / "genie_space_config.json"
    config = load_config(config_path, catalog, schema)

    # Auto-detect warehouse if not provided
    if not warehouse_id:
        warehouses = list(w.warehouses.list())
        running = [wh for wh in warehouses if str(wh.state) == "RUNNING"]
        if running:
            warehouse_id = running[0].id
            print(f"Auto-detected warehouse: {warehouse_id}")
        elif warehouses:
            warehouse_id = warehouses[0].id
            print(f"Using warehouse (may need to start): {warehouse_id}")
        else:
            print("Error: No SQL warehouses found. Create one first.")
            sys.exit(1)

    # Check if space already exists
    existing_spaces = w.genie.list_spaces()
    for space in existing_spaces:
        if space.title == config["display_name"]:
            print(f"Genie space '{config['display_name']}' already exists: {space.space_id}")
            print(f"URL: {w.config.host}/genie/rooms/{space.space_id}")
            return space.space_id

    # Create the Genie space
    print(f"Creating Genie space: {config['display_name']}")

    response = w.genie.create_space(
        display_name=config["display_name"],
        description=config["description"],
        warehouse_id=warehouse_id,
        table_identifiers=config["tables"],
        sample_questions=config["sample_questions"],
    )

    space_id = response.space_id
    print(f"Genie space created successfully!")
    print(f"Space ID: {space_id}")
    print(f"URL: {w.config.host}/genie/rooms/{space_id}")

    # Note about instructions
    print("\n" + "=" * 60)
    print("IMPORTANT: Add Instructions via the Genie UI")
    print("=" * 60)
    print("The Genie API doesn't support setting instructions directly.")
    print("Copy the instructions from resources/genie_space_config.json")
    print("and paste them in the Genie space settings.")
    print("=" * 60)

    return space_id


def main():
    parser = argparse.ArgumentParser(description="Create Juice Shop Genie Space")
    parser.add_argument(
        "--catalog",
        default=os.environ.get("JUICE_SHOP_CATALOG", ""),
        help="Unity Catalog name (default: current_user_demo)"
    )
    parser.add_argument(
        "--schema",
        default=os.environ.get("JUICE_SHOP_SCHEMA", "juice_shop"),
        help="Schema name (default: juice_shop)"
    )
    parser.add_argument(
        "--warehouse-id",
        default=os.environ.get("DATABRICKS_WAREHOUSE_ID", ""),
        help="SQL Warehouse ID (auto-detected if not provided)"
    )

    args = parser.parse_args()

    # Default catalog to username_demo if not provided
    catalog = args.catalog
    if not catalog:
        w = WorkspaceClient()
        username = w.current_user.me().user_name.split("@")[0].replace(".", "_")
        catalog = f"{username}_demo"
        print(f"Using default catalog: {catalog}")

    create_genie_space(
        catalog=catalog,
        schema=args.schema,
        warehouse_id=args.warehouse_id or None
    )


if __name__ == "__main__":
    main()
