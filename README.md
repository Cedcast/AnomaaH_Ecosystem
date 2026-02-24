# AnomaaH Delivery Platform

> **Modern delivery management platform built for Ghanaian businesses and end users**

## 🚀 Overview

AnomaaH is a comprehensive multi-tenant delivery infrastructure SaaS platform designed specifically for the Ghanaian market. It provides a complete solution for businesses to manage deliveries with features tailored for Ghana's unique requirements.

### Key Features

✅ **Core Platform**
- **Simple 1-page booking** (no account creation required)
- **Phone number only** - customers book with just their phone number
- **OTP verification** - secure verification before booking confirmation
- Automatic rider assignment with intelligent 5-factor scoring
- Real-time order tracking with WebSocket support
- Multi-tenant architecture with strict isolation
- Mobile-responsive admin dashboard

✅ **Payment Integration**
- **Hubtel payment gateway only** (mobile money support)
- Support for MTN MoMo, Vodafone Cash, AirtelTigo Money
- Webhook verification with HMAC-SHA256

✅ **Ghana-Specific Features**
- Ghana phone number validation (+233 format)
- **English-only SMS notifications**
- Mobile money provider auto-detection
- Surge pricing for peak traffic hours (7-9 AM, 4-7 PM)
- Support for Ghana's major cities and regions

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15
- Google Maps API key
- Hubtel account (for payments & SMS)

### Local Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/Cedcast/AnomaaH-.git
cd AnomaaH-
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

**Important**: Update SECRET_KEY, POSTGRES_PASSWORD, and API keys

3. **Start the services**

```bash
docker-compose up --build
```

4. **Access the platform**

- API Gateway: http://localhost:8000
- Admin Dashboard: http://localhost:9000
- API Documentation: http://localhost:8000/docs

## 🏗 Architecture

11 microservices including API Gateway, Auth, Booking, Order, Payment, Tracking, Notification, Assignment, Review, Rider Status, and Admin UI services.

**Technology Stack**: Python 3.11, FastAPI, PostgreSQL 15, Redis, Docker

For detailed architecture, see [ARCHITECTURE_DELIVERY_RIDER_SAAS.md](ARCHITECTURE_DELIVERY_RIDER_SAAS.md)

## 🇬🇭 Ghana-Specific Configuration

```bash
# In .env file
BASE_DELIVERY_FEE_GHS=5.00
PER_KM_RATE_GHS=1.50
CURRENCY=GHS
PHONE_COUNTRY_CODE=+233
DEFAULT_TIMEZONE=Africa/Accra
```

**Surge Pricing**:
- Night delivery: 1.5x
- Peak hours: 1.3x

## 🔐 Security

⚠️ **Before production deployment, review**:
- [SECURITY.md](SECURITY.md) - Complete security guidelines
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment

### Quick Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Generate secure SECRET_KEY (32+ characters)
- [ ] Disable API documentation in production
- [ ] Configure HTTPS/TLS with valid certificates
- [ ] Set up rate limiting
- [ ] Review security guidelines

## 📚 Documentation

- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Complete documentation index
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
- [SECURITY.md](SECURITY.md) - Security best practices
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference guide

## 📞 Support

- **Email**: support@anomaah.gh
- **Issues**: [GitHub Issues](https://github.com/Cedcast/AnomaaH-/issues)

## 📄 License

This project is licensed under the MIT License.

---

**Made with ❤️ in Ghana**
