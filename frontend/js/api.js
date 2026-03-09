// frontend/js/api.js: Centralized API Client

const BASE_URL = '/api';

const API = {
    getToken() {
        return localStorage.getItem('b2m_token');
    },

    setSession(token, user) {
        localStorage.setItem('b2m_token', token);
        localStorage.setItem('b2m_user', JSON.stringify(user));
    },

    clearSession() {
        localStorage.removeItem('b2m_token');
        localStorage.removeItem('b2m_user');
    },

    getUser() {
        const u = localStorage.getItem('b2m_user');
        return u ? JSON.parse(u) : null;
    },

    isLoggedIn() {
        return !!this.getToken();
    },

    async request(endpoint, method = 'GET', body = null) {
        const headers = {
            'Content-Type': 'application/json'
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = { method, headers };
        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, config);
            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    this.clearSession(); // Token expired or invalid
                    window.dispatchEvent(new Event('auth-expired'));
                }
                throw new Error(data.error?.message || 'Something went wrong');
            }
            return data.data || data;
        } catch (error) {
            throw error;
        }
    },

    // Auth
    login: (email, password) => API.request('/login', 'POST', { email, password }),
    register: (username, email, password) => API.request('/register', 'POST', { username, email, password }),

    // Upload
    async uploadImage(file) {
        const formData = new FormData();
        formData.append('image', file);

        const headers = {};
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${BASE_URL}/upload`, {
                method: 'POST',
                headers,
                body: formData
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error?.message || 'Upload failed');
            return data.data; // Should return { image_url: '...' }
        } catch (error) {
            throw error;
        }
    },

    // Posts
    getPosts: (type = '', search = '') => API.request(`/posts?type=${type}&search=${search}`),
    createPost: (postData) => API.request('/posts', 'POST', postData),
    deletePost: (id) => API.request(`/posts/${id}`, 'DELETE'),

    // Comments
    getComments: (postId) => API.request(`/posts/${postId}/comments`),
    addComment: (postId, text) => API.request(`/posts/${postId}/comments`, 'POST', { comment_text: text }),

    // Post Status
    resolvePost: (postId) => API.request(`/posts/${postId}/resolve`, 'PUT')
};

window.API = API;
