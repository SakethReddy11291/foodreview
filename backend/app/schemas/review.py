from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewCreate(BaseModel):
    restaurant_id: int
    dish_name: str = Field(min_length=2, max_length=150)
    rating: int = Field(ge=1, le=5)
    price_paid: float = Field(gt=0, le=100000)
    price_tag: Literal["cheap", "fair", "expensive"]
    text: str = Field(min_length=5, max_length=2000)
    suggestions: str | None = Field(default=None, max_length=1000)
    photo_urls: list[str] = Field(default_factory=list, max_length=3)

    @field_validator("photo_urls")
    @classmethod
    def photos_must_be_https(cls, urls: list[str]) -> list[str]:
        for url in urls:
            if not url.startswith("https://") or len(url) > 500:
                raise ValueError("photo URLs must start with https:// and be under 500 characters")
        return urls


class ReviewOut(BaseModel):
    id: int
    user_id: int
    user_name: str
    restaurant_id: int
    dish_id: int
    dish_name: str
    rating: int
    price_paid: float
    price_tag: str
    text: str
    suggestions: str | None
    helpful_count: int
    created_at: datetime
    photos: list[str]


class DishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    avg_price: float
    avg_rating: float
    review_count: int


class HelpfulOut(BaseModel):
    helpful_count: int
    voted: bool


class ReportCreate(BaseModel):
    reason: str = Field(min_length=3, max_length=300)
