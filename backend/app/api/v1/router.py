from fastapi import APIRouter
from app.api.v1 import upload, quality, processing, database, models, assistant

api_router = APIRouter()

# Include sub-routers
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(quality.router, prefix="/quality", tags=["quality"])
api_router.include_router(processing.router, prefix="/processing", tags=["processing"])
api_router.include_router(database.router, prefix="/database", tags=["database"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])


