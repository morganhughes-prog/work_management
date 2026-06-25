import sqlite3
import os

def check_db():
    db_path = './instance/devops_board.db'
    
    if not os.path.exists(db_path):
        print(f"[-] Error: Could not find database file at: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Fetch all available tables first to make selection easy
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("[~] No tables found in the database.")
            return

        # 2. Display the tables
        print("\n=== Available Tables ===")
        for index, table in enumerate(tables, start=1):
            print(f" [{index}] {table}")
        print("========================")
        
        # 3. Get user input for the table
        table_choice = input("\nEnter the name of the table to inspect (or its number): ").strip()
        
        # Resolve the choice (whether they typed the number or the exact name)
        table_name = None
        if table_choice.isdigit() and 1 <= int(table_choice) <= len(tables):
            table_name = tables[int(table_choice) - 1]
        elif table_choice in tables:
            table_name = table_choice
        else:
            print("[-] Invalid table selection. Exiting.")
            return

        # 4. Get user input for number of rows (defaulting to 5 if left blank)
        n_input = input(f"How many rows would you like to grab from '{table_name}'? (Default 5): ").strip()
        n_rows = int(n_input) if n_input.isdigit() else 5
        
        # 5. Get the total record count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\n[+] The table '{table_name}' exists and has {count} records!\n")

        # 6. Fetch the requested rows
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (n_rows,))
        rows = cursor.fetchall()
        
        if not rows:
            print(f"[~] The table '{table_name}' is currently empty.")
            return
        
        # 7. Get column names and print the data vertically
        column_names = [desc[0] for desc in cursor.description]
        print(f"[*] First {len(rows)} rows of data:\n")
        
        for i, row in enumerate(rows, 1):
            print(f"================== ROW {i} ==================")
            for col_name, value in zip(column_names, row):
                print(f"{col_name:<30}: {value}")
            print("\n")

    except sqlite3.OperationalError as e:
        print(f"[-] Database Error: {e}")
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    check_db()