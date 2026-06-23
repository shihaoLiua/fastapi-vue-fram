import axios from 'axios'
import type { Token, User, UserCreate, Message, ChangePasswordRequest } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post<Token>('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export const authApi = {
  async register(data: UserCreate): Promise<User> {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  async login(username: string, password: string): Promise<Token> {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    const response = await axios.post<Token>('/api/v1/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },

  async refresh(refreshToken: string): Promise<Token> {
    const response = await api.post<Token>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  async logout(refreshToken: string): Promise<Message> {
    const response = await api.post<Message>('/auth/logout', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<Message> {
    const response = await api.put<Message>('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return response.data
  },
}
