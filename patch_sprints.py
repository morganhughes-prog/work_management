import sqlite3
import os

def upgrade_database():
    db_path = 'devops_board.db'
    if not os.path.exists(db_path) and os.path.exists(os.path.join('instance', 'devops_board.db')):
        db_path = os.path.join('instance', 'devops_board.db')

    print(f"Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create the Sprint table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sprint (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE
            );
        """)
        print(" [+] Forged the 'sprint' table.")
    except sqlite3.Error as e:
         print(f" [-] Error creating sprint table: {e}")

    # 2. Add sprint_id to Tasks
    try:
        cursor.execute("ALTER TABLE task ADD COLUMN sprint_id INTEGER REFERENCES sprint(id);")
        print(" [+] Added 'sprint_id' column to 'task' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(" [~] Column 'sprint_id' already exists. Skipping.")
        else:
            print(f" [-] Error altering table: {e}")

    # 3. Seed initial sprints
    initial_sprints = ['May 2026', 'June 2026', 'July 2026', 'Future Backlog']
    for sprint_name in initial_sprints:
        try:
            cursor.execute("INSERT INTO sprint (name) VALUES (?)", (sprint_name,))
            print(f" [+] Created Sprint: {sprint_name}")
        except sqlite3.IntegrityError:
            pass # Already exists

    conn.commit()
    conn.close()
    print("\nDatabase sprint upgrade complete!")

if __name__ == '__main__':
    upgrade_database()