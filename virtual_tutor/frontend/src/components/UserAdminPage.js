import React, { useState, useEffect } from 'react';
import AdminSidebar from './AdminSidebar';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';

import AdminTutorsPage from './AdminTutorsPage';
import AdminStudentsPage from './AdminStudentsPage';
import AdminAuditLogsPage from './AdminAuditLogsPage';

function UserAdminPage({ onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();

  const [selectedMenu, setSelectedMenu] = useState('tutors');

  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  const handleThemeToggle = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('darkMode', JSON.stringify(newMode));
    document.body.style.background = newMode ? '#0f0f23' : '#ffffff';
    document.body.style.color = newMode ? '#e5e5e5' : '#0f172a';
    document.body.style.transition = 'all 0.3s ease';
  };

  useEffect(() => {
    document.body.style.background = isDarkMode ? '#0f0f23' : '#ffffff';
    document.body.style.color = isDarkMode ? '#e5e5e5' : '#0f172a';
  }, [isDarkMode]);

  // ✅ URL -> selectedMenu 同步
  useEffect(() => {
    const p = location.pathname;
    if (p.includes('/admin/tutors')) setSelectedMenu('tutors');
    else if (p.includes('/admin/students')) setSelectedMenu('students');
    else if (p.includes('/admin/audit-logs')) setSelectedMenu('audit');
  }, [location.pathname]);

  // ✅ 菜单点击 -> 跳转路由
  const handleSelectMenu = (key) => {
    setSelectedMenu(key);
    if (key === 'tutors') navigate('/admin/tutors');
    if (key === 'students') navigate('/admin/students');
    if (key === 'audit') navigate('/admin/audit-logs');
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <AdminSidebar
        selectedMenu={selectedMenu}
        onSelectMenu={handleSelectMenu}
        onLogout={onLogout}
        isDarkMode={isDarkMode}
        onThemeToggle={handleThemeToggle}
      />

      <div style={{ flex: 1, overflow: 'auto' }}>
        <Routes>
          <Route path="/" element={<Navigate to="tutors" replace />} />
          <Route path="tutors" element={<AdminTutorsPage isDarkMode={isDarkMode} />} />
          <Route path="students" element={<AdminStudentsPage isDarkMode={isDarkMode} />} />
          <Route path="audit-logs" element={<AdminAuditLogsPage isDarkMode={isDarkMode} />} />
          <Route path="*" element={<Navigate to="tutors" replace />} />
        </Routes>
      </div>
    </div>
  );
}

export default UserAdminPage;
