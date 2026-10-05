# File converts raw data from CDC's Youth Risk Behavior Surveillance System (YRBSS.mdb) into two readable CSV files
from pathlib import Path
import pyodbc
import pandas as pd

mdb_file = Path(
    r"High-Academic-Performance-Pressure-vs.-Youth-Mental-Health\YRBSS.mdb"
)

# Connection string for Windows Access Driver
conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_file};"

try:
    # Connect to the MDB database
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Get a list of all tables in the database
    tables = [row.table_name for row in cursor.tables(tableType='TABLE')]
    print(f"Found tables: {tables}")
    
    # Export each table to its own CSV
    for table_name in tables:
        output_csv = f"{table_name}.csv"
        print(f"Exporting {table_name} to {output_csv}...")
        
        query = f"SELECT * FROM [{table_name}]"
        df = pd.read_sql(query, conn)
        df.to_csv(output_csv, index=False)
        
    print("All tables successfully exported to CSV!")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals():
        conn.close()
