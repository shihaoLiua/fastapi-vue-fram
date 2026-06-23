# FastAPI + Vue 全栈脚手架

基于 **FastAPI**（Python）+ **Vue 3**（TypeScript）+ **PostgreSQL** + **Redis** 的生产级全栈项目模板，使用 **Docker Compose** 一键部署。

## 功能特性

### 后端（FastAPI）
- 用户注册、登录、登出
- JWT 双 Token 认证（access + refresh）
- 修改密码
- 用户管理（CRUD，管理员权限）
- 异步 SQLAlchemy + PostgreSQL
- Redis 存储黑名单和刷新令牌
- 首次启动自动创建超级管理员
- 跨域配置（CORS）
- OpenAPI 文档 `/docs`

### 前端（Vue 3）
- TypeScript + 组合式 API（Composition API）
- Vue Router 路由守卫
- Pinia 状态管理
- Axios HTTP 客户端（自动刷新 Token）
- 登录 / 注册 / 仪表盘页面
- 管理后台（管理员操作）
- 响应式设计

## 快速开始

### 前置条件
- Docker 和 Docker Compose

### 启动服务

```bash
git clone git@github.com:shihaoLiua/fastapi-vue-fram.git
cd fastapi-vue-fram

# 启动所有服务
docker compose up -d

# 等待服务就绪后访问：
# 前端页面：  http://localhost
# 后端 API：  http://localhost:8001
# API 文档：  http://localhost:8001/docs
```

### 默认管理员账号

| 字段 | 值 |
|------|-----|
| 邮箱 | `admin@example.com` |
| 密码 | `admin123` |
| 用户名 | `admin` |

## 项目结构

```
├── docker-compose.yml         # Docker Compose 编排文件
├── .env                       # 环境变量
├── FULLSTACK_GUIDE.md         # 后端工程师前端学习指南
├── FRONTEND_DEEP_DIVE.md      # 前端代码深度逐行解析
├── backend/                   # FastAPI 后端
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # FastAPI 入口
│       ├── config.py          # 配置项
│       ├── database.py        # SQLAlchemy 异步引擎
│       ├── redis_client.py    # Redis 客户端
│       ├── models/            # SQLAlchemy 数据模型
│       ├── schemas/           # Pydantic 校验模型
│       ├── api/               # API 路由
│       │   ├── auth.py        # 认证相关接口
│       │   └── users.py       # 用户管理接口
│       ├── services/          # 业务逻辑层
│       └── core/              # 核心工具
│           ├── security.py    # JWT + 密码哈希
│           └── deps.py        # FastAPI 依赖注入
├── frontend/                  # Vue 3 前端
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.ts            # Vue 应用入口
│       ├── App.vue            # 根组件
│       ├── router/            # 路由配置
│       ├── stores/            # Pinia 状态管理
│       ├── api/               # API 调用层
│       ├── views/             # 页面组件
│       ├── components/        # 通用组件
│       └── types/             # TypeScript 类型定义
└── 学习文档已包含在仓库中
```

## API 接口一览

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 注册新用户 | 否 |
| POST | `/api/v1/auth/login` | 登录 | 否 |
| POST | `/api/v1/auth/refresh` | 刷新 Token | 否 |
| POST | `/api/v1/auth/logout` | 登出 | 是 |
| GET | `/api/v1/auth/me` | 获取当前用户 | 是 |
| PUT | `/api/v1/auth/change-password` | 修改密码 | 是 |
| GET | `/api/v1/users/` | 用户列表 | 管理员 |
| GET | `/api/v1/users/{id}` | 查看用户 | 是* |
| PUT | `/api/v1/users/{id}` | 更新用户 | 是* |
| DELETE | `/api/v1/users/{id}` | 删除用户 | 管理员 |
| GET | `/api/health` | 健康检查 | 否 |

*\* 普通用户只能操作自己的数据*

## 开发指南

### 不使用 Docker

**后端：**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# 确保 PostgreSQL 和 Redis 已启动
uvicorn app.main:app --reload --port 8000
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

### Docker 开发

```bash
# 查看日志
docker compose logs -f

# 重新构建某个服务
docker compose build backend
docker compose up -d backend

# 进入容器执行命令
docker compose exec backend bash
```

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | JWT 签名密钥 | `change-this-to-a-random-secret-key-in-production` |
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://postgres:postgres@db:5432/fastapi_vue` |
| `REDIS_URL` | Redis 连接串 | `redis://redis:6379/0` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 访问令牌过期时间（分钟） | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 刷新令牌过期时间（天） | `7` |
| `FIRST_SUPERUSER_EMAIL` | 自动创建的管理员邮箱 | `admin@example.com` |
| `FIRST_SUPERUSER_PASSWORD` | 自动创建的管理员密码 | `admin123` |

## 学习路线

本仓库附带两份学习文档，建议按顺序阅读：

1. **`FULLSTACK_GUIDE.md`** — 后端工程师的前端学习指南，建立前后端概念映射
2. **`FRONTEND_DEEP_DIVE.md`** — 前端代码深度逐行解析，配合实际代码理解每行逻辑

## 协议

MIT
