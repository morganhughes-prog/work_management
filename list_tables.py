import sqlite3
import os

def get_db_path():
    db_path = os.path.join('instance', 'devops_board.db')
    if not os.path.exists(db_path) and os.path.exists('devops_board.db'):
        db_path = 'devops_board.db'
    return db_path

def inspect_table_columns():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"[-] Error: Could not find database file at: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Fetch all user tables
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("[~] No tables found in the database.")
            return

        # 2. Display tables to the user
        print("\n=== Available Tables ===")
        for index, table_name in enumerate(tables, start=1):
            print(f" [{index}] {table_name}")
        print("========================")

        # 3. Get user choice
        choice = input("\nEnter the number of the table you want to inspect: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(tables)):
            print("[-] Invalid selection. Exiting.")
            return
            
        chosen_table = tables[int(choice) - 1]
        
        # 4. Use PRAGMA table_info to pull the exact column structure
        cursor.execute(f"PRAGMA table_info([{chosen_table}]);")
        columns = cursor.fetchall()
        
        # 5. Print out a clean, structured schema overview
        print(f"\n[+] Structure for table: '{chosen_table}'")
        print("-" * 60)
        print(f"{'ID':<4} | {'Column Name':<30} | {'Data Type':<12} | {'Primary Key?':<12}")
        print("-" * 60)
        
        for col in columns:
            # col structure: (cid, name, type, notnull, dflt_value, pk)
            col_id = col[0]
            col_name = col[1]
            col_type = col[2] if col[2] else "TEXT (auto)"
            is_pk = "YES" if col[5] == 1 else "No"
            
            print(f"{col_id:<4} | {col_name:<30} | {col_type:<12} | {is_pk:<12}")
            
        print("-" * 60)
        
    except sqlite3.Error as e:
        print(f"[-] Database inspection failure: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    inspect_table_columns()