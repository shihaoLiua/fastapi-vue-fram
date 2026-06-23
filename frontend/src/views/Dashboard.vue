<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api/user'
import type { User } from '@/types'

const authStore = useAuthStore()
const users = ref<User[]>([])
const loading = ref(false)
const activeTab = ref<'profile' | 'users' | 'password'>('profile')

// Password change form
const oldPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')

// Profile edit
const editMode = ref(false)
const editFullName = ref('')

onMounted(async () => {
  if (authStore.isSuperuser) {
    await loadUsers()
  }
})

async function loadUsers() {
  loading.value = true
  try {
    users.value = await userApi.getUsers()
  } catch (err) {
    console.error('Failed to load users:', err)
  } finally {
    loading.value = false
  }
}

async function handleChangePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (!oldPassword.value || !newPassword.value) {
    passwordError.value = 'Please fill in all fields'
    return
  }

  if (newPassword.value !== confirmNewPassword.value) {
    passwordError.value = 'New passwords do not match'
    return
  }

  if (newPassword.value.length < 6) {
    passwordError.value = 'New password must be at least 6 characters'
    return
  }

  try {
    await authStore.changePassword(oldPassword.value, newPassword.value)
    passwordSuccess.value = 'Password changed successfully!'
    oldPassword.value = ''
    newPassword.value = ''
    confirmNewPassword.value = ''
  } catch (err: any) {
    passwordError.value = err.response?.data?.detail || 'Failed to change password'
  }
}

async function toggleUserStatus(user: User) {
  try {
    await userApi.updateUser(user.id, { is_active: !user.is_active })
    await loadUsers()
  } catch (err) {
    console.error('Failed to update user:', err)
  }
}
</script>

<template>
  <div class="dashboard">
    <div class="welcome-banner">
      <h1>Welcome, {{ authStore.user?.full_name || authStore.user?.username }}</h1>
      <p>You are logged in as <strong>{{ authStore.user?.email }}</strong></p>
    </div>

    <div class="tabs">
      <button
        :class="['tab', { active: activeTab === 'profile' }]"
        @click="activeTab = 'profile'"
      >
        Profile
      </button>
      <button
        v-if="authStore.isSuperuser"
        :class="['tab', { active: activeTab === 'users' }]"
        @click="activeTab = 'users'"
      >
        User Management
      </button>
      <button
        :class="['tab', { active: activeTab === 'password' }]"
        @click="activeTab = 'password'"
      >
        Change Password
      </button>
    </div>

    <!-- Profile Tab -->
    <div v-if="activeTab === 'profile'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>Profile Information</h2>
          <button class="btn btn-sm" @click="editMode = !editMode">
            {{ editMode ? 'Cancel' : 'Edit' }}
          </button>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label>Username</label>
              <span>{{ authStore.user?.username }}</span>
            </div>
            <div class="info-item">
              <label>Email</label>
              <span>{{ authStore.user?.email }}</span>
            </div>
            <div class="info-item">
              <label>Full Name</label>
              <span>{{ authStore.user?.full_name || '—' }}</span>
            </div>
            <div class="info-item">
              <label>Role</label>
              <span :class="['badge', authStore.isSuperuser ? 'badge-admin' : 'badge-user']">
                {{ authStore.isSuperuser ? 'Administrator' : 'User' }}
              </span>
            </div>
            <div class="info-item">
              <label>Status</label>
              <span :class="['badge', authStore.user?.is_active ? 'badge-active' : 'badge-inactive']">
                {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <div class="info-item">
              <label>Member Since</label>
              <span>{{ new Date(authStore.user?.created_at || '').toLocaleDateString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Management Tab (Admin Only) -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>User Management</h2>
          <button class="btn btn-sm" @click="loadUsers" :disabled="loading">
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
        <div class="card-body">
          <div v-if="loading" class="loading">Loading users...</div>
          <div v-else-if="users.length === 0" class="empty">No users found.</div>
          <div v-else class="table-container">
            <table class="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span :class="['badge', user.is_superuser ? 'badge-admin' : 'badge-user']">
                      {{ user.is_superuser ? 'Admin' : 'User' }}
                    </span>
                  </td>
                  <td>
                    <span :class="['badge', user.is_active ? 'badge-active' : 'badge-inactive']">
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td>{{ new Date(user.created_at).toLocaleDateString() }}</td>
                  <td>
                    <button
                      class="btn btn-sm"
                      :class="user.is_active ? 'btn-warning' : 'btn-success'"
                      @click="toggleUserStatus(user)"
                    >
                      {{ user.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Change Password Tab -->
    <div v-if="activeTab === 'password'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>Change Password</h2>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleChangePassword" class="password-form">
            <div v-if="passwordError" class="alert alert-error">{{ passwordError }}</div>
            <div v-if="passwordSuccess" class="alert alert-success">{{ passwordSuccess }}</div>

            <div class="form-group">
              <label for="oldPassword">Current Password</label>
              <input
                id="oldPassword"
                v-model="oldPassword"
                type="password"
                placeholder="Enter current password"
                autocomplete="current-password"
              />
            </div>

            <div class="form-group">
              <label for="newPassword">New Password</label>
              <input
                id="newPassword"
                v-model="newPassword"
                type="password"
                placeholder="Enter new password (min. 6 characters)"
                autocomplete="new-password"
              />
            </div>

            <div class="form-group">
              <label for="confirmNewPassword">Confirm New Password</label>
              <input
                id="confirmNewPassword"
                v-model="confirmNewPassword"
                type="password"
                placeholder="Confirm new password"
                autocomplete="new-password"
              />
            </div>

            <button type="submit" class="btn btn-primary">
              Change Password
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-banner {
  margin-bottom: 2rem;
}

.welcome-banner h1 {
  font-size: 1.75rem;
  margin: 0 0 0.5rem;
  color: #1a202c;
}

.welcome-banner p {
  color: #718096;
  margin: 0;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0;
  border-bottom: 2px solid #e2e8f0;
  padding: 0 0.25rem;
}

.tab {
  padding: 0.75rem 1.25rem;
  border: none;
  background: none;
  font-size: 0.9rem;
  font-weight: 500;
  color: #718096;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab:hover {
  color: #4a5568;
}

.tab.active {
  color: #4299e1;
  border-bottom-color: #4299e1;
}

.tab-content {
  margin-top: 1.5rem;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.card-header h2 {
  margin: 0;
  font-size: 1.125rem;
  color: #1a202c;
}

.card-body {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.info-item label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: #a0aec0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.info-item span {
  font-size: 0.95rem;
  color: #2d3748;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge-admin {
  background: #ebf4ff;
  color: #2b6cb0;
}

.badge-user {
  background: #f0fff4;
  color: #276749;
}

.badge-active {
  background: #f0fff4;
  color: #276749;
}

.badge-inactive {
  background: #fff5f5;
  color: #c53030;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: #718096;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.table th {
  font-size: 0.75rem;
  font-weight: 600;
  color: #a0aec0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table td {
  font-size: 0.875rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  color: #4a5568;
}

.btn:hover:not(:disabled) {
  background: #f7fafc;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

.btn-primary {
  background: #4299e1;
  color: white;
  border-color: #4299e1;
}

.btn-primary:hover:not(:disabled) {
  background: #3182ce;
}

.btn-success {
  background: #48bb78;
  color: white;
  border-color: #48bb78;
}

.btn-success:hover:not(:disabled) {
  background: #38a169;
}

.btn-warning {
  background: #ed8936;
  color: white;
  border-color: #ed8936;
}

.btn-warning:hover:not(:disabled) {
  background: #dd6b20;
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

.password-form {
  max-width: 400px;
}

@media (max-width: 640px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
