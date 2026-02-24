"""
Security utilities for AnomaaH Delivery Platform

Provides security functions including input validation, sanitization,
rate limiting, and authentication helpers.
"""

import os
import re
import hmac
import hashlib
import secrets
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Security constants
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
SENSITIVE_FIELDS = {'password', 'token', 'secret', 'key', 'pin', 'cvv', 'card'}


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength according to security requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter  
    - At least one number
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation result and feedback
        
    Example:
        >>> validate_password_strength("Weak123")
        {
            'valid': False,
            'score': 2,
            'feedback': ['Password must contain a special character']
        }
    """
    result = {
        'valid': False,
        'score': 0,
        'feedback': []
    }
    
    if not password:
        result['feedback'].append('Password is required')
        return result
    
    if len(password) < MIN_PASSWORD_LENGTH:
        result['feedback'].append(f'Password must be at least {MIN_PASSWORD_LENGTH} characters')
    elif len(password) > MAX_PASSWORD_LENGTH:
        result['feedback'].append(f'Password must be less than {MAX_PASSWORD_LENGTH} characters')
    else:
        result['score'] += 1
    
    # Check for uppercase
    if not re.search(r'[A-Z]', password):
        result['feedback'].append('Password must contain at least one uppercase letter')
    else:
        result['score'] += 1
    
    # Check for lowercase
    if not re.search(r'[a-z]', password):
        result['feedback'].append('Password must contain at least one lowercase letter')
    else:
        result['score'] += 1
    
    # Check for digit
    if not re.search(r'\d', password):
        result['feedback'].append('Password must contain at least one number')
    else:
        result['score'] += 1
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result['feedback'].append('Password must contain at least one special character')
    else:
        result['score'] += 1
    
    # Check for common patterns
    common_patterns = [
        'password', '12345', 'qwerty', 'abc123', 'admin', 'letmein'
    ]
    if any(pattern in password.lower() for pattern in common_patterns):
        result['feedback'].append('Password contains common patterns')
    else:
        result['score'] += 1
    
    # Valid if score is high enough
    result['valid'] = result['score'] >= 5 and len(result['feedback']) == 0
    
    return result


def sanitize_input(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ''
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    value = value.strip()
    
    # Limit length
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    # Remove HTML tags (basic)
    value = re.sub(r'<[^>]*>', '', value)
    
    # Remove SQL injection patterns (basic)
    sql_patterns = [
        r'(\bSELECT\b.*\bFROM\b)',
        r'(\bINSERT\b.*\bINTO\b)',
        r'(\bUPDATE\b.*\bSET\b)',
        r'(\bDELETE\b.*\bFROM\b)',
        r'(\bDROP\b.*\bTABLE\b)',
        r'(--)',
        r'(;.*--)',
    ]
    for pattern in sql_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f'Potential SQL injection attempt detected: {value[:50]}')
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
    
    return value


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    if not email:
        return False
    
    # RFC 5322 simplified pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False
    
    # Additional checks
    if len(email) > 254:  # RFC max length
        return False
    
    local, domain = email.rsplit('@', 1)
    if len(local) > 64:  # RFC max local part
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and malicious filenames.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Safe filename
    """
    if not filename:
        return 'unnamed_file'
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250] + ext
    
    # If empty after sanitization, use default
    if not filename:
        filename = 'unnamed_file'
    
    return filename


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive data in dictionary for logging.
    
    Args:
        data: Dictionary potentially containing sensitive data
        
    Returns:
        Dictionary with sensitive fields masked
    """
    if not data:
        return {}
    
    masked = {}
    
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if field is sensitive
        is_sensitive = any(field in key_lower for field in SENSITIVE_FIELDS)
        
        if is_sensitive and value:
            # Mask value
            if isinstance(value, str):
                if len(value) <= 4:
                    masked[key] = '****'
                else:
                    # Show first 2 and last 2 characters
                    masked[key] = value[:2] + '****' + value[-2:]
            else:
                masked[key] = '****'
        elif isinstance(value, dict):
            # Recursively mask nested dictionaries
            masked[key] = mask_sensitive_data(value)
        else:
            masked[key] = value
    
    return masked


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token.
    
    Args:
        length: Token length in bytes
        
    Returns:
        URL-safe token string
    """
    return secrets.token_urlsafe(length)


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    Verify webhook signature using HMAC.
    
    Args:
        payload: Request body as bytes
        signature: Signature from webhook header
        secret: Webhook secret key
        algorithm: Hash algorithm (sha256, sha512)
        
    Returns:
        True if signature is valid
    """
    if not payload or not signature or not secret:
        return False
    
    try:
        # Create expected signature
        if algorithm == 'sha256':
            expected = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
        elif algorithm == 'sha512':
            expected = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha512
            ).hexdigest()
        else:
            raise ValueError(f'Unsupported algorithm: {algorithm}')
        
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected, signature)
    
    except Exception as e:
        logger.error(f'Webhook signature verification error: {e}')
        return False


def check_environment_security() -> Dict[str, Any]:
    """
    Check environment variables for security issues.
    
    Returns:
        Dictionary with security check results
    """
    issues = []
    warnings = []
    
    # Check SECRET_KEY
    secret_key = os.getenv('SECRET_KEY', '')
    if not secret_key:
        issues.append('SECRET_KEY is not set')
    elif secret_key in ['demo-secret-key-change-in-production', 'changeme', 'secret']:
        issues.append('SECRET_KEY is using default/demo value')
    elif len(secret_key) < 32:
        warnings.append(f'SECRET_KEY is short ({len(secret_key)} chars, recommended: 32+)')
    
    # Check DATABASE_URL
    db_url = os.getenv('DATABASE_URL', '')
    if 'postgres:postgres@' in db_url:
        issues.append('DATABASE_URL contains default PostgreSQL credentials')
    
    # Check DEBUG mode
    debug = os.getenv('DEBUG', 'false').lower()
    if debug == 'true':
        warnings.append('DEBUG mode is enabled (should be false in production)')
    
    # Check ENVIRONMENT
    environment = os.getenv('ENVIRONMENT', 'development')
    if environment != 'production':
        warnings.append(f'ENVIRONMENT is set to "{environment}" (should be "production" in prod)')
    
    return {
        'secure': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }


class RequestValidator:
    """Validate API request data."""
    
    @staticmethod
    def validate_pagination(page: int = 1, per_page: int = 20) -> Dict[str, int]:
        """
        Validate and normalize pagination parameters.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Normalized pagination parameters
        """
        page = max(1, int(page))
        per_page = max(1, min(100, int(per_page)))  # Cap at 100
        
        return {
            'page': page,
            'per_page': per_page,
            'offset': (page - 1) * per_page
        }
    
    @staticmethod
    def validate_order_id(order_id: str) -> bool:
        """
        Validate order ID format.
        
        Args:
            order_id: Order ID to validate
            
        Returns:
            True if valid
        """
        if not order_id:
            return False
        
        # Allow alphanumeric, hyphens, underscores (max 64 chars)
        pattern = r'^[a-zA-Z0-9_-]{1,64}$'
        return bool(re.match(pattern, order_id))
    
    @staticmethod
    def validate_coordinates(lat: float, lng: float) -> bool:
        """
        Validate GPS coordinates.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            True if valid coordinates
        """
        try:
            lat = float(lat)
            lng = float(lng)
            
            # Valid ranges
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lng <= 180):
                return False
            
            # Ghana bounds check (rough)
            # Ghana: Lat 4.5°N to 11°N, Lng 3.5°W to 1°E
            if not (4.5 <= lat <= 11.5):
                logger.warning(f'Coordinates outside Ghana: lat={lat}')
            if not (-3.5 <= lng <= 1.5):
                logger.warning(f'Coordinates outside Ghana: lng={lng}')
            
            return True
        
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_amount(amount: float, min_amount: float = 0.01, max_amount: float = 10000.0) -> bool:
        """
        Validate monetary amount.
        
        Args:
            amount: Amount to validate
            min_amount: Minimum allowed amount
            max_amount: Maximum allowed amount
            
        Returns:
            True if valid amount
        """
        try:
            amount = float(amount)
            
            if amount < min_amount:
                return False
            if amount > max_amount:
                return False
            
            # Check for reasonable decimal places (2 for GHS)
            if round(amount, 2) != amount:
                logger.warning(f'Amount has more than 2 decimal places: {amount}')
            
            return True
        
        except (ValueError, TypeError):
            return False


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter.
    
    Note: For production, use Redis-backed distributed rate limiting.
    """
    
    def __init__(self):
        self._requests: Dict[str, List[datetime]] = {}
    
    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if rate limit is exceeded.
        
        Args:
            key: Identifier (e.g., IP address, user ID)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if within limit
            
        Raises:
            RateLimitExceeded: If limit exceeded
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Get or create request list for this key
        if key not in self._requests:
            self._requests[key] = []
        
        # Remove old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self._requests[key]) >= max_requests:
            raise RateLimitExceeded(
                f'Rate limit exceeded: {max_requests} requests per {window_seconds}s'
            )
        
        # Add current request
        self._requests[key].append(now)
        
        return True
    
    def cleanup(self, max_age_seconds: int = 3600):
        """Remove old entries to prevent memory growth."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=max_age_seconds)
        
        keys_to_remove = []
        for key, requests in self._requests.items():
            # Remove old requests
            self._requests[key] = [
                req_time for req_time in requests
                if req_time > cutoff
            ]
            
            # If no recent requests, remove key
            if not self._requests[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._requests[key]


def validate_production_config() -> bool:
    """
    Validate that production configuration is secure.
    
    Returns:
        True if configuration is production-ready
    """
    check = check_environment_security()
    
    if not check['secure']:
        logger.error('❌ Security issues found:')
        for issue in check['issues']:
            logger.error(f'  - {issue}')
        return False
    
    if check['warnings']:
        logger.warning('⚠️  Security warnings:')
        for warning in check['warnings']:
            logger.warning(f'  - {warning}')
    
    logger.info('✅ Production configuration validated')
    return True


if __name__ == '__main__':
    # Demo usage
    print("=== Security Utilities Demo ===\n")
    
    # Password validation
    print("1. Password Strength:")
    passwords = ['weak', 'Weak123', 'Strong@Pass123']
    for pwd in passwords:
        result = validate_password_strength(pwd)
        print(f"  {pwd}: {result}")
    
    # Email validation
    print("\n2. Email Validation:")
    emails = ['test@example.com', 'invalid.email', 'user@anomaah.gh']
    for email in emails:
        valid = validate_email(email)
        print(f"  {email}: {'✅' if valid else '❌'}")
    
    # Sensitive data masking
    print("\n3. Data Masking:")
    data = {
        'user_id': '12345',
        'password': 'secret123',
        'card_number': '1234567890123456',
        'name': 'John Doe'
    }
    masked = mask_sensitive_data(data)
    print(f"  Original: {data}")
    print(f"  Masked: {masked}")
    
    # Environment security check
    print("\n4. Environment Security Check:")
    check = check_environment_security()
    print(f"  Secure: {check['secure']}")
    if check['issues']:
        print(f"  Issues: {check['issues']}")
    if check['warnings']:
        print(f"  Warnings: {check['warnings']}")
