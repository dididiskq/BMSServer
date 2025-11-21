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
 