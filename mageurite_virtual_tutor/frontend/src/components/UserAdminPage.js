import React, { useState } from 'react';
import AdminSidebar from './AdminSidebar';
import UserTable from './UserTable';

function UserAdminPage({ onLogout }) {
    const [selectedMenu, setSelectedMenu] = useState('user');
    const [darkMode, setDarkMode] = useState(false);

    const themeStyles = {
        background: darkMode ? '#23272f' : '#fff',
        color: darkMode ? '#e5e5e5' : '#23272f',
        sidebarBg: darkMode ? '#181c22' : '#F7F9FB',
        sidebarActive: '#FFD600',
        sidebarActiveText: '#23272f',
        sidebarText: darkMode ? '#e5e5e5' : '#23272f',
        sidebarHeaderBackground: darkMode ? '#23272f' : '#fff',
        sidebarHeaderColor: darkMode ? '#e5e5e5' : '#E64003',
        tableHeader: darkMode ? '#23272f' : '#F7F9FB',
        tableBorder: darkMode ? '#333' : '#eee',
        toolbarBg: darkMode ? '#23272f' : '#fff',
        tagText: '#fff',
        tagBg: (color) => {
            const tagColorMap = {
                blue: '#2196f3',
                yellow: '#FFD600',
                green: '#4ADE80',
                pink: '#F06292',
                red: '#FF5252',
                gray: '#BDBDBD'
            };
            return tagColorMap[color] || '#BDBDBD';
        },
        editBtn: (selected) => selected ? '#FF5252' : (darkMode ? '#888' : '#bbb'),
        editBtnBg: (selected) => selected ? '#FFF0F0' : 'transparent',
        createBtn: '#FF9800',
        createBtnText: '#fff',
        pageBtn: (active) => active ? '#FFD600' : (darkMode ? '#23272f' : '#fff'),
        pageBtnText: (active) => active ? '#23272f' : (darkMode ? '#e5e5e5' : '#23272f'),
        shadow: darkMode ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.03)',
        buttonBackground: darkMode ? '#23272f' : '#fff'
    };

    return (
        <div style={{ display: 'flex', height: '100vh', background: themeStyles.background, color: themeStyles.color }}>
            {/* 左側導航欄 */}
            <AdminSidebar
                selectedMenu={selectedMenu}
                onSelectMenu={setSelectedMenu}
                onThemeChange={setDarkMode}
                themeStyles={themeStyles}
                onLogout={onLogout}
            />

            {/* 主工作區域 */}
            <UserTable
                themeStyles={themeStyles}
                selectedMenu={selectedMenu}
                onLogout={onLogout}
            />
        </div>
    );
}

export default UserAdminPage; 