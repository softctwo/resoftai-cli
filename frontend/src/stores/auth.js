import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    username: (state) => state.user?.username || ''
  },

  actions: {
    async login(username, password) {
      try {
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)

        const response = await axios.post(`${API_BASE}/auth/login`, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })

        const { access_token, refresh_token } = response.data

        this.token = access_token
        this.refreshToken = refresh_token

        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)

        await this.fetchUser()

        return { success: true }
      } catch (error) {
        console.error('Login error:', error)
        return {
          success: false,
          error: error.response?.data?.detail || 'Login failed'
        }
      }
    },

    async register(username, email, password) {
      try {
        await axios.post(`${API_BASE}/auth/register`, {
          username,
          email,
          password
        })

        // Auto-login after registration
        return await this.login(username, password)
      } catch (error) {
        console.error('Registration error:', error)
        return {
          success: false,
          error: error.response?.data?.detail || 'Registration failed'
        }
      }
    },

    async fetchUser() {
      try {
        const response = await axios.get(`${API_BASE}/auth/me`, {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })

        this.user = response.data
      } catch (error) {
        console.error('Fetch user error:', error)
        this.logout()
      }
    },

    async refresh() {
      try {
        const response = await axios.post(`${API_BASE}/auth/refresh`, {
          refresh_token: this.refreshToken
        })

        const { access_token, refresh_token } = response.data

        this.token = access_token
        this.refreshToken = refresh_token

        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)

        return true
      } catch (error) {
        console.error('Token refresh error:', error)
        this.logout()
        return false
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null

      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    }
  }
})
