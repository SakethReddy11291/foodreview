from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Dish, Restaurant, Review


def refresh_ratings(db: Session, restaurant_id: int, dish_id: int) -> None:
    """Recalculate stored averages for a dish and its restaurant from the reviews table."""
    avg_rating, avg_price, count = db.execute(
        select(func.avg(Review.rating), func.avg(Review.price_paid), func.count(Review.id)).where(
            Review.dish_id == dish_id
        )
    ).one()
    dish = db.get(Dish, dish_id)
    dish.avg_rating = round(float(avg_rating or 0), 2)
    dish.avg_price = round(float(avg_price or 0), 2)
    dish.review_count = count

    r_avg, r_count = db.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(
            Review.restaurant_id == restaurant_id
        )
    ).one()
    restaurant = db.get(Restaurant, restaurant_id)
    restaurant.avg_rating = round(float(r_avg or 0), 2)
    restaurant.review_count = r_count
