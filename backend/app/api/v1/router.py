from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.profile import router as profile_router
from app.api.v1.preferences import router as preferences_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.semantic import router as semantic_router

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth_router)
api_router.include_router(resumes_router)
api_router.include_router(profile_router)
api_router.include_router(preferences_router)
api_router.include_router(jobs_router)
api_router.include_router(semantic_router)



@api_router.get("/health", summary="Health Check V1")
def health_check_v1():
    return {"status": "ok"}
