# Security Guidelines for AnomaaH Delivery Platform

## 🔐 Security Overview

This document outlines security considerations and best practices for deploying and operating the AnomaaH delivery platform.

---

## Critical Security Checklist

### Before Production Deployment

- [ ] **Change all default credentials**
  - PostgreSQL password
  - JWT SECRET_KEY
  - API keys
  - Admin passwords

- [ ] **Environment Variables**
  - Never commit `.env` to version control
  - Use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
  - Rotate secrets regularly (every 90 days minimum)

- [ ] **API Security**
  - Disable `/docs` and `/redoc` endpoints in production
  - Enable HTTPS/TLS for all services
  - Implement API key authentication for service-to-service calls
  - Add request signing for webhooks

- [ ] **Database Security**
  - Enable SSL/TLS for PostgreSQL connections
  - Implement row-level security for multi-tenancy
  - Regular automated backups
  - Encrypt backups at rest

- [ ] **Rate Limiting**
  - Use Redis-backed distributed rate limiting
  - Implement per-user rate limits
  - Add progressive backoff for failed authentication attempts

- [ ] **Input Validation**
  - Validate all user inputs
  - Sanitize HTML/SQL/script inputs
  - Validate file uploads (size, type, content)
  - Use parameterized queries (SQLAlchemy ORM does this)

---

## Ghana-Specific Security Requirements

### 1. Data Localization
- **Requirement**: Ghana's data protection laws require customer data to be stored within Ghana
- **Implementation**: 
  - Host database servers in Ghana data centers
  - Use Ghana-based cloud providers or Ghana regions (AWS Africa, Azure South Africa)
  - Implement data residency checks

### 2. Payment Security
- **Mobile Money**: 
  - Implement PCI DSS compliance for card transactions
  - Use Hubtel's secure payment gateway
  - Never store card details or mobile money PINs
  - Log all payment transactions with audit trail

### 3. Phone Number Validation
- **Ghana Phone Format**: +233 XX XXX XXXX
- **Validation**: 
  ```python
  import re
  def validate_ghana_phone(phone: str) -> bool:
      # Accepts: +233XXXXXXXXX or 0XXXXXXXXX
      pattern = r'^(\+233|0)[2-5][0-9]{8}$'
      return bool(re.match(pattern, phone))
  ```

### 4. SMS Security
- Validate SMS sender ID with National Communications Authority (NCA)
- Implement SMS rate limiting to prevent abuse
- Use encrypted channels for OTP transmission

---

## Security Best Practices

### Authentication & Authorization

#### 1. Password Security
```python
# Current Implementation (GOOD)
- bcrypt with salt (cost factor: 12)
- Minimum 8 characters for passwords
- JWT tokens with expiration

# Improvements Needed
- Add password complexity requirements
- Implement account lockout after 5 failed attempts
- Add 2FA/MFA for admin accounts
- Use biometric authentication for mobile apps
```

#### 2. JWT Token Security
```python
# Current
SECRET_KEY = os.getenv("SECRET_KEY", "demo-key")  # INSECURE DEFAULT

# Recommended
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "demo-key":
    raise ValueError("SECRET_KEY must be set in production")

# Token Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Short-lived
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"
```

#### 3. Session Management
- Implement session timeout (30 minutes)
- Invalidate tokens on logout
- Track active sessions per user
- Allow users to view/revoke active sessions

### API Security

#### 1. CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

# Strict CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Never use "*" in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)
```

#### 2. Security Headers
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS Redirect
app.add_middleware(HTTPSRedirectMiddleware)

# Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

# Custom Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

#### 3. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Per-endpoint limits
@app.post("/auth/login")
@limiter.limit("5/minute")  # Strict for auth
async def login(request: Request):
    pass

@app.get("/public/tracking")
@limiter.limit("20/minute")  # Relaxed for public
async def track(request: Request):
    pass
```

### Database Security

#### 1. Connection Security
```python
# .env
DATABASE_URL=postgresql://user:password@host:5432/db?sslmode=require

# Additional PostgreSQL security
- Enable SSL/TLS: sslmode=require
- Use connection pooling: max_connections=20
- Enable query logging for auditing
- Regular security updates
```

#### 2. SQL Injection Prevention
```python
# GOOD (SQLAlchemy ORM)
user = session.query(User).filter(User.email == email).first()

# BAD (Never do this)
query = f"SELECT * FROM users WHERE email = '{email}'"  # VULNERABLE!
```

#### 3. Multi-Tenant Data Isolation
```python
# Implement Row-Level Security (RLS) in PostgreSQL
"""
CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.tenant_id')::integer);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
"""

# Set tenant context in session
session.execute(text("SET app.tenant_id = :tenant_id"), {"tenant_id": tenant_id})
```

### Payment Security

#### 1. Webhook Verification
```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# Always verify webhooks
@app.post("/webhooks/payment")
async def payment_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Hubtel-Signature")
    
    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook
```

#### 2. Payment Data Handling
- Never log full payment details
- Mask sensitive data in logs (card numbers, CVV, etc.)
- Use tokenization for stored payment methods
- Implement PCI DSS compliance checklist

### Mobile App Security

#### 1. API Key Storage
```kotlin
// Never hardcode API keys
// Use Android Keystore or encrypted SharedPreferences

// Build config (obfuscated)
buildConfigField("String", "API_KEY", "\"${System.getenv("API_KEY")}\"")
```

#### 2. Certificate Pinning
```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("yourdomain.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

#### 3. Data Encryption
- Encrypt local SQLite database
- Use Android Keystore for sensitive data
- Implement biometric authentication
- Add root/jailbreak detection

---

## Security Monitoring

### 1. Logging
```python
import logging
import json

# Structured logging
logger = logging.getLogger(__name__)

def log_security_event(event_type: str, details: dict):
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "details": details,
        "severity": "security"
    }
    logger.warning(json.dumps(log_data))

# Log security events
log_security_event("failed_login", {
    "user_email": email,
    "ip_address": request.client.host,
    "attempt_count": 3
})
```

### 2. Alerting
- Failed login attempts (>5 in 5 minutes)
- Unusual payment patterns
- Rate limit violations
- Database connection failures
- Service downtime

### 3. Audit Trail
- Log all sensitive operations:
  - User authentication
  - Payment transactions
  - Order modifications
  - Admin actions
  - Data exports

---

## Incident Response

### 1. Security Breach Protocol
1. **Immediate**: Isolate affected systems
2. **Within 1 hour**: Notify security team
3. **Within 24 hours**: Notify affected users (GDPR compliance)
4. **Within 72 hours**: Full incident report

### 2. Data Breach Checklist
- [ ] Identify breach scope
- [ ] Contain the breach
- [ ] Preserve evidence
- [ ] Notify authorities (Data Protection Commission in Ghana)
- [ ] Notify affected users
- [ ] Implement fixes
- [ ] Post-mortem analysis

---

## Compliance Requirements

### Ghana Specific
1. **National Communications Authority (NCA)**
   - SMS sender ID registration
   - Telecom service compliance

2. **Data Protection Commission**
   - User consent for data collection
   - Right to data deletion
   - Data breach notification

3. **Ghana Revenue Authority (GRA)**
   - VAT tracking and reporting
   - Income tax withholding

### International
1. **PCI DSS** (if processing card payments)
2. **GDPR** (if serving EU customers)
3. **WCAG 2.1** (accessibility)

---

## Security Testing

### Regular Security Audits
- [ ] Quarterly penetration testing
- [ ] Monthly dependency vulnerability scans
- [ ] Weekly security patch updates
- [ ] Daily backup verification

### Tools
```bash
# Dependency vulnerability scanning
pip install safety
safety check

# Static code analysis
pip install bandit
bandit -r services/

# Secret scanning
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

---

## Contact

For security issues, contact:
- **Email**: security@anomaah.gh
- **Emergency**: [Phone number]
- **PGP Key**: [Public key for encrypted communication]

**Report vulnerabilities responsibly. Do not disclose publicly until patched.**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-24 | Initial security guidelines |

---

**Last Updated**: 2026-02-24  
**Next Review**: 2026-05-24 (quarterly)
