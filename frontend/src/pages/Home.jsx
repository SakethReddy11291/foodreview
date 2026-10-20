import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import { PRESETS, usePlace } from "../place";

export default function Home() {
  const { user } = useAuth();
  const { place, choose, detect, detecting } = usePlace();

  const known = PRESETS.some((p) => p.label === place.label);

  return (
    <div className="space-y-5">
      <div className="rounded-2xl bg-white p-4 shadow-sm">
        <p className="text-sm text-gray-500">Hi {user.name}, you are in</p>
        <p className="text-xl font-semibold">📍 {place.label}</p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <select
            className="rounded-lg border px-2 py-1 text-sm"
            value={known ? place.label : ""}
            onChange={(e) => choose(PRESETS.find((p) => p.label === e.target.value))}
          >
            {!known && <option value="">{place.label}</option>}
            {PRESETS.map((p) => (
              <option key={p.label}>{p.label}</option>
            ))}
          </select>
          <button
            onClick={detect}
            disabled={detecting}
            className="rounded-lg border px-3 py-1 text-sm hover:bg-gray-100 disabled:opacity-60"
          >
            {detecting ? "Detecting…" : "Use my location"}
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Link to="/explore" className="rounded-2xl bg-orange-600 p-6 text-white shadow hover:bg-orange-700">
          <div className="text-3xl">🔍</div>
          <h2 className="mt-2 text-lg font-semibold">Explore Reviews</h2>
          <p className="text-sm text-orange-100">Find where to eat</p>
        </Link>
        <Link to="/post" className="rounded-2xl bg-white p-6 shadow hover:bg-gray-50">
          <div className="text-3xl">✍️</div>
          <h2 className="mt-2 text-lg font-semibold">Post a Review</h2>
          <p className="text-sm text-gray-500">Share your experience</p>
        </Link>
      </div>
    </div>
  );
}
