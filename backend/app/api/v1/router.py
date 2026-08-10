from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health", summary="Health Check V1")
def health_check_v1():
    return {"status": "ok"}
