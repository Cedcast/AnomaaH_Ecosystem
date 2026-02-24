import os
import logging
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from shared.tenant import TenantMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Hide API docs in production for security
if ENVIRONMENT == "production":
    app = FastAPI(
        title="AnomaaH API Gateway",
        docs_url=None,  # Disable /docs
        redoc_url=None,  # Disable /redoc
        openapi_url=None  # Disable /openapi.json
    )
else:
    app = FastAPI(
        title="AnomaaH API Gateway (Development)",
        version="1.0.0",
        description="API Gateway for AnomaaH Delivery Platform"
    )

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
if ENVIRONMENT != "production" and "*" not in ALLOWED_ORIGINS:
    # Allow all origins in development for easier testing
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"]
)

# Service URLs
BOOKING_URL = os.environ.get("BOOKING_SERVICE_URL", "http://localhost:8100")
AUTH_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8600")
ORDER_URL = os.environ.get("ORDER_SERVICE_URL", "http://localhost:8500")
RIDER_STATUS_URL = os.environ.get("RIDER_STATUS_SERVICE_URL", "http://localhost:8800")

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Only add HSTS in production with HTTPS
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    """Handle tenant identification and authorization."""
    # Public endpoints don't require tenant authentication
    # Note: /docs and /redoc are disabled in production
    public_paths = {"/", "/health", "/book"}
    
    # In development, allow docs
    if ENVIRONMENT != "production":
        public_paths.update({"/docs", "/redoc", "/openapi.json"})
    
    # Add common static paths
    public_paths.update({"/favicon.ico", "/robots.txt"})
    
    if request.url.path in public_paths or request.url.path.startswith("/static"):
        # mark as no tenant (public)
        request.state.tenant_id = None
        request.state.is_super_admin = False
    else:
        try:
            await TenantMiddleware.attach_tenant(request)
        except Exception as e:
            logger.error(f"Tenant middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )
    
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions gracefully."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    if ENVIRONMENT == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal error occurred. Please try again later."}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)}
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    response = {
        "message": "Welcome to AnomaaH Delivery API",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "status": "operational"
    }
    
    # Only show docs link in development
    if ENVIRONMENT != "production":
        response["docs_url"] = "/docs"
        response["health_url"] = "/health"
    
    return response


from datetime import datetime

@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }


@app.post("/book")
async def book(request: Request):
    """
    Public booking endpoint for customers.
    
    This endpoint allows customers to create delivery bookings
    without authentication (for easy access).
    """
    try:
        payload = await request.json()
        
        # Log booking attempt (without sensitive data)
        logger.info(f"Booking request from IP: {request.client.host}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{BOOKING_URL}/book", json=payload)
            r.raise_for_status()
            return r.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Booking service error: {e}")
        return JSONResponse(
            status_code=e.response.status_code,
            content={"detail": "Booking failed. Please check your details and try again."}
        )
    except httpx.RequestError as e:
        logger.error(f"Booking service connection error: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Booking service is temporarily unavailable. Please try again later."}
        )
    except Exception as e:
        logger.error(f"Unexpected booking error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An error occurred while processing your booking."}
        )


# ============= Rider Status Routes =============

@app.post("/status/update")
async def update_rider_status(request: Request):
    """
    Update rider online/offline status.
    Proxies to rider status service.
    """
    try:
        body = await request.json()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{RIDER_STATUS_URL}/status/update",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            r.raise_for_status()
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except httpx.HTTPStatusError as e:
        logger.error(f"Status update error: {e}")
        return JSONResponse(
            status_code=e.response.status_code,
            content={"detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Status update failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Status service unavailable"}
        )


@app.get("/status/{rider_id}")
async def get_rider_status(rider_id: str):
    """
    Get status of a single rider.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{RIDER_STATUS_URL}/status/{rider_id}")
            r.raise_for_status()
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except httpx.HTTPStatusError as e:
        logger.error(f"Get status error: {e}")
        return JSONResponse(
            status_code=e.response.status_code,
            content={"detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Get status failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Status service unavailable"}
        )


@app.get("/status/company/{company_id}")
async def get_company_rider_statuses(company_id: str):
    """
    Get all rider statuses for a company.
    Used by company dashboard to display rider fleet status.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{RIDER_STATUS_URL}/status/company/{company_id}")
            r.raise_for_status()
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except httpx.HTTPStatusError as e:
        logger.error(f"Get company statuses error: {e}")
        return JSONResponse(
            status_code=e.response.status_code,
            content={"detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Get company statuses failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Status service unavailable"}
        )


@app.get("/earnings/{rider_id}")
async def get_rider_earnings(rider_id: str, period: str = "monthly"):
    """
    Get rider earnings from order service.
    Proxies request to order service which calculates earnings from delivered orders.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{ORDER_URL}/earnings/{rider_id}",
                params={"period": period}
            )
            r.raise_for_status()
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except httpx.HTTPStatusError as e:
        logger.error(f"Get earnings error: {e}")
        return JSONResponse(
            status_code=e.response.status_code,
            content={"detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Get earnings failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Order service unavailable"}
        )


# Startup validation
@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    logger.info(f"Starting API Gateway in {ENVIRONMENT} mode")
    
    # Security check
    if ENVIRONMENT == "production":
        secret_key = os.getenv("SECRET_KEY", "")
        if not secret_key or "demo" in secret_key.lower():
            logger.error("⚠️  WARNING: Insecure SECRET_KEY detected in production!")
        
        db_url = os.getenv("DATABASE_URL", "")
        if "postgres:postgres@" in db_url:
            logger.error("⚠️  WARNING: Default database credentials detected!")
    
    logger.info("API Gateway startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("API Gateway shutting down")
