import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { Empty, RestaurantCard, Stars } from "../components";
import { usePlace } from "../place";

const TABS = [
  ["top", "Top rated"],
  ["value", "Best value"],
  ["dishes", "Top dishes"],
];

export default function Explore() {
  const { place } = usePlace();
  const [tab, setTab] = useState("top");
  const [q, setQ] = useState("");
  const [veg, setVeg] = useState("");
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  const searching = q.trim() !== "" || veg !== "";

  useEffect(() => {
    let cancelled = false;
    setItems(null);
    setError("");
    const loc = `lat=${place.lat}&lng=${place.lng}`;
    let path;
    if (searching) {
      path =
        `/restaurants/nearby?${loc}&radius_km=5&limit=30` +
        (q.trim() ? `&q=${encodeURIComponent(q.trim())}` : "") +
        (veg ? `&veg_type=${veg}` : "");
    } else if (tab === "top") path = `/explore/top-rated?${loc}&radius_km=10`;
    else if (tab === "value") path = `/explore/best-value?${loc}&radius_km=10`;
    else path = `/explore/top-dishes?city=${encodeURIComponent(place.city)}`;

    const timer = setTimeout(
      () => {
        api(path, { auth: false })
          .then((data) => !cancelled && setItems(data))
          .catch((e) => !cancelled && setError(e.message));
      },
      q ? 300 : 0
    );
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [tab, q, veg, place, searching]);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold">Explore</h1>
        <p className="text-sm text-gray-500">
          Near 📍 {place.label} ·{" "}
          <Link to="/" className="text-orange-600 underline">
            change area
          </Link>
        </p>
      </div>

      <div className="flex gap-2">
        <input
          className="min-w-0 flex-1 rounded-lg border border-gray-300 px-3 py-2 outline-none focus:border-orange-500"
          placeholder="Search restaurants by name"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select
          className="rounded-lg border border-gray-300 px-2"
          value={veg}
          onChange={(e) => setVeg(e.target.value)}
        >
          <option value="">All</option>
          <option value="veg">Veg</option>
          <option value="non-veg">Non-veg</option>
          <option value="both">Both</option>
        </select>
      </div>

      {!searching && (
        <div className="flex gap-2">
          {TABS.map(([key, label]) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`rounded-full px-4 py-1 text-sm ${
                tab === key ? "bg-orange-600 text-white" : "bg-white text-gray-700 shadow-sm"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      )}

      {tab === "value" && !searching && (
        <p className="text-xs text-gray-500">Tasty and affordable: high rating, and most reviewers say cheap or fair.</p>
      )}

      {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>}
      {!error && items === null && <p className="text-center text-gray-500">Loading…</p>}
      {items?.length === 0 && (
        <Empty>
          {searching
            ? "No restaurants found. Try another name or filter."
            : "No reviews here yet. Try another area, or add the first review."}
        </Empty>
      )}

      <div className="space-y-3">
        {items?.map((item) =>
          !searching && tab === "dishes" ? (
            <Link
              key={item.dish_id}
              to={`/restaurants/${item.restaurant_id}`}
              className="block rounded-2xl bg-white p-4 shadow-sm hover:shadow"
            >
              <div className="flex items-start justify-between">
                <h3 className="font-semibold">{item.dish_name}</h3>
                <span className="text-sm text-gray-600">₹{Math.round(item.avg_price)}</span>
              </div>
              <p className="text-sm text-gray-500">
                {item.restaurant_name}
                {item.area ? ` · ${item.area}` : ""}
              </p>
              <div className="mt-1 text-sm">
                <Stars value={item.avg_rating} /> {item.avg_rating.toFixed(1)} ({item.review_count})
              </div>
            </Link>
          ) : (
            <RestaurantCard key={item.id} r={item} />
          )
        )}
      </div>
    </div>
  );
}
