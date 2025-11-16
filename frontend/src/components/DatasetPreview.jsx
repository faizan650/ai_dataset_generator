// DatasetPreview.jsx
import React from "react";

export default function DatasetPreview({ data = [] }) {
  if (!data || data.length === 0) {
    return <div className="small-muted">No preview available yet.</div>;
  }

  return (
    <div style={{ maxHeight: 300, overflow: "auto" }}>
      <pre style={{ fontSize: 13, lineHeight: 1.5 }}>
        {data.map((obj, i) => {
          try {
            return JSON.stringify(obj, null, 2) + (i < data.length - 1 ? "\n\n" : "");
          } catch {
            return String(obj) + (i < data.length - 1 ? "\n\n" : "");
          }
        }).join("")}
      </pre>
    </div>
  );
}
