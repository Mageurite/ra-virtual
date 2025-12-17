// 配置
const CONFIG = {
    // Web Backend API (用于认证和元数据)
    WEB_BACKEND_URL: 'http://localhost:8000',
    
    // Avatar Service API (直接访问 AI 服务)
    AVATAR_SERVICE_URL: 'http://localhost:8001',
    
    // Tutor ID (从 URL 参数获取，或使用默认值)
    TUTOR_ID: new URLSearchParams(window.location.search).get('tutor_id') || '1'
};

// 全局状态
let conversationHistory = [];
let isConnected = false;
let peerConnection = null;
let localStream = null;

// DOM 元素
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');
const avatarVideo = document.getElementById('avatarVideo');
const videoPlaceholder = document.getElementById('videoPlaceholder');
const loading = document.getElementById('loading');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('Virtual Tutor Frontend Initialized');
    console.log('Tutor ID:', CONFIG.TUTOR_ID);
    
    // 检查服务可用性
    checkServices();
});

// 检查服务状态
async function checkServices() {
    try {
        // 检查 Web Backend
        const backendResponse = await fetch(`${CONFIG.WEB_BACKEND_URL}/health`);
        if (backendResponse.ok) {
            console.log('✓ Web Backend is ready');
        }
        
        // 检查 Avatar Service
        const avatarResponse = await fetch(`${CONFIG.AVATAR_SERVICE_URL}/health`);
        if (avatarResponse.ok) {
            console.log('✓ Avatar Service is ready');
        }
        
        // 检查 Tutor 信息
        const tutorResponse = await fetch(
            `${CONFIG.WEB_BACKEND_URL}/api/tutors/${CONFIG.TUTOR_ID}/health`
        );
        
        if (tutorResponse.ok) {
            const tutorData = await tutorResponse.json();
            console.log('✓ Tutor is available:', tutorData);
            
            if (tutorData.avatar_running) {
                updateStatus('online', 'Avatar 已就绪');
            }
        }
    } catch (error) {
        console.error('Service check failed:', error);
        updateStatus('offline', '服务连接失败');
    }
}

// 更新连接状态
function updateStatus(status, text) {
    statusDot.className = 'status-dot';
    if (status === 'online' || status === 'connected') {
        statusDot.classList.add('connected');
    }
    statusText.textContent = text;
}

// 连接 Avatar
async function connectAvatar() {
    try {
        loading.classList.add('active');
        updateStatus('connecting', '正在连接...');
        
        // 这里实现 WebRTC 连接逻辑
        // 1. 获取 Avatar 信息
        const response = await fetch(
            `${CONFIG.WEB_BACKEND_URL}/api/tutors/${CONFIG.TUTOR_ID}/info`
        );
        
        if (!response.ok) {
            throw new Error('Failed to get tutor info');
        }
        
        const tutorInfo = await response.json();
        console.log('Tutor info:', tutorInfo);
        
        if (!tutorInfo.has_avatar) {
            throw new Error('This tutor does not have an avatar');
        }
        
        if (tutorInfo.avatar_status !== 'running') {
            throw new Error('Avatar is not running. Please ask admin to start it.');
        }
        
        // 2. 初始化 WebRTC 连接
        await initWebRTC();
        
        videoPlaceholder.style.display = 'none';
        avatarVideo.style.display = 'block';
        
        isConnected = true;
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
        
        updateStatus('connected', '已连接');
        
        addMessage('assistant', '视频连接成功！现在可以开始对话了。');
        
    } catch (error) {
        console.error('Connection error:', error);
        updateStatus('offline', '连接失败');
        addMessage('assistant', `连接失败: ${error.message}`);
    } finally {
        loading.classList.remove('active');
    }
}

// 初始化 WebRTC
async function initWebRTC() {
    try {
        // 创建 PeerConnection
        peerConnection = new RTCPeerConnection({
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' }
            ]
        });
        
        // 获取本地音频流（用于发送语音）
        localStream = await navigator.mediaDevices.getUserMedia({ 
            audio: true, 
            video: false 
        });
        
        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });
        
        // 接收远程流（Avatar 视频）
        peerConnection.ontrack = (event) => {
            console.log('Received remote track');
            avatarVideo.srcObject = event.streams[0];
        };
        
        // 创建 Offer
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        
        // 发送 Offer 到 Avatar Service
        const response = await fetch(
            `${CONFIG.WEB_BACKEND_URL}/api/tutors/${CONFIG.TUTOR_ID}/webrtc/offer`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sdp: offer.sdp,
                    type: offer.type
                })
            }
        );
        
        if (!response.ok) {
            throw new Error('Failed to send offer');
        }
        
        const answer = await response.json();
        await peerConnection.setRemoteDescription(
            new RTCSessionDescription(answer)
        );
        
        console.log('WebRTC connection established');
        
    } catch (error) {
        console.error('WebRTC initialization error:', error);
        throw error;
    }
}

// 断开连接
function disconnectAvatar() {
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }
    
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    
    avatarVideo.srcObject = null;
    avatarVideo.style.display = 'none';
    videoPlaceholder.style.display = 'block';
    
    isConnected = false;
    connectBtn.disabled = false;
    disconnectBtn.disabled = true;
    
    updateStatus('offline', '已断开');
    
    addMessage('assistant', '视频连接已断开。');
}

// 发送消息
async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // 添加用户消息到界面
    addMessage('user', message);
    
    // 清空输入框
    chatInput.value = '';
    
    // 禁用发送按钮
    sendBtn.disabled = true;
    
    // 显示输入指示器
    typingIndicator.classList.add('active');
    
    try {
        // 调用 LLM API
        const response = await fetch(
            `${CONFIG.WEB_BACKEND_URL}/api/tutors/${CONFIG.TUTOR_ID}/chat`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: conversationHistory.slice(-10) // 只保留最近 10 条
                })
            }
        );
        
        if (!response.ok) {
            throw new Error('Chat request failed');
        }
        
        const data = await response.json();
        const assistantMessage = data.response;
        
        // 添加到对话历史
        conversationHistory.push({
            role: 'user',
            content: message
        });
        conversationHistory.push({
            role: 'assistant',
            content: assistantMessage
        });
        
        // 隐藏输入指示器
        typingIndicator.classList.remove('active');
        
        // 添加助手回复到界面
        addMessage('assistant', assistantMessage);
        
        // 如果连接了视频，可以同步语音和嘴型
        if (isConnected) {
            await syncAvatarSpeech(assistantMessage);
        }
        
    } catch (error) {
        console.error('Send message error:', error);
        typingIndicator.classList.remove('active');
        addMessage('assistant', '抱歉，发送消息失败，请重试。');
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

// 同步 Avatar 语音（可选功能）
async function syncAvatarSpeech(text) {
    try {
        // 调用 TTS 服务
        const response = await fetch(
            `${CONFIG.AVATAR_SERVICE_URL}/api/tts/synthesize-json`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    engine: 'edge-tts',
                    voice: 'zh-CN-XiaoxiaoNeural'
                })
            }
        );
        
        if (response.ok) {
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            await audio.play();
            
            console.log('Avatar speech synced');
        }
    } catch (error) {
        console.error('Avatar speech sync error:', error);
    }
}

// 添加消息到聊天框
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 处理回车键发送
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 错误处理
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});
