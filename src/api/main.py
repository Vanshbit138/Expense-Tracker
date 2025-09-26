"""
Main FastAPI application module with comprehensive middleware, error handling, and monitoring.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import analytics, auth, categories, expenses
from src.core.config import settings
from src.core.database import create_tables
from src.core.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing."""
    start_time = time.time()

    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
    )

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
    )

    return response


async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


async def add_request_id_header(request: Request, call_next):
    """Add unique request ID to response headers."""
    import uuid

    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Application starting up")
    try:
        create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(
            "Failed to initialize database tables", error=str(e), exc_info=True
        )
        raise

    yield

    # Shutdown
    logger.info("Application shutting down")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A comprehensive expense tracking API with authentication, categories, and analytics",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url=f"{settings.api_v1_str}/docs",
    redoc_url=f"{settings.api_v1_str}/redoc",
    lifespan=lifespan,
)

# Add middleware (order matters - first added is outermost)
app.middleware("http")(add_request_id_header)
app.middleware("http")(add_process_time_header)
app.middleware("http")(add_security_headers)
app.middleware("http")(log_requests)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(
        "Request validation failed",
        url=str(request.url),
        method=request.method,
        errors=exc.errors(),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors(),
            "timestamp": time.time(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        url=str(request.url),
        method=request.method,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": {},
            "timestamp": time.time(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception",
        url=str(request.url),
        method=request.method,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "details": {
                "error": str(exc) if settings.debug else "Internal server error"
            },
            "timestamp": time.time(),
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time(), "version": settings.version}


# Include routers
app.include_router(auth.router, prefix=f"{settings.api_v1_str}/auth", tags=["auth"])
app.include_router(
    categories.router, prefix=f"{settings.api_v1_str}/categories", tags=["categories"]
)
app.include_router(
    expenses.router, prefix=f"{settings.api_v1_str}/expenses", tags=["expenses"]
)
app.include_router(
    analytics.router, prefix=f"{settings.api_v1_str}/analytics", tags=["analytics"]
)


@app.get("/")
def read_root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Expense Tracker API",
        "version": settings.version,
        "docs_url": f"{settings.api_v1_str}/docs",
        "openapi_url": f"{settings.api_v1_str}/openapi.json",
        "health_url": "/health",
    }


# Add structured error responses for common HTTP status codes
@app.get("/api/v1/status/{status_code}")
async def get_status_code(status_code: int):
    """Testing endpoint for different HTTP status codes."""
    if status_code == 200:
        return {"message": "OK"}
    elif status_code == 400:
        raise HTTPException(status_code=400, detail="Bad Request")
    elif status_code == 401:
        raise HTTPException(status_code=401, detail="Unauthorized")
    elif status_code == 403:
        raise HTTPException(status_code=403, detail="Forbidden")
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Not Found")
    elif status_code == 422:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")
    elif status_code == 500:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    else:
        raise HTTPException(
            status_code=status_code, detail=f"Status code {status_code}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)
