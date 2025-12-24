import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Coins API
export const coinsAPI = {
    list: (params) => api.get('/api/coins/', { params }),
    get: (id) => api.get(`/api/coins/${id}`),
    create: (data) => api.post('/api/coins/', data),
    update: (id, data) => api.put(`/api/coins/${id}`, data),
    delete: (id) => api.delete(`/api/coins/${id}`),
    uploadImage: (id, formData) => api.post(`/api/coins/${id}/images`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    stats: (id) => api.get(`/api/coins/${id}/stats`),
};

// Microscope API
export const microscopeAPI = {
    listDevices: () => api.get('/api/microscope/devices'),
    capture: (cameraIndex = 0) => api.post('/api/microscope/capture', null, { params: { camera_index: cameraIndex } }),
    preview: (cameraIndex = 0, cacheBust = '') =>
        `${API_BASE_URL}/api/microscope/preview?camera_index=${cameraIndex}${cacheBust ? `&t=${cacheBust}` : ''}`,
    openCamera: (cameraIndex) => api.post(`/api/microscope/camera/${cameraIndex}/open`),
    closeCamera: () => api.post('/api/microscope/camera/close'),
};

// AI API
export const aiAPI = {
    analyze: (data) => api.post('/api/ai/analyze', data, { timeout: 0 }),
    estimateValue: (coinId) => api.post(`/api/ai/estimate-value/${coinId}`),
    findSimilar: (coinId, limit = 5) => api.get(`/api/ai/similar/${coinId}`, { params: { limit } }),
};

// eBay API
export const ebayAPI = {
    createListing: (data) => api.post('/api/ebay/list', data),
    getListings: (coinId) => api.get(`/api/ebay/listings/${coinId}`),
    getStatus: (itemId) => api.get(`/api/ebay/status/${itemId}`),
    getCategories: () => api.get('/api/ebay/categories'),
};

export default api;
