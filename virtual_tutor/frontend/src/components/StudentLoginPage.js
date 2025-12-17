import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import authService from "../services/authService";

export default function StudentLoginPage({ onLoginSuccess }) {
  const { tutorId } = useParams();
  const navigate = useNavigate();
  const [studentId, setStudentId] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");

    const res = await authService.studentLogin({
      tutor_id: Number(tutorId),
      student_id: studentId,
      password,
    });

    if (!res.success) {
      setErr(res.message || "Login failed");
      return;
    }

    onLoginSuccess({ role: "student" });
    navigate(`/session/${tutorId}`);
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Student Login</h2>
      <div style={{ opacity: 0.7 }}>Tutor ID: {tutorId}</div>

      {err ? <div style={{ color: "red" }}>{err}</div> : null}

      <form onSubmit={onSubmit}>
        <div>
          <label>Student ID</label><br />
          <input value={studentId} onChange={(e) => setStudentId(e.target.value)} />
        </div>
        <div style={{ marginTop: 12 }}>
          <label>Password</label><br />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button style={{ marginTop: 16 }} type="submit">Login</button>
      </form>
    </div>
  );
}
