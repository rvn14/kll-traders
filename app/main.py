from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, HTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.db import create_db_tables
from app.db.session import check_database_connection
from app.api.v1.routes.cart_routes import router as cart_router
from app.api.v1.routes.cutomer_profile_routes import router as customer_profile_router
from app.api.v1.routes.item_routes import router as item_router
from app.api.v1.routes.upload_routes import router as upload_router
from app.api.v1.routes.auth_routes import router as auth_router
from app.api.v1.routes.admin_users_routes import router as admin_users_router
from app.api.v1.routes.order_routes import router as order_router, admin_router as admin_order_router
from app.api.v1.routes.settings_routes import router as settings_router
    
from dotenv import load_dotenv

load_dotenv()
settings = get_settings()

SESSION_SECRET = os.getenv("SESSION_SECRET")

app = FastAPI(
    title="Items CRUD API",
    version="0.1.0",
)


app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
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

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    admin_users_router,
    prefix="/api/v1",
)

app.include_router(
    cart_router,
    prefix="/api/v1",
)

app.include_router(
    customer_profile_router,
    prefix="/api/v1",
)

app.include_router(
    order_router,
    prefix="/api/v1",
)

app.include_router(
    admin_order_router,
    prefix="/api/v1",
)

app.include_router(
    settings_router,
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