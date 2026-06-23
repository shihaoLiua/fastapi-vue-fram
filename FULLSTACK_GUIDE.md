# 后端工程师的前端学习指南

> 从 FastAPI/Python 视角理解 Vue 3 + TypeScript 前端开发
> 基于本项目的 scaffold 作为实操参考

---

## 目录

1. [思维转换：后端 vs 前端](#1-思维转换后端-vs-前端)
2. [项目结构对照](#2-项目结构对照)
3. [TypeScript 速通（给 Python 开发者）](#3-typescript-速通给-python-开发者)
4. [Vue 3 核心概念](#4-vue-3-核心概念)
5. [Pinia：前端的"Service 层"](#5-pinia前端的service-层)
6. [Vue Router：前端的"URL 路由"](#6-vue-router前端的url-路由)
7. [Axios：前端的"HTTP 客户端"](#7-axios前端的http-客户端)
8. [登录鉴权全流程解析](#8-登录鉴权全流程解析)
9. [组件通信模式](#9-组件通信模式)
10. [构建与部署](#10-构建与部署)
11. [常见问题 FAQ](#11-常见问题-faq)

---

## 1. 思维转换：后端 vs 前端

### 核心差异

| 后端概念 | 前端对应 | 说明 |
|---------|---------|------|
| FastAPI route handler | Vue Component | 后端函数返回 JSON，前端组件渲染 HTML |
| Pydantic Model | TypeScript Interface | 都是运行时/编译时的数据校验 |
| Dependency Injection | Pinia Store | 都是共享状态/逻辑的注入方式 |
| SQLAlchemy ORM | Axios API call | 数据库查询 → HTTP API 调用 |
| Alembic Migration | Vite Build | 数据库迁移 → 前端构建打包 |
| uvicorn serve | `npm run dev` | 开发服务器 |
| Python `async/await` | JS `async/await` | 语法几乎相同 |
| `if __name__ == "__main__"` | `main.ts` | 应用入口 |

### 请求生命周期对比

```
后端视角:
  HTTP Request → FastAPI Route → Service Layer → DB/Redis → Response JSON

前端视角:
  User Action → Vue Component → Pinia Store → Axios API → Backend → Update UI
```

---

## 2. 项目结构对照

```
backend/                        frontend/
├── app/                        ├── src/
│   ├── main.py                 │   ├── main.ts           # 应用入口
│   ├── config.py               │   ├── .env              # 环境变量
│   ├── models/                 │   ├── types/            # 数据模型定义
│   │   └── user.py             │   │   └── index.ts      # → Pydantic Model
│   ├── schemas/                │   └── api/              # API 调用层
│   │   └── user.py             │       ├── auth.ts       # → Service Layer
│   ├── api/                    │       └── user.ts
│   │   ├── auth.py             ├── src/stores/           # 状态管理
│   │   └── users.py            │   └── auth.ts           # → Service Layer
│   ├── services/               ├── src/views/            # 页面组件
│   │   ├── auth.py             │   ├── Login.vue         # → Route Handler
│   │   └── user.py             │   ├── Register.vue
│   └── core/                   │   └── Dashboard.vue
│       ├── security.py         ├── src/router/           # URL 路由
│       └── deps.py             │   └── index.ts          # → FastAPI Router
└── requirements.txt            └── package.json          # → requirements.txt
```

**关键理解**：前端和后端都在做同一件事——接收输入、处理逻辑、返回结果。只不过后端返回 JSON，前端返回 HTML/DOM。

---

## 3. TypeScript 速通（给 Python 开发者）

### 3.1 类型系统

```typescript
// Python: Pydantic Model
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

// TypeScript: Interface（编译时类型检查）
export interface UserCreate {
  username: string
  email: string
  password: string
}
```

### 3.2 常用类型对照

| Python | TypeScript | 说明 |
|--------|-----------|------|
| `str` | `string` | 字符串 |
| `int` | `number` | 数字（含整数和浮点） |
| `bool` | `boolean` | 布尔值 |
| `None` | `null` / `undefined` | 空值 |
| `list[str]` | `string[]` | 数组 |
| `dict[str, any]` | `Record<string, any>` | 字典 |
| `Optional[str]` | `string \| null` | 可选值 |
| `Union[str, int]` | `string \| number` | 联合类型 |

### 3.3 函数定义

```typescript
// Python
async def get_user(user_id: int) -> User:
    ...

// TypeScript
async function getUser(userId: number): Promise<User> {
  // Promise<T> 相当于 Python 的 await -> T
}
```

### 3.4 常用运算符

```typescript
// 可选链（避免 None 报错）
user?.full_name        // Python: user.full_name if user else None

// 空值合并
name ?? 'Anonymous'    // Python: name or 'Anonymous'

// 解构赋值
const { id, username } = user  // Python: id, username = user.id, user.username

// 展开运算符
const newUser = { ...user, is_active: false }  // Python: {**user.dict(), "is_active": False}
```

---

## 4. Vue 3 核心概念

### 4.1 单文件组件（SFC）

Vue 组件 = 后端的"视图 + 逻辑"合并在一个文件中：

```vue
<script setup lang="ts">
// 这里相当于后端的 route handler + service 逻辑
import { ref } from 'vue'

const username = ref('')           // 状态变量（类似 self.username）
const error = ref('')

async function handleSubmit() {    // 方法
  // ...调用 API
}
</script>

<template>
  <!-- 这里相当于后端的 Jinja2 模板 / HTML 渲染 -->
  <div class="auth-card">
    <h1>Welcome Back</h1>
    <form @submit.prevent="handleSubmit">
      <input v-model="username" />
      <button type="submit">Login</button>
    </form>
    <p v-if="error">{{ error }}</p>
  </div>
</template>

<style scoped>
/* 这里的 CSS 只作用于当前组件（类似 Python 的局部变量） */
.auth-card { ... }
</style>
```

### 4.2 响应式状态

```typescript
import { ref, computed } from 'vue'

// ref：基础类型（类似 Python 变量）
const count = ref(0)
count.value++                    // 必须 .value 读写

// reactive：对象（类似 Python dict）
const user = reactive({ name: 'Alice', age: 30 })
user.age = 31                    // 直接读写

// computed：计算属性（类似 @property）
const isAdult = computed(() => user.age >= 18)

// watch：监听变化（类似 SQLAlchemy event listener）
watch(count, (newVal, oldVal) => {
  console.log(`Count changed: ${oldVal} -> ${newVal}`)
})
```

### 4.3 生命周期

```typescript
import { onMounted, onUnmounted } from 'vue'

// 对应后端的 FastAPI lifespan / startup 事件
onMounted(async () => {
  // 组件挂载到 DOM 后执行（类似 FastAPI 的 @app.on_event("startup")）
  await fetchData()
})

onUnmounted(() => {
  // 组件销毁前执行（类似 @app.on_event("shutdown")）
  cleanup()
})
```

### 4.4 条件与循环

```vue
<!-- 对应 Python 的 if/else -->
<div v-if="loading">Loading...</div>
<div v-else-if="error">Error: {{ error }}</div>
<div v-else>Content loaded</div>

<!-- 对应 Python 的 for 循环 -->
<tr v-for="user in users" :key="user.id">
  <td>{{ user.username }}</td>
  <td>{{ user.email }}</td>
</tr>
<!-- 等价于 Python: for user in users: ... -->
```

### 4.5 事件绑定

```vue
<!-- 对应 Python 的函数调用 -->
<button @click="handleSubmit">Submit</button>
<!-- 等价于: button.onclick = handleSubmit -->

<input v-model="username" />
<!-- 等价于: input.value = username; input.oninput = (e) => username = e.target.value -->

<form @submit.prevent="handleSubmit">
<!-- .prevent 相当于 e.preventDefault() -->
```

---

## 5. Pinia：前端的"Service 层"

Pinia 是 Vue 的状态管理库，相当于后端的 **Service Layer + Global State**。

### 后端 vs 前端状态管理对照

```python
# 后端: FastAPI Depends + Service
@router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# 依赖注入 -> 每个请求都重新解析
```

```typescript
// 前端: Pinia Store
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)     // 全局用户状态

  const isAuthenticated = computed(() => !!user.value)  // 计算属性

  async function login(username: string, password: string) {
    const tokens = await authApi.login(username, password)
    localStorage.setItem('access_token', tokens.access_token)
    user.value = await authApi.getMe()     // 更新全局状态
  }

  async function logout() {
    localStorage.removeItem('access_token')
    user.value = null                      // 清空全局状态
    window.location.href = '/login'        // 跳转
  }

  return { user, isAuthenticated, login, logout }
})

// 在任何组件中使用：
const authStore = useAuthStore()
authStore.login('admin', 'admin123')
```

### 为什么需要 Pinia？

| 场景 | 无 Pinia（麻烦） | 有 Pinia（简洁） |
|------|-----------------|-----------------|
| 多个页面都需要当前用户 | 每个页面都调一次 API | 共享 `authStore.user` |
| 用户登出 | 每个页面写一遍清除逻辑 | 调用 `authStore.logout()` |
| 更新用户信息 | 到处手动同步 | Store 自动响应式更新 |

---

## 6. Vue Router：前端的"URL 路由"

```typescript
// Python: FastAPI Router
router.add_api_route("/auth/login", login_handler)
router.add_api_route("/dashboard", dashboard_handler)

// TypeScript: Vue Router
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },        // 类似 FastAPI 的 dependencies
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true },         // 需要登录
  },
]
```

### 路由守卫（类似 FastAPI Middleware）

```typescript
// Python: FastAPI Middleware
@app.middleware("http")
async def auth_middleware(request, call_next):
    if request.url.path.startswith("/dashboard"):
        token = request.headers.get("Authorization")
        if not token:
            return RedirectResponse("/login")
    return await call_next(request)

// TypeScript: Navigation Guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) {
    next('/login')          // 跳转登录页
  } else {
    next()                  // 放行
  }
})
```

### `<router-link>` 替代 `<a>` 标签

```vue
<!-- 不要用 <a href="/login">，会导致页面刷新 -->
<router-link to="/login">Login</router-link>
<!-- 等价于后端的: <a href="/login"> 但不会刷新页面 -->
```

---

## 7. Axios：前端的"HTTP 客户端"

```typescript
import axios from 'axios'

// 创建实例（类似后端 httpx.AsyncClient）
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// 请求拦截器（在请求发出前执行）
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    // 相当于后端的: Authorization: Bearer xxx
  }
  return config
})

// 响应拦截器（在响应返回后执行）
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 类似后端的 HTTPException(status_code=401)
      // 尝试刷新 token...
    }
    return Promise.reject(error)
  }
)
```

### API 调用方式

```typescript
// GET 请求
const user = await api.get<User>('/auth/me')

// POST 请求
const token = await api.post<Token>('/auth/login', formData)

// PUT 请求
const updated = await api.put<User>(`/users/${id}`, updateData)

// DELETE 请求
await api.delete(`/users/${id}`)
```

---

## 8. 登录鉴权全流程解析

这是前后端协作最核心的部分，**理解了它就理解了 90% 的全栈交互**。

### 8.1 登录流程

```
用户填写表单                         Frontend                          Backend
        │                              │                                │
        │  点击"Sign In"                │                                │
        ├─────────────────────────────►│                                │
        │                              │                                │
        │                     authStore.login(username, password)        │
        │                              ├───────────────────────────────►│
        │                              │   POST /api/v1/auth/login      │
        │                              │   (username + password)        │
        │                              │                                │
        │                              │   验证密码 ✓                    │
        │                              │   生成 access_token            │
        │                              │   生成 refresh_token           │
        │                              │◄───────────────────────────────┤
        │                              │   { access_token, refresh_token }
        │                              │                                │
        │                     localStorage.setItem('access_token', ...) │
        │                     localStorage.setItem('refresh_token', ...)│
        │                              │                                │
        │                     authApi.getMe()                           │
        │                              ├───────────────────────────────►│
        │                              │   GET /api/v1/auth/me          │
        │                              │   Authorization: Bearer xxx    │
        │                              │◄───────────────────────────────┤
        │                              │   { id, username, email, ... } │
        │                              │                                │
        │                     authStore.user = response                 │
        │                     router.push('/dashboard')                 │
        │◄─────────────────────────────┤                                │
        │  看到仪表盘                                                   │
```

### 8.2 前端如何保持登录状态

```typescript
// App.vue - 应用启动时初始化
onMounted(async () => {
  const token = localStorage.getItem('access_token')
  if (token) {
    // 有 token → 尝试获取用户信息
    // 如果 token 过期 → 用 refresh_token 刷新
    // 如果刷新也失败 → 清除 token，回到登录页
    await authStore.init()
  }
})

// 之后的每个 API 请求：
// 1. 请求拦截器自动添加 Authorization header
// 2. 如果返回 401 → 自动用 refresh_token 重试
// 3. 重试失败 → 清除状态 → 跳转登录页
```

### 8.3 401 自动重试机制

```typescript
// 对应后端的: 过期 token → 返回 401 → 客户端用 refresh token 重试
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      const response = await axios.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken,
      })

      // 保存新 token
      localStorage.setItem('access_token', response.data.access_token)

      // 用新 token 重试原请求
      originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
      return api(originalRequest)
    }
  }
)
```

### 8.4 登出流程

```
用户点击 Logout
  → authStore.logout()
    → POST /api/v1/auth/logout (把 token 加入黑名单)
    → localStorage.removeItem('access_token')
    → localStorage.removeItem('refresh_token')
    → user.value = null
    → window.location.href = '/login'  (跳转登录页)
```

---

## 9. 组件通信模式

### 9.1 父子组件通信

```vue
<!-- 父组件传递数据给子组件（类似函数传参） -->
<ChildComponent
  :user="currentUser"
  @update="handleUpdate"
/>

<!-- 子组件接收 -->
<script setup lang="ts">
const props = defineProps<{
  user: User            // 等价于后端: def child(user: User)
}>()

const emit = defineEmits<{
  update: [id: number]  // 等价于后端: callback function
}>()
</script>
```

### 9.2 跨组件共享状态

```typescript
// 任何组件都可以访问 Store（类似后端的全局单例）
const authStore = useAuthStore()
// authStore.user 在所有组件中保持一致
// 修改后所有引用该 store 的组件自动更新
```

### 9.3 通信方式选择

| 场景 | 方式 | 类比后端 |
|------|------|---------|
| 父子组件传值 | `props` / `emit` | 函数参数 / 回调函数 |
| 全局状态 | Pinia Store | 全局变量 / Redis Cache |
| 跨层级传递 | `provide` / `inject` | ContextVar / ThreadLocal |

---

## 10. 构建与部署

### 10.1 开发流程

```bash
# 后端开发
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 前端开发（新开终端）
cd frontend
npm run dev
# → 启动 Vite 开发服务器 :5173
# → HMR (Hot Module Replacement): 修改代码立即生效，无需刷新页面
```

### 10.2 生产构建

```bash
# 后端：Python 代码无需构建，直接运行
# 前端：需要编译
npm run build
# → vue-tsc --noEmit    (类型检查，类比 mypy)
# → vite build          (打包，类比 webpack)
# → 输出到 dist/ 目录   (静态文件，由 Nginx 托管)
```

### 10.3 环境变量

```typescript
// 前端的编译时环境变量（以 VITE_ 开头）
console.log(import.meta.env.VITE_API_URL)

// 前端的运行时配置（在 index.html 中注入）
// 注意: 前端的 .env 是编译时注入，修改后需要重新构建
```

---

## 11. 常见问题 FAQ

### Q1: 为什么我改了代码页面没变化？

```
检查是否在运行 `npm run dev`（开发模式）而不是打开 index.html。
Vite 开发模式有 HMR（热更新），修改保存即可。
如果还是不行，尝试 Ctrl+C 重新启动或者清浏览器缓存。
```

### Q2: 前端怎么调试？

```typescript
// 1. console.log（前端版 print）
console.log('Current user:', user.value)

// 2. Vue DevTools 浏览器扩展
// 安装后可以看到组件树、Pinia store 状态、路由等

// 3. 浏览器 Network 面板查看 API 请求
// F12 → Network → 查看请求/响应详情（类似后端用 curl 测试）

// 4. 断点调试
// Chrome: Sources → 找到 .vue 文件 → 打 breakpoint
```

### Q3: 怎么找到按钮对应的代码？

```
1. 浏览器 F12 → Elements → 选中按钮
2. 查看 class 或文本内容（如 "Sign In"）
3. 在 IDE 中搜索这个字符串
4. 找到对应的 .vue 文件
```

### Q4: 后端返回 422 或 500，前端怎么查看？

```
1. 浏览器 F12 → Network → 找到失败的请求
2. 查看 Response 中的 detail 字段
3. 后端日志: docker compose logs backend
```

### Q5: TypeScript 报一堆红色错误，是不是代码坏了？

```
不一定是！常见情况：
- 类型推断问题：加上显式类型标注
- 没有安装类型包：npm install @types/xxx
- 还是无法解决：用 `as any` 临时跳过（类似 Python 的 # type: ignore）
```

### Q6: 前端的"编译"和"运行"是什么关系？

| 阶段 | 类似后端 | 前端 |
|------|---------|------|
| 编译时 | mypy 类型检查 | `vue-tsc --noEmit` |
| 构建时 | Python 无此步骤 | `vite build`（打包、压缩、代码分割） |
| 运行时 | `uvicorn serve` | 浏览器执行 JavaScript |

### Q7: 什么是 SPA（单页应用）？

```
传统网站（多页应用）:
  点击链接 → 浏览器请求新页面 → 服务端渲染 → 返回完整 HTML → 页面刷新

SPA（本工程的前端方案）:
  点击链接 → 前端路由拦截 → 只替换部分组件 → 无刷新
  API 数据通过 Axios 异步获取（不重新加载整个页面）

优势：更快的页面切换、更好的用户体验
代价：首次加载较慢、SEO 需要额外配置
```

### Q8: 前端和后端谁先启动有影响吗？

```
没有影响。前端开发时通过 Vite Proxy，生产时通过 Nginx Proxy，
API 调用是运行时发的 HTTP 请求，后端不在也只会返回 502/连接拒绝，
前端依然能正常渲染登录页面。
```

---

## 推荐学习路径

```
1. 先读懂本项目的 Login.vue + auth.ts → 理解组件 + API 调用
2. 修改 Dashboard.vue 的样式 → 熟悉模板语法
3. 在 Dashboard 加一个新 Tab → 理解路由和组件
4. 新增一个页面和路由 → 理解 Vue Router
5. 给 Store 加一个新状态 → 理解 Pinia
6. 从零搭建一个简单的 CRUD 页面 → 融会贯通
```

---

> "全栈不是什么都懂，而是知道每一层在做什么，以及它们如何连接。"
