from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def handle_register(name, email, password, users_db):
    """
    Handle user registration
    """
    # Check if user already exists
    if email in users_db:
        return False
    
    # Basic validation
    if len(password) < 8:
        return False
    
    # Hash password and store user
    users_db[email] = {
        'name': name,
        'email': email,
        'password': generate_password_hash(password),
        'created_at': datetime.now(),
        'is_active': True
    }
    
    return True

def handle_login(email, password, users_db):
    """
    Handle user login
    """
    # Check if user exists
    if email not in users_db:
        return False
    
    user = users_db[email]
    
    # Check if account is active
    if not user.get('is_active', True):
        return False
    
    # Verify password
    if check_password_hash(user['password'], password):
        # Update last login
        user['last_login'] = datetime.now()
        return True
    
    return False

def get_user(email, users_db):
    """
    Get user information
    """
    return users_db.get(email)

def update_user(email, data, users_db):
    """
    Update user information
    """
    if email in users_db:
        users_db[email].update(data)
        users_db[email]['updated_at'] = datetime.now()
        return True
    return False

def change_password(email, current_password, new_password, users_db):
    """
    Change user password
    """
    if email not in users_db:
        return False
    
    user = users_db[email]
    
    # Verify current password
    if not check_password_hash(user['password'], current_password):
        return False
    
    # Update password
    user['password'] = generate_password_hash(new_password)
    user['updated_at'] = datetime.now()
    
    return True