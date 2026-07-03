import React, { useState } from "react";
import "./History.css";

function History({ items }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("ALL"); // ALL, NORMAL, PNEUMONIA

  if (!items) return null;

  // 1. Filter predictions locally by both search term and classification category
  const filteredItems = items.filter((item) => {
    const matchesSearch = item.image_name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    
    const matchesFilter = 
      filterType === "ALL" || 
      item.label === filterType;

    return matchesSearch && matchesFilter;
  });

  const formatDate = (dateStr) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <div className="dashboard-history-section">
      <div className="history-header-row">
        <h2>Diagnostic History Logs</h2>
        <span className="analysis-tag">{items.length} Total Scans</span>
      </div>

      {/* Control Panel: Search & Categorical Pills */}
      <div className="history-controls">
        <input
          type="text"
          placeholder="Search scans by file name..."
          className="history-search-input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        
        <div className="filter-pills-row">
          <button
            className={`filter-pill ${filterType === "ALL" ? "active" : ""}`}
            onClick={() => setFilterType("ALL")}
          >
            All Scans
          </button>
          <button
            className={`filter-pill ${filterType === "NORMAL" ? "active" : ""}`}
            onClick={() => setFilterType("NORMAL")}
          >
            Normal Lungs
          </button>
          <button
            className={`filter-pill ${filterType === "PNEUMONIA" ? "active" : ""}`}
            onClick={() => setFilterType("PNEUMONIA")}
          >
            Pathology Detected
          </button>
        </div>
      </div>

      {/* Scans Listing Table */}
      {filteredItems.length === 0 ? (
        <div className="history-empty-message">
          {items.length === 0 
            ? "No patient scans recorded in this workspace." 
            : "No records match the active search criteria."}
        </div>
      ) : (
        <div className="history-table-container">
          <table className="history-table">
            <thead>
              <tr>
                <th>Patient File</th>
                <th>Diagnostic Label</th>
                <th>Confidence Ratio</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((p) => (
                <tr key={p.id}>
                  <td>
                    <div className="history-file-name" title={p.image_name}>
                      {p.image_name}
                    </div>
                  </td>
                  <td>
                    <span 
                      className={`history-status-badge ${
                        p.label === "NORMAL" ? "badge-normal" : "badge-pneumonia"
                      }`}
                    >
                      {p.label === "NORMAL" ? "Normal" : "Pneumonia"}
                    </span>
                  </td>
                  <td>
                    <strong>{(p.confidence * 100).toFixed(1)}%</strong>
                  </td>
                  <td>
                    {formatDate(p.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default History;
