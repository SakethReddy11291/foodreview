import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { Stars } from "../components";

const TAG_STYLE = {
  cheap: "bg-green-100 text-green-700",
  fair: "bg-blue-100 text-blue-700",
  expensive: "bg-red-100 text-red-700",
};

export default function Restaurant() {
  const { id } = useParams();
  const [summary, setSummary] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [sort, setSort] = useState("newest");
  const [voted, setVoted] = useState({});
  const [note, setNote] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/restaurants/${id}/summary`, { auth: false }).then(setSummary).catch((e) => setError(e.message));
  }, [id]);

  useEffect(() => {
    api(`/restaurants/${id}/reviews?sort=${sort}`, { auth: false })
      .then(setReviews)
      .catch((e) => setError(e.message));
  }, [id, sort]);

  async function toggleHelpful(review) {
    setNote("");
    try {
      const res = await api(`/reviews/${review.id}/helpful`, { method: "POST" });
      setVoted((v) => ({ ...v, [review.id]: res.voted }));
      setReviews((list) =>
        list.map((r) => (r.id === review.id ? { ...r, helpful_count: res.helpful_count } : r))
      );
    } catch (e) {
      setNote(e.message);
    }
  }

  async function report(review) {
    const reason = window.prompt("Why are you reporting this review?");
    if (!reason || reason.trim().length < 3) return;
    try {
      await api(`/reviews/${review.id}/report`, { method: "POST", body: { reason } });
      setNote("Thanks, the review was reported.");
    } catch (e) {
      setNote(e.message);
    }
  }

  if (error) return <p className="rounded-lg bg-red-50 p-3 text-red-600">{error}</p>;
  if (!summary) return <p className="text-center text-gray-500">Loading…</p>;

  const r = summary.restaurant;
  const pb = summary.price_breakdown;
  const total = pb.cheap + pb.fair + pb.expensive;

  return (
    <div className="space-y-4">
      <Link to="/explore" className="text-sm text-orange-600 underline">
        ← Back to explore
      </Link>

      <div className="space-y-3 rounded-2xl bg-white p-4 shadow-sm">
        <div>
          <h1 className="text-xl font-semibold">{r.name}</h1>
          <p className="text-sm text-gray-500">
            {[r.area, r.cuisine, r.city].filter(Boolean).join(" · ")}
          </p>
        </div>

        {r.review_count > 0 ? (
          <>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
              <span className="text-lg">
                <Stars value={r.avg_rating} /> <b>{r.avg_rating.toFixed(1)}</b>
              </span>
              <span className="text-sm text-gray-500">{r.review_count} reviews</span>
              {summary.avg_price_paid && (
                <span className="text-sm text-gray-600">Avg spend ₹{Math.round(summary.avg_price_paid)}</span>
              )}
            </div>

            <div>
              <p className="text-sm font-medium text-green-700">{summary.affordable_pct}% say affordable</p>
              <div className="mt-1 flex h-2 overflow-hidden rounded-full bg-gray-100">
                <div className="bg-green-500" style={{ width: `${(pb.cheap / total) * 100}%` }} />
                <div className="bg-blue-400" style={{ width: `${(pb.fair / total) * 100}%` }} />
                <div className="bg-red-400" style={{ width: `${(pb.expensive / total) * 100}%` }} />
              </div>
              <p className="mt-1 text-xs text-gray-500">
                {pb.cheap} cheap · {pb.fair} fair · {pb.expensive} expensive
              </p>
            </div>

            {summary.top_dishes.length > 0 && (
              <div>
                <p className="mb-1 text-sm font-medium">Top dishes</p>
                <ul className="space-y-1 text-sm">
                  {summary.top_dishes.map((d) => (
                    <li key={d.id} className="flex justify-between">
                      <span>{d.name}</span>
                      <span className="text-gray-600">
                        ★ {d.avg_rating.toFixed(1)} · ₹{Math.round(d.avg_price)}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p className="text-gray-500">No reviews yet for this place.</p>
        )}

        <Link
          to={`/post?restaurant=${r.id}`}
          className="inline-block rounded-lg bg-orange-600 px-4 py-2 text-sm font-medium text-white hover:bg-orange-700"
        >
          ✍️ Write a review
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <h2 className="font-semibold">Reviews</h2>
        <select
          className="rounded-lg border border-gray-300 px-2 py-1 text-sm"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="newest">Newest</option>
          <option value="highest">Highest rated</option>
          <option value="lowest">Lowest rated</option>
          <option value="helpful">Most helpful</option>
        </select>
      </div>

      {note && <p className="rounded-lg bg-orange-100 p-2 text-sm text-orange-800">{note}</p>}

      {reviews?.map((rev) => (
        <div key={rev.id} className="space-y-2 rounded-2xl bg-white p-4 shadow-sm">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-medium">{rev.dish_name}</p>
              <p className="text-xs text-gray-500">
                {rev.user_name} · {new Date(rev.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="text-right">
              <Stars value={rev.rating} />
              <p className="text-xs">
                ₹{Math.round(rev.price_paid)}{" "}
                <span className={`rounded-full px-2 py-0.5 ${TAG_STYLE[rev.price_tag]}`}>{rev.price_tag}</span>
              </p>
            </div>
          </div>
          <p className="text-sm">{rev.text}</p>
          {rev.suggestions && <p className="text-sm text-gray-600">💡 {rev.suggestions}</p>}
          {rev.photos.length > 0 && (
            <div className="flex gap-2 overflow-x-auto">
              {rev.photos.map((url) => (
                <img key={url} src={url} loading="lazy" alt={rev.dish_name} className="h-24 rounded-lg object-cover" />
              ))}
            </div>
          )}
          <div className="flex gap-3 text-sm">
            <button
              onClick={() => toggleHelpful(rev)}
              className={`rounded-lg border px-3 py-1 ${voted[rev.id] ? "border-orange-500 bg-orange-50" : ""}`}
            >
              👍 Helpful ({rev.helpful_count})
            </button>
            <button onClick={() => report(rev)} className="text-gray-500 underline">
              Report
            </button>
          </div>
        </div>
      ))}
      {reviews?.length === 0 && <p className="text-center text-gray-500">No reviews to show.</p>}
    </div>
  );
}
