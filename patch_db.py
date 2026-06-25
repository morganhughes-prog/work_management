import sqlite3
import os

def upgrade_database():
    db_path = 'devops_board.db'
    
    # Check if the database exists in an 'instance' folder (Flask sometimes puts it there)
    if not os.path.exists(db_path) and os.path.exists(os.path.join('instance', 'devops_board.db')):
        db_path = os.path.join('instance', 'devops_board.db')
        
    if not os.path.exists(db_path):
        print(f"Error: Could not find {db_path}. Make sure you run this script in the same directory as your database.")
        return

    print(f"Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Add 'is_admin' to the 'user' table
    try:
        # SQLite stores Booleans as 0 (False) or 1 (True)
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0;")
        print(" [+] Successfully added 'is_admin' column to 'user' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(" [~] Column 'is_admin' already exists. Skipping.")
        else:
            print(f" [-] Error altering user table: {e}")

    # 2. Add 'work_class_id' to the 'task' table
    try:
        cursor.execute("ALTER TABLE task ADD COLUMN work_class_id INTEGER REFERENCES work_class(id);")
        print(" [+] Successfully added 'work_class_id' column to 'task' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(" [~] Column 'work_class_id' already exists. Skipping.")
        else:
            print(f" [-] Error altering task table: {e}")

    # 3. Create the 'work_class' table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_class (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE
            );
        """)
        print(" [+] Successfully ensured 'work_class' table exists.")
    except sqlite3.Error as e:
         print(f" [-] Error creating work_class table: {e}")

    # Save changes and close
    conn.commit()
    conn.close()
    print("\nDatabase upgrade complete! You can now start your Flask app.")

if __name__ == '__main__':
    upgrade_database()