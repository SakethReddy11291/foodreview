from pydantic import BaseModel

from app.schemas.restaurant import RestaurantOut
from app.schemas.review import DishOut


class ExploreRestaurantOut(RestaurantOut):
    distance_km: float
    score: float
    affordable_pct: int


class TopDishOut(BaseModel):
    dish_id: int
    dish_name: str
    avg_rating: float
    avg_price: float
    review_count: int
    restaurant_id: int
    restaurant_name: str
    area: str | None
    score: float


class PriceBreakdown(BaseModel):
    cheap: int = 0
    fair: int = 0
    expensive: int = 0


class RestaurantSummaryOut(BaseModel):
    restaurant: RestaurantOut
    avg_price_paid: float | None
    affordable_pct: int | None
    price_breakdown: PriceBreakdown
    rating_breakdown: dict[int, int]
    top_dishes: list[DishOut]
