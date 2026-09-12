/**
 * Redirects logged-out visitors to the login page. Include before any other
 * script on pages that require a session (index.html, history.html, dashboard.html).
 */
(async () => {
  try {
    const response = await fetch("/auth/me");
    const data = await response.json();
    if (!data.authenticated) {
      window.location.href = "./login.html";
    }
  } catch (err) {
    window.location.href = "./login.html";
  }
})();
