import React from "react";
import "./UploadBox.css";

function UploadBox({ setFile, handlePredict, loading }) {
  return (
    <div className="upload-box">
      <h2>Upload Chest X‑ray</h2>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => {
          const f = e.target.files && e.target.files[0] ? e.target.files[0] : null;
          setFile(f);
        }}
      />
      <button onClick={handlePredict} disabled={loading}>
        {loading ? "Analyzing..." : "Run Prediction"}
      </button>
    </div>
  );
}

export default UploadBox;
