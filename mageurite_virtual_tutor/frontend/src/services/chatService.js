import { http, errorHandler } from '../utils/request';

const API_ENDPOINTS = {
    CHAT: '/chat',
    CREATE_SESSION: '/chat/new',
    LIST_SESSIONS: '/chat/history',
    GET_MESSAGES: '/message/list',
    SET_FAVORITE: (chatId) => `/chat/${chatId}/favorite`,
    DELETE_SESSION: (chatId) => `/chat/${chatId}`,
    RECEIVE_SESSION_ID: '/sessionid'
};

class ChatService {
    /**
     * 发送聊天消息（支持文本、音频、图片、文档）
     * @param {FormData} formData - 包含 message/audio/image/document/session_id
     */
    async chat(formData) {
        try {
            const res = await http.post(API_ENDPOINTS.CHAT, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            return { success: true, data: res, message: 'Chat success' };
        } catch (error) {
            return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }

    /**
     * 创建新会话
     * @param {string} title
     */
    async createSession(title) {
        try {
            const res = await http.post(API_ENDPOINTS.CREATE_SESSION, { title });
            return { success: true, data: res, message: 'Session created' };
        } catch (error) {
            return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }

    /**
     * 获取会话历史
     */
    async listSessions() {
        try {
            const res = await http.get(API_ENDPOINTS.LIST_SESSIONS);
            return { success: true, data: res, message: 'Session list fetched' };
        } catch (error) {
            return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }

    /**
     * 获取会话消息
     * @param {string} session_id
     */
    async getMessages(session_id) {
        try {
            const res = await http.get(API_ENDPOINTS.GET_MESSAGES, { session_id });
            return { success: true, data: res, message: 'Messages fetched' };
        } catch (error) {
            return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }

    /**
     * 设置/取消会话收藏
     * @param {number} chatId
     * @param {boolean} is_favorite
     */
    async setSessionFavorite(chatId, is_favorite = true) {
        try {
            const res = await http.post(API_ENDPOINTS.SET_FAVORITE(chatId), { is_favorite });
            return { success: true, data: res, message: 'Favorite status updated' };
        } catch (error) {
            return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }

    /**
     * 删除会话
     * @param {number} chatId
     */
    async deleteSession(chatId) {
        try {
            const res = await http.delete(API_ENDPOINTS.DELETE_SESSION(chatId));
            return { success: true, data: res, message: 'Session deleted' };
        } catch (error) {
            return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }

    /**
     * 接收/保存 sessionid
     * @param {string|number} sessionid
     */
    async receiveSessionId(sessionid) {
        try {
            const res = await http.post(API_ENDPOINTS.RECEIVE_SESSION_ID, { sessionid });
            return { success: true, data: res, message: 'Session ID received' };
        } catch (error) {
            return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }
}

export default new ChatService(); 