<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const fullName = ref('')
const error = ref('')
const success = ref('')
const isSubmitting = ref(false)

async function handleSubmit() {
  error.value = ''
  success.value = ''

  if (!username.value || !email.value || !password.value) {
    error.value = 'Please fill in all required fields'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  isSubmitting.value = true

  try {
    await authStore.register(
      username.value,
      email.value,
      password.value,
      fullName.value || undefined,
    )
    success.value = 'Registration successful! Redirecting to login...'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Create Account</h1>
        <p>Sign up to get started</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div v-if="error" class="alert alert-error">
          {{ error }}
        </div>
        <div v-if="success" class="alert alert-success">
          {{ success }}
        </div>

        <div class="form-group">
          <label for="username">Username <span class="required">*</span></label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Choose a username"
            :disabled="isSubmitting"
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="email">Email <span class="required">*</span></label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="Enter your email"
            :disabled="isSubmitting"
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label for="fullName">Full Name</label>
          <input
            id="fullName"
            v-model="fullName"
            type="text"
            placeholder="Enter your full name (optional)"
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-group">
          <label for="password">Password <span class="required">*</span></label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Create a password (min. 6 characters)"
            :disabled="isSubmitting"
            autocomplete="new-password"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password <span class="required">*</span></label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            :disabled="isSubmitting"
            autocomplete="new-password"
          />
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="isSubmitting">
          {{ isSubmitting ? 'Creating account...' : 'Create Account' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>
          Already have an account?
          <router-link to="/login">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 2rem;
}

.auth-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h1 {
  font-size: 1.75rem;
  margin: 0 0 0.5rem;
  color: #1a202c;
}

.auth-header p {
  color: #718096;
  margin: 0;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.alert-error {
  background: #fed7d7;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.alert-success {
  background: #c6f6d5;
  color: #276749;
  border: 1px solid #9ae6b4;
}

.required {
  color: #e53e3e;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #4a5568;
  font-size: 0.875rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #4299e1;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #3182ce;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #718096;
}

.auth-footer a {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
