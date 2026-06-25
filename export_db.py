import sqlite3
import csv
import os

def export_database_to_csv():
    # 1. Locate the database
    db_path = 'devops_board.db'
    if not os.path.exists(db_path) and os.path.exists(os.path.join('instance', 'devops_board.db')):
        db_path = os.path.join('instance', 'devops_board.db')

    if not os.path.exists(db_path):
        print(f"[-] Error: Could not find database at {db_path}")
        return

    print(f"[*] Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. Query the internal SQLite master table to get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print("[-] No tables found in the database.")
        return

    # 3. Loop through every table and export it
    for table in tables:
        table_name = table[0]
        
        # Skip internal SQLite sequence/system tables
        if table_name.startswith('sqlite_'):
            continue
            
        print(f"[*] Exporting table: '{table_name}'...")
        
        # Fetch all records
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Fetch column names dynamically
        column_names = [description[0] for description in cursor.description]
        
        # 4. Write to CSV
        csv_filename = f"{table_name}_export.csv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            
            # Write the header row
            csv_writer.writerow(column_names)
            
            # Write all the data rows
            csv_writer.writerows(rows)
            
        print(f"    -> Saved {len(rows)} records to {csv_filename}")

    conn.close()
    print("\n[+] Export complete! Check your project folder for the CSV files.")

if __name__ == '__main__':
    export_database_to_csv()