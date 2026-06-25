from app import app, db
from sqlalchemy import text

def patch():
    with app.app_context():
        conn = db.engine.connect()

        try:
            conn.execute(text("""
                ALTER TABLE task_attachment
                ADD COLUMN label VARCHAR(200)
            """))
            print("[+] Added label column to task_attachment")

        except Exception as e:
            print("[-] Patch may already be applied:", e)

        conn.close()

if __name__ == "__main__":
    patch()
