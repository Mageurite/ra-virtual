import React, { useEffect, useMemo, useState } from "react";
import tutorService from "../services/tutorService";

export default function AdminTutorsPage({ isDarkMode }) {
  const [loading, setLoading] = useState(false);
  const [tutors, setTutors] = useState([]);
  const [error, setError] = useState("");

  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", target_language: "English" });

  const theme = useMemo(() => ({
    pageBg: isDarkMode ? "#0f0f23" : "#f3f4ff",
    cardBg: isDarkMode ? "rgba(26,26,46,0.92)" : "rgba(255,255,255,0.95)",
    text: isDarkMode ? "#e5e7eb" : "#0f172a",
    subText: isDarkMode ? "#94a3b8" : "#64748b",
    border: isDarkMode ? "1px solid rgba(148,163,184,0.15)" : "1px solid rgba(15,23,42,0.08)",
    header: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  }), [isDarkMode]);

  const studentLoginUrl = (tutorId) => `${window.location.origin}/session/${tutorId}/login`;

  const loadTutors = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await tutorService.list();
      const list = Array.isArray(res) ? res : (res?.items || res?.data || []);
      setTutors(list);
    } catch (e) {
      setError(e?.message || "Failed to load tutors");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTutors(); }, []);

  const handleCreate = async () => {
    setError("");
    if (!form.name.trim()) {
      setError("Tutor name is required");
      return;
    }
    setLoading(true);
    try {
      await tutorService.create({
        name: form.name.trim(),
        target_language: form.target_language,
      });
      setOpen(false);
      setForm({ name: "", target_language: "English" });
      await loadTutors();
    } catch (e) {
      setError(e?.message || "Failed to create tutor");
    } finally {
      setLoading(false);
    }
  };

  const copy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      alert("Copied!");
    } catch {
      alert("Copy failed, please copy manually.");
    }
  };

  return (
    <div style={{ minHeight: "100%", padding: 24, background: theme.pageBg }}>
      <div style={{
        background: theme.header, color: "#fff", borderRadius: 16,
        padding: "18px 20px", display: "flex", justifyContent: "space-between", alignItems: "center"
      }}>
        <div>
          <div style={{ fontSize: 20, fontWeight: 800 }}>Tutors</div>
          <div style={{ fontSize: 12, opacity: 0.9 }}>Create tutors and share student login URLs</div>
        </div>
        <button
          onClick={() => setOpen(true)}
          style={{
            border: "none", borderRadius: 12, padding: "10px 14px",
            background: "rgba(255,255,255,0.18)", color: "#fff", cursor: "pointer", fontWeight: 700
          }}
        >
          Create Tutor
        </button>
      </div>

      {error && (
        <div style={{ marginTop: 14, background: "rgba(239,68,68,0.12)", color: "#ef4444", borderRadius: 12, padding: 12 }}>
          {error}
        </div>
      )}

      <div style={{
        marginTop: 16, background: theme.cardBg, borderRadius: 16, padding: 16,
        border: theme.border
      }}>
        <div style={{ color: theme.subText, fontSize: 12, marginBottom: 10 }}>
          {loading ? "Loading..." : `Total: ${tutors.length}`}
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: 0 }}>
            <thead>
              <tr style={{ color: theme.subText, fontSize: 12 }}>
                <th style={{ textAlign: "left", padding: 10 }}>ID</th>
                <th style={{ textAlign: "left", padding: 10 }}>Name</th>
                <th style={{ textAlign: "left", padding: 10 }}>Target Language</th>
                <th style={{ textAlign: "left", padding: 10 }}>Student Login URL</th>
                <th style={{ textAlign: "left", padding: 10 }}>Actions</th>
              </tr>
            </thead>
            <tbody style={{ color: theme.text, fontSize: 14 }}>
              {tutors.length === 0 ? (
                <tr><td colSpan={5} style={{ padding: 16, color: theme.subText }}>No tutors yet.</td></tr>
              ) : tutors.map(t => (
                <tr key={t.id} style={{ borderTop: theme.border }}>
                  <td style={{ padding: 10 }}>{t.id}</td>
                  <td style={{ padding: 10 }}>{t.name || "-"}</td>
                  <td style={{ padding: 10 }}>{t.target_language || "-"}</td>
                  <td style={{ padding: 10 }}>
                    <span style={{ fontSize: 12, color: theme.subText }}>{studentLoginUrl(t.id)}</span>
                  </td>
                  <td style={{ padding: 10 }}>
                    <button
                      onClick={() => copy(studentLoginUrl(t.id))}
                      style={{ border: "none", borderRadius: 10, padding: "8px 10px", cursor: "pointer" }}
                    >
                      Copy URL
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {open && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999
        }} onClick={() => setOpen(false)}>
          <div style={{
            width: 420, background: theme.cardBg, borderRadius: 16, padding: 18,
            border: theme.border
          }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontWeight: 800, color: theme.text, marginBottom: 12 }}>Create Tutor</div>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <input
                value={form.name}
                onChange={(e) => setForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Tutor name"
                style={{ padding: 12, borderRadius: 12, border: theme.border, background: "transparent", color: theme.text }}
              />
              <input
                value={form.target_language}
                onChange={(e) => setForm(prev => ({ ...prev, target_language: e.target.value }))}
                placeholder="Target language (e.g. English)"
                style={{ padding: 12, borderRadius: 12, border: theme.border, background: "transparent", color: theme.text }}
              />
            </div>

            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 14 }}>
              <button onClick={() => setOpen(false)} style={{ padding: "10px 12px", borderRadius: 12, border: "none" }}>
                Cancel
              </button>
              <button onClick={handleCreate} style={{ padding: "10px 12px", borderRadius: 12, border: "none", fontWeight: 800 }}>
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
