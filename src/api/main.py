"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import analytics, auth, categories, expenses
from src.core.config import settings
from src.core.database import create_tables

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="A RESTful Expense Tracker API built with FastAPI",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url=f"{settings.api_v1_str}/docs",
    redoc_url=f"{settings.api_v1_str}/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router, prefix=f"{settings.api_v1_str}/auth", tags=["authentication"]
)
app.include_router(
    expenses.router, prefix=f"{settings.api_v1_str}/expenses", tags=["expenses"]
)
app.include_router(
    categories.router, prefix=f"{settings.api_v1_str}/categories", tags=["categories"]
)
app.include_router(
    analytics.router, prefix=f"{settings.api_v1_str}/analytics", tags=["analytics"]
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to Expense Tracker API",
        "version": settings.version,
        "docs": f"{settings.api_v1_str}/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
