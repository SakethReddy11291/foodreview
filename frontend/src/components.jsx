import { Link } from "react-router-dom";

export function Stars({ value }) {
  const full = Math.round(value);
  return (
    <span className="text-amber-500" aria-label={`${value} out of 5`}>
      {"★".repeat(full)}
      {"☆".repeat(5 - full)}
    </span>
  );
}

export function RestaurantCard({ r }) {
  return (
    <Link to={`/restaurants/${r.id}`} className="block rounded-2xl bg-white p-4 shadow-sm hover:shadow">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold">{r.name}</h3>
          <p className="text-sm text-gray-500">
            {[r.area, r.cuisine].filter(Boolean).join(" · ") || r.city}
          </p>
        </div>
        {r.distance_km != null && (
          <span className="shrink-0 text-xs text-gray-500">{r.distance_km} km</span>
        )}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
        {r.review_count > 0 ? (
          <>
            <Stars value={r.avg_rating} />
            <span>
              {r.avg_rating.toFixed(1)} ({r.review_count})
            </span>
          </>
        ) : (
          <span className="text-gray-400">No reviews yet</span>
        )}
        {r.affordable_pct != null && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700">
            {r.affordable_pct}% say affordable
          </span>
        )}
        {r.veg_type === "veg" && (
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">Veg</span>
        )}
      </div>
    </Link>
  );
}

export function Empty({ children }) {
  return (
    <div className="rounded-2xl bg-white p-6 text-center text-gray-500 shadow-sm">
      <p>{children}</p>
      <Link to="/post" className="mt-3 inline-block text-orange-600 underline">
        Be the first to post a review
      </Link>
    </div>
  );
}
