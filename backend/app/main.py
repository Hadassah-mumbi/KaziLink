from fastapi import FastAPI

from app.db.database import engine
from app.db.base import Base

from app.api.auth import router as auth_router
from app.api.users import router as users_router

app = FastAPI(
    title="KaziLink API",
    version="1.0.0",
    description="KaziLink Backend API"
)

app.include_router(auth_router)
app.include_router(users_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Welcome to KaziLink API 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }