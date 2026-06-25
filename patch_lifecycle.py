import sqlite3
import os

def upgrade_database():
    db_path = 'devops_board.db'
    if not os.path.exists(db_path) and os.path.exists(os.path.join('instance', 'devops_board.db')):
        db_path = os.path.join('instance', 'devops_board.db')

    print(f"[*] Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add lifecycle_stage column with a default fallback
    try:
        cursor.execute("ALTER TABLE task ADD COLUMN lifecycle_stage VARCHAR(100) DEFAULT 'Discovery / Consult';")
        print(" [+] Added 'lifecycle_stage' column to 'task' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(" [~] Column 'lifecycle_stage' already exists. Skipping.")
        else:
            print(f" [-] Error altering table: {e}")

    # Ensure all existing tasks have the default stage if they somehow ended up NULL
    cursor.execute("UPDATE task SET lifecycle_stage = 'Discovery / Consult' WHERE lifecycle_stage IS NULL")

    conn.commit()
    conn.close()
    print("\n[+] Database Lifecycle upgrade complete!")

if __name__ == '__main__':
    upgrade_database()