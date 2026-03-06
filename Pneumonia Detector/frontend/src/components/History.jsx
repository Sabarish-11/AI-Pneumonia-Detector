import React from "react";

function History({ items }) {
  if (!items || items.length === 0) {
    return (
      <p style={{ marginTop: "20px", textAlign: "center" }}>
        No history yet.
      </p>
    );
  }

  return (
    <div className="history">
      <h2>Previous Predictions</h2>
      <table>
        <thead>
          <tr>
            <th>Image</th>
            <th>Label</th>
            <th>Confidence</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.id}>
              <td>{p.image_name}</td>
              <td>{p.label}</td>
              <td>{(p.confidence * 100).toFixed(1)}%</td>
              <td>{new Date(p.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default History;
