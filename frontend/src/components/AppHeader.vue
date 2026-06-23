<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
}
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/dashboard" class="logo">
        FastAPI Vue
      </router-link>

      <nav v-if="authStore.isAuthenticated" class="nav-links">
        <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
      </nav>

      <div class="header-right">
        <template v-if="authStore.isAuthenticated">
          <span class="user-info">
            {{ authStore.user?.username }}
            <span v-if="authStore.isSuperuser" class="admin-badge">Admin</span>
          </span>
          <button class="btn-logout" @click="handleLogout">Logout</button>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-link">Login</router-link>
          <router-link to="/register" class="btn-register">Register</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2b6cb0;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 1rem;
  margin-left: 2rem;
}

.nav-link {
  color: #4a5568;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-link:hover {
  background: #f7fafc;
  color: #2b6cb0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.user-info {
  font-size: 0.875rem;
  color: #4a5568;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.admin-badge {
  background: #ebf4ff;
  color: #2b6cb0;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 600;
}

.btn-logout {
  padding: 0.375rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #e53e3e;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #fff5f5;
  border-color: #feb2b2;
}

.btn-register {
  padding: 0.375rem 1rem;
  background: #4299e1;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-register:hover {
  background: #3182ce;
}
</style>
