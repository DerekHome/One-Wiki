import axios from 'axios'
import { ElMessage } from 'element-plus'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    // 统一解构响应
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      if (!response.data.success && response.data.error) {
        ElMessage.error(response.data.error.message || '操作失败')
        return Promise.reject(response.data.error)
      }
      return response.data
    }
    return response
  },
  (error) => {
    const responseError = error.response?.data?.error
    const detail = error.response?.data?.detail
    const msg = responseError?.message || (typeof detail === 'object' ? detail.message : detail) || error.message || '网络请求错误'
    if (error.response?.status === 401) {
      ElMessage.error(window.location.pathname === '/login' ? msg : '登录状态已失效，请重新登录')
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else if (error.response?.status === 403) {
      ElMessage.error(`权限不足: ${msg}`)
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)
