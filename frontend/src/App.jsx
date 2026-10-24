import { Link, Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import Explore from "./pages/Explore";
import Home from "./pages/Home";
import Restaurant from "./pages/Restaurant";
import Login from "./pages/Login";

function Shell({ children }) {
  const { user, logout } = useAuth();
  return (
    <div className="min-h-screen bg-orange-50">
      <header className="flex items-center justify-between bg-white px-4 py-3 shadow-sm">
        <Link to="/" className="text-lg font-bold text-orange-600">
          🍛 FoodReview
        </Link>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-gray-600">{user?.name}</span>
          <button onClick={logout} className="rounded-lg border px-3 py-1 hover:bg-gray-100">
            Log out
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-2xl p-4">{children}</main>
    </div>
  );
}

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="p-8 text-center text-gray-500">Loading…</p>;
  return user ? <Shell>{children}</Shell> : <Navigate to="/login" replace />;
}

function ComingSoon({ title }) {
  return (
    <div className="rounded-2xl bg-white p-8 text-center shadow-sm">
      <h1 className="text-xl font-semibold">{title}</h1>
      <p className="mt-2 text-gray-500">This screen is built in the next step.</p>
      <Link to="/" className="mt-4 inline-block text-orange-600 underline">
        ← Back to home
      </Link>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected><Home /></Protected>} />
      <Route path="/explore" element={<Protected><Explore /></Protected>} />
      <Route path="/restaurants/:id" element={<Protected><Restaurant /></Protected>} />
      <Route path="/post" element={<Protected><ComingSoon title="Post a Review" /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
