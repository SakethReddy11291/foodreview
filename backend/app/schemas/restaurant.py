from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    address: str | None = Field(default=None, max_length=400)
    area: str | None = Field(default=None, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    cuisine: str | None = Field(default=None, max_length=100)
    veg_type: Literal["veg", "non-veg", "both"] | None = None


class RestaurantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str | None
    area: str | None
    city: str
    lat: float
    lng: float
    cuisine: str | None
    veg_type: str | None
    source: str
    avg_rating: float
    review_count: int


class NearbyRestaurantOut(RestaurantOut):
    distance_km: float
