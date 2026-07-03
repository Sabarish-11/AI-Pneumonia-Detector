import React from "react";
import "./ResultCard.css";

function ResultCard({ result }) {
  if (!result) return null;

  const isNormal = result.prediction === "NORMAL";
  const confidencePercent = (result.confidence * 100).toFixed(1);

  let riskLabel = "";
  let riskClass = "";
  let statusBadgeText = "";

  if (result.prediction === "PNEUMONIA") {
    statusBadgeText = "Pathology Detected";
    if (result.confidence >= 0.85) {
      riskLabel = "CRITICAL DIAGNOSIS: High risk of pneumonia. Urgent clinical escalation advised.";
      riskClass = "status-critical";
    } else if (result.confidence >= 0.6) {
      riskLabel = "ELEVATED RISK: Suggests potential pneumonia flags. Clinical triage requested.";
      riskClass = "status-warning";
    } else {
      riskLabel = "MARGINAL INDICATION: Low AI confidence. Secondary radiographic examination suggested.";
      riskClass = "status-marginal";
    }
  } else {
    statusBadgeText = "No Anomalies Found";
    if (result.confidence >= 0.85) {
      riskLabel = "CLEAR DIAGNOSIS: High probability of clear lung scans. Standard follow-up.";
      riskClass = "status-clear";
    } else {
      riskLabel = "BORDERLINE NORMAL: Low AI confidence normal index. Clinician correlation advised.";
      riskClass = "status-marginal";
    }
  }

  return (
    <div className={`diagnostic-card-wrapper ${isNormal ? "diag-normal" : "diag-pneumonia"}`}>
      <div className="diagnostic-badge-row">
        <span className="analysis-tag">Radiology Diagnostics</span>
        <span className={`diagnostic-status-pill ${riskClass}`}>
          {statusBadgeText}
        </span>
      </div>

      <div className="diagnostic-main-content">
        {/* Left Side Shield Icon */}
        <div className="diagnostic-status-icon">
          {isNormal ? (
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          ) : (
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </div>

        {/* Diagnostic Results Text */}
        <div className="diagnostic-results-info">
          <h2>{result.prediction}</h2>
          <div className="confidence-indicator-row">
            <span className="confidence-label">AI Diagnostic Confidence:</span>
            <span className="confidence-percentage">{confidencePercent}%</span>
          </div>
        </div>
      </div>

      {/* Graphical Progress Bar */}
      <div className="diagnostic-progress-bar-container">
        <div 
          className="diagnostic-progress-fill" 
          style={{ 
            width: `${confidencePercent}%`,
            background: isNormal 
              ? "linear-gradient(90deg, #10b981 0%, #059669 100%)" 
              : "linear-gradient(90deg, #f59e0b 0%, #ef4444 100%)"
          }}
        ></div>
      </div>

      {/* Clinical Warning Details Footer */}
      <div className="diagnostic-footer-warning">
        <p className={riskClass}>{riskLabel}</p>
      </div>
    </div>
  );
}

export default ResultCard;
