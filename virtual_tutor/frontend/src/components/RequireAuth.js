import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { auth } from "../utils/request";

export default function RequireAuth({ allowRoles, redirectTo, children }) {
  const location = useLocation();
  const token = localStorage.getItem("token");
  const user = auth.getUser();

  if (!token || !user) {
    return <Navigate to={redirectTo} replace state={{ from: location }} />;
  }

  if (allowRoles && !allowRoles.includes(user.role)) {
    // 角色不匹配：清掉旧 token，避免 admin/student 在同一浏览器里串号
    auth.clearAuth();
    return <Navigate to={redirectTo} replace />;
  }

  return children;
}
