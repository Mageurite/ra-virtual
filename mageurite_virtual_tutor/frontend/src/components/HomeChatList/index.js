import React, { useState, useEffect, useRef } from 'react';
import adminService from '../../services/adminService';

// 直接使用动态URL，不依赖config文件
const getWebRTCUrl = () => {
    const hostname = window.location.hostname;
    return `http://${hostname}:8615`;
};

const getBackendUrl = () => {
    const hostname = window.location.hostname;
    return `http://${hostname}:8203`;
};

// 默认AI模型选项（作为备用）
const defaultAiModels = [
    { id: 'tutor-model-1', name: 'Tutor Model 1', description: 'Basic teaching model, suitable for beginners' },
    { id: 'tutor-model-2', name: 'Tutor Model 2', description: 'Advanced teaching model, suitable for learners with foundation' },
    { id: 'tutor-model-3', name: 'Tutor Model 3', description: 'Professional teaching model, suitable for deep learning' },
    { id: 'tutor-model-4', name: 'Tutor Model 4', description: 'Expert-level teaching model, suitable for advanced users' }
];

// WebRTC Video Avatar Component (Square, with connection button in bottom right)
function VideoAvatar({ style }) {
    const videoRef = useRef(null);
    const pcRef = useRef(null);
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(false);

    // 啟動 WebRTC 連接
    const startConnection = async () => {
        setLoading(true);
        try {
            let pc;
            let stopped = false;
            const config = {
                sdpSemantics: 'unified-plan',
                iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }]
            };
            pc = new window.RTCPeerConnection(config);
            pcRef.current = pc;

            pc.addTransceiver('video', { direction: 'recvonly' });
            pc.addTransceiver('audio', { direction: 'recvonly' });

            pc.addEventListener('track', (evt) => {
                if (evt.track.kind === 'video' && videoRef.current) {
                    videoRef.current.srcObject = evt.streams[0];
                } else if (evt.track.kind === 'audio') {
                    const audio = new Audio();
                    audio.srcObject = evt.streams[0];
                    audio.autoplay = true;
                }
            });

            await pc.setLocalDescription(await pc.createOffer());
            await new Promise((resolve) => {
                if (pc.iceGatheringState === 'complete') {
                    resolve();
                } else {
                    const checkState = () => {
                        if (pc.iceGatheringState === 'complete') {
                            pc.removeEventListener('icegatheringstatechange', checkState);
                            resolve();
                        }
                    };
                    pc.addEventListener('icegatheringstatechange', checkState);
                }
            });

            const offer = pc.localDescription;
            const webrtcUrl = getWebRTCUrl();
            const response = await fetch(`${webrtcUrl}/offer`, {
                body: JSON.stringify({ sdp: offer.sdp, type: offer.type }),
                headers: { 'Content-Type': 'application/json' },
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }
            
            const answer = await response.json();
            if (answer.sessionid) {
                const token = localStorage.getItem('token'); // 取得 token
                const backendUrl = getBackendUrl();
                await fetch(`${backendUrl}/api/sessionid`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'sessionid': answer.sessionid,
                        'Authorization': `Bearer ${token}` // 加入 token
                    },
                    body: JSON.stringify({ sessionid: answer.sessionid })
                });
            }
            if (!stopped) {
                await pc.setRemoteDescription(answer);
                setConnected(true);
            }
        } catch (error) {
            console.error('WebRTC connection failed:', error);
            alert(`视频连接失败: ${error.message}\n\n请先选择一个Avatar并等待切换完成后再尝试连接视频。`);
            if (pcRef.current) {
                pcRef.current.close();
                pcRef.current = null;
            }
        } finally {
            setLoading(false);
        }
    };

    // 關閉 WebRTC 連接
    const stopConnection = () => {
        if (pcRef.current) {
            pcRef.current.close();
            pcRef.current = null;
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }
        setConnected(false);
    };

    // 卸載時自動關閉
    useEffect(() => {
        return () => {
            stopConnection();
        };
    }, []);

    return (
        <div style={{
            width: '100%',
            height: '100%',
            borderRadius: 12,
            overflow: 'hidden',
            background: '#000',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 16px #4F378A22',
            position: 'relative',
            ...style
        }}>
            <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 0 }}
            />
            {/* 右下角連接/斷開按鈕 */}
            <button
                onClick={connected ? stopConnection : startConnection}
                disabled={loading}
                style={{
                    position: 'absolute',
                    right: 10,
                    bottom: 10,
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    background: connected ? 'linear-gradient(135deg, #FF7E5F 0%, #FFB86C 100%)' : 'linear-gradient(135deg, #4ADE80 0%, #6EE7B7 100%)',
                    border: 'none',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 2px 8px #0002',
                    color: '#fff',
                    fontSize: 20,
                    fontWeight: 700,
                    transition: 'all 0.2s',
                    opacity: loading ? 0.6 : 1
                }}
                title={connected ? 'Disconnect Video' : 'Connect Video'}
            >
                {loading ? '...' : connected ? '⏹' : '▶'}
            </button>
        </div>
    );
}

function HomeChatList({ themeStyles }) {
    const [selectedModel, setSelectedModel] = useState('');
    const [availableAvatars, setAvailableAvatars] = useState([]);
    const [loadingAvatars, setLoadingAvatars] = useState(false);
    const [switchingModel, setSwitchingModel] = useState(false);

    // 获取可用Avatar列表
    const fetchAvailableAvatars = async () => {
        setLoadingAvatars(true);
        try {
            const result = await adminService.getAvailableAvatars();
            if (result.success && result.data) {
                // 转换API响应格式
                let avatarList = [];
                if (typeof result.data === 'object' && !Array.isArray(result.data)) {
                    avatarList = Object.entries(result.data).map(([key, avatar]) => ({
                        id: key,
                        name: key,
                        description: avatar.description || `Avatar: ${key}`,
                        status: avatar.status || 'active'
                    }));
                } else if (Array.isArray(result.data)) {
                    avatarList = result.data.map(avatar => ({
                        id: avatar.name || avatar.id,
                        name: avatar.name || avatar.id,
                        description: avatar.description || `Avatar: ${avatar.name || avatar.id}`,
                        status: avatar.status || 'active'
                    }));
                }

                setAvailableAvatars(avatarList);

                // 设置默认选中的模型并自动启动
                if (avatarList.length > 0 && !selectedModel) {
                    const defaultAvatarId = avatarList[0].id;
                    setSelectedModel(defaultAvatarId);
                    // 自动启动默认avatar
                    adminService.startAvatar(defaultAvatarId).then(result => {
                        if (result.success) {
                            console.log(`Auto-started default avatar: ${defaultAvatarId}`);
                        } else {
                            console.warn(`Failed to auto-start avatar: ${result.message}`);
                        }
                    }).catch(error => {
                        console.error(`Error auto-starting avatar:`, error);
                    });
                }
            } else {
                console.warn('Failed to fetch available avatars:', result.message);
                // 使用默认模型
                setAvailableAvatars(defaultAiModels);
                if (!selectedModel) {
                    setSelectedModel(defaultAiModels[0].id);
                }
            }
        } catch (error) {
            console.error('Error fetching available avatars:', error);
            // 使用默认模型
            setAvailableAvatars(defaultAiModels);
            if (!selectedModel) {
                setSelectedModel(defaultAiModels[0].id);
            }
        } finally {
            setLoadingAvatars(false);
        }
    };

    // 切换Avatar模型
    const handleModelSwitch = async (modelId) => {
        if (modelId === selectedModel) return;

        setSwitchingModel(true);
        try {
            const result = await adminService.startAvatar(modelId);
            if (result.success) {
                setSelectedModel(modelId);
                console.log(`Successfully switched to avatar: ${modelId}`);
            } else {
                console.error('Failed to switch avatar:', result.message);
                alert(`Failed to switch avatar: ${result.message}`);
            }
        } catch (error) {
            console.error('Error switching avatar:', error);
            alert(`Error switching avatar: ${error.message}`);
        } finally {
            setSwitchingModel(false);
        }
    };

    // 组件加载时获取Avatar列表
    useEffect(() => {
        fetchAvailableAvatars();
    }, []);

    return (
        <div style={{
            flex: 6,
            background: themeStyles?.chatListBackground || '#F7F9FB',
            borderRadius: 16,
            margin: 8,
            padding: 16,
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            transition: 'all 0.3s ease'
        }}>
            {/* 左上角 AI 模型選擇 */}
            <div style={{ position: 'absolute', top: 16, left: 16, zIndex: 10 }}>
                <div style={{ position: 'relative' }}>
                    <select
                        value={selectedModel}
                        onChange={(e) => handleModelSwitch(e.target.value)}
                        disabled={loadingAvatars || switchingModel}
                        style={{
                            padding: '8px 12px',
                            borderRadius: 8,
                            border: `1px solid ${themeStyles?.inputBorder || '#E2E2E2'}`,
                            background: themeStyles?.inputBackground || '#fff',
                            fontSize: 14,
                            fontWeight: 500,
                            color: themeStyles?.inputColor || '#333',
                            cursor: loadingAvatars || switchingModel ? 'not-allowed' : 'pointer',
                            minWidth: 140,
                            boxShadow: themeStyles?.shadow || '0 2px 8px rgba(0,0,0,0.1)',
                            appearance: 'none',
                            backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e")`,
                            backgroundRepeat: 'no-repeat',
                            backgroundPosition: 'right 8px center',
                            backgroundSize: '16px',
                            paddingRight: '32px',
                            transition: 'all 0.3s ease',
                            opacity: loadingAvatars || switchingModel ? 0.6 : 1
                        }}
                    >
                        {loadingAvatars ? (
                            <option value="">Loading avatars...</option>
                        ) : availableAvatars.length > 0 ? (
                            availableAvatars.map(model => (
                                <option key={model.id} value={model.id}>
                                    {model.name}
                                </option>
                            ))
                        ) : (
                            <option value="">No avatars available</option>
                        )}
                    </select>

                    {/* 切换状态指示器 */}
                    {switchingModel && (
                        <div style={{
                            position: 'absolute',
                            top: '50%',
                            right: '40px',
                            transform: 'translateY(-50%)',
                            width: 16,
                            height: 16,
                            border: '2px solid #e0e0e0',
                            borderTop: '2px solid #1976d2',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite'
                        }}></div>
                    )}

                    <div style={{
                        position: 'absolute',
                        top: '100%',
                        left: 0,
                        background: themeStyles?.inputBackground || '#fff',
                        borderRadius: 8,
                        boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
                        padding: '8px 0',
                        marginTop: 4,
                        minWidth: 200,
                        display: 'none'
                    }}>
                        {availableAvatars.map(model => (
                            <div key={model.id} style={{
                                padding: '8px 12px',
                                fontSize: 12,
                                color: themeStyles?.placeholderColor || '#666',
                                borderBottom: '1px solid #f0f0f0'
                            }}>
                                {model.description}
                            </div>
                        ))}
                    </div>
                </div>
            </div>



            {/* 虛擬導師大頭像（改為方形視頻流+連接按鈕） */}
            <div style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: 0,
                minWidth: 0
            }}>
                <VideoAvatar />
            </div>
        </div>
    );
}

export default HomeChatList; 