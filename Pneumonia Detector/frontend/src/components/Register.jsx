import React, { useState } from "react";
import api from "../api";
import { Link } from "react-router-dom";
import Toast from "./Toast.jsx";

function Register({ onRegisterSuccess }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setToast({ message: "Please fill all fields.", type: "error" });
      return;
    }
    try {
      setLoading(true);
      await api.post("/register", { name, email, password });
      onRegisterSuccess();
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail || "Register failed. Please check your connection.";
      setToast({ message: detail, type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      {/* Brand Side Column */}
      <div className="auth-brand-side">
        <div className="brand-header">
          <div className="brand-logo-icon">P</div>
          <span className="brand-name">Pneumonia Detector</span>
        </div>
        
        <div className="brand-body">
          <h1>Advanced Chest X‑ray Diagnostics</h1>
          <p>
            An enterprise-level clinical assistant powered by Deep Learning. Upload chest X‑rays to perform instantaneous diagnostic screening for pneumonia signs with high confidence analysis.
          </p>
        </div>
        
        <div className="brand-footer">
          <div className="telemetry-row">
            <div className="telemetry-item">
              <span className="telemetry-dot"></span>
              <span>AI Engine Online</span>
            </div>
          </div>
          <span>v2.1.0-secure</span>
        </div>
      </div>

      {/* Form Side Column */}
      <div className="auth-form-side">
        <div className="auth-container">
          <h2>Create Account</h2>
          <p className="auth-subtitle">Register your clinician account to begin.</p>
          
          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label">FULL NAME</label>
              <input
                type="text"
                placeholder="Dr. Alex Carter"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label className="input-label">EMAIL ADDRESS</label>
              <input
                type="email"
                placeholder="name@hospital.org"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label className="input-label">PASSWORD</label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Registering..." : "Create Account"}
            </button>
          </form>

          <p className="auth-redirect-text">
            Already have an account? <Link to="/login">Sign In</Link>
          </p>
        </div>
      </div>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

export default Register;
