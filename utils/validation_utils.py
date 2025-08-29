import secrets
import string
import re
from typing import Optional, Tuple, List

def generate_secure_api_key(length: int = 64) -> str:
    """
    Generate a secure random API key
    
    Args:
        length: Length of the API key (default: 64)
    
    Returns:
        Secure random API key string
    """
    if length < 32:
        raise ValueError("API key length must be at least 32 characters")
    
    # Use secrets module for cryptographically secure random generation
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_api_key_format(key: str) -> Tuple[bool, Optional[str]]:
    """
    Validate API key format
    
    Args:
        key: API key string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not key:
        return False, "API key is required"
    
    if len(key) < 32:
        return False, "API key must be at least 32 characters long"
    
    if len(key) > 128:
        return False, "API key must be no more than 128 characters long"
    
    # Check if key contains only valid characters
    key_pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(key_pattern, key):
        return False, "API key can only contain letters, numbers, hyphens, and underscores"
    
    return True, None

def sanitize_input(text: str, max_length: int = 100) -> str:
    """
    Sanitize user input text
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    return text
