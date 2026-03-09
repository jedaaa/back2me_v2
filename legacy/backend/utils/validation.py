"""
Input validation and sanitization utilities
Prevents XSS, SQL injection, and validates user input
"""

import re
from html import escape
from typing import Optional, Dict, Any

class ValidationError(Exception):
    """Custom validation error"""
    pass

def sanitize_html(text: str) -> str:
    """
    Escape HTML special characters to prevent XSS
    """
    if not text:
        return ""
    return escape(str(text))

def validate_email(email: str) -> str:
    """
    Validate and sanitize email address
    """
    email = sanitize_html(email.strip().lower())
    
    # Email regex pattern
    pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    
    if len(email) > 255:
        raise ValidationError("Email too long (max 255 characters)")
    
    return email

def validate_username(username: str) -> str:
    """
    Validate and sanitize username
    - Alphanumeric and underscores only
    - 3-30 characters
    """
    username = sanitize_html(username.strip())
    
    if not username:
        raise ValidationError("Username is required")
    
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters")
    
    if len(username) > 30:
        raise ValidationError("Username too long (max 30 characters)")
    
    # Only alphanumeric and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Username can only contain letters, numbers, and underscores")
    
    return username

def validate_password(password: str) -> str:
    """
    Validate password strength
    - At least 8 characters
    - Contains letter and number
    """
    if not password:
        raise ValidationError("Password is required")
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    
    if len(password) > 128:
        raise ValidationError("Password too long (max 128 characters)")
    
    # Must contain at least one letter and one number
    if not re.search(r'[a-zA-Z]', password):
        raise ValidationError("Password must contain at least one letter")
    
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number")
    
    return password

def validate_string(text: str, field_name: str, min_len: int = 1, max_len: int = 1000, allow_empty: bool = False) -> str:
    """
    Generic string validation
    """
    if not text and not allow_empty:
        raise ValidationError(f"{field_name} is required")
    
    if not text:
        return ""
    
    text = sanitize_html(text.strip())
    
    if len(text) < min_len:
        raise ValidationError(f"{field_name} must be at least {min_len} characters")
    
    if len(text) > max_len:
        raise ValidationError(f"{field_name} too long (max {max_len} characters)")
    
    return text

def validate_post_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate post creation data
    """
    validated = {}
    
    # Post type
    post_type = data.get('post_type', '').lower()
    if post_type not in ['lost', 'found']:
        raise ValidationError("Post type must be 'lost' or 'found'")
    validated['post_type'] = post_type
    
    # Item name
    validated['item_name'] = validate_string(data.get('item_name', ''), 'Item name', 2, 100)
    
    # Location
    validated['location'] = validate_string(data.get('location', ''), 'Location', 2, 200)
    
    # Description (optional)
    validated['description'] = validate_string(data.get('description', ''), 'Description', 0, 2000, allow_empty=True)
    
    # Place (optional)
    validated['place'] = validate_string(data.get('place', ''), 'Place', 0, 200, allow_empty=True)
    
    # Time (optional)
    validated['time'] = validate_string(data.get('time', ''), 'Time', 0, 100, allow_empty=True)
    
    return validated

def validate_message_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate message data
    """
    validated = {}
    
    # Recipient
    validated['to_user'] = validate_username(data.get('to_user', ''))
    
    # Message content
    validated['message'] = validate_string(data.get('message', ''), 'Message', 1, 5000)
    
    return validated
