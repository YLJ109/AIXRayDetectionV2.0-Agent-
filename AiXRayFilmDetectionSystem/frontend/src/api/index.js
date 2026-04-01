import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// Token 自动刷新状态
let isRefreshing = false
let pendingRequests = []

function onTokenRefreshed(newToken) {
  pendingRequests.forEach(cb => cb(newToken))
  pendingRequests = []
}

function addPendingRequest(callback) {
  pendingRequests.push(callback)
}

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      if (res.code === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        router.push('/login')
      }
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    const originalRequest = error.config
    const status = error.response?.status

    if (status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken && !originalRequest.url?.includes('/api/auth/')) {
        if (isRefreshing) {
          return new Promise(resolve => {
            addPendingRequest(token => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(request(originalRequest))
            })
          })
        }
        originalRequest._retry = true
        isRefreshing = true

        return axios.post('/api/auth/refresh', {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        }).then(res => {
          const newToken = res.data?.data?.access_token
          if (newToken) {
            localStorage.setItem('access_token', newToken)
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            onTokenRefreshed(newToken)
            return request(originalRequest)
          }
          throw new Error('Token refresh failed')
        }).catch(() => {
          pendingRequests = []
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
          return Promise.reject(error)
        }).finally(() => {
          isRefreshing = false
        })
      }

      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else if (status === 403) {
      ElMessage.error('权限不足')
    } else {
      ElMessage.error(error.response?.data?.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

// ========== 认证接口 ==========
export const authApi = {
  login: (data) => request.post('/api/auth/login', data),
  getUserInfo: () => request.get('/api/auth/info'),
  changePassword: (data) => request.put('/api/auth/change-password', data)
}

// ========== 诊断接口 ==========
export const diagnosisApi = {
  uploadAndDiagnose: (formData) => request.post('/api/diagnosis/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getList: (params) => request.get('/api/diagnosis/list', { params }),
  getDetail: (id) => request.get(`/api/diagnosis/${id}`),
  review: (id, data) => request.put(`/api/diagnosis/${id}/review`, data),
  generateReport: (id) => request.post(`/api/diagnosis/${id}/report`),
  delete: (id) => request.delete(`/api/diagnosis/${id}`),
  getStatistics: () => request.get('/api/diagnosis/statistics')
}

// ========== 患者接口 ==========
export const patientApi = {
  getList: (params) => request.get('/api/patient/list', { params }),
  getDetail: (id) => request.get(`/api/patient/${id}`),
  create: (data) => request.post('/api/patient/create', data),
  update: (id, data) => request.put(`/api/patient/${id}`, data),
  delete: (id) => request.delete(`/api/patient/${id}`),
  getDiagnoses: (id, params) => request.get(`/api/patient/${id}/diagnoses`, { params })
}

// ========== 用户管理接口 ==========
export const userApi = {
  getList: (params) => request.get('/api/user/list', { params }),
  getDetail: (id) => request.get(`/api/user/${id}`),
  create: (data) => request.post('/api/user/create', data),
  update: (id, data) => request.put(`/api/user/${id}`, data),
  delete: (id) => request.delete(`/api/user/${id}`),
  resetPassword: (id, data) => request.put(`/api/user/${id}/reset-password`, data)
}

// ========== 系统接口 ==========
export const systemApi = {
  getSystemInfo: () => request.get('/api/system/info'),
  healthCheck: () => request.get('/api/system/health'),
  getDashboard: () => request.get('/api/system/dashboard'),
  getAuditLogs: (params) => request.get('/api/system/audit-logs', { params }),
  // 管理员专用
  getAdminOverview: () => request.get('/api/system/admin/overview'),
  getAdminStatistics: () => request.get('/api/system/admin/statistics'),
  // 系统配置
  getConfigs: (params) => request.get('/api/system/configs', { params }),
  createConfig: (data) => request.post('/api/system/configs', data),
  updateConfig: (id, data) => request.put(`/api/system/configs/${id}`, data),
  deleteConfig: (id) => request.delete(`/api/system/configs/${id}`),
  // 模型管理
  listModels: () => request.get('/api/system/admin/models'),
  uploadModel: (formData) => request.post('/api/system/admin/models/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  switchModel: (data) => request.put('/api/system/admin/models/switch', data),
  updateModelParams: (data) => request.put('/api/system/admin/models/params', data),
  // API管理
  listApiRoutes: () => request.get('/api/system/admin/api-routes')
}

// ========== LLM大模型管理接口 ==========
export const llmApi = {
  // 提供商管理
  getProviders: () => request.get('/api/llm/providers'),
  createProvider: (data) => request.post('/api/llm/providers', data),
  updateProvider: (id, data) => request.put(`/api/llm/providers/${id}`, data),
  deleteProvider: (id) => request.delete(`/api/llm/providers/${id}`),
  testProvider: (id) => request.post(`/api/llm/providers/${id}/test`),
  // 调用接口 - 支持取消请求
  chat: (data, config = {}) => request.post('/api/llm/chat', data, config),
  // 日志
  getLogs: (params) => request.get('/api/llm/logs', { params }),
  // 提供商类型
  getProviderTypes: () => request.get('/api/llm/provider-types')
}

export default request
