import axios from 'axios';

const API_URL = 'https://resume-builder-live.onrender.com/api';
// ✅ Allow cookies/session handling
axios.defaults.withCredentials = true;

// ✅ Initial backend connection check
axios.get(`${API_URL}/status`)
    .then((response) => {
        console.log("✅ Backend connection successful:", response.data);
    })
    .catch((error) => {
        console.error("❌ Failed to connect to backend:", error.message);
    });

// ================================
// 🔐 AUTHENTICATION FUNCTIONS
// ================================

export const register = (username, password) =>
    axios.post(`${API_URL}/register`, { username, password });

export const login = (username, password) =>
    axios.post(`${API_URL}/login`, { username, password });

export const logout = () =>
    axios.post(`${API_URL}/logout`);

export const getStatus = () =>
    axios.get(`${API_URL}/status`);

// ================================
// 🤖 RESUME OPTIMIZATION FUNCTIONS
// ================================

// --- Both functions accept FormData objects ---
export const optimizeResume = (formData) => {
    return axios.post(`${API_URL}/optimize`, formData);
};

export const generatePdf = (formData) => {
    return axios.post(`${API_URL}/generate-pdf`, formData, {
        responseType: 'blob', // Crucial for file downloads
    });
};
// ✅ ADD THIS NEW FUNCTION AT THE BOTTOM OF api.js
export const sendFeedback = (feedbackData) =>
    axios.post(`${API_URL}/contact`, feedbackData);
