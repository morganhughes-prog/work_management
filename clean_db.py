import sqlite3
import os

db_path = 'devops_board.db'
if not os.path.exists(db_path) and os.path.exists(os.path.join('instance', 'devops_board.db')):
    db_path = os.path.join('instance', 'devops_board.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Convert empty strings and zeroes into true NULLs
cursor.execute("UPDATE task SET work_class_id = NULL WHERE work_class_id = '' OR work_class_id = 0;")
rows_fixed = cursor.rowcount

conn.commit()
conn.close()

print(f"[+] Database cleansed! {rows_fixed} ghost records fixed.")