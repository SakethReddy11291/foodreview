import pytest
from pydantic import ValidationError

from app.schemas.review import ReviewCreate

VALID = dict(
    restaurant_id=1, dish_name="Chicken Biryani", rating=4,
    price_paid=250, price_tag="fair", text="Tasty and filling",
)


def test_valid_review():
    assert ReviewCreate(**VALID).rating == 4


@pytest.mark.parametrize("change", [
    {"rating": 6}, {"rating": 0}, {"price_paid": 0},
    {"price_tag": "cheapish"}, {"photo_urls": ["http://x.com/a.jpg"]},
])
def test_invalid_review(change):
    with pytest.raises(ValidationError):
        ReviewCreate(**{**VALID, **change})
