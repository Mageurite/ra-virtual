import React from "react";

export default function AdminAuditLogsPage({ isDarkMode }) {
  return (
    <div style={{ minHeight: "100%", padding: 24, background: isDarkMode ? "#0f0f23" : "#f3f4ff" }}>
      <div style={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "#fff", borderRadius: 16, padding: "18px 20px"
      }}>
        <div style={{ fontSize: 20, fontWeight: 800 }}>Audit Logs</div>
        <div style={{ fontSize: 12, opacity: 0.9 }}>
          Hook this page to your backend audit log API when ready.
        </div>
      </div>
    </div>
  );
}
