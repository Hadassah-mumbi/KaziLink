from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple timing middleware to log request durations for debugging slow endpoints
@app.middleware("http")
async def log_request_time(request, call_next):
    import time, logging
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logging.getLogger("uvicorn.access").info(f"{request.method} {request.url.path} completed_in={duration:.1f}ms status={response.status_code}")
    return response


# Serve uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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