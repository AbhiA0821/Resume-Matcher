from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware configuration
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Root level health endpoint
@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    return {"status": "ok"}

# Root level status endpoint
@app.get("/", tags=["Root"], summary="Root Status")
def root():
    return {
        "message": "HireAgent API is running",
        "status": "ok"
    }

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)
