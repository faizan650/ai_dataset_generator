// ProgressBar.jsx
import React from "react";

export default function ProgressBar({ progress = 0 }) {
  const pct = Math.max(0, Math.min(100, progress || 0));
  return (
    <div style={{ width: "100%" }}>
      <div className="progress-track" aria-hidden>
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
