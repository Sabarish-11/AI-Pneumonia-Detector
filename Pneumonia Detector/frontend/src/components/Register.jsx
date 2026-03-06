import React, { useState } from "react";
import api from "../api";
import { Link } from "react-router-dom";


function Register({ onRegisterSuccess }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      alert("Please fill all fields.");
      return;
    }
    try {
      setLoading(true);
      await api.post("/register", { name, email, password });
      alert("Registered successfully. You can login now.");
      onRegisterSuccess();
    } catch (err) {
      console.error(err);
      alert("Register failed. Maybe email already exists.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>Register</h2>
      <form className="auth-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Full name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

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
          {loading ? "Registering..." : "Register"}
        </button>
      </form>

      <p style={{ marginTop: "10px", textAlign: "center" }}>
  Already have an account? <Link to="/login">Login</Link>
</p>

    </div>
  );
}

export default Register;
