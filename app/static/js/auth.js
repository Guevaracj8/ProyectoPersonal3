if (localStorage.getItem("ferrestock_token")) {
  window.location.href = "/dashboard";
}

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const email    = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const errorDiv = document.getElementById("errorMsg");
  const btn      = document.getElementById("loginBtn");

  errorDiv.classList.add("hidden");
  btn.disabled    = true;
  btn.textContent = "Iniciando...";

  try {
    const res = await fetch("/api/auth/login/json", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Error al iniciar sesión.");
    }

    localStorage.setItem("ferrestock_token", data.access_token);
    localStorage.setItem("ferrestock_rol",   data.rol);

    window.location.href = "/dashboard";

  } catch (err) {
    errorDiv.textContent = err.message;
    errorDiv.classList.remove("hidden");
  } finally {
    btn.disabled    = false;
    btn.textContent = "Iniciar Sesión";
  }
});
