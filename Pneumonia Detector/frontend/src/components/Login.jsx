import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

import api from "../api";
import Toast from "./Toast.jsx";

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const location = useLocation();

  useEffect(() => {
    if (location.state && location.state.toastMessage) {
      setToast({
        message: location.state.toastMessage,
        type: location.state.toastType || "error"
      });
      // Clear router state to prevent toast showing again on page refresh
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setToast({ message: "Please enter email and password.", type: "error" });
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
      const detail = err.response?.data?.detail || "Login failed. Please check your connection.";
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
          <h2>Sign In</h2>
          <p className="auth-subtitle">Access your clinical screening workspace.</p>
          
          <form className="auth-form" onSubmit={handleSubmit}>
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
              {loading ? "Authenticating..." : "Sign In to Workspace"}
            </button>
          </form>

          <p className="auth-redirect-text">
            New user? <Link to="/register">Create an account</Link>
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

export default Login;
