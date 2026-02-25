# BMS Server

电池管理系统服务器，基于FastAPI和SQLite实现。提供用户管理、OTA固件更新和BMS BLE协议支持。

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
- 下载固件文件

### BMS BLE协议支持
- 基于Modbus RTU协议的BLE通信
- 支持读取电池状态（电压、电流、温度、SOC、SOH等）
- 支持配置BMS参数（电池组串数、电池类型、保护阈值等）
- 支持监控报警状态
- 完整的报文解析和CRC校验功能

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
- `GET /ota/download/{update_id}` - 下载固件文件
- `PUT /ota/updates/{update_id}/status` - 更新固件状态
- `DELETE /ota/updates/{update_id}` - 删除固件

### 系统
- `GET /` - 根路径
- `GET /health` - 健康检查

## 工具脚本

### 数据管理
- `data_seeder.py` - 数据库种子数据生成工具
- `verify_data.py` - 数据验证工具

### 固件管理
- `upload_firmware.py` - 固件上传脚本
- `download_client.py` - 固件下载客户端示例
- `test_firmware.py` - 固件测试脚本

## 文档

- `README.md` - 项目说明文档（本文件）
- `API_TESTING_GUIDE.md` - API测试指南，包含详细的测试方法和常见问题解决
- `APP_CLIENT_GUIDE.md` - 客户端应用开发指南，包含Android和iOS实现示例
- `CLIENT_FIRMWARE_DOWNLOAD_EXAMPLES.md` - 客户端固件下载示例
- `.trae/skills/self_ble/SKILL.md` - BMS BLE协议技能文档，包含完整的协议说明和报文示例

## BMS BLE协议

本项目包含完整的BMS BLE协议支持，基于Modbus RTU协议实现。协议技能位于 `.trae/skills/self_ble/SKILL.md`，提供以下功能：

### 协议特性
- 帧格式：子节点地址(1字节) + 功能代码(1字节) + 数据(N字节) + CRC校验(2字节)
- 功能码：0x03(读取保持寄存器)、0x10(写入多个保持寄存器)
- CRC16校验：Modbus标准校验算法

### 寄存器映射
- **Table1** - 设备信息寄存器（只读）：温度、电压、电流、SOC、SOH、电池状态等
- **Table2** - 设备信息寄存器（可读写）：电池组串数、电池类型、保护阈值等配置参数
- **Table3** - 内部动态记录参数：循环次数、保护事件记录等

### 使用示例
- 读取电池电量：`16 03 00 14 00 01 35 F6`
- 读取固件版本：`16 03 00 13 00 01 34 36`
- 修改休眠延时：`16 10 02 06 00 01 02 01 2C 6A 1E`

详细协议说明和更多报文示例请参考 `.trae/skills/self_ble/SKILL.md`

## 注意事项

1. 数据库会自动在项目根目录创建 `bms.db`
2. 固件文件会保存在 `uploads` 目录
3. 本项目未实现用户认证机制，生产环境应添加
4. 密码仅存储哈希值，请在客户端进行密码哈希处理

## 项目结构

```
BMSServer/
├── main.py                           # 主应用文件
├── requirements.txt                  # 项目依赖
├── bms.db                            # SQLite数据库文件（自动创建）
├── uploads/                          # 上传的固件文件目录（自动创建）
├── .trae/
│   └── skills/
│       └── self_ble/
│           └── SKILL.md              # BMS BLE协议技能文档
├── data_seeder.py                    # 数据库种子数据生成工具
├── verify_data.py                    # 数据验证工具
├── upload_firmware.py                # 固件上传脚本
├── download_client.py                # 固件下载客户端示例
├── test_firmware.py                  # 固件测试脚本
├── self_ble.txt                      # BMS BLE协议原始文档
├── README.md                         # 项目说明文档
├── API_TESTING_GUIDE.md              # API测试指南
├── APP_CLIENT_GUIDE.md               # 客户端应用开发指南
└── CLIENT_FIRMWARE_DOWNLOAD_EXAMPLES.md  # 客户端固件下载示例
```

## BMS BLE协议技能使用

### 如何使用BLE协议技能

1. **查看协议文档**
   - 阅读 `.trae/skills/self_ble/SKILL.md` 了解完整的协议规范
   - 文档包含寄存器映射、报文格式、CRC校验算法等详细信息

2. **生成报文示例**
   - 使用协议技能生成各种报文（读取电量、读取版本、修改参数等）
   - 所有报文都包含完整的十六进制格式和Python代码示例

3. **集成到应用**
   - 根据协议文档实现BLE通信功能
   - 参考APP_CLIENT_GUIDE.md了解如何集成到移动应用

### 常用报文快速参考

| 功能 | 寄存器地址 | 请求报文 | 说明 |
|------|-----------|----------|------|
| 读取电池电量 | 0x0014 | `16 03 00 14 00 01 35 F6` | 获取SOC和SOH |
| 读取固件版本 | 0x0013 | `16 03 00 13 00 01 34 36` | 获取版本号 |
| 修改休眠延时 | 0x0206 | `16 10 02 06 00 01 02 01 2C 6A 1E` | 设置为300秒 |
| 读取电池组总电压 | 0x0004 | `16 03 00 04 00 02 1D 6D` | 读取2个寄存器 |
| 读取电池组总电流 | 0x0006 | `16 03 00 06 00 02 3D AD` | 读取2个寄存器 |

### 报文解析流程

1. **构建请求报文**
   - 确定从机地址（默认0x16）
   - 选择功能码（0x03读取或0x10写入）
   - 设置寄存器地址和数量
   - 计算CRC16校验值

2. **发送报文**
   - 通过BLE连接发送报文到BMS设备
   - 等待设备响应

3. **解析响应报文**
   - 验证CRC校验
   - 提取数据字段
   - 根据寄存器类型解析数据（温度、电压、电流等）

4. **处理数据**
   - 温度：开尔文转摄氏度（°C = K - 273.15）
   - 电流：正数为充电，负数为放电
   - 版本号：高8位主版本，低8位次版本

## 开发指南

### 快速开始BLE开发

1. **学习协议基础**
   ```bash
   # 查看BLE协议技能文档
   cat .trae/skills/self_ble/SKILL.md
   ```

2. **测试报文生成**
   - 使用协议技能生成测试报文
   - 验证CRC校验算法

3. **集成BLE通信**
   - 参考APP_CLIENT_GUIDE.md了解移动端集成
   - 实现报文封装和解析功能

### 客户端开发资源

- **移动应用开发**：参考 `APP_CLIENT_GUIDE.md`
- **API测试**：参考 `API_TESTING_GUIDE.md`
- **固件下载**：参考 `CLIENT_FIRMWARE_DOWNLOAD_EXAMPLES.md`