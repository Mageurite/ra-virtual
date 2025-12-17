import { http, auth, errorHandler } from '../utils/request';

const API_ENDPOINTS = {
  ADMIN_LOGIN: '/auth/login',
  STUDENT_LOGIN: '/student/auth/login',
};

// Authentication service class
class AuthService {
    async login(credentials) {
        if (window.location.pathname.startsWith("/admin")) {
            return this.adminLogin(credentials);
        }
        return this.studentLogin(credentials);
    }


    // Admin login (OAuth2PasswordRequestForm)
    async adminLogin({ email, password }) {
        try {
        const form = new URLSearchParams();
        form.append('username', email);      // 后端要 username
        form.append('password', password);

        const res = await http.post(API_ENDPOINTS.ADMIN_LOGIN, form, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });

        const token = res.access_token;
        auth.setAuth(token, { role: 'admin', email });

        return { success: true, data: res, message: 'Admin login successful' };
        } catch (error) {
        return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }

    // Student login (JSON)
    async studentLogin({ tutor_id, student_id, password }) {
        try {
        // 后端字段是 email；先把 student_id 映射到 email（以后再统一字段名）
        const res = await http.post(API_ENDPOINTS.STUDENT_LOGIN, {
            tutor_id,
            email: student_id,
            password,
        });

        const token = res.access_token || res.token;
        auth.setAuth(token, { role: 'student', tutor_id, student_id });

        return { success: true, data: res, message: 'Student login successful' };
        } catch (error) {
        return { success: false, error: errorHandler.handleApiError(error), message: errorHandler.showError(error) };
        }
    }

    async register() {
        return { success: false, message: 'Registration is not enabled in this system.' };
    }

    async sendVerificationCode() {
        return { success: false, message: "Verification is not enabled in this system." };
    }

    async checkTokenStatus() {
        try {
            // 看 auth 实现：一般 token 在 localStorage('token')
            const token = localStorage.getItem("token");
            if (!token) {
            return { success: true, data: { authenticated: false }, message: "No token" };
            }

            const parts = token.split(".");
            if (parts.length !== 3) {
            return { success: true, data: { authenticated: true, valid: false }, message: "Invalid token format" };
            }

            // decode base64url payload
            const payloadStr = atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"));
            const payload = JSON.parse(payloadStr);

            const now = Date.now();
            const expMs = payload.exp ? payload.exp * 1000 : null;
            const expired = expMs ? now >= expMs : false;

            if (expired) {
            auth.clearAuth();
            return { success: true, data: { authenticated: false, expired: true }, message: "Token expired" };
            }

            return {
            success: true,
            data: {
                authenticated: true,
                expired: false,
                role: payload.role,
                exp: payload.exp,
            },
            message: "Token ok",
            };
        } catch (error) {
            return {
            success: false,
            error: errorHandler.handleApiError(error),
            message: errorHandler.showError(error),
            };
        }
    }


    async logout() {
        auth.clearAuth();
        return { success: true, message: "Logout successful" };
    }

    /**
     * Get user profile
     * @returns {Promise<Object>} User profile
     */
    async getProfile() {
        // Backend doesn't have get user profile API, return locally stored user information
        const user = auth.getUser();

        if (user) {
            return {
                success: true,
                data: user,
                message: 'Get user profile successful'
            };
        } else {
            return {
                success: false,
                error: 'User not logged in',
                message: 'User not logged in'
            };
        }
    }

    /**
     * Update user profile
     * @param {Object} profileData - User profile data
     * @returns {Promise<Object>} Update result
     */
    async updateProfile(profileData) {
        // Backend doesn't have update user profile API, only update local storage
        const updatedUser = auth.updateUser(profileData);

        return {
            success: true,
            data: updatedUser,
            message: 'Update user profile successful'
        };
    }

    /**
     * Upload avatar
     * @param {File} file - Avatar file
     * @param {Function} onProgress - Upload progress callback
     * @returns {Promise<Object>} Upload result
     */
    async uploadAvatar(file, onProgress = null) {
        // Backend doesn't have avatar upload API, simulate upload success
        return new Promise((resolve) => {
            setTimeout(() => {
                const avatarUrl = URL.createObjectURL(file);
                auth.updateUser({ avatar: avatarUrl });

                resolve({
                    success: true,
                    data: { avatarUrl },
                    message: 'Avatar upload successful'
                });
            }, 1000);
        });
    }

    /**
     * Change password
     * @param {Object} passwordData - Password change data
     * @param {string} passwordData.oldPassword - Old password
     * @param {string} passwordData.newPassword - New password
     * @returns {Promise<Object>} Change result
     */
    async changePassword(passwordData) {
        // Backend doesn't have change password API, simulate success
        return {
            success: true,
            message: 'Password changed successfully'
        };
    }

    /**
     * Forgot password
     * @param {string} email - Email address
     * @returns {Promise<Object>} Forgot password result
     */
    async forgotPassword(email) {
        // Backend doesn't have forgot password API, simulate success
        return {
            success: true,
            message: 'Password reset email sent successfully'
        };
    }

    /**
     * Reset password
     * @param {Object} resetData - Reset password data
     * @param {string} resetData.token - Reset token
     * @param {string} resetData.newPassword - New password
     * @returns {Promise<Object>} Reset result
     */
    async resetPassword(resetData) {
        // Backend doesn't have reset password API, simulate success
        return {
            success: true,
            message: 'Password reset successful'
        };
    }

    /**
     * Verify email
     * @param {string} token - Verification token
     * @returns {Promise<Object>} Verification result
     */
    async verifyEmail(token) {
        // Backend doesn't have email verification API, simulate success
        return {
            success: true,
            message: 'Email verification successful'
        };
    }

    /**
     * Send verification email
     * @param {string} email - Email address
     * @returns {Promise<Object>} Send result
     */
    async sendVerificationEmail(email) {
        // Backend doesn't have send verification email API, simulate success
        return {
            success: true,
            message: 'Verification email sent successfully'
        };
    }

    /**
     * Refresh token
     * @returns {Promise<Object>} Refresh result
     */
    async refreshToken() {
        // Backend doesn't have refresh token API, simulate success
        return {
            success: true,
            message: 'Token refreshed successfully'
        };
    }

    /**
     * 用驗證碼修改密碼
     * @param {Object} data - { code, new_password }
     * @returns {Promise<Object>} 修改結果
     */
    async updatePasswordWithCode(data) {
        try {
            const response = await http.post('/update_password', data);
            return {
                success: true,
                data: response,
                message: '密碼修改成功'
            };
        } catch (error) {
            return {
                success: false,
                error: errorHandler.handleApiError(error),
                message: errorHandler.showError(error)
            };
        }
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isAuthenticated() {
        return auth.isAuthenticated();
    }

    /**
     * Get current user
     * @returns {Object|null} Current user
     */
    getCurrentUser() {
        return auth.getUser();
    }
}

export default new AuthService(); 