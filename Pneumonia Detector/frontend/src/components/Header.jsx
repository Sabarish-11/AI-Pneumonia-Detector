import React from "react";
import "./Header.css";

function Header() {
  return (
    <header className="dashboard-header">
      <div className="dashboard-logo-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      <div className="dashboard-header-text">
        <h1>Pneumonia Detection</h1>
        <p>AI-assisted Chest X-ray Analysis Workspace</p>
      </div>
    </header>
  );
}

export default Header;
