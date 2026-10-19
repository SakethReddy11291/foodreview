import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models import Restaurant, User
from app.schemas.restaurant import NearbyRestaurantOut, RestaurantCreate, RestaurantOut

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


def distance_m(lat: float, lng: float):
    """Distance in meters from (lat, lng) to each restaurant, computed by PostGIS."""
    return func.ST_DistanceSphere(
        func.ST_MakePoint(Restaurant.lng, Restaurant.lat),
        func.ST_MakePoint(lng, lat),
    )


@router.get("/nearby", response_model=list[NearbyRestaurantOut])
def nearby(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    radius_km: float = Query(3.0, gt=0, le=20),
    limit: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, description="Search by restaurant name"),
    cuisine: str | None = None,
    veg_type: str | None = Query(None, pattern="^(veg|non-veg|both)$"),
    db: Session = Depends(get_db),
):
    dist = distance_m(lat, lng)
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * max(math.cos(math.radians(lat)), 0.01))

    stmt = select(Restaurant, dist.label("distance_m")).where(
        Restaurant.lat.between(lat - lat_delta, lat + lat_delta),
        Restaurant.lng.between(lng - lng_delta, lng + lng_delta),
        dist <= radius_km * 1000,
    )
    if q:
        stmt = stmt.where(Restaurant.name.ilike(f"%{q}%"))
    if cuisine:
        stmt = stmt.where(Restaurant.cuisine.ilike(f"%{cuisine}%"))
    if veg_type:
        stmt = stmt.where(Restaurant.veg_type == veg_type)

    rows = db.execute(stmt.order_by(dist).limit(limit)).all()
    return [
        RestaurantOut.model_validate(r).model_dump() | {"distance_km": round(d / 1000, 2)}
        for r, d in rows
    ]


@router.get("/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.post("", response_model=RestaurantOut, status_code=201)
def add_restaurant(
    data: RestaurantCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    duplicate_id = db.scalar(
        select(Restaurant.id)
        .where(
            func.lower(Restaurant.name) == data.name.strip().lower(),
            distance_m(data.lat, data.lng) < 100,
        )
        .limit(1)
    )
    if duplicate_id:
        raise HTTPException(
            status_code=409, detail=f"This restaurant already exists (id {duplicate_id})"
        )

    restaurant = Restaurant(
        **data.model_dump(exclude={"name"}),
        name=data.name.strip(),
        source="user",
        added_by=user.id,
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant
