# AIfriend

一个基于 `Vue 3 + Django + LangGraph` 的 AI 虚拟好友应用。  
用户可以创建角色并进行文本/语音对话，系统支持流式回复、长期记忆与向量检索增强。

## 项目亮点

- 全栈架构：前端 `Vue 3`，后端 `Django + DRF`，前后端分离开发。
- AI 对话：后端基于 `LangGraph` 构建多节点聊天流程，支持工具调用。
- 流式交互：使用 `SSE` 实现边生成边展示回复。
- 语音能力：支持前端语音采集（VAD）和后端语音转写（ASR）。
- 记忆机制：结合短期上下文与长期记忆摘要，增强角色连续对话体验。
- 检索增强：使用 `LanceDB` 存储向量并进行相似度检索。

## 技术栈

### 前端

- `Vue 3`
- `Vite`
- `Vue Router`
- `Pinia`
- `Axios`
- `Tailwind CSS + DaisyUI`
- `@microsoft/fetch-event-source`（SSE）
- `@ricky0123/vad-web`（语音活动检测）

### 后端

- `Django`
- `Django REST framework`
- `SimpleJWT`
- `django-cors-headers`
- `LangChain / LangGraph`
- `OpenAI Compatible API`（Qwen）
- `LanceDB`
- `SQLite`（默认开发数据库）

## 目录结构

```text
AIfriend/
├─ backend/                    # Django 后端
│  ├─ backend/                 # Django 配置
│  ├─ web/                     # 业务应用（用户/角色/好友/消息/AI）
│  ├─ media/                   # 上传文件
│  ├─ static/                  # 静态资源（含前端构建输出）
│  ├─ manage.py
│  └─ requirements.txt
├─ frontend/                   # Vue 前端
│  ├─ src/
│  ├─ public/
│  ├─ package.json
│  └─ vite.config.js
├─ requirements.txt            # 根目录 Python 依赖（扩展环境）
└─ README.md
```

## 核心功能

- 用户注册、登录、刷新令牌、退出登录、资料更新。
- 角色创建、编辑、删除、列表与详情查询。
- 角色好友关系建立与好友列表管理。
- 聊天消息历史查询（分页加载）。
- 文本聊天流式返回（SSE）。
- 语音输入转写（ASR）并接入聊天链路。

## 环境要求

- `Python 3.11+`
- `Node.js 20+`
- `npm 10+`

## 环境变量

后端通过 `python-dotenv` 读取 `backend/.env`。可按需配置：

```env
API_KEY=your_api_key
API_BASE=your_openai_compatible_base_url
WSS_URL=your_asr_websocket_url
VOICE_URL=your_tts_or_voice_service_url
```

> 注意：请勿将真实密钥提交到仓库。

## 快速开始

### 1) 启动后端

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

后端默认地址：`http://127.0.0.1:8000`

### 2) 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：`http://localhost:5173`

### 3) 前端构建并交给 Django 托管

```bash
cd frontend
npm run build
```

构建输出目录为：`backend/static/frontend`

## 常用命令

### 前端

```bash
npm run dev      # 本地开发
npm run build    # 生产构建
npm run preview  # 预览构建产物
```

### 后端

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
```

## API 概览

部分接口示例：

- `/api/user/account/login/`
- `/api/user/account/register/`
- `/api/user/account/refresh_token/`
- `/api/homepage/index/`
- `/api/create/character/create/`
- `/api/friend/message/chat/`
- `/api/friend/message/asr/asr/`

## 备注

- 当前测试用例较少，建议补充后端 API 自动化测试与前端关键交互测试。
- 生产环境部署时建议关闭 `DEBUG`，并通过 Nginx/网关托管静态资源与媒体文件。
