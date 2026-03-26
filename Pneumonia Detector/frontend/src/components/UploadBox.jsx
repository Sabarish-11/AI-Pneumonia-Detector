import React from "react";
import "./UploadBox.css";

function UploadBox({ setFile, handlePredict, loading, errorMessage }) {
  return (
    <div className="upload-box">
      <h2>Upload Chest X-ray</h2>
      <input
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/webp"
        onChange={(e) => {
          const f = e.target.files && e.target.files[0] ? e.target.files[0] : null;
          setFile(f);
        }}
      />
      {errorMessage && <p className="upload-error">{errorMessage}</p>}
      <button onClick={handlePredict} disabled={loading}>
        {loading ? "Analyzing..." : "Run Prediction"}
      </button>
    </div>
  );
}

export default UploadBox;
