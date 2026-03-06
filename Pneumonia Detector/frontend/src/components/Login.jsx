import React, { useState } from "react";
import { Link } from "react-router-dom";

import api from "../api";

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      alert("Please enter email and password.");
      return;
    }
    try {
      setLoading(true);
      const response = await api.post("/login", {
        email,
        password,
      });
      localStorage.setItem("access_token", response.data.access_token);
      onLoginSuccess();
    } catch (err) {
      console.error(err);
      alert("Login failed. Check email/password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      <form className="auth-form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      <p style={{ marginTop: "10px", textAlign: "center" }}>
  New user? <Link to="/register">Register here</Link>
        </p>

    </div>
  );
}

export default Login;
