from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from models import User, db
import bleach

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from JWT token"""
    try:
        current_user_id = get_jwt_identity()
        print("Current Id:",current_user_id)
        if current_user_id:
            return User.query.get(current_user_id)
    except:
        print(current_user_id)
    return None

def sanitize_html(content):
    """Sanitize HTML content to prevent XSS"""
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 
        'h4', 'h5', 'h6', 'blockquote', 'code', 'pre', 'a', 'img'
    ]
    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
        '*': ['class']
    }
    
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def create_notification(user_id, notification_type, message, data=None):
    """Helper function to create notifications"""
    from models import Notification
    
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        data=data or {}
    )
    
    db.session.add(notification)
    try:
        db.session.commit()
        return notification
    except Exception as e:
        db.session.rollback()
        return None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 20:
        return False, "Username must be no more than 20 characters long"
    if not username.replace('_', '').isalnum():
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, "Email is valid"

def login_user(username_or_email, password):
    """Authenticate user and return tokens"""
    # Try to find user by username or email
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()
    
    if not user or not user.is_active:
        return None, "Invalid credentials"
    
    if not user.check_password(password):
        return None, "Invalid credentials"
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }, None

def register_user(username, email, password):
    """Register a new user"""
    # Validate input
    username_valid, username_msg = validate_username(username)
    if not username_valid:
        return None, username_msg
    
    email_valid, email_msg = validate_email(email)
    if not email_valid:
        return None, email_msg
    
    password_valid, password_msg = validate_password(password)
    if not password_valid:
        return None, password_msg
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return None, "Username already exists"
    
    if User.query.filter_by(email=email).first():
        return None, "Email already exists"
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    try:
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, None
        
    except Exception as e:
        db.session.rollback()
        return None, "Registration failed. Please try again."