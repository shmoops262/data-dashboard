import sqlite3

db_file = r"c:\Users\22kel\OneDrive - Michigan State University\Coding\mydata.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables in database: {[t[0] for t in tables]}\n")

# Inspect each table
for table in tables:
    table_name = table[0]
    print(f"=== TABLE: {table_name} ===")
    
    # Get table schema
    cursor.execute(f"PRAGMA table_info([{table_name}]);")
    columns = cursor.fetchall()
    print(f"Columns ({len(columns)}):")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM [{table_name}];")
    row_count = cursor.fetchone()[0]
    print(f"Row count: {row_count}")
    
    # Check for NULL values in each column
    print("NULL value counts:")
    for col in columns:
        col_name = col[1]
        cursor.execute(f"SELECT COUNT(*) FROM [{table_name}] WHERE [{col_name}] IS NULL;")
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"  - {col_name}: {null_count} NULLs")
    
    # Check for primary key
    cursor.execute(f"PRAGMA primary_key([{table_name}]);")
    pk = cursor.fetchall()
    print(f"Primary key: {pk if pk else 'NONE'}")
    
    print()

conn.close()
