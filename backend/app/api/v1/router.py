from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

api_router = APIRouter()

# Include authentication router
api_router.include_router(auth_router)

@api_router.get("/health", summary="Health Check V1")
def health_check_v1():
    return {"status": "ok"}
