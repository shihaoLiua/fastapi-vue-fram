# 前端代码深度逐行解析

> 面向后端工程师，逐文件、逐行解释每一段代码"为什么存在"和"对应后端的什么"

---

## 目录

- [前置知识：前端项目是如何跑起来的](#前置知识前端项目是如何跑起来的)
- [文件 1: `package.json` — 前端的 requirements.txt](#文件-1-packagejson--前端的-requirementstxt)
- [文件 2: `index.html` — 前端的入口点](#文件-2-indexhtml--前端的入口点)
- [文件 3: `main.ts` — 前端的 uvicorn](#文件-3-maints--前端的-uvicorn)
- [文件 4: `App.vue` — 前端的根路由](#文件-4-appvue--前端的根路由)
- [文件 5: `types/index.ts` — 前端的 Pydantic Model](#文件-5-typesindexts--前端的-pydantic-model)
- [文件 6: `api/auth.ts` — 前端的 Service Layer（认证）](#文件-6-apiauthts--前端的-service-layer认证)
- [文件 7: `api/user.ts` — 前端的 Service Layer（用户管理）](#文件-7-apiuserts--前端的-service-layer用户管理)
- [文件 8: `stores/auth.ts` — 前端的全局状态管理](#文件-8-storesauthts--前端的全局状态管理)
- [文件 9: `router/index.ts` — 前端的 URL 路由](#文件-9-routerindexts--前端的-url-路由)
- [文件 10: `views/Login.vue` — 前端的登录页面](#文件-10-viewsloginvue--前端的登录页面)
- [文件 11: `views/Register.vue` — 前端的注册页面](#文件-11-viewsregistrevue--前端的注册页面)
- [文件 12: `views/Dashboard.vue` — 前端的仪表盘页面](#文件-12-viewsdashboardvue--前端的仪表盘页面)
- [文件 13: `components/AppHeader.vue` — 前端的通用导航栏](#文件-13-componentsappheadervue--前端的通用导航栏)
- [文件 14: `vite.config.ts` — 前端的构建配置](#文件-14-viteconfigts--前端的构建配置)
- [文件 15: `tsconfig.json` — 前端的 mypy 配置](#文件-15-tsconfigjson--前端的-mypy-配置)
- [文件 16: `nginx.conf` — 前端的生产部署配置](#文件-16-nginxconf--前端的生成部署配置)
- [完整数据流全景](#完整数据流全景)
- [调试技巧大全](#调试技巧大全)
- [常见错误与解决方案](#常见错误与解决方案)

---

## 前置知识：前端项目是如何跑起来的

### 开发模式（你写代码时）

```
终端命令:  npm run dev
              │
              ▼
          Vite 开发服务器 (端口 5173)
              │
              ├─ 读取 vue/ts 文件
              ├─ 实时编译成浏览器能跑的 JS
              ├─ 提供 HMR (修改代码后不刷新页面即时生效)
              └─ 代理 /api/* 请求到后端 http://backend:8000
```

**类比后端**: `uvicorn app.main:app --reload --port 8000`

### 生产模式（Docker 部署时）

```
npm run build
    │
    ▼
vue-tsc --noEmit    ← 类型检查（类比 mypy）
vite build          ← 打包（把几十个 .vue/.ts 文件合并成几个 .js 文件）
    │
    ▼
输出到 dist/ 目录
    │
    ▼
Nginx 托管 dist/ 目录
    │
    ▼
用户访问 http://localhost → Nginx 返回 index.html → 浏览器加载 JS
```

---

## 文件 1: `package.json` — 前端的 requirements.txt

```json
{
  "name": "fastapi-vue-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",                  // npm run dev   → 启动开发服务器
    "build": "vue-tsc --noEmit && vite build",  // npm run build → 构建生产包
    "preview": "vite preview"       // 预览构建结果
  },
  "dependencies": {
    "axios": "^1.7.2",      // HTTP 客户端（类比 Python 的 httpx/requests）
    "pinia": "^2.1.7",      // 状态管理（类比后端全局变量 + Service 模式）
    "vue": "^3.4.29",       // 前端框架本身
    "vue-router": "^4.4.0"  // 前端路由（类比 FastAPI 的 @router.get）
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.5",   // Vite 的 Vue 插件
    "typescript": "~5.4.5",           // TypeScript 编译器
    "vite": "^5.3.1",                 // 构建工具（类比 webpack 的升级版）
    "vue-tsc": "^2.0.21"             // Vue 专属的类型检查器
  }
}
```

### 关键概念：dependencies vs devDependencies

| 类别 | 类比后端 | 包含在构建产物中？ |
|------|---------|-------------------|
| `dependencies` | requirements.txt 里的包 | ✅ 是，这些是运行时需要的 |
| `devDependencies` | pip 安装的 black / mypy / pytest | ❌ 否，只在开发时用 |

### 关键概念：npm install 到底做了什么？

```bash
npm install
    │
    ├─ 读取 package.json
    ├─ 下载所有 dependencies 和 devDependencies
    ├─ 放入 node_modules/ 目录
    └─ 生成 package-lock.json（锁定版本，确保所有人安装一致的版本）
```

**类比后端**: `pip install -r requirements.txt` + `pip freeze > requirements.lock`

---

## 文件 2: `index.html` — 前端的入口点

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>FastAPI Vue App</title>
  </head>
  <body>
    <div id="app"></div>
    <!-- 上面这个 <div id="app"> 是 Vue 的挂载点 -->
    <!-- Vue 会把整个应用渲染到这个 div 里面 -->

    <script type="module" src="/src/main.ts"></script>
    <!-- type="module" 表示使用 ES Module 标准 -->
    <!-- 浏览器加载 main.ts → Vite 编译后替换成编译好的 JS -->
  </body>
</html>
```

### 这和后端的区别
- **后端**: `main.py` 里直接启动服务器，监听端口
- **前端**: `index.html` 是浏览器加载的第一份文件，它引用 `main.ts`，`main.ts` 启动 Vue 应用

### SPA 的核心机制
```html
<!-- 不论用户访问 /login 还是 /dashboard -->
<!-- Nginx 都返回同一个 index.html -->
<!-- Vue Router 在浏览器端决定显示哪个页面 -->

<!-- Nginx 配置的关键： -->
location / {
    try_files $uri $uri/ /index.html;
    # 如果 URL 没有对应的真实文件，就返回 index.html
    # 让 Vue Router 来处理路由
}
```

---

## 文件 3: `main.ts` — 前端的 uvicorn

```typescript
import { createApp } from 'vue'        // 引入 Vue 框架
import { createPinia } from 'pinia'    // 引入状态管理库
import App from './App.vue'            // 引入根组件（类比 FastAPI 的 app 对象）
import { router } from './router'      // 引入路由配置

// 创建 Vue 应用实例
// 类比: app = FastAPI()
const app = createApp(App)

// 创建 Pinia 状态管理实例
// 类比: 创建一个全局字典来存储共享状态
const pinia = createPinia()

// 挂载 Pinia 到应用
// 类比: app.add_middleware(GlobalStateMiddleware)
app.use(pinia)

// 挂载路由到应用
// 类比: app.include_router(auth_router)
app.use(router)

// 把 Vue 应用挂载到 index.html 的 <div id="app"> 上
// 类比: uvicorn.run(app, host="0.0.0.0", port=8000)
app.mount('#app')
```

### 执行顺序

```
1. createApp(App)      ← 创建 Vue 应用
2. app.use(pinia)      ← 注册 Pinia（这样所有组件都能用 useXxxStore）
3. app.use(router)     ← 注册 Router（这样模板里能用 <router-link> <router-view>）
4. app.mount('#app')   ← 开始渲染
     │
     ▼
   App.vue 的 onMounted 被执行
     │
     ▼
   authStore.init() 被调用（检查本地是否有 token）
     │
     ▼
   Router 根据当前 URL 决定显示 Login/Dashboard/Register
```

---

## 文件 4: `App.vue` — 前端的根路由

```vue
<script setup lang="ts">
// <script setup> 是 Vue 3 的写法
// 类比 FastAPI 的：@app.on_event("startup")
// 这里的代码在组件创建时执行一次

import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/AppHeader.vue'

const authStore = useAuthStore()
// 获取 auth store 的实例
// 类比: auth_service = AuthService()

onMounted(async () => {
  // onMounted: 组件挂载到 DOM 后执行
  // 类比: @app.on_event("startup")
  // 在应用启动时检查用户是否已登录
  await authStore.init()
})
</script>

<template>
  <!-- template: 组件的 HTML 模板 -->
  <!-- 类比: Jinja2 模板文件 -->

  <div class="app">
    <AppHeader />
    <!-- 导航栏组件，所有页面共享 -->

    <main class="main-content">
      <router-view />
      <!-- ★ 核心：router-view 会根据当前 URL 自动切换显示哪个页面 -->
      <!-- /login     → 显示 Login.vue -->
      <!-- /register  → 显示 Register.vue -->
      <!-- /dashboard → 显示 Dashboard.vue -->
    </main>
  </div>
</template>
```

### App.vue 的职责

```
App.vue
  ├─ onMounted 时初始化认证状态
  ├─ 始终显示 AppHeader（导航栏）
  ├─ <router-view> 根据 URL 切换页面内容
  └─ 定义全局 CSS 样式
```

### `@/` 是什么？

```typescript
import { useAuthStore } from '@/stores/auth'
// @ 是路径别名，在 vite.config.ts 中配置
// 等价于: import { useAuthStore } from '../src/stores/auth'
// 类比 Python 的: from app.stores import auth
```

---

## 文件 5: `types/index.ts` — 前端的 Pydantic Model

```typescript
// 这个文件定义所有 API 请求/响应的数据结构
// ★ 它和后端的 Pydantic Model 是一一对应的！

// 后端对应: class UserResponse(BaseModel)
// Python 有运行时类型检查（pydantic）
// TypeScript 只在编译时检查（编译后类型信息就没了）
export interface User {
  id: number
  username: string
  email: string
  full_name: string | null    // | null 相当于 Python 的 Optional[str]
  is_active: boolean
  is_superuser: boolean
  created_at: string           // 注意：前端用 string 表示日期
  updated_at: string           // 后端用 datetime，JSON 序列化后变成 string
}

// 后端对应: class UserCreate(BaseModel)
export interface UserCreate {
  username: string
  email: string
  password: string
  full_name?: string            // ? 表示可选字段（Python 的 Optional）
}

// 后端对应: class UserUpdate(BaseModel) — 所有字段都可选
export interface UserUpdate {
  username?: string
  email?: string
  full_name?: string
  password?: string
  is_active?: boolean
  is_superuser?: boolean
}

// 后端对应: class Token(BaseModel)
export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface TokenRefresh {
  refresh_token: string
}

// 后端对应: class Message(BaseModel)
export interface Message {
  message: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

// 后端返回的错误格式
export interface ApiError {
  detail: string    // FastAPI 默认的错误格式
}
```

### 后端模型 vs 前端接口对照表

| 后端 (Python) | 前端 (TypeScript) | 说明 |
|-------------|------------------|------|
| `class UserResponse(BaseModel)` | `interface User` | 返回的用户数据 |
| `class UserCreate(BaseModel)` | `interface UserCreate` | 注册请求体 |
| `class Token(BaseModel)` | `interface Token` | 登录返回的 token |
| `class Message(BaseModel)` | `interface Message` | 通用消息响应 |
| `detail: str` (422 错误) | `interface ApiError` | 错误信息 |
| `list[User]` | `User[]` | 用户列表 |

### 为什么前端需要重复定义类型？

```
后端:
  Pydantic 在运行时校验数据 → 返回给前端的 JSON 肯定符合类型

前端:
  TypeScript interface 只在编译时检查
  作用：写代码时有自动补全、防止拼写错误
  运行时：interface 不存在了，只是普通的 JavaScript 对象

★ 关键：前后端类型必须手动保持同步！
```

---

## 文件 6: `api/auth.ts` — 前端的 Service Layer（认证）

这是前端最核心的文件之一，包含了**所有认证相关的 API 调用**和**两个关键拦截器**。

```typescript
import axios from 'axios'
import type { Token, User, UserCreate, Message, ChangePasswordRequest } from '@/types'

// ============================
// 第一步：创建 axios 实例
// ============================
// 类比: httpx.AsyncClient(base_url="http://backend:8000/api/v1")
const api = axios.create({
  baseURL: '/api/v1',      // 所有请求的前缀
  headers: {
    'Content-Type': 'application/json',  // 默认请求格式
  },
})

// ============================
// 第二步：请求拦截器（最关键的部分之一）
// ============================
// 在每次发送请求前自动执行
// 类比: FastAPI 的 @app.middleware("http")
//       或者 Depends(get_current_user) 的自动注入
api.interceptors.request.use((config) => {
  // 从 localStorage（浏览器本地存储）取出 token
  const token = localStorage.getItem('access_token')

  if (token) {
    // 自动给每个请求加上 Authorization header
    // 后端对应: Authorization: Bearer xxx
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ============================
// 第三步：响应拦截器（自动处理 401）
// ============================
// 在收到响应后自动执行
// ★ 这是前端"无感刷新 token"的核心机制
api.interceptors.response.use(
  // 请求成功 → 直接返回响应
  (response) => response,

  // 请求失败 → 尝试处理错误
  async (error) => {
    const originalRequest = error.config

    // 如果是 401 错误，且没有重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // 尝试用 refresh_token 换取新的 access_token
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          // 注意：这里用独立的 axios 请求，避免循环拦截
          const response = await axios.post<Token>('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          })

          // 保存新 token
          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          // 用新 token 重试原来的请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch {
          // 刷新失败 → 清除所有 token → 跳转登录页
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        // 没有 refresh_token → 直接跳转登录页
        window.location.href = '/login'
      }
    }

    // 其他错误正常抛出，让调用方处理
    return Promise.reject(error)
  }
)

// ============================
// 第四步：API 方法
// ============================
export const authApi = {
  // POST /api/v1/auth/register
  async register(data: UserCreate): Promise<User> {
    const response = await api.post<User>('/auth/register', data)
    return response.data
    // 前端: response.data 就是后端返回的 JSON 解析后的对象
    // 后端: return user → JSON 序列化 → HTTP response body
  },

  // POST /api/v1/auth/login
  // ★ 注意：登录用表单格式，不是 JSON
  async login(username: string, password: string): Promise<Token> {
    const params = new URLSearchParams()
    // URLSearchParams 生成: username=xxx&password=xxx
    // 因为后端 OAuth2PasswordRequestForm 需要 application/x-www-form-urlencoded
    params.append('username', username)
    params.append('password', password)
    const response = await axios.post<Token>('/api/v1/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },

  // POST /api/v1/auth/refresh
  async refresh(refreshToken: string): Promise<Token> {
    const response = await api.post<Token>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  // POST /api/v1/auth/logout
  async logout(refreshToken: string): Promise<Message> {
    const response = await api.post<Message>('/auth/logout', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  // GET /api/v1/auth/me
  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  // PUT /api/v1/auth/change-password
  async changePassword(oldPassword: string, newPassword: string): Promise<Message> {
    const response = await api.put<Message>('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return response.data
  },
}
```

### 请求拦截器的作用

```
┌─────────────────────────────────────────────────────────┐
│  每次 API 请求自动经过拦截器                               │
│                                                         │
│  authApi.getMe()                                         │
│       │                                                  │
│       ▼                                                  │
│  请求拦截器: config.headers.Authorization = "Bearer xxx"   │
│       │                                                  │
│       ▼                                                  │
│  GET /api/v1/auth/me (带 Authorization header)           │
│       │                                                  │
│       ▼                                                  │
│  响应拦截器: 检查 status code                              │
│       │                                                  │
│       ├─ 200 → 返回 response                             │
│       └─ 401 → 自动刷新 token → 重试请求                   │
└─────────────────────────────────────────────────────────┘
```

### 为什么 login 方法不用 api 实例而是用独立的 axios？

```typescript
// 登录时不能走请求拦截器！
// 因为此时还没有 token，请求拦截器加了 Authorization: Bearer null 反而坏事

// 登录用独立的 axios.post，不走拦截器
const response = await axios.post<Token>('/api/v1/auth/login', params, { ... })

// 登录后的其他请求用 api 实例（带拦截器）
const response = await api.get<User>('/auth/me')
```

---

## 文件 7: `api/user.ts` — 前端的 Service Layer（用户管理）

```typescript
import axios from 'axios'
import type { User, UserUpdate, Message } from '@/types'

// 创建同样的 api 实例
const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// 同样的请求拦截器（自动加 token）
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const userApi = {
  // GET /api/v1/users/?skip=0&limit=100
  async getUsers(skip = 0, limit = 100): Promise<User[]> {
    const response = await api.get<User[]>('/users/', {
      params: { skip, limit },    // query 参数
    })
    return response.data
  },

  // GET /api/v1/users/{id}
  async getUser(id: number): Promise<User> {
    const response = await api.get<User>(`/users/${id}`)
    return response.data
  },

  // PUT /api/v1/users/{id}
  async updateUser(id: number, data: UserUpdate): Promise<User> {
    const response = await api.put<User>(`/users/${id}`, data)
    return response.data
  },

  // DELETE /api/v1/users/{id}
  async deleteUser(id: number): Promise<Message> {
    const response = await api.delete<Message>(`/users/${id}`)
    return response.data
  },
}
```

### 为什么 auth.ts 和 user.ts 各有一个 api 实例？

这是**设计选择**。可以有多种做法：

| 方式 | 优点 | 缺点 |
|------|------|------|
| 各自创建 api 实例 | 文件独立，互不影响 | 重复代码 |
| 共享一个 api 实例 | 少写重复代码 | 文件耦合 |
| 封装一个 `http.ts` 统一导出 | ★ 最佳实践 | 多一个文件 |

**本项目用了简单的各自创建方式**，便于理解。在实际项目中，通常会抽一个 `http.ts`：

```typescript
// http.ts（最佳实践）
import axios from 'axios'

const http = axios.create({ baseURL: '/api/v1' })
http.interceptors.request.use(/* 加 token */)
http.interceptors.response.use(/* 处理 401 */)

export default http

// auth.ts
import http from './http'
export const authApi = {
  getMe: () => http.get('/auth/me'),
}
```

---

## 文件 8: `stores/auth.ts` — 前端的全局状态管理

这是前端最关键的逻辑文件，它**管理所有和用户认证相关的状态**。

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api/auth'

// ============================
// defineStore 定义一个"状态容器"
// 第一个参数 'auth' 是 store 的唯一 ID
// 第二个参数是工厂函数，返回 store 的属性和方法
// ============================
// 类比:
//   class AuthService:
//       user: User | None = None
//       loading: bool = False
//       initialized: bool = False
//
//       @property
//       def is_authenticated(self): return self.user is not None
//
//       async def login(self, username, password): ...
//
//   auth_service = AuthService()  // 全局单例
export const useAuthStore = defineStore('auth', () => {

  // ============================
  // 状态（State）—— 类比 Python 的实例变量
  // ============================

  // ref 创建响应式数据
  // 类比: self.user: User | None = None
  // 区别: 在 Python 中 user = None，赋值就是 user = new_value
  //       在 Vue 中 user = ref(null)，赋值必须 user.value = new_value
  //       ★ 模板中自动解包，不需要 .value
  const user = ref<User | null>(null)

  // ref(true/false) 表示加载状态
  const loading = ref(false)

  // 是否已经完成初始化检查
  const initialized = ref(false)

  // ============================
  // 计算属性（Getters）—— 类比 Python 的 @property
  // ============================

  // computed 会根据依赖自动重新计算
  // 当 user.value 变化时，isAuthenticated 自动更新
  const isAuthenticated = computed(() => !!user.value)
  // !! 的作用：把值转成 boolean
  // null → false, User对象 → true

  const isSuperuser = computed(() => user.value?.is_superuser ?? false)
  // ?. 是可选链：如果 user.value 是 null，不会报错，返回 undefined
  // ?? 是空值合并：如果 ?? 左边是 null/undefined，用右边的 false

  // ============================
  // 动作（Actions）—— 类比 Python 的 async method
  // ============================

  // ★ init() 是应用的启动初始化
  // 被 App.vue 的 onMounted 调用
  async function init() {
    // 1. 检查 localStorage 是否有 access_token
    const token = localStorage.getItem('access_token')
    if (!token) {
      // 没有 token → 未登录状态
      initialized.value = true
      return
    }

    try {
      loading.value = true
      // 2. 有 token → 尝试获取用户信息
      user.value = await authApi.getMe()
    } catch {
      // 3. getMe 失败（token 过期）→ 尝试刷新
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          // 4. 刷新成功 → 保存新 token → 重新获取用户信息
          const tokens = await authApi.refresh(refreshToken)
          localStorage.setItem('access_token', tokens.access_token)
          localStorage.setItem('refresh_token', tokens.refresh_token)
          user.value = await authApi.getMe()
        } catch {
          // 5. 刷新也失败 → 清除所有 token
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

  // login() 被 Login.vue 调用
  async function login(username: string, password: string) {
    loading.value = true
    try {
      // 1. 调 API 登录
      const tokens = await authApi.login(username, password)
      // 2. 保存 token 到 localStorage（浏览器持久存储）
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      // 3. 获取用户信息，更新全局状态
      user.value = await authApi.getMe()
      return true
    } catch (error) {
      // 登录失败 → 清除可能残留的 token
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      throw error  // 继续抛出，让 Login.vue 显示错误
    } finally {
      loading.value = false
    }
  }

  // register() 被 Register.vue 调用
  async function register(username: string, email: string, password: string, fullName?: string) {
    loading.value = true
    try {
      await authApi.register({ username, email, password, full_name: fullName })
      return true
    } finally {
      loading.value = false
    }
  }

  // logout() 被 AppHeader.vue 调用
  async function logout() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        // 通知后端将 token 加入黑名单
        await authApi.logout(refreshToken)
      } catch {
        // 即使后端请求失败，前端也要清除本地状态
      }
    }
    // 清除本地所有认证信息
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    // 跳转到登录页
    window.location.href = '/login'
  }

  // changePassword() 被 Dashboard.vue 调用
  async function changePassword(oldPassword: string, newPassword: string) {
    await authApi.changePassword(oldPassword, newPassword)
  }

  // ============================
  // 导出 store 的公共接口
  // ============================
  return {
    // 状态
    user,         // 当前用户信息
    loading,      // 是否正在加载
    initialized,  // 是否已完成初始化

    // 计算属性
    isAuthenticated,  // 是否已登录（根据 user 是否为 null 自动判断）
    isSuperuser,      // 是否是管理员

    // 方法
    init,
    login,
    register,
    logout,
    changePassword,
  }
})
```

### Pinia Store 的核心概念

```
┌──────────────────────────────────────────────────────┐
│                     Pinia Store                        │
│                                                        │
│  State (状态)   →  user, loading, initialized           │
│                     ↓ 读写                              │
│  Getters (计算)  →  isAuthenticated, isSuperuser        │
│                     当 user 变化时自动重新计算            │
│                     ↓ 只读                              │
│  Actions (方法)  →  login, logout, init, ...            │
│                     调用 API、更新 State                 │
└──────────────────────────────────────────────────────┘
```

### 为什么需要 `user.value` 而不是直接 `user`？

```typescript
// ref 是 Vue 的响应式包装器
const user = ref<User | null>(null)

// 在 <script> 中读写必须用 .value
user.value = newUser       // 设置值
console.log(user.value)    // 读取值

// 在 <template> 中不需要 .value，Vue 自动解包
// <span>{{ user?.username }}</span>  ← 正确
// <span>{{ user.value?.username }}</span>  ← 错误
```

### localStorage 是什么？

```typescript
// localStorage 是浏览器提供的持久化存储
// 类比: Python 中的文件存储或 Redis

// 写入（数据关闭浏览器后仍然存在）
localStorage.setItem('access_token', 'xxx')

// 读取
const token = localStorage.getItem('access_token')

// 删除
localStorage.removeItem('access_token')

// ★ 和 Session 的区别
// localStorage:  手动清除或代码清除，关闭浏览器不会丢失
// sessionStorage: 关闭浏览器标签页自动清除
```

---

## 文件 9: `router/index.ts` — 前端的 URL 路由

```typescript
import { createRouter, createWebHistory } from 'vue-router'
// createRouter: 创建路由实例
// createWebHistory: 使用 HTML5 History 模式（URL 中没有 #）
//                   浏览器支持在 JS 中修改 URL 而不刷新页面

import type { RouteRecordRaw } from 'vue-router'

// ============================
// 定义路由表
// ============================
// 类比: FastAPI 的 router.include_router(...)
// 或者 Flask 的 @app.route("/login")
const routes: RouteRecordRaw[] = [
  {
    path: '/',              // 访问根路径
    redirect: '/dashboard',  // 重定向到 /dashboard
  },
  {
    path: '/login',
    name: 'Login',
    // 懒加载：只有访问 /login 时才加载 Login.vue
    // 类比 Python 的: from app.views import login
    // 只在需要的时候导入，减少首次加载体积
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },  // 自定义元数据：不需要登录
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true },   // 需要登录才能访问
  },
]

// 创建路由实例
export const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ============================
// 导航守卫（最重要的部分）
// ============================
// 类比: FastAPI 的 @app.middleware("http")
// 每次 URL 变化时执行
router.beforeEach(async (to, from, next) => {
  // to:   要跳转到的路由
  // from: 当前路由
  // next: 放行函数

  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth !== false && !token) {
    // 需要登录但没 token → 跳转到登录页
    next('/login')
  } else if ((to.name === 'Login' || to.name === 'Register') && token) {
    // 已登录但访问登录/注册页 → 跳转到仪表盘
    next('/dashboard')
  } else {
    // 其他情况正常放行
    next()
  }
})

// ★ 三种 next() 的作用：
// next()          → 正常放行
// next('/login')  → 跳转到登录页
// next(false)     → 取消导航（留在当前页）
```

### 路由守卫的决策流程

```
用户访问 /dashboard
       │
       ▼
  router.beforeEach 执行
       │
       ├─ meta.requiresAuth = true
       │      │
       │      ├─ 有 token → next() ✅ 放行
       │      └─ 无 token → next('/login') 🔒 跳转登录页
       │
       ├─ 访问 /login
       │      │
       │      ├─ 有 token → next('/dashboard') ✅ 跳转仪表盘
       │      └─ 无 token → next() ✅ 放行
       │
       └─ 其他页面 → next() ✅ 放行
```

### 懒加载（Lazy Loading）

```typescript
// ❌ 普通导入（所有页面在首次加载时全部下载）
import LoginView from '@/views/Login.vue'
import DashboardView from '@/views/Dashboard.vue'

// ✅ 懒加载（只有在需要时才下载）
// 用户访问 /login → 才下载 Login.vue 的代码
// 用户访问 /dashboard → 才下载 Dashboard.vue 的代码
component: () => import('@/views/Login.vue')
```

---

## 文件 10: `views/Login.vue` — 前端的登录页面

这是一个完整的 Vue 组件，包含**逻辑、模板、样式**三部分。

### `<script setup>` 部分（逻辑）

```vue
<script setup lang="ts">
// <script setup> 是 Vue 3 的组合式 API 写法
// ★ 这里的代码相当于后端的 route handler
// ★ 每次组件创建时执行一次

// 导入 Vue 功能
import { ref } from 'vue'
// ref: 创建响应式数据（数据变化时，视图自动更新）

// 导入 Vue Router
import { useRouter } from 'vue-router'
// useRouter: 获取路由实例，用于页面跳转

// 导入 Pinia Store
import { useAuthStore } from '@/stores/auth'

// ============================
// 获取实例
// ============================
const router = useRouter()
// 类比: 获取 FastAPI 的 Request 对象，可以 redirect

const authStore = useAuthStore()
// 类比: 获取 AuthService 单例

// ============================
// 响应式状态
// ============================
// 每个 ref 对应表单中的一个输入框
const username = ref('')        // 绑定到 <input v-model="username">
const password = ref('')        // 绑定到 <input v-model="password">
const error = ref('')           // 错误信息，显示在 <div v-if="error">
const isSubmitting = ref(false) // 防止重复提交，禁用按钮

// ============================
// 处理方法
// ============================
async function handleSubmit() {
  // 1. 前端校验（类比 Pydantic 校验）
  if (!username.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }

  isSubmitting.value = true
  error.value = ''

  try {
    // 2. 调用 Store 的 login 方法
    // Store 里会调 API、存 token、更新 user 状态
    await authStore.login(username.value, password.value)

    // 3. 登录成功 → 跳转到仪表盘
    router.push('/dashboard')
    // 类比: RedirectResponse(url="/dashboard")
  } catch (err: any) {
    // 4. 登录失败 → 显示错误信息
    // err.response.data.detail 就是后端返回的:
    //   HTTPException(detail="Incorrect username or password")
    error.value = err.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

### `<template>` 部分（HTML 模板）

```vue
<template>
  <div class="auth-container">
    <div class="auth-card">

      <!-- 头部 -->
      <div class="auth-header">
        <h1>Welcome Back</h1>
        <p>Sign in to your account</p>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleSubmit" class="auth-form">
        <!-- @submit.prevent 等同于:
             form.addEventListener('submit', (e) => {
               e.preventDefault()   // 阻止页面刷新
               handleSubmit()
             })
        -->

        <!-- 错误提示：v-if="error" 只在有错误时显示 -->
        <div v-if="error" class="alert alert-error">
          {{ error }}
          <!-- {{ }} 是插值表达式，显示变量的值 -->
        </div>

        <!-- 用户名输入框 -->
        <div class="form-group">
          <label for="username">Username or Email</label>
          <input
            id="username"
            v-model="username"
            <!-- ★ v-model 双向绑定：
                 输入框的值 → username.value
                 username.value → 输入框的值
                 类比: input.value = username; input.oninput = (e) => username = e.target.value
            -->
            type="text"
            placeholder="Enter your username or email"
            :disabled="isSubmitting"
            <!-- :disabled 是属性绑定，等于 disabled={isSubmitting} -->
            autocomplete="username"
          />
        </div>

        <!-- 密码输入框 -->
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
            :disabled="isSubmitting"
            autocomplete="current-password"
          />
        </div>

        <!-- 提交按钮 -->
        <button
          type="submit"
          class="btn btn-primary btn-block"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? 'Signing in...' : 'Sign In' }}
          <!-- 三目运算符：提交中显示 "Signing in..."，否则显示 "Sign In" -->
        </button>
      </form>

      <!-- 底部链接 -->
      <div class="auth-footer">
        <p>
          Don't have an account?
          <router-link to="/register">Register</router-link>
          <!-- ★ router-link 是 Vue 路由链接
               不会刷新页面，只切换组件
               类比 <a href="/register"> 但更好的用户体验
          -->
        </p>
      </div>

    </div>
  </div>
</template>
```

### `<style scoped>` 部分（样式）

```vue
<style scoped>
/* scoped 表示样式只对当前组件生效 */
/* 类比: CSS Modules 或 BEM 命名规范的效果 */

.auth-container {
  /* display: flex 实现垂直居中 */
  display: flex;
  justify-content: center;  /* 水平居中 */
  align-items: center;      /* 垂直居中 */
  min-height: 80vh;
  /* vh = viewport height（视口高度）
     80vh = 浏览器可视区域高度的 80% */
  padding: 2rem;  /* 1rem = 16px（默认） */
}

.auth-card {
  background: white;
  border-radius: 12px;           /* 圆角 */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);  /* 阴影 */
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
}
</style>
```

### v-model 双向绑定详解

```vue
<!-- ★ v-model 是 Vue 最常用的指令 -->
<!-- 它是语法糖，等价于： -->

<!-- 这样写： -->
<input v-model="username" />

<!-- 等于这样写： -->
<input
  :value="username"
  @input="username = $event.target.value"
/>

<!-- 类比 Python:
     input_value = ""
     input_value = request.form["username"]  # 读取
     request.form["username"] = input_value  # 写入
-->
```

### v-if 条件渲染

```vue
<!-- v-if: 条件为 true 时才渲染该元素 -->
<!-- 类比 Python: if error: print(error) -->

<!-- 只显示错误信息 -->
<div v-if="error" class="alert alert-error">{{ error }}</div>

<!-- 多分支 -->
<div v-if="loading">Loading...</div>
<div v-else-if="error">Error: {{ error }}</div>
<div v-else>Content loaded</div>
```

---

## 文件 11: `views/Register.vue` — 前端的注册页面

和 Login.vue 结构完全相同，只多了一些字段和校验逻辑。重点看差异部分：

```vue
<script setup lang="ts">
// ... 相同部分省略 ...

// 多了这些状态：
const email = ref('')
const confirmPassword = ref('')
const fullName = ref('')
const success = ref('')  // 成功提示

async function handleSubmit() {
  error.value = ''
  success.value = ''

  // 校验必需字段
  if (!username.value || !email.value || !password.value) {
    error.value = 'Please fill in all required fields'
    return
  }

  // 校验密码一致性（后端的 ChangePasswordRequest 也有类似校验）
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  // 校验密码长度
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  isSubmitting.value = true

  try {
    // 注册（不自动登录）
    await authStore.register(
      username.value,
      email.value,
      password.value,
      fullName.value || undefined,
    )
    success.value = 'Registration successful! Redirecting to login...'
    // 2秒后跳转到登录页
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err: any) {
    // 显示后端返回的错误信息
    error.value = err.response?.data?.detail || 'Registration failed.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

---

## 文件 12: `views/Dashboard.vue` — 前端的仪表盘页面

这是最复杂的页面，包含了**三个 Tab 的切换**和**管理员用户管理**。

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api/user'
import type { User } from '@/types'

const authStore = useAuthStore()

// 用户列表数据
const users = ref<User[]>([])
const loading = ref(false)

// 当前激活的 Tab
// 类型注解: activeTab 只能是这三个字符串之一
// 类比 Python 的 Literal["profile", "users", "password"]
const activeTab = ref<'profile' | 'users' | 'password'>('profile')

// 修改密码表单
const oldPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')

// 组件挂载后，管理员自动加载用户列表
onMounted(async () => {
  if (authStore.isSuperuser) {
    await loadUsers()
  }
})

// 加载用户列表（GET /api/v1/users/）
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

// 修改密码
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
    // 清空表单
    oldPassword.value = ''
    newPassword.value = ''
    confirmNewPassword.value = ''
  } catch (err: any) {
    passwordError.value = err.response?.data?.detail || 'Failed to change password'
  }
}

// 激活/停用用户（管理员功能）
async function toggleUserStatus(user: User) {
  try {
    // PUT /api/v1/users/{id} { is_active: !user.is_active }
    await userApi.updateUser(user.id, { is_active: !user.is_active })
    await loadUsers()  // 重新加载列表
  } catch (err) {
    console.error('Failed to update user:', err)
  }
}
</script>
```

### Tab 切换机制

```vue
<template>
  <div class="tabs">
    <!-- 点击按钮时改变 activeTab 的值 -->
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

  <!-- ★ 根据 activeTab 的值显示对应的内容 -->
  <div v-if="activeTab === 'profile'" class="tab-content">
    ...Profile内容...
  </div>

  <div v-if="activeTab === 'users'" class="tab-content">
    ...用户管理...
  </div>

  <div v-if="activeTab === 'password'" class="tab-content">
    ...修改密码...
  </div>
</template>
```

这是一个非常简单的 Tab 切换实现，没有用 Vue Router 的子路由。

### `v-for` 循环渲染

```vue
<!-- ★ v-for 是循环渲染 -->
<!-- 类比 Python: for user in users: -->
<!-- :key 是唯一标识，帮助 Vue 高效更新列表 -->

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Username</th>
      <th>Email</th>
      <th>Role</th>
      <th>Status</th>
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
```

### 条件类名（:class 的多种用法）

```vue
<!-- :class 语法灵活，有多种写法 -->

<!-- 1. 字符串 -->
<button class="btn btn-primary">
<!-- 最终: class="btn btn-primary" -->

<!-- 2. 数组（可以混合字符串和对象） -->
<span :class="['badge', user.is_superuser ? 'badge-admin' : 'badge-user']">
<!-- 如果 is_superuser=true: class="badge badge-admin" -->
<!-- 如果 is_superuser=false: class="badge badge-user" -->

<!-- 3. 对象（true 的 key 会被添加） -->
<button :class="{ active: activeTab === 'profile' }">
<!-- 如果 activeTab === 'profile': class="active" -->
<!-- 否则: class="" -->
```

---

## 文件 13: `components/AppHeader.vue` — 前端的通用导航栏

这是所有页面共享的顶部导航栏。

```vue
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

      <!-- Logo -->
      <router-link to="/dashboard" class="logo">
        FastAPI Vue
      </router-link>

      <!-- 导航链接（仅登录后显示） -->
      <nav v-if="authStore.isAuthenticated" class="nav-links">
        <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
      </nav>

      <!-- 右侧区域 -->
      <div class="header-right">

        <!-- 已登录 -->
        <template v-if="authStore.isAuthenticated">
          <span class="user-info">
            {{ authStore.user?.username }}
            <span v-if="authStore.isSuperuser" class="admin-badge">Admin</span>
          </span>
          <button class="btn-logout" @click="handleLogout">Logout</button>
        </template>

        <!-- 未登录 -->
        <template v-else>
          <router-link to="/login" class="nav-link">Login</router-link>
          <router-link to="/register" class="btn-register">Register</router-link>
        </template>

      </div>
    </div>
  </header>
</template>
```

### 条件渲染两种不同状态

```vue
<!-- 根据登录状态显示不同的 UI -->

<!-- 如果已登录 -->
<template v-if="authStore.isAuthenticated">
  <span>{{ authStore.user.username }}</span>
  <button @click="handleLogout">Logout</button>
</template>

<!-- 如果未登录 -->
<template v-else>
  <a href="/login">Login</a>
  <a href="/register">Register</a>
</template>
```

---

## 文件 14: `vite.config.ts` — 前端的构建配置

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  // Vue 插件（让 Vite 能处理 .vue 文件）
  plugins: [vue()],

  // 路径别名
  resolve: {
    alias: {
      // @ 指向 src/ 目录
      // 这样写 import xxx from '@/types' 就不用写相对路径了
      '@': resolve(__dirname, 'src'),
    },
  },

  // 开发服务器配置
  server: {
    port: 5173,      // 开发服务器端口
    host: true,       // 监听所有网络接口（Docker 内部需要）
    proxy: {
      // ★ 代理配置：解决跨域问题
      // 开发时前端在 :5173，后端在 :8000
      // 浏览器禁止直接跨域请求，通过代理转发
      '/api': {
        target: 'http://backend:8000',  // 转发到后端
        changeOrigin: true,
      },
    },
  },
})
```

### 为什么需要代理？

```
开发模式（无代理）:
  浏览器 http://localhost:5173  → 请求 /api/xxx
  → 浏览器向 localhost:5173 发请求
  → 但后端在 localhost:8000！
  → 浏览器报错: 跨域请求被拒绝（CORS error）

开发模式（有代理）:
  浏览器 http://localhost:5173  → 请求 /api/xxx
  → Vite 开发服务器接收到请求
  → Vite 把请求转发到 http://backend:8000/api/xxx
  → 后端处理，返回响应
  → Vite 把响应返回给浏览器
  → 浏览器以为是从 :5173 返回的，没有跨域问题

生产模式（无代理，通过 Nginx）:
  浏览器 http://localhost  → 请求 /api/xxx
  → Nginx 收到请求
  → Nginx proxy_pass 到 backend:8000/api/xxx
  → 后端返回响应
  → Nginx 返回给浏览器
  → ★ 浏览器访问的是同一个域名:80，没有跨域问题
```

---

## 文件 15: `tsconfig.json` — 前端的 mypy 配置

```json
{
  "compilerOptions": {
    "target": "ES2020",           // 编译目标：输出 ES2020 标准的 JS
    "module": "ESNext",           // 模块标准：使用最新的 ES Module
    "lib": ["ES2020", "DOM"],     // 标准库：包含 JS 和浏览器 API 的类型
    "strict": true,               // ★ 严格模式（类比 mypy --strict）
    "noUnusedLocals": false,      // 允许未使用的局部变量
    "noUnusedParameters": false,  // 允许未使用的参数
    "paths": {
      "@/*": ["./src/*"]          // 路径别名 @ → src/
    }
  },
  "include": ["src/**/*.ts", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 文件 16: `nginx.conf` — 前端的生成部署配置

```
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;  # Vue 构建产物放在这里
    index index.html;

    # ★ SPA 核心：所有路由都返回 index.html
    location / {
        try_files $uri $uri/ /index.html;
        # $uri: 请求的路径（如 /login）
        # 先尝试找真实文件 → 找不到就返回 index.html
        # 让 Vue Router 处理路由
    }

    # ★ API 代理：把 /api/ 请求转发到后端
    location /api/ {
        proxy_pass http://backend:8000;
        # 当用户访问 /api/v1/auth/login
        # Nginx 转发到 http://backend:8000/api/v1/auth/login
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 完整数据流全景

### 登录完整链路

```
用户访问 http://localhost
         │
         ▼
   Nginx 返回 index.html
         │
         ▼
   浏览器加载 JavaScript
         │
         ▼
   main.ts 启动 Vue 应用
         │
         ▼
   App.vue 的 onMounted 执行
         │
         ▼
   authStore.init()
         ├─ localStorage 无 token → initialized = true
         │
         ▼
   Router 导航守卫 → 无 token → 重定向到 /login
         │
         ▼
   Login.vue 渲染
         │
         ▼
   用户输入 admin / admin123 → 点击 "Sign In"
         │
         ▼
   handleSubmit()
         │
         ├─ 前端校验（非空检查）
         │
         ▼
   authStore.login("admin", "admin123")
         │
         ├─ authApi.login()
         │      │
         │      ▼
         │   POST /api/v1/auth/login
         │   (username=admin&password=admin123)
         │      │
         │      ▼
         │   后端验证成功 → 返回 { access_token, refresh_token }
         │
         ├─ 保存 token 到 localStorage
         │
         ├─ authApi.getMe()
         │      │
         │      ▼
         │   GET /api/v1/auth/me
         │   Authorization: Bearer xxx
         │      │
         │      ▼
         │   后端返回 { id: 1, username: "admin", ... }
         │
         ├─ user.value = { id: 1, username: "admin", ... }
         │
         ▼
   router.push('/dashboard')
         │
         ▼
   Router 导航守卫 → 有 token → 放行
         │
         ▼
   Dashboard.vue 渲染
         │
         ├─ 显示 "Welcome, Admin"
         │
         └─ authStore.isSuperuser === true
                 │
                 ▼
              onMounted → loadUsers()
                 │
                 ▼
              GET /api/v1/users/ (带 token)
                 │
                 ▼
              显示用户表格
```

### 数据流方向总结

```
单向数据流（核心原则）:

  API 响应（后端） →  Pinia Store  →  组件 (template)
                           │
                     用户操作触发
                      (点击/输入)

类比后端:
  DB 查询结果 → Service 层 → API 路由 → JSON 响应
```

---

## 调试技巧大全

### 1. 查看 API 请求和响应

```
浏览器 F12 → Network 标签
  ├─ 查看所有发出的 HTTP 请求
  ├─ 点击某请求查看 Request Headers（包括 Authorization）
  ├─ 查看 Response（后端返回的 JSON）
  └─ 查看 Status Code（200/401/422/500）

★ 这是调试 API 问题的第一工具！
```

### 2. 查看前端状态

```typescript
// 在浏览器控制台输出 store 状态
// F12 → Console
const authStore = useAuthStore()
console.log('User:', authStore.user)
console.log('Auth:', authStore.isAuthenticated)

// 查看 localStorage
console.log(localStorage.getItem('access_token'))

// 查看 Vue 组件状态（需要安装 Vue DevTools）
// Chrome 扩展商店搜索 "Vue DevTools"
```

### 3. 查看路由状态

```typescript
// 当前路由
import { useRoute } from 'vue-router'
const route = useRoute()
console.log('Current path:', route.path)
console.log('Route meta:', route.meta)
```

### 4. 常见调试手段

| 想排查的问题 | 怎么做 |
|------------|--------|
| API 返回 401 | Network → 看 Request Headers 有没有 Authorization |
| API 返回 422 | Network → Response → detail 字段显示什么校验失败 |
| API 返回 500 | 看后端日志 `docker compose logs backend` |
| 页面没更新 | 检查 ref.value 是否赋值了，console.log 确认 |
| 路由跳转不对 | 在 router.beforeEach 加 console.log(to.path, from.path) |
| 样式不对 | F12 → Elements → 检查元素的 class 和 CSS |

### 5. console 家族

```typescript
console.log('普通信息', someVariable)    // 类比 print()
console.error('错误信息', error)          // 红色输出
console.warn('警告信息')                  // 黄色输出
console.table(array)                     // 表格形式显示数组
console.time('label')                    // 性能计时开始
console.timeEnd('label')                 // 性能计时结束
```

---

## 常见错误与解决方案

### Error 1: `Cannot find module '@/xxx'`
```
原因: 路径别名没有正确配置

解决:
  1. 确认 vite.config.ts 中有 @ 别名配置
  2. 确认 tsconfig.json 中有 paths 配置
  3. 重启 Vite 开发服务器
```

### Error 2: `Property 'xxx' does not exist on type 'never'`
```
原因: 类型推断失败，TS 不知道变量的类型

解决:
  1. 加上显式类型注解
     const users = ref<User[]>([])  // 而不是 ref([])
  2. 或者用 as 断言
     const data = response.data as User
```

### Error 3: `Cannot read properties of null (reading 'xxx')`
```
原因: 尝试访问 null 对象的属性

解决:
  使用可选链 ?.
    user?.username       // 如果 user 是 null，返回 undefined 而不是报错
    user?.full_name ?? '—'  // 如果 null 或 undefined，显示 '—'
```

### Error 4: 页面空白，没有任何内容
```
原因:
  1. 浏览器控制台有 JS 错误
  2. index.html 的 <div id="app"> 和 main.ts 的 mount('#app') 不匹配
  3. Vue 组件有编译错误

解决:
  1. F12 → Console 查看错误信息
  2. 确认 mount 的 id 和 index.html 一致
```

### Error 5: API 请求跨域（CORS）
```
浏览器的报错: Access to XMLHttpRequest has been blocked by CORS policy

开发环境:
  Vite proxy 配置不对 → 检查 vite.config.ts 的 proxy 配置

生产环境:
  Nginx proxy_pass 配置不对 → 检查 nginx.conf

★ 跨域只存在于浏览器，后端用 httpx/curl 测试不会有这个问题
```

### Error 6: `Type 'null' is not assignable to type 'User'`
```
原因: 声明类型时没有包含 null

解决:
  const user = ref<User | null>(null)
  // 而不是 const user = ref<User>(null)
```

---

## 快速索引表

### 指令大全

| Vue 指令 | 作用 | 类比 |
|---------|------|------|
| `v-model="xxx"` | 表单双向绑定 | `input.value = xxx; input.oninput = () => xxx = ...` |
| `v-if="cond"` | 条件渲染 | `if cond:` |
| `v-else` | 否则 | `else:` |
| `v-for="item in list"` | 循环 | `for item in list:` |
| `v-on:click` / `@click` | 点击事件 | `button.onclick = handler` |
| `v-bind:src` / `:src` | 属性绑定 | `img.src = value` |
| `v-show="cond"` | 显示/隐藏（CSS display） | `element.style.display = cond ? '' : 'none'` |
| `v-html="html"` | 渲染原始 HTML | `element.innerHTML = html` |

### 常用 API HTTP 方法

| 前端写法 | HTTP | 后端对应 |
|---------|------|---------|
| `api.get('/users/')` | GET | `@router.get("/users/")` |
| `api.post('/auth/login', data)` | POST | `@router.post("/auth/login")` |
| `api.put('/users/1', data)` | PUT | `@router.put("/users/{id}")` |
| `api.delete('/users/1')` | DELETE | `@router.delete("/users/{id}")` |

### 组件通信方式速查

| 方式 | 方向 | 使用场景 |
|------|------|---------|
| `props` | 父 → 子 | 父组件给子组件传数据 |
| `emit` | 子 → 父 | 子组件通知父组件某事发生了 |
| Pinia Store | 任意组件 | 全局状态（用户信息、token 等） |
| `provide/inject` | 祖先 → 后代 | 跨多层传递（较少用） |

---

> 推荐学习路径：现在打开 `http://localhost`，按 F12 → Network，登录一次，观察每一个请求怎么发出的、返回了什么数据。这是最快理解前后端如何协作的方式。
