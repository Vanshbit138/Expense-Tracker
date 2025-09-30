from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.api.authentication.auth import router as auth_router
from src.api.category.categories import router as categories_router
from src.api.expense.expenses import router as expenses_router
from src.api.user.analytics import router as analytics_router
from src.core.config import settings
from src.core.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A comprehensive expense tracking API with authentication, categories, and analytics",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url=f"{settings.api_v1_str}/docs",
    redoc_url=f"{settings.api_v1_str}/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth_router, prefix=f"{settings.api_v1_str}/auth", tags=["authentication"]
)
app.include_router(
    categories_router, prefix=f"{settings.api_v1_str}/categories", tags=["categories"]
)
app.include_router(
    expenses_router, prefix=f"{settings.api_v1_str}/expenses", tags=["expenses"]
)
app.include_router(
    analytics_router, prefix=f"{settings.api_v1_str}/analytics", tags=["analytics"]
)


def clean_validation_errors(errors):
    """Clean validation errors for better readability."""
    cleaned_errors = []
    for error in errors:
        cleaned_error = {
            "loc": list(error["loc"]),
            "msg": error["msg"],
            "type": error["type"],
        }
        if "ctx" in error and error["ctx"]:
            ctx = error["ctx"]
            if "reason" in ctx:
                cleaned_error["msg"] = ctx["reason"]

        cleaned_errors.append(cleaned_error)
    return cleaned_errors


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(
        "Validation error occurred",
        url=str(request.url),
        method=request.method,
        errors=exc.errors(),
    )

    cleaned_errors = clean_validation_errors(exc.errors())

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": cleaned_errors},
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(
        "Pydantic validation error occurred",
        url=str(request.url),
        method=request.method,
        errors=exc.errors(),
    )

    cleaned_errors = clean_validation_errors(exc.errors())

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": cleaned_errors},
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    logger.warning(
        "Value error occurred",
        url=str(request.url),
        method=request.method,
        error=str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception occurred",
        url=str(request.url),
        method=request.method,
        error=str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting up Expense Tracker API")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Expense Tracker API")
