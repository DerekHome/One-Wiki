import { defineStore } from 'pinia'
import { apiClient } from '../api/client'

export interface UserInfo {
  id: number
  username: string
  role: string
  is_active: boolean
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    user: JSON.parse(localStorage.getItem('user_info') || 'null') as UserInfo | null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => {
      if (!state.user) return false
      const role = state.user.role?.toLowerCase()
      const username = state.user.username?.toLowerCase()
      // admin、owner 或用户名为 admin 的账号均拥有管理权限
      return role === 'admin' || role === 'owner' || username === 'admin'
    }
  },
  actions: {
    async login(credentials: { username: string; password: string }) {
      const res: any = await apiClient.post('/auth/login', credentials)
      const data = res.data
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('access_token', this.token)
      localStorage.setItem('user_info', JSON.stringify(this.user))
    },
    async fetchProfile() {
      if (!this.token) return
      try {
        const res: any = await apiClient.get('/auth/me')
        this.user = res.data
        localStorage.setItem('user_info', JSON.stringify(this.user))
      } catch (e) {
        this.logout()
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      window.location.href = '/login'
    }
  }
})
