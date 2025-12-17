import React, { useRef, useState, useEffect } from 'react';
import uploadService from '../../services/uploadService';
import adminService from '../../services/adminService';

// 允许的文档类型 - 与后端保持一致
const ALLOWED_DOCUMENT_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
];

// 文件类型对应的扩展名和描述
const FILE_TYPE_INFO = {
    'application/pdf': { ext: '.pdf', name: 'PDF' },
    'application/msword': { ext: '.doc', name: 'Word 97-2003' },
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { ext: '.docx', name: 'Word' },
    'text/plain': { ext: '.txt', name: 'Text' },
    'application/vnd.ms-excel': { ext: '.xls', name: 'Excel 97-2003' },
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': { ext: '.xlsx', name: 'Excel' }
};

// 添加旋转动画样式
const spinKeyframes = `
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;

// 将样式注入到页面中
if (typeof document !== 'undefined') {
    const styleElement = document.createElement('style');
    styleElement.textContent = spinKeyframes;
    if (!document.head.querySelector('style[data-spin-animation]')) {
        styleElement.setAttribute('data-spin-animation', 'true');
        document.head.appendChild(styleElement);
    }
}

const PaperPlaneIcon = () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 2L11 13" /><path d="M22 2L15 22L11 13L2 9L22 2Z" /></svg>
);
const FileIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14,2 14,8 20,8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <line x1="10" y1="9" x2="8" y2="9" />
    </svg>
);
const MicIcon = () => <span role="img" aria-label="mic" style={{ fontSize: 20, color: '#fff' }}>🎤</span>;
const PlusIcon = () => <span role="img" aria-label="plus" style={{ fontSize: 22, color: '#fff' }}>＋</span>;
const FolderIcon = () => <span role="img" aria-label="folder" style={{ fontSize: 20, color: '#fff' }}>📁</span>;

const DeleteIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="3,6 5,6 21,6"></polyline>
        <path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
        <line x1="10" y1="11" x2="10" y2="17"></line>
        <line x1="14" y1="11" x2="14" y2="17"></line>
    </svg>
);

function HomeFooter({ onSendMessage, onSendFile, onNewChat, themeStyles }) {
    const [input, setInput] = useState("");
    const [listening, setListening] = useState(false);
    const [progress, setProgress] = useState(1); // 1~0
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);

    const [showUserFiles, setShowUserFiles] = useState(false);
    const [userFiles, setUserFiles] = useState([]);
    const [loadingUserFiles, setLoadingUserFiles] = useState(false);
    const [deletingFiles, setDeletingFiles] = useState(new Set());

    const fileInputRef = useRef();
    const recognitionRef = useRef(null);
    const micTimeoutRef = useRef();
    const progressAnimRef = useRef();
    const [bars, setBars] = useState(Array(8).fill(8));
    const audioContextRef = useRef();
    const analyserRef = useRef();
    const dataArrayRef = useRef();
    const mediaStreamRef = useRef();
    const stopListeningOnceRef = useRef(false);

    // 获取用户已上传文件
    const fetchUserFiles = async () => {
        setLoadingUserFiles(true);
        try {
            const result = await adminService.getUserFiles();
            if (result.success && result.data && result.data.files) {
                setUserFiles(result.data.files);
            } else {
                setUserFiles([]);
            }
        } catch (error) {
            console.error('Failed to fetch user files:', error);
            setUserFiles([]);
        } finally {
            setLoadingUserFiles(false);
        }
    };

    // 删除文件
    const handleDeleteFile = async (fileName) => {
        if (!window.confirm(`Are you sure you want to delete "${fileName}"?`)) {
            return;
        }

        // 设置删除状态
        setDeletingFiles(prev => new Set(prev).add(fileName));

        try {
            const result = await uploadService.deleteFile(fileName);
            if (result.success) {
                // 删除成功后重新获取文件列表
                await fetchUserFiles();
                console.log('File deleted successfully:', fileName);
            } else {
                console.error('Failed to delete file:', result.message);
                alert(`Failed to delete file: ${result.message}`);
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            alert('An error occurred while deleting the file.');
        } finally {
            // 清除删除状态
            setDeletingFiles(prev => {
                const newSet = new Set(prev);
                newSet.delete(fileName);
                return newSet;
            });
        }
    };

    // 处理显示用户文件
    const handleShowUserFiles = () => {
        if (!showUserFiles) {
            fetchUserFiles();
        }
        setShowUserFiles(!showUserFiles);
    };

    // 發送文字
    const handleSend = () => {
        if (input.trim()) {
            onSendMessage(input);
            setInput("");
        }
    };
    // 發送文件
    const handleFileClick = () => {
        if (uploading) return; // 如果正在上传，禁止再次点击
        fileInputRef.current && fileInputRef.current.click();
    };



    // 提取文件上传逻辑为独立函数
    const handleFileUpload = async (file) => {
        // 前端验证文件类型
        if (!ALLOWED_DOCUMENT_TYPES.includes(file.type)) {
            const allowedExtensions = Object.values(FILE_TYPE_INFO).map(info => info.ext).join(', ');
            const allowedNames = Object.values(FILE_TYPE_INFO).map(info => info.name).join(', ');
            alert(`Only the following document types are supported:\n${allowedNames}\nFile extensions: ${allowedExtensions}`);
            return;
        }

        // 文件大小验证 (20MB)
        const maxSize = 20 * 1024 * 1024;
        if (file.size > maxSize) {
            alert(`File size cannot exceed 20MB. Current file size: ${(file.size / 1024 / 1024).toFixed(2)}MB`);
            return;
        }

        setUploading(true);
        setUploadProgress(0);

        try {
            // 根据文件类型选择上传方法
            const fileType = uploadService.getFileType(file);

            const formData = new FormData();
            formData.append('file', file);
            // 调试：打印文件信息
            console.log('📁 文件详细信息:', {
                name: file.name,
                size: file.size,
                type: file.type,
                lastModified: file.lastModified,
                constructor: file.constructor.name
            });

            // 调试：验证 FormData
            console.log('📦 FormData 验证:');
            for (let [key, value] of formData.entries()) {
                if (value instanceof File) {
                    console.log(`  ${key}:`, {
                        name: value.name,
                        size: value.size,
                        type: value.type,
                        lastModified: value.lastModified
                    });
                } else {
                    console.log(`  ${key}:`, value);
                }
            }

            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('No authentication token found');
            }

            console.log('🔑 使用的 Token:', token.substring(0, 50) + '...');

            const response = await fetch('http://localhost:8203/api/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData
            });

            console.log('📡 响应状态:', response.status, response.statusText);
            console.log('📡 响应头:');
            for (let [key, value] of response.headers.entries()) {
                console.log(`  ${key}: ${value}`);
            }

            const responseText = await response.text();

            let result;
            if (response.ok) {
                try {
                    const data = JSON.parse(responseText);
                    result = {
                        success: true,
                        data: data,
                        fileInfo: {
                            name: file.name,
                            size: file.size,
                            type: file.type,
                            uploadType: fileType
                        }
                    };
                } catch (e) {
                    result = {
                        success: false,
                        message: 'Invalid JSON response from server'
                    };
                }
            } else {
                try {
                    const errorData = JSON.parse(responseText);
                    result = {
                        success: false,
                        message: errorData.msg || errorData.message || `Server error: ${response.status}`
                    };
                } catch (e) {
                    result = {
                        success: false,
                        message: `Server error: ${response.status} - ${responseText}`
                    };
                }
            }

            if (result.success) {
                // 调用父组件的回调函数，传递文件信息
                onSendFile && onSendFile({
                    file: result.data,
                    fileInfo: result.fileInfo,
                    type: fileType
                });
            } else {
                alert(`Upload failed: ${result.message}`);
            }
        } catch (error) {
            console.error('File upload error:', error);
            alert('File upload failed, please try again');
        } finally {
            setUploading(false);
            setUploadProgress(0);
        }
    };

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        await handleFileUpload(file);
        e.target.value = ''; // 清空文件选择
    };
    // 語音輸入
    const handleMicClick = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Current browser does not support speech recognition');
            return;
        }
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!recognitionRef.current) {
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.lang = 'en-US';
            recognitionRef.current.continuous = true;
            recognitionRef.current.interimResults = false;
            recognitionRef.current.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setInput(transcript);
                stopListening();
            };
            recognitionRef.current.onerror = stopListening;
            recognitionRef.current.onend = stopListening;
        }
        if (listening) {
            stopListening();
            return;
        }
        setListening(true);
        setProgress(1);
        recognitionRef.current.start();
        startProgressAnim();
        micTimeoutRef.current = setTimeout(() => {
            stopListening();
        }, 60000);
        stopListeningOnceRef.current = false;
    };
    function stopListening() {
        if (stopListeningOnceRef.current) return;
        stopListeningOnceRef.current = true;
        setListening(false);
        setProgress(1);
        if (recognitionRef.current) {
            try { recognitionRef.current.stop(); } catch (e) { }
        }
        clearTimeout(micTimeoutRef.current);
        cancelProgressAnim();
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(track => track.stop());
            mediaStreamRef.current = null;
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }
        setBars(Array(8).fill(8));
    }
    // 進度條動畫
    function startProgressAnim() {
        let start = Date.now();
        function step() {
            const elapsed = Date.now() - start;
            let p = Math.max(0, 1 - elapsed / 60000);
            setProgress(p);
            if (p > 0 && listening) {
                progressAnimRef.current = requestAnimationFrame(step);
            }
        }
        progressAnimRef.current = requestAnimationFrame(step);
    }
    function cancelProgressAnim() {
        if (progressAnimRef.current) cancelAnimationFrame(progressAnimRef.current);
    }
    // 真實音量音波動畫
    React.useEffect(() => {
        let anim;
        let closed = false;
        function cleanup() {
            if (closed) return;
            closed = true;
            anim && cancelAnimationFrame(anim);
            if (mediaStreamRef.current) {
                mediaStreamRef.current.getTracks().forEach(track => track.stop());
                mediaStreamRef.current = null;
            }
            if (audioContextRef.current) {
                audioContextRef.current.close();
                audioContextRef.current = null;
            }
            setBars(Array(8).fill(8));
        }
        if (listening) {
            navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
                mediaStreamRef.current = stream;
                audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContextRef.current.createMediaStreamSource(stream);
                analyserRef.current = audioContextRef.current.createAnalyser();
                analyserRef.current.fftSize = 64;
                source.connect(analyserRef.current);
                dataArrayRef.current = new Uint8Array(analyserRef.current.frequencyBinCount);
                function animate() {
                    analyserRef.current.getByteFrequencyData(dataArrayRef.current);
                    const chunk = Math.floor(dataArrayRef.current.length / 8);
                    const barsData = Array(8).fill(0).map((_, i) => {
                        const start = i * chunk;
                        const end = start + chunk;
                        const avg = dataArrayRef.current.slice(start, end).reduce((a, b) => a + b, 0) / chunk;
                        return 8 + Math.min(avg * 0.8, 24); // 限制最大高度 32px
                    });
                    setBars(barsData);
                    anim = requestAnimationFrame(animate);
                }
                anim = requestAnimationFrame(animate);
            });
        } else {
            cleanup();
        }
        return cleanup;
    }, [listening]);
    return (
        <footer style={{
            height: 96,
            background: themeStyles?.footerBackground || '#F0F0F0',
            borderRadius: 24,
            margin: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '0 32px',
            gap: 12,
            boxShadow: themeStyles?.shadow || '0 4px 24px #0004',
            transition: 'all 0.3s ease'
        }}>
            {/* New Chat 柔和藍灰色大圓角按鈕 */}
            <button onClick={onNewChat} style={{
                height: 48,
                minWidth: 120,
                background: 'linear-gradient(90deg, #5A6BFF 0%, #6BCBFF 100%)',
                color: '#fff',
                border: 'none',
                borderRadius: 32,
                fontSize: 16,
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
                padding: '0 24px',
                boxShadow: '0 2px 8px #5A6BFF22',
                cursor: 'pointer',
                transition: 'all 0.2s'
            }}>
                <PlusIcon /> New Chat
            </button>


            {/* 麥克風按鈕外圍進度條 */}
            <div style={{ position: 'relative', width: 54, height: 54, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="54" height="54" style={{ position: 'absolute', top: 0, left: 0 }}>
                    <circle
                        cx="27" cy="27" r="25"
                        stroke={progress > 0.66 ? '#4ADE80' : progress > 0.33 ? '#FFD600' : '#FF4D4F'}
                        strokeWidth="4"
                        fill="none"
                        strokeDasharray={2 * Math.PI * 25}
                        strokeDashoffset={(1 - progress) * 2 * Math.PI * 25}
                        style={{ transition: 'stroke 0.2s' }}
                    />
                </svg>
                <div style={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    background: listening ? '#E573C7' : 'linear-gradient(135deg, #E573C7 0%, #F7B2E6 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 2px 8px #E573C722',
                    cursor: 'pointer',
                    border: listening ? '2px solid #5A6BFF' : 'none',
                    zIndex: 1
                }} onClick={handleMicClick} title={listening ? 'Listening...' : 'Voice Input'}>
                    <MicIcon />
                </div>
            </div>
            {/* 音波動畫 */}
            <div style={{ height: 32, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', marginBottom: 2, width: 48, overflow: 'hidden' }}>
                {bars.map((h, i) => (
                    <div key={i} style={{
                        width: 4,
                        height: h,
                        background: listening ? '#E573C7' : (themeStyles?.barColor || '#eee'),
                        margin: '0 1px',
                        borderRadius: 2,
                        transition: 'height 0.1s, background 0.2s',
                        maxHeight: 32
                    }} />
                ))}
            </div>
            {/* 青綠色圓形文件上传 */}
            <div style={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                background: uploading
                    ? 'linear-gradient(135deg, #FFA500 0%, #FF6347 100%)'
                    : 'linear-gradient(135deg, #4ADE80 0%, #6EE7B7 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 8px',
                boxShadow: '0 2px 8px #4ADE8022',
                cursor: uploading ? 'not-allowed' : 'pointer',
                position: 'relative',
                transition: 'all 0.3s ease'
            }} onClick={handleFileClick} title={uploading ? `Uploading... ${uploadProgress}%` : 'Select Document (PDF, Word, Excel, TXT)'}>
                {uploading ? (
                    <div style={{
                        width: 20,
                        height: 20,
                        border: '2px solid #fff',
                        borderTop: '2px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                    }} />
                ) : (
                    <FileIcon />
                )}
                <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={handleFileChange}
                    disabled={uploading}
                />
                {uploading && (
                    <div style={{
                        position: 'absolute',
                        bottom: -8,
                        left: '50%',
                        transform: 'translateX(-50%)',
                        fontSize: 10,
                        color: '#666',
                        background: '#fff',
                        padding: '2px 6px',
                        borderRadius: 8,
                        boxShadow: '0 1px 4px rgba(0,0,0,0.1)'
                    }}>
                        {uploadProgress}%
                    </div>
                )}
                {/* 文件类型提示 */}
                <div style={{
                    position: 'absolute',
                    bottom: -20,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontSize: 8,
                    color: '#999',
                    background: 'rgba(255,255,255,0.9)',
                    padding: '1px 4px',
                    borderRadius: 4,
                    whiteSpace: 'nowrap',
                    opacity: uploading ? 0 : 1,
                    transition: 'opacity 0.3s ease'
                }}>
                    PDF, DOC, XLS, TXT
                </div>
            </div>

            {/* 蓝色圆形已上传文件按钮 */}
            <div style={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                background: showUserFiles
                    ? 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)'
                    : 'linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 8px',
                boxShadow: '0 2px 8px #3B82F622',
                cursor: 'pointer',
                position: 'relative',
                transition: 'all 0.3s ease'
            }} onClick={handleShowUserFiles} title="My Uploaded Files">
                {loadingUserFiles ? (
                    <div style={{
                        width: 20,
                        height: 20,
                        border: '2px solid #fff',
                        borderTop: '2px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                    }} />
                ) : (
                    <FolderIcon />
                )}

                {/* 文件数量提示 */}
                {userFiles.length > 0 && !loadingUserFiles && (
                    <div style={{
                        position: 'absolute',
                        top: -4,
                        right: -4,
                        background: '#EF4444',
                        color: '#fff',
                        borderRadius: '50%',
                        width: 20,
                        height: 20,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 10,
                        fontWeight: 600,
                        boxShadow: '0 1px 4px rgba(0,0,0,0.2)'
                    }}>
                        {userFiles.length}
                    </div>
                )}

                {/* 文件列表提示 */}
                <div style={{
                    position: 'absolute',
                    bottom: -20,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontSize: 8,
                    color: '#999',
                    background: 'rgba(255,255,255,0.9)',
                    padding: '1px 4px',
                    borderRadius: 4,
                    whiteSpace: 'nowrap',
                    opacity: 1,
                    transition: 'opacity 0.3s ease'
                }}>
                    My Files
                </div>
            </div>
            {/* 紫色圓角輸入框 */}
            <div style={{
                flex: 1,
                maxWidth: 480,
                height: 48,
                background: 'linear-gradient(90deg, #AF52DE 0%, #B983FF 100%)',
                borderRadius: 24,
                margin: '0 2px',
                display: 'flex',
                alignItems: 'center',
                padding: '0 20px',
                position: 'relative',
                boxShadow: '0 2px 8px #AF52DE22'
            }}>
                <input
                    type="text"
                    placeholder="Type message"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
                    style={{
                        flex: 1,
                        height: 32,
                        border: 'none',
                        outline: 'none',
                        background: 'transparent',
                        color: '#fff',
                        fontSize: 16,
                        fontWeight: 400,
                        paddingRight: 0,
                    }}
                />
            </div>
            {/* 橙黃柔和圓形紙飛機發送 */}
            <div style={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #FFB86C 0%, #FF7E5F 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 0',
                cursor: 'pointer',
                boxShadow: '0 2px 8px #FFB86C22'
            }} onClick={handleSend}>
                <PaperPlaneIcon />
            </div>

            {/* 用户文件列表弹窗 */}
            {showUserFiles && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }} onClick={() => setShowUserFiles(false)}>
                    <div style={{
                        background: '#fff',
                        borderRadius: 16,
                        padding: 24,
                        maxWidth: 500,
                        width: '90%',
                        maxHeight: '80vh',
                        overflow: 'auto',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
                    }} onClick={(e) => e.stopPropagation()}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                            <h3 style={{ margin: 0, color: '#333', fontSize: 18, fontWeight: 600 }}>
                                My Uploaded Files
                            </h3>
                            <button
                                onClick={() => setShowUserFiles(false)}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    fontSize: 20,
                                    cursor: 'pointer',
                                    color: '#999'
                                }}
                            >
                                ×
                            </button>
                        </div>

                        {loadingUserFiles ? (
                            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                                <div style={{
                                    width: 32,
                                    height: 32,
                                    border: '3px solid #f3f3f3',
                                    borderTop: '3px solid #3B82F6',
                                    borderRadius: '50%',
                                    animation: 'spin 1s linear infinite',
                                    margin: '0 auto 16px'
                                }}></div>
                                <div style={{ color: '#666', fontSize: 14 }}>Loading your files...</div>
                            </div>
                        ) : userFiles.length > 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                {userFiles.map((filename, index) => (
                                    <div key={index} style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        padding: '12px 16px',
                                        background: '#f8f9fa',
                                        borderRadius: 8,
                                        border: '1px solid #e9ecef',
                                        transition: 'all 0.2s'
                                    }} onMouseEnter={(e) => {
                                        e.target.style.background = '#e9ecef';
                                    }} onMouseLeave={(e) => {
                                        e.target.style.background = '#f8f9fa';
                                    }}>
                                        <div style={{ marginRight: 12 }}>
                                            <span role="img" aria-label="file" style={{ fontSize: 20 }}>
                                                📄
                                            </span>
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontWeight: 500, color: '#333', fontSize: 14 }}>
                                                {filename}
                                            </div>
                                            <div style={{ fontSize: 12, color: '#666', marginTop: 2 }}>
                                                {filename.split('.').pop()?.toUpperCase() || 'Unknown'} file
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteFile(filename);
                                            }}
                                            disabled={deletingFiles.has(filename)}
                                            style={{
                                                background: deletingFiles.has(filename) ? '#ccc' : '#ff4757',
                                                color: '#fff',
                                                border: 'none',
                                                borderRadius: 6,
                                                padding: '8px',
                                                cursor: deletingFiles.has(filename) ? 'not-allowed' : 'pointer',
                                                transition: 'all 0.2s',
                                                marginLeft: 12,
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}
                                            onMouseEnter={(e) => {
                                                if (!deletingFiles.has(filename)) {
                                                    e.target.style.background = '#ff3742';
                                                }
                                            }}
                                            onMouseLeave={(e) => {
                                                if (!deletingFiles.has(filename)) {
                                                    e.target.style.background = '#ff4757';
                                                }
                                            }}
                                            title={deletingFiles.has(filename) ? "Deleting..." : "Delete file"}
                                        >
                                            {deletingFiles.has(filename) ? (
                                                <div style={{
                                                    width: 14,
                                                    height: 14,
                                                    border: '2px solid #fff',
                                                    borderTop: '2px solid transparent',
                                                    borderRadius: '50%',
                                                    animation: 'spin 1s linear infinite'
                                                }}></div>
                                            ) : (
                                                <DeleteIcon />
                                            )}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#666' }}>
                                <div style={{ fontSize: 48, marginBottom: 16 }}>📁</div>
                                <div style={{ fontSize: 16, marginBottom: 8 }}>No files uploaded yet</div>
                                <div style={{ fontSize: 14, color: '#999' }}>
                                    Upload your first document to see it here
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </footer>
    );
}

export default HomeFooter; 