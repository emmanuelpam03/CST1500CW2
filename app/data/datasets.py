import pandas as pd
from app.data.db import connect_database
from pathlib import Path

def insert_dataset_metadata(dataset_name, category, source, last_updated, record_count, file_size_mb):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    lastid = cursor.lastrowid
    conn.close()
    return lastid

def get_all_datasets_metadata():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", conn)
    conn.close()
    return df

def migrate_datasets_metadata_from_file(file_path="DATA/datasets_metadata.csv"):
    """
    Migrate datasets_metadata from CSV file.
    CSV format: dataset_id,name,rows,columns,uploaded_by,upload_date
    Table format: dataset_name, category, source, last_updated, record_count, file_size_mb
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
    if cursor.fetchone()[0] == 0:
        filepath = Path(file_path)
        if not filepath.exists():
            print(f"Datasets metadata file not found at {file_path}")
            conn.close()
            return 0
        
        migrated = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) < 6:
                    continue
                
                dataset_id, name, rows, columns, uploaded_by, upload_date = parts
                
                # Map CSV columns to table columns
                dataset_name = name
                category = uploaded_by  # Using uploaded_by as category
                source = "CSV Import"
                last_updated = upload_date
                record_count = int(rows) if rows.isdigit() else 0
                file_size_mb = float(columns) / 1000 if columns.isdigit() else 0.0  # Approximate
                
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO datasets_metadata
                        (dataset_name, category, source, last_updated, record_count, file_size_mb)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
                    if cursor.rowcount:
                        migrated += 1
                except Exception as e:
                    print(f"Error migrating dataset {name}: {e}")
        
        conn.commit()
        print(f"Migrated {migrated} datasets from {filepath.name}")
        conn.close()
        return migrated
    else:
        conn.close()
        return 0

def load_csv_to_table(csv_path, table_name, if_exists='append'):
    import pandas as pd
    conn = connect_database()
    df = pd.read_csv(csv_path)
    df.to_sql(name=table_name, con=conn, if_exists=if_exists, index=False)
    conn.close()
    return len(df)