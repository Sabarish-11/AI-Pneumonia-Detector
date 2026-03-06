import React from "react";
import "./ResultCard.css";

function ResultCard({ result }) {
  if (!result) return null;

  const isNormal = result.prediction === "NORMAL";
  const confidencePercent = (result.confidence * 100).toFixed(2);

  let riskLabel = "";
  let riskClass = "";

  if (result.prediction === "PNEUMONIA") {
    if (result.confidence >= 0.85) {
      riskLabel = "High risk – strong AI indication of pneumonia";
      riskClass = "risk-high";
    } else if (result.confidence >= 0.6) {
      riskLabel = "Moderate risk – AI suggests possible pneumonia";
      riskClass = "risk-medium";
    } else {
      riskLabel = "Low confidence – AI is uncertain, clinical review required";
      riskClass = "risk-low";
    }
  } else {
    if (result.confidence >= 0.85) {
      riskLabel = "Low risk – AI suggests lungs appear normal";
      riskClass = "risk-low";
    } else {
      riskLabel = "Uncertain – AI is not confident, clinical correlation advised";
      riskClass = "risk-medium";
    }
  }

  return (
    <div className="result-card">
      <h2>AI Interpretation</h2>
      <p className={isNormal ? "normal" : "pneumonia"}>{result.prediction}</p>
      <p>Confidence: {confidencePercent}%</p>
      <p className={riskClass}>{riskLabel}</p>
    </div>
  );
}

export default ResultCard;
