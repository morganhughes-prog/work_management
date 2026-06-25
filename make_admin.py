from app import app, db, User

def toggle_admin():
    # We must run this inside the 'app_context' so SQLAlchemy knows which database to talk to
    with app.app_context():
        print("\n=== Grand Archmage Promotion Tool ===")
        
        # 1. Ask for the username
        target_username = input("Enter the Mage Name (username) to manage: ").strip()
        
        # 2. Find the user in the database
        user = User.query.filter_by(username=target_username).first()
        
        if not user:
            print(f"[-] Error: Could not find any mage named '{target_username}' in the archives.")
            return
            
        # 3. Show current status
        current_status = "Admin" if user.is_admin else "Standard Member"
        print(f"[*] Found user: {user.username} | Current Status: {current_status}")
        
        # 4. Ask for action
        action = input("Do you want to grant this user Admin status? (y/n): ").strip().lower()
        
        if action == 'y':
            user.is_admin = True
            db.session.commit()
            print(f"[+] Success! '{user.username}' has been promoted to Admin.")
        elif action == 'n':
            user.is_admin = False
            db.session.commit()
            print(f"[+] Success! '{user.username}' is now a standard Guild Member.")
        else:
            print("[-] Invalid input. The incantation was cancelled.")

if __name__ == '__main__':
    toggle_admin()