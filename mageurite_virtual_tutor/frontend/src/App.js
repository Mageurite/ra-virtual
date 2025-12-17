import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AuthPage from './components/AuthPage';
import HomePage from './components/HomePage';
import UserAdminPage from './components/UserAdminPage';
import TokenExpiryModal from './components/TokenExpiryModal';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import { Button } from '@mui/material';
import authService from './services/authService';
import tokenService from './services/tokenService';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// 創建主題
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));
  const [userRole, setUserRole] = useState(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      return user.role;
    }
    return null;
  });
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [tokenModalData, setTokenModalData] = useState({
    isExpired: false,
    remainingTime: 0
  });

  const handleLoginSuccess = (userData) => {
    setIsLoggedIn(true);
    setUserRole(userData.role);
    // 登录成功后开始token监控
    tokenService.startTokenMonitoring(handleTokenExpired, handleTokenWarning);
  };

  const handleLogout = () => {
    authService.logout();
    tokenService.stopTokenMonitoring();
    setIsLoggedIn(false);
    setUserRole(null);
  };

  // Token过期处理
  const handleTokenExpired = async (message) => {
    const remainingTime = await tokenService.getTokenRemainingTime();
    setTokenModalData({
      isExpired: true,
      remainingTime: 0
    });
    setShowTokenModal(true);
  };

  // Token即将过期警告
  const handleTokenWarning = async (message) => {
    const remainingTime = await tokenService.getTokenRemainingTime();
    setTokenModalData({
      isExpired: false,
      remainingTime: remainingTime
    });
    setShowTokenModal(true);
  };

  // 延长会话
  const handleExtendSession = () => {
    setShowTokenModal(false);
    // 这里可以调用后端接口延长token有效期
    console.log('Session extended');
  };

  // 关闭token模态框
  const handleCloseTokenModal = () => {
    setShowTokenModal(false);
  };

  // Listen for localStorage changes to ensure state is in sync
  useEffect(() => {
    const checkAuthStatus = () => {
      const token = localStorage.getItem('token');
      const userStr = localStorage.getItem('user');

      if (!token) {
        setIsLoggedIn(false);
        setUserRole(null);
        tokenService.stopTokenMonitoring();
      } else if (userStr) {
        try {
          const user = JSON.parse(userStr);
          setUserRole(user.role);
          // 开始token监控
          tokenService.startTokenMonitoring(handleTokenExpired, handleTokenWarning);
        } catch (e) {
          console.error('Error parsing user data:', e);
          setIsLoggedIn(false);
          setUserRole(null);
          tokenService.stopTokenMonitoring();
        }
      }
    };

    // Check on mount
    checkAuthStatus();

    // Listen for storage events (when localStorage changes in other tabs)
    const handleStorageChange = (e) => {
      if (e.key === 'token' || e.key === 'user') {
        checkAuthStatus();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      tokenService.stopTokenMonitoring();
    };
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={
            isLoggedIn ? <Navigate to="/" /> : <AuthPage onLoginSuccess={handleLoginSuccess} />
          } />
          <Route path="/" element={
            isLoggedIn ? (
              userRole === 'tutor' ? (
                <UserAdminPage onLogout={handleLogout} />
              ) : (
                <HomePage onLogout={handleLogout} />
              )
            ) : <Navigate to="/login" />
          } />

        </Routes>

        {/* Token过期提示模态框 */}
        <TokenExpiryModal
          isOpen={showTokenModal}
          onClose={handleCloseTokenModal}
          onExtend={handleExtendSession}
          onLogout={handleLogout}
          remainingTime={tokenModalData.remainingTime}
          isExpired={tokenModalData.isExpired}
        />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
