const API_BASE = "/api";   

function getToken() {
  return localStorage.getItem("ferrestock_token");
}

function getRol() {
  return localStorage.getItem("ferrestock_rol");
}

function logout() {
  localStorage.removeItem("ferrestock_token");
  localStorage.removeItem("ferrestock_rol");
  window.location.href = "/";
}

function requireAuth() {
  if (!getToken()) window.location.href = "/";
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    logout();
    return null;
  }

  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.detail || `Error ${res.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }

  return data;
}

const api = {
  get:    (path)         => apiFetch(path, { method: "GET" }),
  post:   (path, body)   => apiFetch(path, { method: "POST",   body: JSON.stringify(body) }),
  put:    (path, body)   => apiFetch(path, { method: "PUT",    body: JSON.stringify(body) }),
  delete: (path)         => apiFetch(path, { method: "DELETE" }),
};
