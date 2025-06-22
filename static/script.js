// Login handler
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  document.getElementById("message").textContent = data.status === "success" 
    ? "Login successful!" : data.message;
});

// Register handler
document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const first_name = document.getElementById("firstName").value;
  const last_name = document.getElementById("lastName").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ first_name, last_name, email, password })
  });

  const data = await res.json();
  document.getElementById("message").textContent = data.status === "success" 
    ? "Account created!" : data.message;
});
