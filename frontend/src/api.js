const BASE = import.meta.env.VITE_API_URL || "http://localhost:8001";

export function getToken() {
  try {
    return localStorage.getItem("token");
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");
  } catch {
    /* storage unavailable */
  }
}

export async function api(path, { method = "GET", body, auth = true } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const data = await res.json();
      message =
        typeof data.detail === "string" ? data.detail : data.detail?.[0]?.msg || message;
    } catch {
      /* keep default message */
    }
    const error = new Error(message);
    error.status = res.status;
    throw error;
  }
  return res.json();
}
