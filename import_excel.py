import pandas as pd
import sqlite3
import os
import shutil
import time

# File paths
excel_file = r"c:\Users\22kel\OneDrive - Michigan State University\Coding\first research assignment.xlsx"
db_file = r"c:\Users\22kel\OneDrive - Michigan State University\Coding\mydata.db"
temp_excel = r"C:\Temp\first_research_temp.xlsx"

# Create temp directory if needed
os.makedirs(r"C:\Temp", exist_ok=True)

# Copy file to temp location to avoid OneDrive lock issues
print(f"Copying Excel file to temp location...")
time.sleep(0.5)  # Wait a moment
shutil.copy2(excel_file, temp_excel)

# Read Excel file from temp location
print(f"Reading Excel file: {excel_file}")
xls = pd.ExcelFile(temp_excel)
print(f"Sheet names: {xls.sheet_names}")

# Connect to SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Import each sheet
for sheet_name in xls.sheet_names:
    print(f"\nImporting sheet: {sheet_name}")
    df = pd.read_excel(temp_excel, sheet_name=sheet_name)
    
    # Clean column names for SQL (remove spaces, special characters)
    df.columns = [col.replace(' ', '_').replace('-', '_').lower() for col in df.columns]
    
    # Create table name from sheet name
    table_name = sheet_name.replace(' ', '_').replace('-', '_').lower()
    
    print(f"  Columns: {list(df.columns)}")
    print(f"  Rows: {len(df)}")
    
    # Write to SQLite
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"  ✓ Table '{table_name}' created successfully")

conn.commit()
conn.close()

# Clean up temp file
try:
    os.remove(temp_excel)
except PermissionError:
    pass  # File may still be locked, that's okay

print("\n✓ Import complete! Your data is now in mydata.db")
