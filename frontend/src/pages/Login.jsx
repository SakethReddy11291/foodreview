import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Login() {
  const { user, login, signup } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(form.email, form.password);
      else await signup(form.name, form.email, form.password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const input = "w-full rounded-lg border border-gray-300 px-3 py-2 outline-none focus:border-orange-500";

  return (
    <div className="flex min-h-screen items-center justify-center bg-orange-50 p-4">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 rounded-2xl bg-white p-6 shadow">
        <h1 className="text-center text-2xl font-bold text-orange-600">🍛 FoodReview</h1>
        <p className="text-center text-sm text-gray-500">Find where to eat, from real reviews</p>

        {mode === "signup" && (
          <input className={input} placeholder="Your name" value={form.name} onChange={set("name")} required />
        )}
        <input className={input} type="email" placeholder="Email" value={form.email} onChange={set("email")} required />
        <input
          className={input}
          type="password"
          placeholder="Password (8+ characters)"
          value={form.password}
          onChange={set("password")}
          minLength={8}
          required
        />

        {error && <p className="rounded-lg bg-red-50 p-2 text-sm text-red-600">{error}</p>}

        <button
          disabled={busy}
          className="w-full rounded-lg bg-orange-600 py-2 font-medium text-white hover:bg-orange-700 disabled:opacity-60"
        >
          {busy ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
        </button>

        <p className="text-center text-sm text-gray-600">
          {mode === "login" ? "New here?" : "Already have an account?"}{" "}
          <button
            type="button"
            className="text-orange-600 underline"
            onClick={() => {
              setMode(mode === "login" ? "signup" : "login");
              setError("");
            }}
          >
            {mode === "login" ? "Create an account" : "Log in"}
          </button>
        </p>
      </form>
    </div>
  );
}
