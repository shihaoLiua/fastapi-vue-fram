import axios from 'axios'
import type { User, UserUpdate, Message } from '@/types'

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

export const userApi = {
  async getUsers(skip = 0, limit = 100): Promise<User[]> {
    const response = await api.get<User[]>('/users/', {
      params: { skip, limit },
    })
    return response.data
  },

  async getUser(id: number): Promise<User> {
    const response = await api.get<User>(`/users/${id}`)
    return response.data
  },

  async updateUser(id: number, data: UserUpdate): Promise<User> {
    const response = await api.put<User>(`/users/${id}`, data)
    return response.data
  },

  async deleteUser(id: number): Promise<Message> {
    const response = await api.delete<Message>(`/users/${id}`)
    return response.data
  },
}
