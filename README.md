# BMS Server

电池管理系统服务器，基于FastAPI和SQLite实现。提供用户管理和OTA固件更新功能。

## 功能特性

### 用户管理
- 创建用户
- 获取用户列表
- 获取单个用户信息
- 更新用户信息
- 删除用户

### OTA固件更新
- 上传固件文件
- 获取固件更新列表
- 获取单个固件信息
- 获取最新固件版本
- 更新固件状态（激活/停用）
- 删除固件更新

## 技术栈
- Python 3.7+
- FastAPI
- SQLite
- SQLAlchemy
- Uvicorn

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动。

### 3. 访问API文档

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API端点

### 用户管理
- `POST /users/` - 创建新用户
- `GET /users/` - 获取用户列表
- `GET /users/{user_id}` - 获取用户详情
- `PUT /users/{user_id}` - 更新用户信息
- `DELETE /users/{user_id}` - 删除用户

### OTA固件更新
- `POST /ota/upload` - 上传新固件
- `GET /ota/updates` - 获取固件列表
- `GET /ota/updates/{update_id}` - 获取固件详情
- `GET /ota/latest` - 获取最新固件
- `PUT /ota/updates/{update_id}/status` - 更新固件状态
- `DELETE /ota/updates/{update_id}` - 删除固件

### 系统
- `GET /` - 根路径
- `GET /health` - 健康检查

## 注意事项

1. 数据库会自动在项目根目录创建 `bms.db`
2. 固件文件会保存在 `uploads` 目录
3. 本项目未实现用户认证机制，生产环境应添加
4. 密码仅存储哈希值，请在客户端进行密码哈希处理

## 项目结构

```
BMSServer/
├── main.py           # 主应用文件
├── requirements.txt  # 项目依赖
├── bms.db            # SQLite数据库文件（自动创建）
├── uploads/          # 上传的固件文件目录（自动创建）
└── README.md         # 项目说明文档
```