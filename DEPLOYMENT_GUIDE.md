# Production Deployment Guide - AnomaaH Delivery Platform

## 🚀 Overview

This guide covers deploying the AnomaaH delivery platform to production for Ghanaian businesses.

**Target Audience**: DevOps engineers, System administrators  
**Prerequisites**: Docker, PostgreSQL, Domain name, SSL certificates

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Service Deployment](#service-deployment)
6. [Ghana-Specific Configuration](#ghana-specific-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### ✅ Security
- [ ] Generated strong SECRET_KEY (min 32 characters)
- [ ] Changed PostgreSQL default password
- [ ] Obtained SSL/TLS certificates (Let's Encrypt recommended)
- [ ] Configured firewall rules (allow only necessary ports)
- [ ] Disabled API documentation endpoints (`/docs`, `/redoc`)
- [ ] Set up rate limiting with Redis
- [ ] Implemented database backups
- [ ] Reviewed SECURITY.md guidelines

### ✅ External Services
- [ ] Google Maps API key obtained and quota set
- [ ] Hubtel account created (mobile money & SMS)
  - Client ID and Secret
  - SMS Sender ID registered with NCA Ghana
- [ ] Payment provider configured (Hubtel/Paystack/Flutterwave)
- [ ] Domain name registered and DNS configured
- [ ] Email service configured (SMTP or SendGrid)

### ✅ Infrastructure
- [ ] Server(s) provisioned (min 4GB RAM, 2 CPUs)
- [ ] PostgreSQL database server (separate or managed service)
- [ ] Redis server (for caching and rate limiting)
- [ ] CDN configured (optional, for static assets)
- [ ] Load balancer configured (if multi-server)
- [ ] Monitoring tools set up (Prometheus, Grafana, or cloud-native)

### ✅ Code & Configuration
- [ ] All services tested locally
- [ ] Environment variables documented
- [ ] Database migrations created
- [ ] Health check endpoints verified
- [ ] Error handling tested
- [ ] Rate limiting tested

---

## Infrastructure Requirements

### Minimum Production Setup

#### Option 1: Single Server (Small Business)
**Specs**: 4GB RAM, 2 CPUs, 50GB SSD  
**OS**: Ubuntu 22.04 LTS  
**Cost**: ~$20-40/month (Linode, DigitalOcean, AWS Lightsail)

```
┌─────────────────────────────────────┐
│         Load Balancer (Nginx)        │
│            :80, :443                 │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│    Docker Compose (All Services)     │
│  - API Gateway                       │
│  - Auth Service                      │
│  - Booking Service                   │
│  - Order Service                     │
│  - Payment Service                   │
│  - Tracking Service                  │
│  - Notification Service              │
│  - Assignment Service                │
│  - Review Service                    │
│  - Rider Status Service              │
│  - Admin UI                          │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│       PostgreSQL + Redis             │
└─────────────────────────────────────┘
```

#### Option 2: Multi-Server (Enterprise)
**Load Balancer**: 2GB RAM  
**App Servers (x2)**: 4GB RAM each  
**Database**: 8GB RAM (managed PostgreSQL recommended)  
**Cost**: ~$100-200/month

```
                    Internet
                       │
              ┌────────▼────────┐
              │  Load Balancer  │
              │   (DigitalOcean │
              │   Load Balancer)│
              └────┬──────┬─────┘
                   │      │
         ┌─────────▼──┐ ┌─▼─────────┐
         │ App Server1│ │App Server2│
         │  (Docker)  │ │ (Docker)  │
         └─────┬──────┘ └──┬────────┘
               │            │
          ┌────▼────────────▼─────┐
          │ Managed PostgreSQL    │
          │ (DigitalOcean/AWS RDS)│
          └──────────────────────┘
```

### Cloud Provider Recommendations for Ghana

1. **AWS (Recommended)**
   - Region: `af-south-1` (Cape Town, South Africa - closest to Ghana)
   - Services: EC2, RDS PostgreSQL, ElastiCache Redis
   - CDN: CloudFront
   - Pros: Reliable, scalable, compliance-ready
   - Cons: Higher cost

2. **DigitalOcean (Good for SMEs)**
   - Region: `ams3` (Amsterdam) or `lon1` (London)
   - Services: Droplets, Managed PostgreSQL, Spaces CDN
   - Pros: Simple, affordable, good documentation
   - Cons: No Ghana-specific region

3. **Linode**
   - Region: `eu-west` (London)
   - Pros: Affordable, good support
   - Cons: Limited managed services

4. **Local Ghana Options**
   - Consider Ghana-based hosting for data residency
   - Check with Ghana Data Center providers

---

## Environment Configuration

### 1. Generate Production Secrets

```bash
# Generate SECRET_KEY (32+ characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate strong PostgreSQL password
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 2. Create Production .env File

**⚠️ NEVER commit this file to version control!**

```bash
# Copy template
cp .env.example .env.production

# Edit with secure values
nano .env.production
```

**Sample `.env.production`:**

```bash
# ==========================================
# DATABASE (CRITICAL - CHANGE DEFAULTS!)
# ==========================================
POSTGRES_HOST=your-db-host.com
POSTGRES_PORT=5432
POSTGRES_USER=anomaah_prod
POSTGRES_PASSWORD=<GENERATED_STRONG_PASSWORD>
POSTGRES_DB=delivery_production
DATABASE_URL=postgresql://anomaah_prod:<PASSWORD>@your-db-host.com:5432/delivery_production?sslmode=require

# ==========================================
# SECURITY (CRITICAL - NEVER USE DEMO VALUES!)
# ==========================================
SECRET_KEY=<GENERATED_SECRET_KEY_32_CHARS>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==========================================
# SERVICE URLS (Internal Docker Network)
# ==========================================
API_GATEWAY_URL=http://api-gateway:8000
AUTH_SERVICE_URL=http://auth-service:8600
BOOKING_SERVICE_URL=http://booking-service:8100
ORDER_SERVICE_URL=http://order-service:8500
PAYMENT_SERVICE_URL=http://payment-service:8200
TRACKING_SERVICE_URL=http://tracking-service:8300
NOTIFICATION_SERVICE_URL=http://notification-service:8400
ASSIGNMENT_SERVICE_URL=http://assignment-service:8900
REVIEW_SERVICE_URL=http://review-service:8700
RIDER_STATUS_SERVICE_URL=http://rider-status-service:8800

# ==========================================
# GOOGLE MAPS (Required)
# ==========================================
GOOGLE_MAPS_API_KEY=<YOUR_GOOGLE_MAPS_API_KEY>
GOOGLE_MAPS_REGION=GH  # Ghana

# ==========================================
# HUBTEL (Payment & SMS - Ghana)
# ==========================================
HUBTEL_CLIENT_ID=<YOUR_HUBTEL_CLIENT_ID>
HUBTEL_CLIENT_SECRET=<YOUR_HUBTEL_CLIENT_SECRET>
HUBTEL_MERCHANT_ID=<YOUR_HUBTEL_MERCHANT_ID>
HUBTEL_API_BASE=https://api.hubtel.com
HUBTEL_SMS_SENDER=ANOMAAH  # Register with NCA
HUBTEL_SMS_API=https://api.hubtel.com/v1/messages/sms

# ==========================================
# PAYMENT PROVIDERS (Optional Additional)
# ==========================================
# Flutterwave (Alternative)
FLUTTERWAVE_PUBLIC_KEY=<YOUR_FLW_PUBLIC_KEY>
FLUTTERWAVE_SECRET_KEY=<YOUR_FLW_SECRET_KEY>
FLUTTERWAVE_ENCRYPTION_KEY=<YOUR_FLW_ENCRYPTION_KEY>

# Paystack (Alternative)
PAYSTACK_PUBLIC_KEY=<YOUR_PAYSTACK_PUBLIC_KEY>
PAYSTACK_SECRET_KEY=<YOUR_PAYSTACK_SECRET_KEY>

# ==========================================
# NOTIFICATION SERVICES
# ==========================================
# SMS (Primary: Hubtel, Fallback: Twilio)
TWILIO_ACCOUNT_SID=<YOUR_TWILIO_SID>
TWILIO_AUTH_TOKEN=<YOUR_TWILIO_TOKEN>
TWILIO_PHONE_NUMBER=<YOUR_TWILIO_NUMBER>

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@anomaah.gh
SMTP_PASSWORD=<APP_SPECIFIC_PASSWORD>
SMTP_FROM=AnomaaH Delivery <noreply@anomaah.gh>

# ==========================================
# REDIS (Rate Limiting & Caching)
# ==========================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<REDIS_PASSWORD>
REDIS_DB=0
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# ==========================================
# APPLICATION SETTINGS
# ==========================================
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Domain
DOMAIN=anomaah.gh
API_BASE_URL=https://api.anomaah.gh
FRONTEND_URL=https://anomaah.gh
ADMIN_URL=https://admin.anomaah.gh

# Pricing (Ghana Cedis - GHS)
BASE_DELIVERY_FEE_GHS=5.00
PER_KM_RATE_GHS=1.50
PLATFORM_FEE_PERCENT=10
CURRENCY=GHS

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE_AUTH=5
RATE_LIMIT_PER_MINUTE_PUBLIC=20
RATE_LIMIT_PER_MINUTE_API=100

# ==========================================
# MONITORING (Optional but Recommended)
# ==========================================
SENTRY_DSN=<YOUR_SENTRY_DSN>
PROMETHEUS_ENABLED=true

# ==========================================
# GHANA-SPECIFIC SETTINGS
# ==========================================
DEFAULT_COUNTRY=GH
DEFAULT_CURRENCY=GHS
DEFAULT_TIMEZONE=Africa/Accra
PHONE_COUNTRY_CODE=+233
SUPPORTED_LANGUAGES=en,tw,ga  # English, Twi, Ga

# Service Hours (Ghana Time - GMT)
SERVICE_START_HOUR=6  # 6 AM
SERVICE_END_HOUR=22   # 10 PM
```

### 3. Validate Environment Variables

Create a validation script:

```python
# scripts/validate_env.py
import os
import sys

REQUIRED_VARS = [
    "DATABASE_URL",
    "SECRET_KEY",
    "GOOGLE_MAPS_API_KEY",
    "HUBTEL_CLIENT_ID",
    "HUBTEL_CLIENT_SECRET",
]

def validate_env():
    missing = []
    insecure = []
    
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        elif var == "SECRET_KEY" and len(value) < 32:
            insecure.append(f"{var} (too short: {len(value)} chars)")
        elif "demo" in value.lower() or "example" in value.lower():
            insecure.append(f"{var} (contains demo/example)")
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    
    if insecure:
        print(f"⚠️  Insecure environment variables: {', '.join(insecure)}")
        sys.exit(1)
    
    print("✅ All environment variables validated!")

if __name__ == "__main__":
    validate_env()
```

Run validation:
```bash
python3 scripts/validate_env.py
```

---

## Database Setup

### 1. Create Database (Managed Service)

**DigitalOcean Managed PostgreSQL:**
```bash
# Create database cluster
doctl databases create anomaah-prod \
  --engine pg \
  --region lon1 \
  --size db-s-2vcpu-4gb \
  --num-nodes 1

# Create database
doctl databases db create <cluster-id> delivery_production

# Get connection string
doctl databases connection <cluster-id>
```

**AWS RDS:**
```bash
aws rds create-db-instance \
  --db-instance-identifier anomaah-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.3 \
  --master-username anomaah_admin \
  --master-user-password <STRONG_PASSWORD> \
  --allocated-storage 50 \
  --storage-type gp3 \
  --storage-encrypted \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --multi-az \
  --publicly-accessible false
```

### 2. Initialize Database Schema

```bash
# SSH into app server
ssh user@your-server.com

# Navigate to project
cd /opt/anomaah

# Run migrations (when implemented)
# python3 alembic_config.py upgrade head

# Or initialize with SQL script
docker-compose exec postgres psql -U anomaah_prod -d delivery_production -f /sql/init.sql
```

### 3. Create Superadmin User

```bash
# Run seed script
docker-compose exec api-gateway python3 /app/create_superadmin.py
```

---

## Service Deployment

### Option 1: Docker Compose (Single Server)

1. **Install Docker & Docker Compose**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

2. **Clone Repository**

```bash
cd /opt
sudo git clone https://github.com/Cedcast/AnomaaH-.git anomaah
cd anomaah
sudo chown -R $USER:$USER /opt/anomaah
```

3. **Configure Environment**

```bash
# Copy production env
cp .env.production .env

# Verify
cat .env | grep -i "secret"  # Should NOT see "demo"
```

4. **Update docker-compose.yml for Production**

Edit `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    restart: always  # Changed from unless-stopped
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "127.0.0.1:5432:5432"  # Bind to localhost only
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redisdata:/data
    networks:
      - backend

  # ... other services (api-gateway, auth-service, etc.)
  # Add restart: always to all services
  # Add networks: backend to all services

volumes:
  pgdata:
  redisdata:

networks:
  backend:
    driver: bridge
```

5. **Deploy Services**

```bash
# Build and start
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f api-gateway

# Test health
curl http://localhost:8000/health
```

6. **Configure Nginx Reverse Proxy**

```bash
# Install Nginx
sudo apt install nginx -y

# Create site configuration
sudo nano /etc/nginx/sites-available/anomaah
```

**Nginx Configuration:**

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name api.anomaah.gh anomaah.gh;
    
    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - API Gateway
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.anomaah.gh;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.anomaah.gh/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.anomaah.gh/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    # Logging
    access_log /var/log/nginx/anomaah-api-access.log;
    error_log /var/log/nginx/anomaah-api-error.log;
    
    # Proxy to API Gateway
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket support for tracking
    location /ws {
        proxy_pass http://127.0.0.1:8300;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# HTTPS - Admin UI
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name admin.anomaah.gh;
    
    ssl_certificate /etc/letsencrypt/live/admin.anomaah.gh/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.anomaah.gh/privkey.pem;
    
    # Same security headers as above
    
    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/anomaah /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

7. **Obtain SSL Certificate (Let's Encrypt)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d api.anomaah.gh -d admin.anomaah.gh

# Auto-renewal (cron job)
sudo crontbot -e
# Add: 0 0 * * * certbot renew --quiet
```

---

## Ghana-Specific Configuration

### 1. Register SMS Sender ID with NCA Ghana

**National Communications Authority (NCA) Requirements:**

1. Visit NCA Ghana office or apply online
2. Submit:
   - Company registration documents
   - Application letter
   - Proposed sender ID (e.g., "ANOMAAH", max 11 characters)
3. Pay registration fee
4. Wait for approval (7-14 days)
5. Configure approved sender ID in `.env`:

```bash
HUBTEL_SMS_SENDER=ANOMAAH  # Your approved sender ID
```

### 2. Configure Hubtel Payment Gateway

```bash
# Register at https://developers.hubtel.com
# Get credentials from dashboard
HUBTEL_CLIENT_ID=<from_dashboard>
HUBTEL_CLIENT_SECRET=<from_dashboard>
HUBTEL_MERCHANT_ID=<from_dashboard>

# Test mode vs Production
HUBTEL_ENVIRONMENT=production  # or 'sandbox' for testing
```

### 3. Set Ghana-Specific Defaults

```bash
# Time zone
TZ=Africa/Accra

# Phone validation
PHONE_COUNTRY_CODE=+233
PHONE_REGEX='^(\+233|0)[2-5][0-9]{8}$'

# Currency
CURRENCY=GHS
CURRENCY_SYMBOL=₵

# Regions for delivery
SUPPORTED_REGIONS=Accra,Kumasi,Takoradi,Tema,Cape Coast
```

---

## Monitoring & Logging

### 1. Application Logging

**Configure structured logging:**

```python
# shared/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "api-gateway",  # Change per service
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

### 2. Prometheus Metrics (Optional)

```python
# pip install prometheus-fastapi-instrumentator

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### 3. Health Monitoring

```bash
# Create monitoring script
cat > /opt/anomaah/scripts/health_check.sh << 'EOF'
#!/bin/bash

# Check all services
services=(
    "api-gateway:8000"
    "auth-service:8600"
    "booking-service:8100"
    "order-service:8500"
)

for service in "${services[@]}"; do
    name="${service%:*}"
    port="${service#*:}"
    
    if curl -f -s "http://localhost:${port}/health" > /dev/null; then
        echo "✅ ${name} - healthy"
    else
        echo "❌ ${name} - unhealthy"
        # Send alert
        curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
            -d "chat_id=<CHAT_ID>&text=Alert: ${name} is down!"
    fi
done
EOF

chmod +x /opt/anomaah/scripts/health_check.sh

# Add to cron (every 5 minutes)
crontab -e
# */5 * * * * /opt/anomaah/scripts/health_check.sh
```

---

## Backup & Recovery

### 1. Automated Database Backups

```bash
# Create backup script
cat > /opt/anomaah/scripts/backup_db.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/anomaah/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/anomaah_${DATE}.sql.gz"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Dump database
docker-compose exec -T postgres pg_dump -U anomaah_prod delivery_production | gzip > ${BACKUP_FILE}

# Upload to cloud storage (optional)
# aws s3 cp ${BACKUP_FILE} s3://anomaah-backups/

# Keep only last 7 days
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}"
EOF

chmod +x /opt/anomaah/scripts/backup_db.sh

# Schedule daily backups (3 AM)
crontab -e
# 0 3 * * * /opt/anomaah/scripts/backup_db.sh
```

### 2. Restore from Backup

```bash
# Stop services
docker-compose down

# Restore database
gunzip < /opt/anomaah/backups/anomaah_20260224_030000.sql.gz | \
    docker-compose exec -T postgres psql -U anomaah_prod delivery_production

# Restart services
docker-compose up -d
```

---

## Troubleshooting

### Common Issues

#### 1. Service won't start

```bash
# Check logs
docker-compose logs service-name

# Check environment
docker-compose exec service-name env | grep DATABASE

# Restart service
docker-compose restart service-name
```

#### 2. Database connection failed

```bash
# Test connection
docker-compose exec postgres psql -U anomaah_prod -d delivery_production -c "SELECT 1"

# Check DATABASE_URL format
echo $DATABASE_URL
```

#### 3. High memory usage

```bash
# Check Docker stats
docker stats

# Limit container memory in docker-compose.yml
services:
  api-gateway:
    mem_limit: 512m
```

#### 4. Slow API responses

```bash
# Check service health
curl http://localhost:8000/health

# Check database connections
docker-compose exec postgres psql -U anomaah_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Enable query logging
# In PostgreSQL: ALTER SYSTEM SET log_statement = 'all';
```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Run smoke tests
bash smoke_test.sh

# Check all endpoints
curl https://api.anomaah.gh/health
curl https://admin.anomaah.gh
```

### 2. Create First Company

```bash
# Use Admin UI at https://admin.anomaah.gh
# Or use API:
curl -X POST https://api.anomaah.gh/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.gh",
    "password": "SecurePassword123!",
    "role": "company_admin",
    "company_name": "My Delivery Company"
  }'
```

### 3. Monitor Logs

```bash
# Follow logs
docker-compose logs -f --tail=100

# Or use log aggregation (ELK, Datadog, etc.)
```

---

## Scaling

### Horizontal Scaling

1. **Set up load balancer** (DigitalOcean, AWS ALB)
2. **Create multiple app servers** (clone current setup)
3. **Use external PostgreSQL** (managed service)
4. **Use external Redis** (for shared state)
5. **Configure session affinity** (sticky sessions for WebSockets)

### Vertical Scaling

```bash
# Increase server resources
# Update docker-compose.yml resource limits
services:
  api-gateway:
    cpus: '2.0'
    mem_limit: 2g
```

---

## Support

For deployment issues:
- **Email**: devops@anomaah.gh
- **Slack**: #anomaah-deployments
- **Documentation**: https://docs.anomaah.gh

---

**Last Updated**: 2026-02-24  
**Version**: 1.0
