from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    address: Mapped[str | None] = mapped_column(String(400))
    area: Mapped[str | None] = mapped_column(String(100), index=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    cuisine: Mapped[str | None] = mapped_column(String(100))
    veg_type: Mapped[str | None] = mapped_column(String(20))  # veg / non-veg / both
    source: Mapped[str] = mapped_column(String(20), default="user")  # osm / user
    added_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    avg_rating: Mapped[float] = mapped_column(Float, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    dishes: Mapped[list["Dish"]] = relationship(back_populates="restaurant")


class Dish(Base):
    __tablename__ = "dishes"
    __table_args__ = (UniqueConstraint("restaurant_id", "name", name="uq_dish_per_restaurant"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    avg_price: Mapped[float] = mapped_column(Float, default=0)
    avg_rating: Mapped[float] = mapped_column(Float, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    restaurant: Mapped[Restaurant] = relationship(back_populates="dishes")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "dish_id", name="uq_one_review_per_user_dish"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_rating_range"),
        CheckConstraint("price_paid > 0", name="ck_price_positive"),
        CheckConstraint("price_tag IN ('cheap','fair','expensive')", name="ck_price_tag"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    price_paid: Mapped[float] = mapped_column(Float)
    price_tag: Mapped[str] = mapped_column(String(20))
    text: Mapped[str] = mapped_column(Text)
    suggestions: Mapped[str | None] = mapped_column(Text)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    photos: Mapped[list["ReviewPhoto"]] = relationship(back_populates="review")


class ReviewPhoto(Base):
    __tablename__ = "review_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    image_url: Mapped[str] = mapped_column(String(500))

    review: Mapped[Review] = relationship(back_populates="photos")


class HelpfulVote(Base):
    __tablename__ = "helpful_votes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), primary_key=True)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
