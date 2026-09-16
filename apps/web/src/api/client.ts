import axios from 'axios'
import { ElMessage } from 'element-plus'

const COLLECTION_PATHS = new Set([
  '/spaces',
  '/users',
  '/tags',
  '/knowledge',
  '/audit',
  '/modules',
  '/search'
])

function withCollectionSlash(url?: string) {
  if (!url) return url
  const [path, query] = url.split('?')
  if (!COLLECTION_PATHS.has(path)) return url
  return query ? `${path}/?${query}` : `${path}/`
}

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use((config) => {
  config.url = withCollectionSlash(config.url)
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
    const status = error.response?.status
    const requestUrl = String(error.config?.url || '')
    const isAuthRequest = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')
    const responseError = error.response?.data?.error
    const detail = error.response?.data?.detail
    const msg = responseError?.message || (typeof detail === 'object' ? detail.message : detail) || error.message || '网络请求错误'
    if (status === 401) {
      if (isAuthRequest || window.location.pathname === '/login') {
        ElMessage.error(msg)
      } else {
        ElMessage.error('登录状态已失效，请重新登录')
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_info')
        window.location.replace('/login')
      }
    } else if (status === 403) {
      ElMessage.error(`权限不足: ${msg}`)
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)
