import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthService from "../services/authService";

// 你也可以用你现有的 MUI 表单组件；这里先用最小可跑版本
export default function AdminLoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const res = await AuthService.login({ email, password }); // 你已经改成 admin 的 form-urlencoded login
    if (!res.success) {
      setError(res.message || "Login failed");
      return;
    }
    navigate("/admin/tutors");
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Admin Login</h2>
      {error ? <div style={{ color: "red" }}>{error}</div> : null}

      <form onSubmit={onSubmit}>
        <div>
          <label>Email</label><br/>
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div style={{ marginTop: 12 }}>
          <label>Password</label><br/>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>

        <button style={{ marginTop: 16 }} type="submit">Login</button>
      </form>
    </div>
  );
}
