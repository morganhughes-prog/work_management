import sqlite3
import os

def upgrade_database():
    db_path = 'devops_board.db'
    if not os.path.exists(db_path) and os.path.exists(os.path.join('instance', 'devops_board.db')):
        db_path = os.path.join('instance', 'devops_board.db')

    print(f"Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Add the parent_id column
    try:
        cursor.execute("ALTER TABLE work_class ADD COLUMN parent_id INTEGER REFERENCES work_class(id);")
        print(" [+] Added 'parent_id' column to 'work_class' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(" [~] Column 'parent_id' already exists. Skipping.")
        else:
            print(f" [-] Error altering table: {e}")

    # 2. Define the new hierarchy requested
    hierarchy = {
        'asset': ['reporting', 'systems', 'training', 'technology'],
        'workforce': ['contractor', 'permanent', 'resources'],
        'governance': ['documentation', 'policies', 'framework'],
        'forums': ['multi disciplinary teams', 'fortnightly catchup', 'stand ups', 'branch stand up']
    }

    # 3. Insert the new 2nd-tier classes
    for parent_name, children in hierarchy.items():
        # Find the parent ID
        cursor.execute("SELECT id FROM work_class WHERE name = ?", (parent_name,))
        result = cursor.fetchone()
        
        if result:
            parent_id = result[0]
            for child_name in children:
                try:
                    cursor.execute(
                        "INSERT INTO work_class (name, parent_id) VALUES (?, ?)", 
                        (child_name, parent_id)
                    )
                    print(f" [+] Forged subclass: {parent_name} > {child_name}")
                except sqlite3.IntegrityError:
                    print(f" [~] Subclass '{child_name}' already exists. Skipping.")
        else:
            print(f" [-] Warning: Could not find parent class '{parent_name}' to attach children.")

    conn.commit()
    conn.close()
    print("\nDatabase hierarchy upgrade complete!")

if __name__ == '__main__':
    upgrade_database()