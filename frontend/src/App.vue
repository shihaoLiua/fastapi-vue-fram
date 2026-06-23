<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/AppHeader.vue'

const authStore = useAuthStore()

onMounted(async () => {
  await authStore.init()
})
</script>

<template>
  <div class="app">
    <AppHeader />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style>
/* Global Styles */
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  background: #f7fafc;
  color: #2d3748;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: #4299e1;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.app {
  min-height: 100vh;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
