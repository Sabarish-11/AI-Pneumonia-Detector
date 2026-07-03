import React, { useState, useRef } from "react";
import "./UploadBox.css";

function UploadBox({ file, setFile, handlePredict, loading, errorMessage }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      // Basic type validation
      if (droppedFile.type.startsWith("image/")) {
        setFile(droppedFile);
      }
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files && e.target.files[0] ? e.target.files[0] : null;
    setFile(selectedFile);
  };

  const handleClearFile = (e) => {
    e.stopPropagation(); // Prevent triggering browse click on container
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  };

  return (
    <div className="upload-box-wrapper">
      <div
        className={`upload-dropzone ${isDragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
      >
        <input
          type="file"
          ref={fileInputRef}
          className="hidden-file-input"
          accept="image/png,image/jpeg,image/jpg,image/webp"
          onChange={handleFileChange}
        />

        {!file ? (
          <div className="upload-prompt">
            <div className="upload-icon-cloud">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 16V11M12 11L9.5 13.5M12 11L14.5 13.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M17.5 18H18C20.2091 18 22 16.2091 22 14C22 11.9654 20.4851 10.2847 18.5 10.0436C18.2255 6.63412 15.4124 4 12 4C9.176 4 6.7454 5.82086 5.88102 8.44199C3.6934 8.9482 2 10.8924 2 13.25C2 15.8734 4.12665 18 6.75 18H7.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3>Drag & Drop Chest X-ray</h3>
            <p className="upload-subtext">or click to browse your computer</p>
            <span className="upload-formats">Supports JPEG, PNG, WebP (Max 10MB)</span>
          </div>
        ) : (
          <div className="selected-file-details">
            <div className="file-icon-wrapper">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M9 17H15M9 13H15M12 9H12.01M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17 21Z" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div className="file-info-text">
              <span className="file-name">{file.name}</span>
              <span className="file-size">{formatBytes(file.size)}</span>
            </div>
            <button className="clear-file-btn" onClick={handleClearFile} title="Remove image">
              &times;
            </button>
          </div>
        )}
      </div>

      {errorMessage && <p className="upload-error-msg">{errorMessage}</p>}

      <button 
        className="predict-action-btn"
        onClick={handlePredict} 
        disabled={loading || !file}
      >
        {loading ? (
          <span className="spinner-loader">
            <span className="spinner"></span>
            Analyzing Scan...
          </span>
        ) : (
          "Run AI Diagnostics"
        )}
      </button>
    </div>
  );
}

export default UploadBox;
