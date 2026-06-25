import sqlite3
import os

def upgrade_database():
    db_path = 'devops_board.db'
    if not os.path.exists(db_path) and os.path.exists(os.path.join('instance', 'devops_board.db')):
        db_path = os.path.join('instance', 'devops_board.db')

    print(f"Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create the TaskAssignment ledger table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_assignment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                unassigned_at DATETIME,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY(task_id) REFERENCES task(id),
                FOREIGN KEY(user_id) REFERENCES user(id)
            );
        """)
        print(" [+] Forged the 'task_assignment' ledger table.")
    except sqlite3.Error as e:
         print(f" [-] Error creating table: {e}")

    # 2. Migrate existing task owners into the ledger
    try:
        # We only insert if the task isn't already in the ledger to prevent duplicates if you run this twice
        cursor.execute("""
            INSERT INTO task_assignment (task_id, user_id, assigned_at, is_active)
            SELECT id, user_id, CURRENT_TIMESTAMP, 1 
            FROM task 
            WHERE id NOT IN (SELECT task_id FROM task_assignment);
        """)
        print(f" [+] Migrated existing task authors into the assignment ledger.")
    except sqlite3.Error as e:
         print(f" [-] Error migrating data: {e}")

    conn.commit()
    conn.close()
    print("\nDatabase upgrade complete! Your archives are ready.")

if __name__ == '__main__':
    upgrade_database()