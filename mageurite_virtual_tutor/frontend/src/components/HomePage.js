import React, { useState } from 'react';
import HomeSidebar from './HomeSidebar';
import HomeHeader from './HomeHeader';
import HomeChatList from './HomeChatList';
import HomeChatWindow from './HomeChatWindow';
import HomeFooter from './HomeFooter';
import chatService from '../services/chatService';

// Chat mock data
const initialChatMessages = {
    chat1: [
        { id: 1, from: 'user', text: 'Hello, mentor!' },
        { id: 2, from: 'mentor', text: 'Hello, how can I help you?' },
        {
            id: 3,
            from: 'user',
            file: {
                name: 'example-document.pdf',
                size: 1024000,
                type: 'application/pdf',
                url: '#'
            }
        },
        { id: 4, from: 'mentor', text: 'I can see you uploaded a PDF document. How can I help you with it?' },
    ],
    chat2: [
        { id: 1, from: 'user', text: 'This is Chat2 message.' },
        { id: 2, from: 'mentor', text: 'Received, this is Chat2.' },
    ],
    chat3: [
        { id: 1, from: 'user', text: 'Yesterday\'s conversation.' },
        { id: 2, from: 'mentor', text: 'This is yesterday\'s message.' },
    ],
};

// Chat metadata, including favorite status
const initialChatMetadata = {
    chat1: { title: 'Chat 1', subtitle: 'Recent conversation', isFavorite: false },
    chat2: { title: 'Chat 2', subtitle: 'Important conversation', isFavorite: true },
    chat3: { title: 'Chat 3', subtitle: 'Yesterday\'s conversation', isFavorite: false },
};

function HomePage(props) {
    const [sessions, setSessions] = useState([]);
    const [selectedChatId, setSelectedChatId] = useState(null);
    const [isDarkMode, setIsDarkMode] = useState(false);
    const [sessionMessages, setSessionMessages] = useState({}); // { sessionId: [msg, ...] }
    const [messages, setMessages] = useState([]);

    const fetchMessages = async (session_id) => {
        // Prefer rendering from local cache if available
        if (sessionMessages[session_id]) {
            setMessages(sessionMessages[session_id]);
        } else {
            setMessages([]);
        }
        // Sync with backend
        const res = await chatService.getMessages(session_id);
        if (res.success && Array.isArray(res.data)) {
            const msgs = res.data.map((msg, idx) => ({
                id: idx,
                from: msg.role === 'user' ? 'user' : 'mentor',
                text: msg.content,
                image: msg.file_type && msg.file_type.startsWith('image') ? msg.file_path : undefined
            }));
            setSessionMessages(prev => ({ ...prev, [session_id]: msgs }));
            setMessages(msgs);
        }
    };

    // Load sessions on initial mount
    React.useEffect(() => {
        refreshSessions();
    }, []);
    const refreshSessions = async (autoSelectId) => {
        const res = await chatService.listSessions();
        console.log('listSessions response', res);
        if (res.success && Array.isArray(res.data)) {
            setSessions(res.data);
            if (autoSelectId) {
                setSelectedChatId(autoSelectId);
                fetchMessages(autoSelectId); // Fetch messages when auto-selecting
            } else if (!selectedChatId && res.data.length > 0) {
                setSelectedChatId(res.data[0].id);
                fetchMessages(res.data[0].id); // Fetch messages on first load
            }
        } else {
            setSessions([]);
        }
    };
    // Create new session
    const handleNewChat = async () => {
        const res = await chatService.createSession('New Chat');
        console.log('createSession response', res);
        if (res.success && res.data && res.data.session_id) {
            await refreshSessions(res.data.session_id);
        } else {
            alert(res.message || 'Failed to create new session');
        }
    };
    // Select session
    const handleSelectChat = (id) => {
        setSelectedChatId(id);
        if (sessionMessages[id]) {
            setMessages(sessionMessages[id]);
        } else {
            setMessages([]);
        }
        fetchMessages(id);
    };

    // Send message
    const handleSendMessage = async (text) => {
        if (!selectedChatId || !text) return;
        // 1. Insert locally immediately
        setSessionMessages(prev => {
            const prevMsgs = prev[selectedChatId] || [];
            const newMsgs = [
                ...prevMsgs,
                { id: Date.now(), from: 'user', text, pending: true }
            ];
            setMessages(newMsgs);
            return { ...prev, [selectedChatId]: newMsgs };
        });
        // 2. Call backend
        const formData = new FormData();
        formData.append('message', text);
        formData.append('session_id', selectedChatId);
        const res = await chatService.chat(formData);
        // 3. Complete after receiving reply
        if (res.success && res.data && res.data.text_output) {
            setSessionMessages(prev => {
                const prevMsgs = prev[selectedChatId] || [];
                // 移除 pending
                const filtered = prevMsgs.filter(m => !m.pending);
                const newMsgs = [
                    ...filtered,
                    { id: Date.now() + 1, from: 'user', text },
                    { id: Date.now() + 2, from: 'mentor', text: res.data.text_output }
                ];
                setMessages(newMsgs);
                return { ...prev, [selectedChatId]: newMsgs };
            });
        }
    };

    // 發送文件
    const handleSendFile = async (fileData) => {
        if (!selectedChatId || !fileData) return;

        console.log('Process file upload data:', fileData);

        // 1. Insert file message locally immediately
        const fileMessage = {
            id: Date.now(),
            from: 'user',
            file: {
                name: fileData.fileInfo.name,
                size: fileData.fileInfo.size,
                type: fileData.fileInfo.type,
                // 根据实际后端响应构建下载URL
                url: fileData.file.file_path ?
                    `http://localhost:8203/api/download/${fileData.file.file_id}` :
                    '#', // 临时占位符
                file_id: fileData.file.file_id,
                file_path: fileData.file.file_path,
                chunk_count: fileData.file.chunk_count
            },
            pending: true
        };

        setSessionMessages(prev => {
            const prevMsgs = prev[selectedChatId] || [];
            const newMsgs = [...prevMsgs, fileMessage];
            setMessages(newMsgs);
            return { ...prev, [selectedChatId]: newMsgs };
        });

        // 2. Remove pending status and complete file message display
        setTimeout(() => {
            setSessionMessages(prev => {
                const prevMsgs = prev[selectedChatId] || [];
                // 移除 pending
                const filtered = prevMsgs.filter(m => !m.pending);
                const newMsgs = [
                    ...filtered,
                    { ...fileMessage, pending: false },
                ];

                setMessages(newMsgs);
                return { ...prev, [selectedChatId]: newMsgs };
            });
        }, 500); // 短暂延迟以显示上传状态
    };

    // Handle theme switching
    const handleThemeChange = (newMode) => {
        setIsDarkMode(newMode);
        // You can add more theme-related logic here
        document.body.style.background = newMode ? '#1a1a1a' : '#fff';
        document.body.style.color = newMode ? '#e5e5e5' : '#333';
    };


    // Theme styles
    const themeStyles = {
        background: isDarkMode ? '#1a1a1a' : '#fff',
        color: isDarkMode ? '#e5e5e5' : '#333',
        sidebarBackground: isDarkMode ? '#2d2d2d' : '#F0F0F0',
        sidebarHeaderBackground: isDarkMode ? '#3d3d3d' : '#fff',
        sidebarHeaderColor: isDarkMode ? '#e5e5e5' : '#E64003',
        chatListBackground: isDarkMode ? '#2a2a2a' : '#F7F9FB',
        chatItemBackground: isDarkMode ? '#3d3d3d' : '#fff',
        chatItemSelectedBackground: isDarkMode ? '#AF52DE' : '#AF52DE',
        chatItemColor: isDarkMode ? '#e5e5e5' : '#1C1C1C',
        chatItemSubtitleColor: isDarkMode ? '#b0b0b0' : '#757575',
        inputBackground: isDarkMode ? '#3d3d3d' : '#fff',
        inputBorder: isDarkMode ? '#555' : '#E2E2E2',
        inputColor: isDarkMode ? '#e5e5e5' : '#333',
        placeholderColor: isDarkMode ? '#888' : '#999',
        buttonBackground: isDarkMode ? '#3d3d3d' : '#fff',
        buttonColor: isDarkMode ? '#e5e5e5' : '#333',
        shadow: isDarkMode ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.03)',
        // Additional styles
        activeBackground: isDarkMode ? '#3d3d3d' : '#fff',
        activeColor: isDarkMode ? '#AF52DE' : '#14B48D',
        inactiveColor: isDarkMode ? '#e5e5e5' : '#3B3B3B',
        activeShadow: isDarkMode ? '0 2px 8px rgba(175,82,222,0.2)' : '0 2px 8px rgba(20,180,141,0.08)',
        activeCountBackground: isDarkMode ? 'rgba(175,82,222,0.2)' : 'rgba(16,163,127,0.15)',
        inactiveCountBackground: isDarkMode ? 'rgba(138,138,138,0.2)' : 'rgba(138,138,138,0.11)',
        activeCountColor: isDarkMode ? '#AF52DE' : '#14B48D',
        inactiveCountColor: isDarkMode ? '#e5e5e5' : '#3B3B3B',
        groupTitleColor: isDarkMode ? '#b0b0b0' : '#757575',
        selectedBackground: isDarkMode ? '#AF52DE' : '#AF52DE',
        selectedColor: isDarkMode ? '#fff' : '#fff',
        selectedShadow: isDarkMode ? '0 2px 8px rgba(175,82,222,0.3)' : '0 2px 8px #AF52DE22',
        selectedSubtitleColor: isDarkMode ? '#fff' : '#fff',
        inactiveSubtitleColor: isDarkMode ? '#b0b0b0' : '#757575',
        footerBackground: isDarkMode ? '#2d2d2d' : '#F0F0F0',
        barColor: isDarkMode ? '#555' : '#eee'
    };

    return (
        <div style={{
            display: 'flex',
            height: '100vh',
            background: themeStyles.background,
            color: themeStyles.color,
            transition: 'all 0.3s ease'
        }}>
            <HomeSidebar
                sessions={sessions}
                selectedChatId={selectedChatId}
                onSelectChat={handleSelectChat}
                onRefreshSessions={refreshSessions}
                onThemeChange={handleThemeChange}
                themeStyles={themeStyles}
                onLogout={props.onLogout}
            />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <HomeHeader themeStyles={themeStyles} onLogout={props.onLogout} />
                <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
                    <HomeChatList themeStyles={themeStyles} />
                    <HomeChatWindow key={selectedChatId} chatId={selectedChatId} messages={messages} themeStyles={themeStyles} />
                </div>
                <HomeFooter onSendMessage={handleSendMessage} onSendFile={handleSendFile} chatId={selectedChatId} onNewChat={handleNewChat} themeStyles={themeStyles} />
            </div>
        </div>
    );
}

export default HomePage; 