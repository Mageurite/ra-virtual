import React, { useEffect, useMemo, useState } from "react";
import tutorService from "../services/tutorService";
import adminStudentService from "../services/adminStudentService";

export default function AdminStudentsPage({ isDarkMode }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [tutors, setTutors] = useState([]);
  const [tutorId, setTutorId] = useState("");

  const [students, setStudents] = useState([]);

  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ email: "", password: "" });

  const theme = useMemo(() => ({
    pageBg: isDarkMode ? "#0f0f23" : "#f3f4ff",
    cardBg: isDarkMode ? "rgba(26,26,46,0.92)" : "rgba(255,255,255,0.95)",
    text: isDarkMode ? "#e5e7eb" : "#0f172a",
    subText: isDarkMode ? "#94a3b8" : "#64748b",
    border: isDarkMode ? "1px solid rgba(148,163,184,0.15)" : "1px solid rgba(15,23,42,0.08)",
    header: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  }), [isDarkMode]);

  const loadTutors = async () => {
    const res = await tutorService.list();
    const list = Array.isArray(res) ? res : (res?.items || res?.data || []);
    setTutors(list);
    if (!tutorId && list.length) setTutorId(String(list[0].id));
  };

  const loadStudents = async (tid) => {
    if (!tid) return;
    const res = await adminStudentService.list(tid);
    const list = Array.isArray(res) ? res : (res?.items || res?.data || []);
    setStudents(list);
  };

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError("");
      try {
        await loadTutors();
      } catch (e) {
        setError(e?.message || "Failed to load tutors");
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    (async () => {
      if (!tutorId) return;
      setLoading(true);
      setError("");
      try {
        await loadStudents(tutorId);
      } catch (e) {
        setError(e?.message || "Failed to load students");
      } finally {
        setLoading(false);
      }
    })();
  }, [tutorId]);

  const handleCreate = async () => {
    setError("");
    if (!tutorId) return setError("Please select a tutor first");
    if (!form.email.trim()) return setError("Student email is required");
    if (!form.password) return setError("Initial password is required");

    setLoading(true);
    try {
      const res = await adminStudentService.create(tutorId, {
        email: form.email.trim(),
        password: form.password,
      });
      setOpen(false);
      setForm({ email: "", password: "" });

      // 有些后端会返回生成的密码/账号信息，你可以在这里提示
      if (res?.password) alert(`Created! Initial password: ${res.password}`);
      await loadStudents(tutorId);
    } catch (e) {
      setError(e?.message || "Failed to create student");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100%", padding: 24, background: theme.pageBg }}>
      <div style={{
        background: theme.header, color: "#fff", borderRadius: 16,
        padding: "18px 20px", display: "flex", justifyContent: "space-between", alignItems: "center"
      }}>
        <div>
          <div style={{ fontSize: 20, fontWeight: 800 }}>Students</div>
          <div style={{ fontSize: 12, opacity: 0.9 }}>Create/list students under a tutor</div>
        </div>
        <button
          onClick={() => setOpen(true)}
          style={{
            border: "none", borderRadius: 12, padding: "10px 14px",
            background: "rgba(255,255,255,0.18)", color: "#fff", cursor: "pointer", fontWeight: 700
          }}
        >
          Create Student
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
        <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12 }}>
          <div style={{ color: theme.subText, fontSize: 12 }}>Tutor:</div>
          <select
            value={tutorId}
            onChange={(e) => setTutorId(e.target.value)}
            style={{ padding: 10, borderRadius: 12, border: theme.border, background: "transparent", color: theme.text }}
          >
            {tutors.map(t => (
              <option key={t.id} value={t.id}>{t.name || `Tutor #${t.id}`}</option>
            ))}
          </select>
          <div style={{ marginLeft: "auto", color: theme.subText, fontSize: 12 }}>
            {loading ? "Loading..." : `Total: ${students.length}`}
          </div>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: 0 }}>
            <thead>
              <tr style={{ color: theme.subText, fontSize: 12 }}>
                <th style={{ textAlign: "left", padding: 10 }}>ID</th>
                <th style={{ textAlign: "left", padding: 10 }}>Email</th>
                <th style={{ textAlign: "left", padding: 10 }}>Active</th>
                <th style={{ textAlign: "left", padding: 10 }}>Created At</th>
              </tr>
            </thead>
            <tbody style={{ color: theme.text, fontSize: 14 }}>
              {students.length === 0 ? (
                <tr><td colSpan={4} style={{ padding: 16, color: theme.subText }}>No students yet.</td></tr>
              ) : students.map(s => (
                <tr key={s.id}>
                  <td style={{ padding: 10 }}>{s.id}</td>
                  <td style={{ padding: 10 }}>{s.email || s.username || "-"}</td>
                  <td style={{ padding: 10 }}>{String(s.is_active ?? s.active ?? true)}</td>
                  <td style={{ padding: 10 }}>{s.created_at || "-"}</td>
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
            <div style={{ fontWeight: 800, color: theme.text, marginBottom: 12 }}>Create Student</div>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <input
                value={form.email}
                onChange={(e) => setForm(prev => ({ ...prev, email: e.target.value }))}
                placeholder="Student email"
                style={{ padding: 12, borderRadius: 12, border: theme.border, background: "transparent", color: theme.text }}
              />
              <input
                value={form.password}
                onChange={(e) => setForm(prev => ({ ...prev, password: e.target.value }))}
                placeholder="Initial password"
                type="password"
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
