import React, { useRef, useState, useEffect } from 'react';
import chatService from '../../services/chatService';

function HomeChatWindow({ chatId, messages }) {
    // Draggable divider
    const [width, setWidth] = useState(0); // 0 means auto flex:4
    const dragging = useRef(false);
    const startX = useRef(0);
    const startWidth = useRef(0);

    const onMouseDown = e => {
        dragging.current = true;
        startX.current = e.clientX;
        startWidth.current = width || 0;
        document.body.style.cursor = 'col-resize';
    };
    useEffect(() => {
        const onMouseMove = e => {
            if (dragging.current) {
                let delta = startX.current - e.clientX;
                let newWidth = Math.max(320, startWidth.current + delta);
                setWidth(newWidth);
            }
        };
        const onMouseUp = () => {
            dragging.current = false;
            document.body.style.cursor = '';
        };
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
        return () => {
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
        };
    }, [width]);

    return (
        <div style={{
            flex: width ? 'none' : 4,
            width: width ? width : 'auto',
            background: '#fff',
            borderRadius: 16,
            margin: 8,
            padding: 0,
            minWidth: 320,
            maxWidth: '100%',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            boxShadow: '0 2px 16px #0001',
        }}>
            {/* Draggable divider */}
            <div
                style={{ position: 'absolute', left: -8, top: 0, width: 16, height: '100%', cursor: 'col-resize', zIndex: 10 }}
                onMouseDown={onMouseDown}
            />
            {/* History messages */}
            <div style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
                {!chatId ? (
                    <div style={{ color: '#aaa', textAlign: 'center' }}>Please create a session first.</div>
                ) : messages.length === 0 ? (
                    <div style={{ color: '#aaa', textAlign: 'center' }}>No messages yet.</div>
                ) : (
                    messages
                        .filter(msg => msg.text || msg.image) // Only show messages with text or images
                        .map((msg, idx) => (
                            <div key={msg.id || idx} style={{
                                alignSelf: msg.from === 'user' ? 'flex-end' : 'flex-start',
                                background: msg.from === 'user' ? '#5A6BFF' : '#F7F9FB',
                                color: msg.from === 'user' ? '#fff' : '#333',
                                borderRadius: 16,
                                padding: '12px 20px',
                                maxWidth: 320,
                                fontSize: 16,
                                boxShadow: '0 2px 8px #0001',
                                wordBreak: 'break-all',
                                display: 'flex',
                                flexDirection: 'column'
                            }}>
                                {msg.image ? (
                                    <img src={msg.image} alt="Image message" style={{ maxWidth: 200, maxHeight: 200, borderRadius: 12 }} />
                                ) : msg.text ? (
                                    <div>{msg.text}</div>
                                ) : null}
                            </div>
                        ))
                )}
            </div>
        </div>
    );
}

export default HomeChatWindow; 