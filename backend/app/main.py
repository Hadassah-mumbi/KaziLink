from fastapi import FastAPI

from app.db.database import engine, SessionLocal
from app.db.base import Base

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.providers import router as providers_router
from app.api.admin import router as admin_router
from app.api.category import router as category_router
from app.api.provider_categories import (
    router as provider_categories_router
)
from app.api.provider_availability import (
    router as provider_availability_router
)
from app.api.booking import router as booking_router
from app.api.reviews import router as reviews_router

from app.services.admin_setup import create_default_admin


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="KaziLink API",
    version="1.0.0",
    description="KaziLink Backend API"
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(auth_router)

app.include_router(users_router)

app.include_router(providers_router)

app.include_router(admin_router)

app.include_router(category_router)

app.include_router(provider_categories_router)

app.include_router(provider_availability_router)

app.include_router(booking_router)

app.include_router(reviews_router)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup():

    # Create database tables if they do not already exist
    Base.metadata.create_all(
        bind=engine
    )

    # Create default administrator account
    db = SessionLocal()

    try:

        create_default_admin(db)

    finally:

        db.close()


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Welcome to KaziLink API 🚀"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }