from app.services.osm_parse import build_query, parse_elements


def test_parse_node_and_way():
    elements = [
        {"type": "node", "lat": 17.44, "lon": 78.38,
         "tags": {"name": "Test Biryani", "cuisine": "south_indian;biryani",
                  "addr:suburb": "Madhapur", "diet:vegetarian": "no"}},
        {"type": "way", "center": {"lat": 17.40, "lon": 78.45},
         "tags": {"name": "Green Cafe", "diet:vegetarian": "only"}},
        {"type": "node", "lat": 17.1, "lon": 78.1, "tags": {"amenity": "cafe"}},
    ]
    rows = parse_elements(elements)
    assert len(rows) == 2
    assert rows[0]["cuisine"] == "south indian, biryani"
    assert rows[0]["area"] == "Madhapur"
    assert rows[1]["veg_type"] == "veg"
    assert rows[1]["lat"] == 17.40


def test_build_query_contains_bbox():
    assert "17.2,78.25,17.6,78.65" in build_query(17.2, 78.25, 17.6, 78.65)
