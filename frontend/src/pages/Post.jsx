import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api, uploadPhoto } from "../api";
import { usePlace } from "../place";

const input = "w-full rounded-lg border border-gray-300 px-3 py-2 outline-none focus:border-orange-500";
const card = "space-y-4 rounded-2xl bg-white p-4 shadow-sm";
const TAGS = [
  ["cheap", "Cheap"],
  ["fair", "Fair"],
  ["expensive", "Expensive"],
];

export default function Post() {
  const [params] = useSearchParams();
  const [restaurant, setRestaurant] = useState(null);
  const [adding, setAdding] = useState(false);
  const [loading, setLoading] = useState(!!params.get("restaurant"));

  useEffect(() => {
    const id = params.get("restaurant");
    if (!id) return;
    api(`/restaurants/${id}`, { auth: false })
      .then(setRestaurant)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [params]);

  if (loading) return <p className="text-center text-gray-500">Loading…</p>;
  if (restaurant) return <ReviewForm restaurant={restaurant} onChange={() => setRestaurant(null)} />;
  if (adding)
    return (
      <AddRestaurant
        onDone={(r) => {
          setRestaurant(r);
          setAdding(false);
        }}
        onCancel={() => setAdding(false)}
      />
    );
  return <SelectRestaurant onPick={setRestaurant} onAdd={() => setAdding(true)} />;
}

function SelectRestaurant({ onPick, onAdd }) {
  const { place } = usePlace();
  const [q, setQ] = useState("");
  const [items, setItems] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const timer = setTimeout(() => {
      const search = q.trim() ? `&q=${encodeURIComponent(q.trim())}` : "";
      api(`/restaurants/nearby?lat=${place.lat}&lng=${place.lng}&radius_km=5&limit=20${search}`, { auth: false })
        .then((data) => !cancelled && setItems(data))
        .catch(() => !cancelled && setItems([]));
    }, 300);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [q, place]);

  return (
    <div className={card}>
      <div>
        <h1 className="text-xl font-semibold">Which restaurant did you visit?</h1>
        <p className="text-sm text-gray-500">Showing places near 📍 {place.label}</p>
      </div>
      <input className={input} placeholder="Search by restaurant name" value={q} onChange={(e) => setQ(e.target.value)} />
      {items === null && <p className="text-center text-gray-500">Loading…</p>}
      <div className="space-y-2">
        {items?.map((r) => (
          <button
            key={r.id}
            onClick={() => onPick(r)}
            className="flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left hover:bg-orange-50"
          >
            <span>
              <span className="font-medium">{r.name}</span>
              <span className="block text-xs text-gray-500">
                {[r.area, r.cuisine].filter(Boolean).join(" · ") || r.city}
              </span>
            </span>
            <span className="text-xs text-gray-500">{r.distance_km} km</span>
          </button>
        ))}
      </div>
      {items?.length === 0 && <p className="text-center text-sm text-gray-500">No matching restaurants found.</p>}
      <button onClick={onAdd} className="text-sm text-orange-600 underline">
        Can't find your restaurant? Add it
      </button>
    </div>
  );
}

function AddRestaurant({ onDone, onCancel }) {
  const { place } = usePlace();
  const [f, setF] = useState({ name: "", area: "", cuisine: "", veg_type: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const r = await api("/restaurants", {
        method: "POST",
        body: {
          name: f.name,
          area: f.area || null,
          city: place.city,
          lat: place.lat,
          lng: place.lng,
          cuisine: f.cuisine || null,
          veg_type: f.veg_type || null,
        },
      });
      onDone(r);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className={card}>
      <h1 className="text-xl font-semibold">Add a restaurant</h1>
      <p className="text-sm text-gray-500">It will be placed near 📍 {place.label}, {place.city}.</p>
      <input className={input} placeholder="Restaurant name" value={f.name} onChange={set("name")} required />
      <input className={input} placeholder="Area (e.g. Madhapur)" value={f.area} onChange={set("area")} />
      <input className={input} placeholder="Cuisine (e.g. south indian)" value={f.cuisine} onChange={set("cuisine")} />
      <select className={input} value={f.veg_type} onChange={set("veg_type")}>
        <option value="">Veg / non-veg (optional)</option>
        <option value="veg">Veg</option>
        <option value="non-veg">Non-veg</option>
        <option value="both">Both</option>
      </select>
      {error && <p className="rounded-lg bg-red-50 p-2 text-sm text-red-600">{error}</p>}
      <div className="flex gap-3">
        <button disabled={busy} className="rounded-lg bg-orange-600 px-4 py-2 font-medium text-white hover:bg-orange-700 disabled:opacity-60">
          {busy ? "Adding…" : "Add and continue"}
        </button>
        <button type="button" onClick={onCancel} className="text-gray-600 underline">
          Cancel
        </button>
      </div>
    </form>
  );
}

function ReviewForm({ restaurant, onChange }) {
  const navigate = useNavigate();
  const [dishes, setDishes] = useState([]);
  const [dish, setDish] = useState("");
  const [rating, setRating] = useState(0);
  const [price, setPrice] = useState("");
  const [tag, setTag] = useState("");
  const [text, setText] = useState("");
  const [suggestions, setSuggestions] = useState("");
  const [photos, setPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/restaurants/${restaurant.id}/dishes`, { auth: false }).then(setDishes).catch(() => {});
  }, [restaurant.id]);

  async function addPhoto(e) {
    const file = e.target.files[0];
    e.target.value = "";
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type))
      return setError("Please choose a JPG, PNG or WEBP image.");
    if (file.size > 5 * 1024 * 1024) return setError("Image must be 5 MB or smaller.");
    setError("");
    setUploading(true);
    try {
      const url = await uploadPhoto(file);
      setPhotos((p) => [...p, url]);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function submit(e) {
    e.preventDefault();
    if (!rating) return setError("Please choose a star rating.");
    if (!tag) return setError("Please tell us if the price was cheap, fair or expensive.");
    setError("");
    setBusy(true);
    try {
      await api("/reviews", {
        method: "POST",
        body: {
          restaurant_id: restaurant.id,
          dish_name: dish,
          rating,
          price_paid: Number(price),
          price_tag: tag,
          text,
          suggestions: suggestions.trim() || null,
          photo_urls: photos,
        },
      });
      navigate(`/restaurants/${restaurant.id}`);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className={card}>
      <div>
        <p className="text-sm text-gray-500">Reviewing</p>
        <h1 className="text-xl font-semibold">{restaurant.name}</h1>
        <button type="button" onClick={onChange} className="text-sm text-orange-600 underline">
          Choose a different restaurant
        </button>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Dish name</label>
        <input className={input} list="dish-list" placeholder="e.g. Chicken Dum Biryani" value={dish} onChange={(e) => setDish(e.target.value)} minLength={2} required />
        <datalist id="dish-list">
          {dishes.map((d) => (
            <option key={d.id} value={d.name} />
          ))}
        </datalist>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Overall rating</label>
        <div className="flex gap-1 text-3xl">
          {[1, 2, 3, 4, 5].map((n) => (
            <button key={n} type="button" onClick={() => setRating(n)} className={n <= rating ? "text-amber-500" : "text-gray-300"} aria-label={`${n} stars`}>
              ★
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Price you paid (₹)</label>
        <input className={input} type="number" min="1" placeholder="e.g. 250" value={price} onChange={(e) => setPrice(e.target.value)} required />
        <div className="mt-2 flex gap-2">
          {TAGS.map(([key, label]) => (
            <button key={key} type="button" onClick={() => setTag(key)} className={`flex-1 rounded-lg border py-2 text-sm ${tag === key ? "border-orange-500 bg-orange-50 font-medium" : ""}`}>
              {label}
            </button>
          ))}
        </div>
        <p className="mt-1 text-xs text-gray-500">Was the price cheap, fair or expensive for what you got?</p>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Your review</label>
        <textarea className={input} rows={4} placeholder="How was the taste, portion and service?" value={text} onChange={(e) => setText(e.target.value)} minLength={5} maxLength={2000} required />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Suggestions to improve (optional)</label>
        <textarea className={input} rows={2} value={suggestions} onChange={(e) => setSuggestions(e.target.value)} maxLength={1000} />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Photos (up to 3)</label>
        <div className="flex flex-wrap gap-2">
          {photos.map((url) => (
            <div key={url} className="relative">
              <img src={url} alt="Your dish" className="h-20 w-20 rounded-lg object-cover" />
              <button type="button" onClick={() => setPhotos((p) => p.filter((u) => u !== url))} className="absolute -right-2 -top-2 h-6 w-6 rounded-full bg-gray-800 text-xs text-white" aria-label="Remove photo">
                ×
              </button>
            </div>
          ))}
          {photos.length < 3 && (
            <label className="flex h-20 w-20 cursor-pointer items-center justify-center rounded-lg border-2 border-dashed text-center text-xs text-gray-500">
              {uploading ? "Uploading…" : "+ Add photo"}
              <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={addPhoto} disabled={uploading} />
            </label>
          )}
        </div>
      </div>

      {error && <p className="rounded-lg bg-red-50 p-2 text-sm text-red-600">{error}</p>}

      <button disabled={busy || uploading} className="w-full rounded-lg bg-orange-600 py-2 font-medium text-white hover:bg-orange-700 disabled:opacity-60">
        {busy ? "Posting…" : "Post review"}
      </button>
    </form>
  );
}
