"""Import restaurants from OpenStreetMap.

Run inside Docker:  python -m app.services.osm_import
Safe to run again: places already in the database are skipped.
"""
import httpx
from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import Restaurant
from app.services.osm_parse import HYDERABAD_BBOX, build_query, parse_elements

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def fetch_elements(bbox) -> list[dict]:
    response = httpx.post(
        OVERPASS_URL,
        data={"data": build_query(*bbox)},
        headers={"User-Agent": "FoodReviewApp/0.1 (learning project)"},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()["elements"]


def run() -> None:
    print("Downloading restaurants from OpenStreetMap (can take 1-2 minutes)...")
    items = parse_elements(fetch_elements(HYDERABAD_BBOX))
    print(f"Fetched {len(items)} places")

    with SessionLocal() as db:
        existing = {
            (n.lower(), round(la, 4), round(lo, 4))
            for n, la, lo in db.execute(select(Restaurant.name, Restaurant.lat, Restaurant.lng))
        }
        added = 0
        for item in items:
            key = (item["name"].lower(), round(item["lat"], 4), round(item["lng"], 4))
            if key in existing:
                continue
            existing.add(key)
            db.add(Restaurant(**item, source="osm"))
            added += 1
        db.commit()
    print(f"Added {added} new restaurants")


if __name__ == "__main__":
    run()
