"""Pure helpers for turning OpenStreetMap data into restaurant rows (no network, no DB)."""

# (south, west, north, east) covering Hyderabad
HYDERABAD_BBOX = (17.20, 78.25, 17.60, 78.65)


def build_query(south: float, west: float, north: float, east: float) -> str:
    return (
        "[out:json][timeout:150];"
        f'nwr["amenity"~"^(restaurant|cafe|fast_food)$"]["name"]({south},{west},{north},{east});'
        "out center tags;"
    )


def _veg_type(tags: dict) -> str | None:
    diet = tags.get("diet:vegetarian")
    if diet == "only":
        return "veg"
    if diet == "yes":
        return "both"
    return None


def parse_elements(elements: list[dict], city: str = "Hyderabad") -> list[dict]:
    rows = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        center = el.get("center", {})
        lat = el.get("lat", center.get("lat"))
        lng = el.get("lon", center.get("lon"))
        if not name or lat is None or lng is None:
            continue

        address = " ".join(
            p for p in (tags.get("addr:housenumber"), tags.get("addr:street")) if p
        )
        area = tags.get("addr:suburb") or tags.get("addr:neighbourhood") or tags.get("addr:quarter")
        cuisine = tags.get("cuisine")
        if cuisine:
            cuisine = cuisine.replace("_", " ").replace(";", ", ")

        rows.append(
            {
                "name": name.strip()[:200],
                "address": address[:400] or None,
                "area": area[:100] if area else None,
                "city": city,
                "lat": float(lat),
                "lng": float(lng),
                "cuisine": cuisine[:100] if cuisine else None,
                "veg_type": _veg_type(tags),
            }
        )
    return rows
