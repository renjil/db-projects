"""
7-Eleven Store Intelligence Demo — Data Loader (one-step bootstrap).

Generates synthetic data and loads it into the Silver tables.

Configuration via environment variables:
    DATABRICKS_CATALOG       (required)   e.g. retail_demo
    DATABRICKS_SCHEMA        (required)   e.g. store_demo
    DATABRICKS_WAREHOUSE_ID  (required)   SQL warehouse ID
    DATABRICKS_PROFILE       (optional)   CLI profile name (default: DEFAULT)

Prerequisites:
    - `databricks` CLI installed and authenticated.
    - Silver schema and tables already created (see README step 2).
    - For the fast Parquet path: pandas + pyarrow installed locally.

Methods:
    --method auto   (default) Try fast (Parquet + COPY INTO via UC Volume);
                     fall back to api (JSON via Statement Execution API) on failure.
    --method fast   Force the Parquet + UC Volume path.
    --method api    Force the JSON + INSERT-via-API path (no UC Volume needed).

Other flags:
    --skip-generate   Reuse files already in ./data/ instead of regenerating.
    --data-dir DIR    Directory for local data files (default: ./data relative to this script).

Examples:
    python src/setup/load_data.py
    python src/setup/load_data.py --method api
    python src/setup/load_data.py --skip-generate
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Make this script runnable from any cwd:
THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
import _data_generator as gen  # noqa: E402


# ----------------------------------------------------------------------------
# Configuration (env-driven)
# ----------------------------------------------------------------------------
CATALOG = os.environ.get('DATABRICKS_CATALOG')
SCHEMA = os.environ.get('DATABRICKS_SCHEMA')
WAREHOUSE_ID = os.environ.get('DATABRICKS_WAREHOUSE_ID')
PROFILE = os.environ.get('DATABRICKS_PROFILE', 'DEFAULT')

DEFAULT_DATA_DIR = THIS_DIR.parent.parent / 'data'  # repo-root/data


# Column ordering required for JSON-INSERT fallback (matches Silver DDL).
TABLE_COLUMNS = {
    'silver_store_clusters':     {'cols': ['cluster_id', 'cluster_code', 'cluster_name', 'state', 'region', 'store_count'], 'extra': {}},
    'silver_stores':             {'cols': ['store_id', 'store_code', 'store_name', 'address', 'city', 'state', 'postcode',
                                            'cluster_id', 'territory', 'format_type', 'open_date', 'is_active'],
                                  'extra': {'updated_at': 'CURRENT_TIMESTAMP()'}},
    'silver_categories':         {'cols': ['category_id', 'category_code', 'category_name', 'subcategory', 'department',
                                            'layout_group', 'is_food_service', 'is_active'], 'extra': {}},
    'silver_vendors':            {'cols': ['vendor_id', 'vendor_code', 'vendor_name', 'contact_email', 'contact_phone',
                                            'lead_time_days', 'delivery_days', 'is_active'], 'extra': {}},
    'silver_articles':           {'cols': ['article_id', 'article_code', 'article_name', 'ean', 'category_id', 'vendor_id',
                                            'unit_cost', 'unit_price', 'margin_pct', 'purchase_margin_pct', 'pack_qty',
                                            'case_size', 'min_order_qty', 'max_order_qty', 'shelf_life_days',
                                            'is_food_service', 'is_active'],
                                  'extra': {'updated_at': 'CURRENT_TIMESTAMP()'}},
    'silver_store_layouts':      {'cols': ['store_id', 'article_id', 'layout_location', 'shelf_position', 'facing_count',
                                            'is_tailored_in', 'effective_date'],
                                  'extra': {'updated_at': 'CURRENT_TIMESTAMP()'}},
    'silver_team_members':       {'cols': ['member_id', 'member_code', 'store_id', 'member_name', 'role', 'hire_date', 'is_active'], 'extra': {}},
    'silver_budgets':            {'cols': ['budget_id', 'store_id', 'category_id', 'period_type', 'period_start', 'period_end',
                                            'budget_sales', 'budget_gp', 'budget_units'], 'extra': {}},
    'silver_inventory':          {'cols': ['store_id', 'article_id', 'snapshot_date', 'soh_qty', 'soh_value',
                                            'last_receipt_date', 'last_sale_date', 'days_since_last_sale', 'first_oos_date'],
                                  'extra': {'updated_at': 'CURRENT_TIMESTAMP()'}},
    'silver_purchases':          {'cols': ['purchase_id', 'store_id', 'article_id', 'vendor_id', 'receipt_date',
                                            'receipt_timestamp', 'qty_ordered', 'qty_received', 'unit_cost', 'total_cost',
                                            'po_number'], 'extra': {}},
    'silver_write_offs':         {'cols': ['writeoff_id', 'store_id', 'article_id', 'writeoff_date', 'writeoff_time',
                                            'writeoff_hour', 'quantity', 'value', 'reason_code', 'reason_desc',
                                            'team_member_id', 'team_member_name'], 'extra': {}},
    'silver_sales_transactions': {'cols': ['txn_id', 'store_id', 'article_id', 'txn_date', 'txn_hour', 'txn_minute',
                                            'txn_timestamp', 'day_of_week', 'is_weekend', 'units_sold', 'revenue',
                                            'cost', 'gross_profit', 'txn_type'], 'extra': {}},
    'silver_customer_reviews':   {'cols': ['store_id', 'store_code', 'review_date', 'review_source', 'rating',
                                            'review_text', 'customer_name'], 'extra': {}},
}


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def run_sql(statement, wait_timeout='50s'):
    """Execute a SQL statement via the Statement Execution API. Returns (state, error_message)."""
    cmd = ['databricks', 'api', 'post', '/api/2.0/sql/statements', '-p', PROFILE,
           '--json', json.dumps({
               'warehouse_id': WAREHOUSE_ID,
               'catalog': CATALOG,
               'schema': SCHEMA,
               'statement': statement,
               'wait_timeout': wait_timeout,
           })]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        response = json.loads(result.stdout)
        status = response.get('status', {})
        return status.get('state', 'ERROR'), status.get('error', {}).get('message', '')
    except json.JSONDecodeError:
        return 'ERROR', result.stderr.strip() or result.stdout.strip()


def fs_cp(local_path, volume_path):
    """Upload a local file to a UC Volume via `databricks fs cp`. Returns (success, error)."""
    result = subprocess.run(
        ['databricks', 'fs', 'cp', '--overwrite', str(local_path), volume_path, '-p', PROFILE],
        capture_output=True, text=True,
    )
    return result.returncode == 0, result.stderr.strip()


# ----------------------------------------------------------------------------
# Method: FAST (Parquet + COPY INTO via UC Volume)
# ----------------------------------------------------------------------------
def load_fast(data_dir):
    """Upload Parquet files to a UC Volume and COPY INTO each Silver table."""
    volume_name = 'demo_data'
    volume_path = f'/Volumes/{CATALOG}/{SCHEMA}/{volume_name}'

    print(f"[fast] Ensuring UC Volume exists: {volume_path}")
    state, err = run_sql(
        f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{volume_name}"
    )
    if state != 'SUCCEEDED':
        raise RuntimeError(f"Could not create/access volume: {err}")

    # Ensure Parquet files exist; if not, generate them inline.
    if not any(data_dir.glob('*.parquet')):
        print(f"[fast] No Parquet files in {data_dir} — generating now.")
        gen.generate_all(str(data_dir), fmt='parquet')

    print(f"[fast] Uploading Parquet files to {volume_path} ...")
    for parquet in sorted(data_dir.glob('silver_*.parquet')):
        ok, err = fs_cp(parquet, f"{volume_path}/{parquet.name}")
        status = "ok" if ok else f"FAIL: {err}"
        print(f"  {parquet.name}: {status}")
        if not ok:
            raise RuntimeError(f"Upload failed for {parquet.name}: {err}")

    print(f"[fast] Loading Silver tables via COPY INTO ...")
    failures = []
    for table in TABLE_COLUMNS:
        run_sql(f"TRUNCATE TABLE {CATALOG}.{SCHEMA}.{table}")
        sql = (f"COPY INTO {CATALOG}.{SCHEMA}.{table} "
               f"FROM '{volume_path}/{table}.parquet' "
               f"FILEFORMAT = PARQUET "
               f"COPY_OPTIONS ('mergeSchema' = 'true')")
        state, err = run_sql(sql)
        mark = "✓" if state == 'SUCCEEDED' else "✗"
        print(f"  {mark} {table}" + (f" — {err[:80]}" if state != 'SUCCEEDED' else ""))
        if state != 'SUCCEEDED':
            failures.append((table, err))

    if failures:
        raise RuntimeError(f"{len(failures)} tables failed to load via fast path.")
    print("[fast] All Silver tables loaded.")


# ----------------------------------------------------------------------------
# Method: API (JSON + INSERT via Statement Execution API)
# ----------------------------------------------------------------------------
def load_api(data_dir):
    """Load JSON Lines files into Silver tables via Statement Execution API.

    Slower than the fast path; works without UC Volume access.
    """
    # Ensure JSON files exist; if not, generate them.
    if not any(data_dir.glob('silver_*.json')):
        print(f"[api] No JSON files in {data_dir} — generating now.")
        gen.generate_all(str(data_dir), fmt='json')

    print("[api] Loading Silver tables via INSERT batches ...")
    failures = []
    for table, cfg in TABLE_COLUMNS.items():
        json_file = data_dir / f"{table}.json"
        if not json_file.exists():
            print(f"  ✗ {table} — missing file {json_file.name}")
            failures.append((table, "missing file"))
            continue

        # Truncate
        run_sql(f"TRUNCATE TABLE {CATALOG}.{SCHEMA}.{table}")

        with open(json_file) as f:
            records = [json.loads(line) for line in f if line.strip()]

        if not records:
            print(f"  ✓ {table} (empty)")
            continue

        # Insert in batches to keep statement size reasonable.
        batch_size = 500
        cols = cfg['cols']
        extra = cfg['extra']
        insert_cols = cols + list(extra.keys())
        col_clause = ', '.join(insert_cols)

        rows_inserted = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            values = []
            for rec in batch:
                pieces = [_sql_literal(rec.get(c)) for c in cols] + list(extra.values())
                values.append(f"({', '.join(pieces)})")
            sql = (f"INSERT INTO {CATALOG}.{SCHEMA}.{table} ({col_clause}) "
                   f"VALUES {', '.join(values)}")
            state, err = run_sql(sql, wait_timeout='50s')
            if state != 'SUCCEEDED':
                failures.append((table, err))
                print(f"  ✗ {table} batch {i // batch_size} — {err[:80]}")
                break
            rows_inserted += len(batch)
        else:
            print(f"  ✓ {table} ({rows_inserted:,} rows)")

    if failures:
        raise RuntimeError(f"{len(failures)} tables failed via API path.")
    print("[api] All Silver tables loaded.")


def _sql_literal(value):
    """Quote a Python value as a SQL literal."""
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value).replace("'", "''")
    return f"'{s}'"


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic data and load it into the 7-Eleven Silver tables.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--method', choices=['auto', 'fast', 'api'], default='auto',
                        help="Loading method (default: auto).")
    parser.add_argument('--skip-generate', action='store_true',
                        help="Reuse existing files in --data-dir; don't regenerate.")
    parser.add_argument('--data-dir', default=str(DEFAULT_DATA_DIR),
                        help=f"Local data directory (default: {DEFAULT_DATA_DIR}).")
    args = parser.parse_args()

    # Validate env
    missing = [v for v in ('DATABRICKS_CATALOG', 'DATABRICKS_SCHEMA', 'DATABRICKS_WAREHOUSE_ID')
               if not os.environ.get(v)]
    if missing:
        print(f"ERROR: required env vars not set: {', '.join(missing)}", file=sys.stderr)
        print("       Set them in your shell, e.g.:", file=sys.stderr)
        print("           export DATABRICKS_CATALOG=retail_demo", file=sys.stderr)
        print("           export DATABRICKS_SCHEMA=store_demo", file=sys.stderr)
        print("           export DATABRICKS_WAREHOUSE_ID=<your-warehouse-id>", file=sys.stderr)
        sys.exit(2)

    data_dir = Path(args.data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("7-Eleven Store Intelligence — load_data.py")
    print("=" * 60)
    print(f"  catalog        = {CATALOG}")
    print(f"  schema         = {SCHEMA}")
    print(f"  warehouse_id   = {WAREHOUSE_ID}")
    print(f"  profile        = {PROFILE}")
    print(f"  data_dir       = {data_dir}")
    print(f"  method         = {args.method}")
    print(f"  skip-generate  = {args.skip_generate}")
    print()

    # 1) Generate (unless reusing files)
    if not args.skip_generate:
        fmt = 'parquet' if args.method in ('auto', 'fast') else 'json'
        gen.generate_all(str(data_dir), fmt=fmt)
    else:
        print(f"Reusing existing files in {data_dir}/ (--skip-generate set).")
        print()

    # 2) Load
    t0 = time.time()
    if args.method == 'fast':
        load_fast(data_dir)
    elif args.method == 'api':
        load_api(data_dir)
    else:  # auto
        try:
            load_fast(data_dir)
        except Exception as e:
            print(f"[auto] Fast path failed: {e}")
            print("[auto] Falling back to API path ...")
            load_api(data_dir)

    elapsed = time.time() - t0
    print()
    print("=" * 60)
    print(f"Load complete in {elapsed:.1f}s")
    print("=" * 60)


if __name__ == '__main__':
    main()
