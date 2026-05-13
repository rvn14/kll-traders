from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.db import create_db_tables
from app.db.session import check_database_connection
from app.api.v1.routes.item_routes import router as item_router
from app.api.v1.routes.upload_routes import router as upload_router



settings = get_settings()


app = FastAPI(
    title="Items CRUD API",
    version="0.1.0",
)


register_exception_handlers(app)

app.include_router(
    item_router,
    prefix="/api/v1",
)

app.include_router(
    upload_router,
    prefix="/api/v1",
)

@app.get("/")
def root():
    return {
        "message": "Items CRUD API is running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
    }

@app.get("/db-health")
def db_health_check():
    try:
        is_connected = check_database_connection()
        
        return {
            "database": "connected" if is_connected else "disconnected",
            "status": "ok" if is_connected else "error",
        }
    except:
      raise HTTPException(
          status_code=500,
          detail="Failed to check database connection"
      )