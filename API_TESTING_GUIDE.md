# BMS Server API 测试指南

本文档详细介绍如何正确测试 BMS Server 的 API 端点，特别是解决常见的 422 错误问题。

## 常见错误说明

### 422 Unprocessable Entity 错误

当您看到 `422 Unprocessable Entity` 错误时，通常表示：

1. **缺少必需字段** - 您的请求没有提供所有必需的参数
2. **参数格式错误** - 提供的参数类型或格式不正确
3. **参数验证失败** - 参数不符合验证规则

从服务器日志和您提供的截图来看，当前错误是缺少必需的 `email` 字段。

## API 使用指南

### 1. 创建用户 (POST /users/)

**必需字段：**
- `username` (字符串) - 用户名
- `email` (字符串) - 电子邮件地址
- `password_hash` (字符串) - 密码哈希值
- `full_name` (字符串) - 用户全名

**Postman 设置：**
1. 选择 `POST` 方法
2. 输入 URL: `http://localhost:8000/users/`
3. 在 `Body` 标签中选择 `form-data`
4. 添加以下键值对：
   - `username`: `testuser1`
   - `email`: `test@example.com`
   - `password_hash`: `hashed_password_here`
   - `full_name`: `Test User`

**成功响应示例：**
```json
{
    "id": 1,
    "username": "testuser1",
    "email": "test@example.com"
}
```

### 2. 获取所有用户 (GET /users/)

**查询参数（可选）：**
- `skip` (整数) - 跳过的记录数，默认为 0
- `limit` (整数) - 返回的最大记录数，默认为 100

**Postman 设置：**
1. 选择 `GET` 方法
2. 输入 URL: `http://localhost:8000/users/`

### 3. 获取单个用户 (GET /users/{user_id})

**路径参数：**
- `user_id` (整数) - 用户 ID

**Postman 设置：**
1. 选择 `GET` 方法
2. 输入 URL: `http://localhost:8000/users/1` (将 1 替换为实际用户 ID)

### 4. 更新用户 (PUT /users/{user_id})

**路径参数：**
- `user_id` (整数) - 用户 ID

**表单参数（可选）：**
- `username` (字符串)
- `email` (字符串)
- `password_hash` (字符串)
- `full_name` (字符串)
- `is_active` (布尔值)

**Postman 设置：**
1. 选择 `PUT` 方法
2. 输入 URL: `http://localhost:8000/users/1` (将 1 替换为实际用户 ID)
3. 在 `Body` 标签中选择 `form-data`
4. 添加您想要更新的字段和值

### 5. 上传固件 (POST /ota/upload)

**必需字段：**
- `version` (字符串) - 固件版本号
- `description` (字符串) - 固件描述
- `file` (文件) - 固件文件

**Postman 设置：**
1. 选择 `POST` 方法
2. 输入 URL: `http://localhost:8000/ota/upload`
3. 在 `Body` 标签中选择 `form-data`
4. 添加以下键值对：
   - `version`: `1.2.0`
   - `description`: `新功能更新`
   - `file`: 选择一个二进制文件（将 `Key Type` 从 `Text` 改为 `File`）

## 表单数据 vs JSON 数据

**重要提示：** 所有 API 端点都使用 `form-data` 格式接收数据，而不是 JSON 格式。请确保在 Postman 中正确设置。

## 测试技巧

1. **先测试 GET 请求** - 在尝试创建或修改数据前，先测试获取数据的 API 以确保服务器正常运行
2. **查看详细错误信息** - 422 错误通常会在响应体中包含具体的错误详情，请检查这些信息以了解具体的问题
3. **使用 API 文档** - 访问 `http://localhost:8000/docs` 查看交互式 API 文档

## 排查步骤

如果遇到 422 错误，请按以下步骤排查：

1. 确认所有必需字段都已提供
2. 检查字段名称是否正确（区分大小写）
3. 确保数据类型正确（例如，布尔值应为 `true` 或 `false`）
4. 验证数据格式是否符合要求

## 常见问题

**Q: 为什么使用 form-data 而不是 JSON？**
A: 为了支持文件上传功能，并确保 API 的一致性，所有端点都统一使用 form-data 格式。

**Q: 如何处理密码？**
A: 目前 API 直接接收 `password_hash`，在实际应用中，密码哈希应该在客户端计算后再发送。

**Q: 如何测试文件上传？**
A: 在 Postman 中，将字段类型设置为 `File` 而不是 `Text`，然后选择要上传的文件。