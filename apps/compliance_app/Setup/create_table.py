"""
Script to create and populate the document compliance table in Databricks Lakebase (PostgreSQL).
This table tracks documents uploaded by various business units in the bank.

Run this script once from a Databricks notebook to initialize the table with sample data.

Reference: https://docs.databricks.com/aws/en/oltp/instances/query/notebook
"""

import psycopg2
from psycopg2.extras import execute_batch
from databricks.sdk import WorkspaceClient
import uuid
from datetime import datetime, timedelta
import random

# Lakebase Configuration
INSTANCE_NAME = "chat-db"       # Lakebase instance name
DATABASE = "compliance_app"      # PostgreSQL database name  
SCHEMA = "audit"                 # PostgreSQL schema name
TABLE = "document_registry"      # Table name
POSTGRES_USER = "06c27421-2fda-44bc-8891-bd83bb09e08c"  # Update with yourService principal ID for Databricks App

# Initialize Databricks Workspace Client
w = WorkspaceClient()

print(f"Connecting to Lakebase instance: {INSTANCE_NAME}")
print(f"Database: {DATABASE}")
print(f"Schema: {SCHEMA}")
print(f"Table: {TABLE}")

def get_postgres_connection():
    """Get a connection to the Lakebase PostgreSQL instance using OAuth token"""
    try:
        # Get the Lakebase instance details
        instance = w.database.get_database_instance(name=INSTANCE_NAME)
        
        # Generate OAuth credential for authentication
        cred = w.database.generate_database_credential(
            request_id=str(uuid.uuid4()), 
            instance_names=[INSTANCE_NAME]
        )
        
        # Connect to PostgreSQL using psycopg2
        conn = psycopg2.connect(
            host=instance.read_write_dns,
            dbname=DATABASE,
            user=POSTGRES_USER,
            password=cred.token,
            sslmode="require",
            port=5432
        )
        
        print(f"✓ Connected to Lakebase instance: {instance.read_write_dns}")
        return conn
        
    except Exception as e:
        print(f"Error connecting to Lakebase: {e}")
        raise

def create_schema_if_not_exists(conn):
    """Create the PostgreSQL schema if it doesn't exist"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
            conn.commit()
        print(f"✓ Schema '{SCHEMA}' created or already exists")
    except Exception as e:
        conn.rollback()
        print(f"Note: Schema creation - {e}")
        print(f"  If schema already exists, continuing...")

def create_table(conn):
    """Create the document registry table in Lakebase PostgreSQL"""
    try:
        with conn.cursor() as cursor:
            # Drop table if exists to ensure clean state
            drop_table_sql = f"DROP TABLE IF EXISTS {SCHEMA}.{TABLE} CASCADE"
            cursor.execute(drop_table_sql)
            print(f"✓ Dropped existing table {SCHEMA}.{TABLE} (if it existed)")
            
            # Create table using PostgreSQL syntax
            create_table_sql = f"""
            CREATE TABLE {SCHEMA}.{TABLE} (
                document_id VARCHAR(50) NOT NULL PRIMARY KEY,
                document_name VARCHAR(500) NOT NULL,
                document_type VARCHAR(100) NOT NULL,
                business_unit VARCHAR(100) NOT NULL,
                owner_name VARCHAR(200) NOT NULL,
                owner_email VARCHAR(200) NOT NULL,
                upload_date TIMESTAMP NOT NULL,
                last_modified_date TIMESTAMP NOT NULL,
                file_size_mb DECIMAL(10,2) NOT NULL,
                classification VARCHAR(50) NOT NULL,
                retention_period_years INTEGER NOT NULL,
                marked_for_archival BOOLEAN NOT NULL,
                archival_date TIMESTAMP,
                compliance_status VARCHAR(50) NOT NULL,
                review_required BOOLEAN NOT NULL,
                reviewer_name VARCHAR(200),
                last_review_date TIMESTAMP,
                next_review_date TIMESTAMP,
                storage_location VARCHAR(1000) NOT NULL,
                encryption_status VARCHAR(100) NOT NULL,
                tags VARCHAR(500),
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            print(f"✓ Table {SCHEMA}.{TABLE} created successfully")
            
    except Exception as e:
        conn.rollback()
        print(f"Error creating table: {e}")
        raise

def generate_sample_data(num_records=500):
    """Generate sample document data"""
    
    # Sample data lists
    document_types = [
        "Policy Document", "Contract", "Regulatory Report", "Audit Report",
        "Financial Statement", "Risk Assessment", "Compliance Report",
        "Customer Agreement", "Loan Document", "Investment Prospectus",
        "Internal Memo", "Board Resolution", "Trading Record", "KYC Document"
    ]
    
    business_units = [
        "Retail Banking", "Corporate Banking", "Investment Banking",
        "Wealth Management", "Risk Management", "Compliance",
        "Treasury", "Operations", "Legal", "Human Resources",
        "IT Security", "Internal Audit"
    ]
    
    classifications = ["Public", "Internal", "Confidential", "Highly Confidential"]
    
    compliance_statuses = ["Compliant", "Non-Compliant", "Pending Review", "Under Investigation"]
    
    encryption_statuses = ["Encrypted", "Encrypted at Rest", "End-to-End Encrypted"]
    
    owner_names = [
        "John Smith", "Sarah Johnson", "Michael Chen", "Emily Davis",
        "Robert Wilson", "Lisa Anderson", "David Martinez", "Jennifer Taylor",
        "William Brown", "Jessica Garcia", "James Miller", "Mary Rodriguez",
        "Christopher Lee", "Patricia White", "Daniel Harris"
    ]
    
    reviewer_names = [
        "Compliance Team A", "Compliance Team B", "Legal Review",
        "Risk Committee", "Audit Department", None
    ]
    
    data = []
    base_date = datetime.now() - timedelta(days=730)  # 2 years ago
    
    for i in range(num_records):
        upload_date = base_date + timedelta(days=random.randint(0, 730))
        last_modified = upload_date + timedelta(days=random.randint(0, 30))
        
        # Determine retention and archival
        retention_years = random.choice([3, 5, 7, 10, 15, 20])
        marked_for_archival = random.random() < 0.15  # 15% marked for archival
        
        archival_date = None
        if marked_for_archival:
            archival_date = upload_date + timedelta(days=retention_years * 365)
        
        # Review dates
        review_required = random.random() < 0.7  # 70% require review
        last_review_date = None
        next_review_date = None
        reviewer = None
        
        if review_required:
            last_review_date = upload_date + timedelta(days=random.randint(30, 180))
            next_review_date = last_review_date + timedelta(days=random.choice([90, 180, 365]))
            reviewer = random.choice(reviewer_names)
        
        # Generate compliance status
        compliance_status = random.choice(compliance_statuses)
        
        # Business unit and owner
        business_unit = random.choice(business_units)
        owner_name = random.choice(owner_names)
        owner_email = f"{owner_name.lower().replace(' ', '.')}@globalbank.com"
        
        # Document details
        doc_type = random.choice(document_types)
        doc_name = f"{doc_type}_{business_unit.replace(' ', '_')}_{i+1}.pdf"
        
        # Storage location
        storage_location = f"/Volumes/main/banking_compliance/documents/{business_unit.replace(' ', '_')}/{doc_name}"
        
        # Tags
        tags = random.choice([
            "urgent,regulatory",
            "annual,financial",
            "customer,onboarding",
            "risk,assessment",
            "internal,policy",
            None
        ])
        
        record = {
            "document_id": f"DOC{str(i+1).zfill(8)}",
            "document_name": doc_name,
            "document_type": doc_type,
            "business_unit": business_unit,
            "owner_name": owner_name,
            "owner_email": owner_email,
            "upload_date": upload_date,
            "last_modified_date": last_modified,
            "file_size_mb": round(random.uniform(0.1, 50.0), 2),
            "classification": random.choice(classifications),
            "retention_period_years": retention_years,
            "marked_for_archival": marked_for_archival,
            "archival_date": archival_date,
            "compliance_status": compliance_status,
            "review_required": review_required,
            "reviewer_name": reviewer,
            "last_review_date": last_review_date,
            "next_review_date": next_review_date,
            "storage_location": storage_location,
            "encryption_status": random.choice(encryption_statuses),
            "tags": tags,
            "created_at": upload_date,
            "updated_at": last_modified
        }
        
        data.append(record)
    
    return data

def populate_table(conn, num_records=500):
    """Populate the Lakebase PostgreSQL table with sample data"""
    try:
        print(f"Generating {num_records} sample records...")
        sample_data = generate_sample_data(num_records)
        
        print(f"Inserting {num_records} records into {SCHEMA}.{TABLE}...")
        
        # Prepare INSERT statement
        insert_sql = f"""
        INSERT INTO {SCHEMA}.{TABLE} (
            document_id, document_name, document_type, business_unit,
            owner_name, owner_email, upload_date, last_modified_date,
            file_size_mb, classification, retention_period_years,
            marked_for_archival, archival_date, compliance_status,
            review_required, reviewer_name, last_review_date,
            next_review_date, storage_location, encryption_status,
            tags, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        # Convert data to tuples for batch insert
        records = [
            (
                record["document_id"], record["document_name"], record["document_type"],
                record["business_unit"], record["owner_name"], record["owner_email"],
                record["upload_date"], record["last_modified_date"], record["file_size_mb"],
                record["classification"], record["retention_period_years"],
                record["marked_for_archival"], record["archival_date"],
                record["compliance_status"], record["review_required"],
                record["reviewer_name"], record["last_review_date"],
                record["next_review_date"], record["storage_location"],
                record["encryption_status"], record["tags"],
                record["created_at"], record["updated_at"]
            )
            for record in sample_data
        ]
        
        # Use batch insert for better performance
        with conn.cursor() as cursor:
            execute_batch(cursor, insert_sql, records, page_size=100)
            conn.commit()
        
        print(f"✓ Successfully inserted {num_records} records into {SCHEMA}.{TABLE}")
        
        # Display sample records
        print("\nSample records:")
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT document_id, document_name, business_unit, compliance_status FROM {SCHEMA}.{TABLE} LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(f"  {row[0]} | {row[1][:50]}... | {row[2]} | {row[3]}")
        
        # Display summary statistics
        print("\nTable statistics:")
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT business_unit) as business_units,
                    SUM(CASE WHEN marked_for_archival THEN 1 ELSE 0 END) as marked_for_archival,
                    SUM(CASE WHEN compliance_status = 'Non-Compliant' THEN 1 ELSE 0 END) as non_compliant,
                    SUM(CASE WHEN review_required THEN 1 ELSE 0 END) as requiring_review
                FROM {SCHEMA}.{TABLE}
            """)
            stats = cursor.fetchone()
            print(f"  Total documents: {stats[0]}")
            print(f"  Business units: {stats[1]}")
            print(f"  Marked for archival: {stats[2]}")
            print(f"  Non-compliant: {stats[3]}")
            print(f"  Requiring review: {stats[4]}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error populating table: {e}")
        raise

def main():
    """Main execution function"""
    print("=" * 80)
    print("Document Compliance Table Setup (Databricks Lakebase - PostgreSQL)")
    print("=" * 80)
    
    print(f"\nLakebase Instance: {INSTANCE_NAME}")
    print(f"Database: {DATABASE}")
    print(f"Schema: {SCHEMA}")
    print(f"Table: {TABLE}")
    print(f"Postgres User: {POSTGRES_USER}")
    
    conn = None
    try:
        # Step 1: Connect to Lakebase
        print("\n[1/4] Connecting to Lakebase instance...")
        conn = get_postgres_connection()
        
        # Step 2: Create schema
        print("\n[2/4] Creating schema...")
        create_schema_if_not_exists(conn)
        
        # Step 3: Create table
        print("\n[3/4] Creating table...")
        create_table(conn)
        
        # Step 4: Populate with sample data
        print("\n[4/4] Populating table with sample data...")
        populate_table(conn, num_records=500)
        
        print("\n" + "=" * 80)
        print("✓ Setup complete!")
        print("=" * 80)
        print(f"\nYou can now query the table using:")
        print(f"  SELECT * FROM {SCHEMA}.{TABLE} LIMIT 10;")
        print("\nOr access it in your app using the Lakebase connection.")
        print(f"\nReference: https://docs.databricks.com/aws/en/oltp/instances/query/notebook")
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        raise
    finally:
        if conn:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    main()

