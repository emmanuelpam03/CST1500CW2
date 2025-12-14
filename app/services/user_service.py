import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user

DATA_DIR = Path(__file__).resolve().parents[2] / "DATA"

def register_user(username, password, role='user'):
    """
    Register a user using bcrypt for hashing.
    Returns (True, message) on success, (False, message) on failure.
    """
    # check exists
    if get_user_by_username(username):
        return False, f"User '{username}' already exists."

    # hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password_hash = hashed.decode('utf-8')

    lastid = insert_user(username, password_hash, role)
    return True, f"User '{username}' registered (id={lastid})."

def login_user(username, password):
    user = get_user_by_username(username)
    if not user:
        return False, "User not found."

    stored_hash = user[2]  # password_hash column
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, f"Login successful for {username}."
    else:
        return False, "Incorrect password."

def ensure_default_admin():
    """
    Check if there are any admin users. If not, create a default admin.
    Default admin: username='admin', password='admin'
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    # Check if any admin exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        # Create default admin
        default_username = "admin"
        default_password = "admin"
        
        # Check if admin username already exists (as regular user)
        cursor.execute("SELECT * FROM users WHERE username = ?", (default_username,))
        existing_user = cursor.fetchone()
        
        if not existing_user:
            # Hash password
            hashed = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
            password_hash = hashed.decode('utf-8')
            
            # Insert admin
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (default_username, password_hash, 'admin')
            )
            conn.commit()
            print(f"Created default admin user: username='{default_username}', password='{default_password}'")
        else:
            # Update existing user to admin
            hashed = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
            password_hash = hashed.decode('utf-8')
            cursor.execute(
                "UPDATE users SET password_hash = ?, role = 'admin' WHERE username = ?",
                (password_hash, default_username)
            )
            conn.commit()
            print(f"Updated existing user '{default_username}' to admin role")
    
    conn.close()

def migrate_users_from_file(filepath=None):
    """
    Migrate users from DATA/users.txt into database.
    Format expected: username,password_hash,role
    If the file has plain-text passwords (Week 7), the safe approach is to ask the user.
    This implementation expects bcrypt hashes already in file.
    """
    filepath = filepath or (DATA_DIR / "users.txt")
    if not filepath.exists():
        print(f"No users file found at {filepath}")
        return 0

    conn = connect_database()
    cursor = conn.cursor()
    migrated = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) < 2:
                continue
            username = parts[0].strip()
            password_hash = parts[1].strip()
            role = parts[2].strip() if len(parts) > 2 else 'user'
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                if cursor.rowcount:
                    migrated += 1
            except Exception as e:
                print("Error migrating", username, e)
    conn.commit()
    conn.close()
    print(f"Migrated {migrated} users from {filepath.name}")
    return migrated
