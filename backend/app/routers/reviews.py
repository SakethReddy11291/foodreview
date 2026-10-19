import string
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models import Dish, HelpfulVote, Report, Restaurant, Review, ReviewPhoto, User
from app.schemas.review import (
    DishOut,
    HelpfulOut,
    ReportCreate,
    ReviewCreate,
    ReviewOut,
)
from app.services.ratings import refresh_ratings

router = APIRouter(tags=["reviews"])


def _to_out(review: Review, user_name: str, dish_name: str) -> dict:
    return {
        "id": review.id,
        "user_id": review.user_id,
        "user_name": user_name,
        "restaurant_id": review.restaurant_id,
        "dish_id": review.dish_id,
        "dish_name": dish_name,
        "rating": review.rating,
        "price_paid": review.price_paid,
        "price_tag": review.price_tag,
        "text": review.text,
        "suggestions": review.suggestions,
        "helpful_count": review.helpful_count,
        "created_at": review.created_at,
        "photos": [p.image_url for p in review.photos],
    }


@router.post("/reviews", response_model=ReviewOut, status_code=201)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    restaurant = db.get(Restaurant, data.restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    dish_name = " ".join(data.dish_name.split())
    dish = db.scalar(
        select(Dish).where(
            Dish.restaurant_id == restaurant.id,
            func.lower(Dish.name) == dish_name.lower(),
        )
    )
    if dish is None:
        dish = Dish(restaurant_id=restaurant.id, name=string.capwords(dish_name))
        db.add(dish)
        db.flush()
    elif db.scalar(select(Review.id).where(Review.user_id == user.id, Review.dish_id == dish.id)):
        raise HTTPException(status_code=409, detail="You already reviewed this dish")

    review = Review(
        user_id=user.id,
        restaurant_id=restaurant.id,
        dish_id=dish.id,
        rating=data.rating,
        price_paid=data.price_paid,
        price_tag=data.price_tag,
        text=data.text.strip(),
        suggestions=(data.suggestions or "").strip() or None,
    )
    db.add(review)
    db.flush()
    for url in data.photo_urls:
        db.add(ReviewPhoto(review_id=review.id, image_url=url))
    db.flush()

    refresh_ratings(db, restaurant.id, dish.id)
    db.commit()
    db.refresh(review)
    return _to_out(review, user.name, dish.name)


@router.get("/restaurants/{restaurant_id}/reviews", response_model=list[ReviewOut])
def list_reviews(
    restaurant_id: int,
    sort: Literal["newest", "highest", "lowest", "helpful"] = "newest",
    dish_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if db.get(Restaurant, restaurant_id) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    stmt = (
        select(Review, User.name, Dish.name)
        .join(User, User.id == Review.user_id)
        .join(Dish, Dish.id == Review.dish_id)
        .where(Review.restaurant_id == restaurant_id)
    )
    if dish_id:
        stmt = stmt.where(Review.dish_id == dish_id)

    order = {
        "newest": Review.created_at.desc(),
        "highest": Review.rating.desc(),
        "lowest": Review.rating.asc(),
        "helpful": Review.helpful_count.desc(),
    }[sort]
    rows = db.execute(stmt.order_by(order, Review.id.desc()).limit(limit).offset(offset)).all()
    return [_to_out(review, user_name, dish_name) for review, user_name, dish_name in rows]


@router.get("/restaurants/{restaurant_id}/dishes", response_model=list[DishOut])
def list_dishes(restaurant_id: int, db: Session = Depends(get_db)):
    if db.get(Restaurant, restaurant_id) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db.scalars(
        select(Dish)
        .where(Dish.restaurant_id == restaurant_id)
        .order_by(Dish.avg_rating.desc(), Dish.review_count.desc())
    ).all()


@router.post("/reviews/{review_id}/helpful", response_model=HelpfulOut)
def toggle_helpful(
    review_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id == user.id:
        raise HTTPException(status_code=400, detail="You can't vote on your own review")

    vote = db.get(HelpfulVote, (user.id, review_id))
    if vote:
        db.delete(vote)
        voted = False
    else:
        db.add(HelpfulVote(user_id=user.id, review_id=review_id))
        voted = True
    db.flush()

    count = db.scalar(
        select(func.count()).select_from(HelpfulVote).where(HelpfulVote.review_id == review_id)
    )
    review.helpful_count = count
    db.commit()
    return {"helpful_count": count, "voted": voted}


@router.post("/reviews/{review_id}/report", status_code=201)
def report_review(
    review_id: int,
    data: ReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if db.get(Review, review_id) is None:
        raise HTTPException(status_code=404, detail="Review not found")
    already = db.scalar(
        select(Report.id).where(Report.review_id == review_id, Report.reporter_id == user.id)
    )
    if already:
        raise HTTPException(status_code=409, detail="You already reported this review")
    db.add(Report(review_id=review_id, reporter_id=user.id, reason=data.reason.strip()))
    db.commit()
    return {"status": "reported"}
