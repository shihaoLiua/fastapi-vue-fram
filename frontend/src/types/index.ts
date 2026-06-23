export interface User {
  id: number
  username: string
  email: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface UserUpdate {
  username?: string
  email?: string
  full_name?: string
  password?: string
  is_active?: boolean
  is_superuser?: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface TokenRefresh {
  refresh_token: string
}

export interface Message {
  message: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export interface ApiError {
  detail: string
}
