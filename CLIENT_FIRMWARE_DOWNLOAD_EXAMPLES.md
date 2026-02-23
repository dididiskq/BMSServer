# 客户端固件升级包请求指南

本文档提供客户端如何请求并下载固件升级包的详细指南和示例代码。

## API概述

服务器提供以下与固件相关的API端点：

1. `GET /ota/latest` - 获取最新固件信息（包含下载链接）
2. `GET /ota/download/{update_id}` - 下载特定固件文件
3. `GET /ota/updates` - 获取所有固件更新列表
4. `GET /ota/updates/{update_id}` - 获取特定固件详情

## 推荐的固件请求流程

1. **获取最新固件信息**：客户端首先调用`/ota/latest`获取最新固件的元数据
2. **版本比较**：客户端比较本地固件版本与最新版本
3. **下载固件**：如果有新版本，通过返回的`download_url`下载固件文件

## 示例代码

### Python示例

```python
import requests
import os
import sys
from packaging import version

# 服务器地址
BASE_URL = "http://localhost:8000"

# 当前设备固件版本
CURRENT_VERSION = "1.0.0"

def check_for_updates():
    """检查是否有新的固件更新"""
    try:
        # 获取最新固件信息
        response = requests.get(f"{BASE_URL}/ota/latest")
        response.raise_for_status()
        
        latest_firmware = response.json()
        print(f"最新固件版本: {latest_firmware['version']}")
        print(f"固件描述: {latest_firmware['description']}")
        
        # 版本比较
        if version.parse(latest_firmware['version']) > version.parse(CURRENT_VERSION):
            print("发现新版本固件，开始下载...")
            return latest_firmware
        else:
            print("当前已是最新版本")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"检查更新失败: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def download_firmware(firmware_info, save_path="."):
    """下载固件文件"""
    try:
        # 构建完整的下载URL
        download_url = f"{BASE_URL}{firmware_info['download_url']}"
        
        # 定义保存文件名
        filename = firmware_info['filename']
        filepath = os.path.join(save_path, filename)
        
        # 下载文件
        print(f"开始下载固件: {filename}")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # 显示下载进度
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # 计算并显示进度
                    progress = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                    sys.stdout.write(f"\r下载进度: {progress:.1f}% ({downloaded_size}/{total_size} bytes)")
                    sys.stdout.flush()
        
        print(f"\n固件下载完成，保存至: {filepath}")
        return filepath
        
    except requests.exceptions.RequestException as e:
        print(f"下载固件失败: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def main():
    # 检查更新
    firmware_info = check_for_updates()
    
    if firmware_info:
        # 下载固件
        download_firmware(firmware_info)
        # 这里可以添加固件验证和安装的代码
        print("固件下载完成，请进行验证和安装")

if __name__ == "__main__":
    main()

 
 

## 固件验证和安装注意事项

1. **固件校验**：下载完成后，建议对固件文件进行校验（如MD5/SHA256校验）以确保完整性
2. **蓝牙传输**：如果需要通过蓝牙将固件传输到设备，请参考APP_CLIENT_GUIDE.md中的蓝牙传输最佳实践
3. **错误处理**：实现健壮的错误处理机制，处理网络中断、服务器错误等情况
4. **进度反馈**：为用户提供清晰的下载进度反馈
5. **版本管理**：维护本地固件版本信息，避免重复下载

## 常见问题排查

1. **无法连接服务器**：检查网络连接和服务器地址配置
2. **下载失败**：检查存储空间是否充足，网络连接是否稳定
3. **版本比较错误**：确保版本号格式一致，使用标准的语义化版本格式
4. **固件文件损坏**：实现文件校验机制，如计算校验和

如需更多帮助，请参考API_TESTING_GUIDE.md或联系技术支持。