import sqlite3
import os
from datetime import datetime, date
import calendar

def upgrade_database():
    db_path = 'devops_board.db'
    if not os.path.exists(db_path) and os.path.exists(os.path.join('instance', 'devops_board.db')):
        db_path = os.path.join('instance', 'devops_board.db')

    print(f"[*] Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Add end_date column
    try:
        cursor.execute("ALTER TABLE sprint ADD COLUMN end_date DATE;")
        print(" [+] Added 'end_date' column to 'sprint' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(" [~] Column 'end_date' already exists. Skipping.")
        else:
            print(f" [-] Error altering table: {e}")

    # 2. Automatically calculate deadlines for existing sprints
    cursor.execute("SELECT id, name FROM sprint")
    sprints = cursor.fetchall()

    for sprint_id, name in sprints:
        try:
            # Try to parse names like "May 2026"
            dt = datetime.strptime(name, "%B %Y")
            last_day = calendar.monthrange(dt.year, dt.month)[1]
            end_date_str = date(dt.year, dt.month, last_day).isoformat()
        except ValueError:
            # If it's a custom name like "Future Backlog", set it far into the future
            end_date_str = date(2099, 12, 31).isoformat()
            
        cursor.execute("UPDATE sprint SET end_date = ? WHERE id = ?", (end_date_str, sprint_id))
        print(f" [+] Set deadline for '{name}' to {end_date_str}")

    conn.commit()
    conn.close()
    print("\n[+] Database sprint dates upgrade complete!")

if __name__ == '__main__':
    upgrade_database()