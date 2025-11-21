from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

# Hardcoded users (in production, use a database)
USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin'
    },
    'housekeeping': {
        'password': 'house123',
        'role': 'housekeeping'
    }
}

def get_user(username):
    """Retrieve user by username"""
    if username in USERS:
        return User(username, username, USERS[username]['role'])
    return None

def verify_password(username, password):
    """Verify user credentials"""
    if username in USERS:
        return USERS[username]['password'] == password
    return False