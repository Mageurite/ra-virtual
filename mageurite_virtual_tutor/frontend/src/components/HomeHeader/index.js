import React, { useState } from 'react';

const BASE_URL = 'http://localhost:8203/';
const DEFAULT_AVATAR = 'https://cdn.jsdelivr.net/gh/edent/SuperTinyIcons/images/svg/user.svg'; // Replace with a local default avatar if desired

function HomeHeader({ onLogout }) {
    const [showMenu, setShowMenu] = useState(false);
    const [imgError, setImgError] = useState(false);
    const handleLogoutClick = () => {
        if (window.confirm('Are you sure you want to log out?')) {
            onLogout();
        }
    };
    // Get user avatar from localStorage
    let avatar = null;
    const userStr = localStorage.getItem('user');
    if (userStr) {
        const user = JSON.parse(userStr);
        avatar = user.avatar || user.avatar_url || null;
    }
    const avatarSrc = imgError || !avatar ? DEFAULT_AVATAR : (avatar.startsWith('http') ? avatar : `${BASE_URL}${avatar}`);
    return (
        <header style={{ height: 80, background: '#fff', borderBottom: '1px solid #eee', display: 'flex', alignItems: 'center', padding: '0 40px', justifyContent: 'flex-end', position: 'relative' }}>
            <div
                style={{ position: 'relative', display: 'inline-block' }}
                onMouseEnter={() => setShowMenu(true)}
                onMouseLeave={() => setShowMenu(false)}
            >
                <img
                    src={avatarSrc}
                    alt="User avatar"
                    style={{ width: 64, height: 64, borderRadius: '50%', objectFit: 'cover', border: '3px solid #eee', boxShadow: '0 4px 16px #eee', cursor: 'pointer', transition: 'box-shadow 0.2s', background: '#f0f0f0' }}
                    onError={() => setImgError(true)}
                />
                {showMenu && (
                    <div style={{
                        position: 'absolute',
                        top: 70,
                        right: 0,
                        background: '#fff',
                        border: '1px solid #eee',
                        borderRadius: 8,
                        boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
                        minWidth: 140,
                        zIndex: 10,
                        padding: '10px 0',
                        textAlign: 'center'
                    }}>
                        <button
                            onClick={handleLogoutClick}
                            style={{
                                width: '100%',
                                padding: '10px 0',
                                background: 'none',
                                color: '#1976d2',
                                border: 'none',
                                borderRadius: 0,
                                cursor: 'pointer',
                                fontWeight: 500,
                                fontSize: 17,
                                transition: 'background 0.2s',
                                outline: 'none'
                            }}
                            onMouseDown={e => e.preventDefault()}
                        >
                            Logout
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
}

export default HomeHeader; 