const Auth = {
  token: () => localStorage.getItem("token"),
  role: () => localStorage.getItem("role"),
  name: () => localStorage.getItem("name"),
  save(d) { localStorage.setItem("token", d.token); localStorage.setItem("role", d.role); localStorage.setItem("name", d.name); },
  logout() { localStorage.clear(); location.href = "/index.html"; },
};

async function api(path, method = "GET", body) {
  const res = await fetch("/api" + path, {
    method,
    headers: { "Content-Type": "application/json", ...(Auth.token() ? { Authorization: "Bearer " + Auth.token() } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && Auth.token()) Auth.logout();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

// Call on protected pages. adminOnly redirects non-staff (UI guard only; server enforces the real rule).
function guard(adminOnly = false) {
  if (!Auth.token()) location.href = "/index.html";
  if (adminOnly && Auth.role() !== "librarian") location.href = "/dashboard.html";
}

function renderNav() {
  const admin = Auth.role() === "librarian" ? '<a href="/admin.html">Admin</a>' : "";
  document.getElementById("nav").innerHTML =
    `<strong>📚 Library</strong><a href="/dashboard.html">Books</a><a href="/profile.html">My Loans</a>${admin}
     <span class="spacer"></span><span>${esc(Auth.name())}</span><a href="#" onclick="Auth.logout()">Logout</a>`;
}

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
