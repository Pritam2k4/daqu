import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// API Methods
export const api = {
    // Health check
    health: async () => {
        const response = await apiClient.get('/health')
        return response.data
    },

    // ====================
    // FILE UPLOAD
    // ====================

    uploadFile: async (file) => {
        const formData = new FormData()
        formData.append('file', file)

        const response = await apiClient.post('/api/v1/upload/file', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return response.data
    },

    // ====================
    // DATABASE CONNECTION
    // ====================

    testDatabaseConnection: async (config) => {
        const response = await apiClient.post('/api/v1/database/test', config)
        return response.data
    },

    listTables: async (config) => {
        const response = await apiClient.post('/api/v1/database/list-tables', config)
        return response.data
    },

    analyzeTable: async (config) => {
        const response = await apiClient.post('/api/v1/database/analyze-table', config)
        return response.data
    },

    // ====================
    // QUALITY ANALYSIS
    // ====================

    analyzeQuality: async (sourceId) => {
        const response = await apiClient.post('/api/v1/quality/analyze', null, {
            params: { source_id: sourceId }
        })
        return response.data
    },

    getQualityReport: async (sourceId) => {
        const response = await apiClient.get(`/api/v1/quality/report/${sourceId}`)
        return response.data
    },

    getDemoReport: async () => {
        const response = await apiClient.get('/api/v1/quality/demo-report')
        return response.data
    },

    // ====================
    // AI SUGGESTIONS
    // ====================

    getSuggestions: async (sourceId) => {
        const response = await apiClient.get(`/api/v1/processing/suggestions/${sourceId}`)
        return response.data
    },

    applyFixes: async (sourceId, fixes) => {
        const response = await apiClient.post('/api/v1/processing/apply-fixes', fixes, {
            params: { source_id: sourceId }
        })
        return response.data
    },

    // ====================
    // EXPORT
    // ====================

    exportReport: async (sourceId, format = 'json') => {
        const response = await apiClient.get(`/api/v1/processing/export/${sourceId}`, {
            params: { format },
            responseType: 'blob'
        })
        return response
    },

    // ====================
    // MODEL STUDIO
    // ====================

    getSupportedModels: async () => {
        const response = await apiClient.get('/api/v1/models/supported')
        return response.data
    },

    getModelRecommendations: async (config) => {
        const response = await apiClient.post('/api/v1/models/recommend', config)
        return response.data
    },

    chatWithModelAssistant: async (config) => {
        const response = await apiClient.post('/api/v1/models/chat', config)
        return response.data
    },

    trainModel: async (config) => {
        const response = await apiClient.post('/api/v1/models/train', config)
        return response.data
    },

    compareModels: async (config) => {
        const response = await apiClient.post('/api/v1/models/compare', config)
        return response.data
    },

    getTrainingResults: async (trainingId) => {
        const response = await apiClient.get(`/api/v1/models/results/${trainingId}`)
        return response.data
    },

    getDemoModelAnalysis: async () => {
        const response = await apiClient.get('/api/v1/models/demo-analysis')
        return response.data
    },

    // ====================
    // AI ASSISTANT (Global)
    // ====================

    sendAssistantMessage: async (message) => {
        const response = await apiClient.post('/api/v1/assistant/message', { message })
        return response.data
    },

    getAssistantStatus: async () => {
        const response = await apiClient.get('/api/v1/assistant/status')
        return response.data
    },
}

export default apiClient
