/**
 * CacauFito Login / Registration Page
 */

const form = document.getElementById("auth-form");
const identifierInput = document.getElementById("identifier");
const passwordInput = document.getElementById("password");
const errorEl = document.getElementById("auth-error");
const errorMessageEl = document.getElementById("auth-error-message");
const submitBtn = document.getElementById("submit-btn");
const toggleModeBtn = document.getElementById("toggle-mode-btn");
const formTitle = document.getElementById("form-title");

let mode = "login"; // or "register"

toggleModeBtn.addEventListener("click", () => {
  mode = mode === "login" ? "register" : "login";
  if (mode === "register") {
    formTitle.textContent = "Criar conta";
    submitBtn.textContent = "Criar conta";
    toggleModeBtn.textContent = "Já tenho conta";
  } else {
    formTitle.textContent = "Entrar";
    submitBtn.textContent = "Entrar";
    toggleModeBtn.textContent = "Criar conta";
  }
  errorEl.hidden = true;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorEl.hidden = true;

  const identifier = identifierInput.value.trim();
  const password = passwordInput.value;

  try {
    if (mode === "register") {
      const registerResponse = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, password }),
      });
      if (!registerResponse.ok) {
        const data = await registerResponse.json().catch(() => ({}));
        throw new Error(data.detail || "Não foi possível criar a conta.");
      }
    }

    const loginResponse = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password }),
    });
    if (!loginResponse.ok) {
      const data = await loginResponse.json().catch(() => ({}));
      throw new Error(data.detail || "Credenciais inválidas.");
    }

    window.location.href = "./";
  } catch (err) {
    errorEl.hidden = false;
    errorMessageEl.textContent = err.message;
  }
});
