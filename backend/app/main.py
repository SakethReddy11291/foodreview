from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.routers import auth, explore, restaurants, reviews, uploads

app = FastAPI(title="FoodReview API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(reviews.router)
app.include_router(uploads.router)
app.include_router(explore.router)


@app.get("/")
def root():
    return {"message": "FoodReview API is running"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    try:
        postgis = db.execute(text("SELECT PostGIS_Version()")).scalar()
    except Exception:
        postgis = None
    return {"status": "ok", "database": "connected", "postgis": postgis}
