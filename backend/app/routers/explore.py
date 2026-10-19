import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Float, cast, func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Dish, Restaurant, Review
from app.routers.restaurants import distance_m
from app.schemas.explore import (
    ExploreRestaurantOut,
    PriceBreakdown,
    RestaurantSummaryOut,
    TopDishOut,
)
from app.schemas.restaurant import RestaurantOut
from app.schemas.review import DishOut

router = APIRouter(tags=["explore"])

# Ranking uses a "weighted rating": a place with 1 five-star review should not beat
# a place with 40 reviews averaging 4.6. PRIOR_WEIGHT acts like this many imaginary
# average reviews added to every place.
PRIOR_WEIGHT = 3


def _global_mean(db: Session) -> float:
    return float(db.scalar(select(func.avg(Review.rating))) or 3.5)


def _ranked_restaurants(
    db: Session,
    lat: float,
    lng: float,
    radius_km: float,
    limit: int,
    min_reviews: int,
    by_value: bool,
) -> list[dict]:
    mean = _global_mean(db)
    dist = distance_m(lat, lng)
    weighted = (Restaurant.review_count * Restaurant.avg_rating + PRIOR_WEIGHT * mean) / (
        Restaurant.review_count + PRIOR_WEIGHT
    )

    # share of reviews that say "cheap" or "fair" for each restaurant
    affordable = (
        select(
            Review.restaurant_id.label("rid"),
            (
                cast(func.count(Review.id).filter(Review.price_tag.in_(("cheap", "fair"))), Float)
                / func.count(Review.id)
            ).label("share"),
        )
        .group_by(Review.restaurant_id)
        .subquery()
    )

    score = (weighted * affordable.c.share) if by_value else weighted
    score_col = score.label("score")

    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * max(math.cos(math.radians(lat)), 0.01))

    stmt = (
        select(Restaurant, dist.label("distance_m"), score_col, affordable.c.share)
        .select_from(Restaurant)
        .join(affordable, affordable.c.rid == Restaurant.id)
        .where(
            Restaurant.lat.between(lat - lat_delta, lat + lat_delta),
            Restaurant.lng.between(lng - lng_delta, lng + lng_delta),
            dist <= radius_km * 1000,
            Restaurant.review_count >= min_reviews,
        )
        .order_by(score_col.desc(), Restaurant.review_count.desc())
        .limit(limit)
    )
    return [
        RestaurantOut.model_validate(r).model_dump()
        | {
            "distance_km": round(d / 1000, 2),
            "score": round(float(s), 2),
            "affordable_pct": round(float(share) * 100),
        }
        for r, d, s, share in db.execute(stmt).all()
    ]


@router.get("/explore/top-rated", response_model=list[ExploreRestaurantOut])
def top_rated(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    radius_km: float = Query(5.0, gt=0, le=30),
    limit: int = Query(20, ge=1, le=50),
    min_reviews: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    return _ranked_restaurants(db, lat, lng, radius_km, limit, min_reviews, by_value=False)


@router.get("/explore/best-value", response_model=list[ExploreRestaurantOut])
def best_value(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    radius_km: float = Query(5.0, gt=0, le=30),
    limit: int = Query(20, ge=1, le=50),
    min_reviews: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    """Tasty AND affordable: weighted rating multiplied by the share of 'cheap/fair' reviews."""
    return _ranked_restaurants(db, lat, lng, radius_km, limit, min_reviews, by_value=True)


@router.get("/explore/top-dishes", response_model=list[TopDishOut])
def top_dishes(
    city: str = "Hyderabad",
    q: str | None = Query(None, description="Search dish name, e.g. biryani"),
    limit: int = Query(20, ge=1, le=50),
    min_reviews: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    mean = _global_mean(db)
    weighted = (Dish.review_count * Dish.avg_rating + PRIOR_WEIGHT * mean) / (
        Dish.review_count + PRIOR_WEIGHT
    )
    score_col = weighted.label("score")

    stmt = (
        select(Dish, Restaurant, score_col)
        .join(Restaurant, Restaurant.id == Dish.restaurant_id)
        .where(func.lower(Restaurant.city) == city.lower(), Dish.review_count >= min_reviews)
    )
    if q:
        stmt = stmt.where(Dish.name.ilike(f"%{q}%"))
    rows = db.execute(
        stmt.order_by(score_col.desc(), Dish.review_count.desc()).limit(limit)
    ).all()
    return [
        {
            "dish_id": dish.id,
            "dish_name": dish.name,
            "avg_rating": dish.avg_rating,
            "avg_price": dish.avg_price,
            "review_count": dish.review_count,
            "restaurant_id": restaurant.id,
            "restaurant_name": restaurant.name,
            "area": restaurant.area,
            "score": round(float(score), 2),
        }
        for dish, restaurant, score in rows
    ]


@router.get("/restaurants/{restaurant_id}/summary", response_model=RestaurantSummaryOut)
def restaurant_summary(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    price_counts = dict(
        db.execute(
            select(Review.price_tag, func.count(Review.id))
            .where(Review.restaurant_id == restaurant_id)
            .group_by(Review.price_tag)
        ).all()
    )
    rating_counts = dict(
        db.execute(
            select(Review.rating, func.count(Review.id))
            .where(Review.restaurant_id == restaurant_id)
            .group_by(Review.rating)
        ).all()
    )
    avg_price = db.scalar(
        select(func.avg(Review.price_paid)).where(Review.restaurant_id == restaurant_id)
    )
    top = db.scalars(
        select(Dish)
        .where(Dish.restaurant_id == restaurant_id, Dish.review_count > 0)
        .order_by(Dish.avg_rating.desc(), Dish.review_count.desc())
        .limit(3)
    ).all()

    total = sum(price_counts.values())
    affordable = price_counts.get("cheap", 0) + price_counts.get("fair", 0)
    return RestaurantSummaryOut(
        restaurant=RestaurantOut.model_validate(restaurant),
        avg_price_paid=round(float(avg_price), 2) if avg_price else None,
        affordable_pct=round(affordable / total * 100) if total else None,
        price_breakdown=PriceBreakdown(
            cheap=price_counts.get("cheap", 0),
            fair=price_counts.get("fair", 0),
            expensive=price_counts.get("expensive", 0),
        ),
        rating_breakdown={star: rating_counts.get(star, 0) for star in range(1, 6)},
        top_dishes=[DishOut.model_validate(d) for d in top],
    )
