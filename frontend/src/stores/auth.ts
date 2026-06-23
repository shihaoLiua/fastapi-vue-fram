import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  async function init() {
    const token = localStorage.getItem('access_token')
    if (!token) {
      initialized.value = true
      return
    }

    try {
      loading.value = true
      user.value = await authApi.getMe()
    } catch {
      // Token invalid, try refresh
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const tokens = await authApi.refresh(refreshToken)
          localStorage.setItem('access_token', tokens.access_token)
          localStorage.setItem('refresh_token', tokens.refresh_token)
          user.value = await authApi.getMe()
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      } else {
        localStorage.removeItem('access_token')
      }
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function login(username: string, password: string) {
    loading.value = true
    try {
      const tokens = await authApi.login(username, password)
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      user.value = await authApi.getMe()
      return true
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      throw error
    } finally {
      loading.value = false
    }
  }

  async function register(username: string, email: string, password: string, fullName?: string) {
    loading.value = true
    try {
      await authApi.register({ username, email, password, full_name: fullName })
      return true
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken)
      } catch {
        // Ignore logout errors
      }
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    window.location.href = '/login'
  }

  async function changePassword(oldPassword: string, newPassword: string) {
    await authApi.changePassword(oldPassword, newPassword)
  }

  return {
    user,
    loading,
    initialized,
    isAuthenticated,
    isSuperuser,
    init,
    login,
    register,
    logout,
    changePassword,
  }
})
