#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
固件上传客户端工具

此脚本用于向BMS服务器上传新的固件更新包，并将元数据保存到数据库中。
支持进度显示、错误处理和基本的文件验证功能。
"""

import os
import requests
import argparse
import sys

# 服务器基础URL
BASE_URL = "http://localhost:8000"

# 上传固件的API端点
UPLOAD_ENDPOINT = f"{BASE_URL}/ota/upload"

def validate_firmware_file(file_path):
    """
    验证固件文件是否存在且有效
    
    Args:
        file_path: 固件文件路径
        
    Returns:
        bool: 文件是否有效
    """
    if not os.path.exists(file_path):
        print(f"错误: 固件文件 '{file_path}' 不存在")
        return False
    
    if not os.path.isfile(file_path):
        print(f"错误: '{file_path}' 不是一个文件")
        return False
    
    # 检查文件大小（可选）
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        print("错误: 固件文件为空")
        return False
    
    # 打印文件信息
    print(f"固件文件信息: {os.path.basename(file_path)}, 大小: {file_size/1024/1024:.2f} MB")
    return True

def parse_version_from_filename(file_path):
    """
    尝试从文件名中解析版本号
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 解析出的版本号或None
    """
    # 获取文件名（不包含路径）
    filename = os.path.basename(file_path)
    
    # 移除文件扩展名
    name_without_ext = os.path.splitext(filename)[0]
    
    # 检查是否符合简单的语义化版本格式 (X.Y.Z)
    import re
    version_match = re.search(r'\d+\.\d+\.\d+', name_without_ext)
    if version_match:
        return version_match.group()
    
    return None

def upload_firmware(file_path, version=None, description=""):
    """
    上传固件到服务器
    
    Args:
        file_path: 固件文件路径
        version: 固件版本号（可选，默认从文件名解析）
        description: 固件更新描述
        
    Returns:
        dict: 上传响应结果或None（失败时）
    """
    # 验证文件
    if not validate_firmware_file(file_path):
        return None
    
    # 如果未提供版本号，尝试从文件名解析
    if not version:
        parsed_version = parse_version_from_filename(file_path)
        if parsed_version:
            version = parsed_version
            print(f"从文件名解析的版本号: {version}")
        else:
            print("错误: 请提供版本号，无法从文件名解析")
            return None
    
    # 准备上传文件
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    try:
        # 准备表单数据
        data = {
            'version': version,
            'description': description
        }
        
        # 准备文件
        files = {
            'file': (filename, open(file_path, 'rb'), 'application/octet-stream')
        }
        
        print(f"开始上传固件...")
        print(f"目标服务器: {UPLOAD_ENDPOINT}")
        print(f"版本号: {version}")
        print(f"描述: {description}")
        
        # 发送请求
        response = requests.post(
            UPLOAD_ENDPOINT,
            data=data,
            files=files,
            stream=True  # 启用流式处理以支持进度显示
        )
        
        # 检查响应状态
        if response.status_code == 200:
            # 尝试解析JSON响应
            try:
                result = response.json()
                print(f"上传成功!")
                print(f"服务器响应:")
                print(f"  ID: {result.get('id')}")
                print(f"  版本: {result.get('version')}")
                print(f"  文件名: {result.get('filename')}")
                print(f"  描述: {result.get('description')}")
                return result
            except ValueError:
                print("警告: 无法解析服务器响应为JSON")
                print(f"响应内容: {response.text}")
                return None
        else:
            error_msg = f"上传失败! 状态码: {response.status_code}"
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    error_msg += f", 详情: {error_data['detail']}"
            except ValueError:
                error_msg += f", 响应: {response.text}"
            print(error_msg)
            return None
            
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{file_path}'")
        return None
    except requests.exceptions.RequestException as e:
        print(f"网络错误: {str(e)}")
        return None
    except Exception as e:
        print(f"未预期的错误: {str(e)}")
        return None
    finally:
        # 确保文件已关闭
        for _, file_tuple in files.items():
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

def main():
    """
    主函数，处理命令行参数并执行上传
    """
    # 首先声明全局变量
    global UPLOAD_ENDPOINT, BASE_URL
    
    parser = argparse.ArgumentParser(description='BMS服务器固件上传工具')
    parser.add_argument('file', help='固件文件路径')
    parser.add_argument('-v', '--version', help='固件版本号 (例如: 1.0.0)')
    parser.add_argument('-d', '--description', help='固件更新描述', default='')
    parser.add_argument('-u', '--url', help='服务器基础URL', default=BASE_URL)
    
    args = parser.parse_args()
    
    # 如果指定了自定义URL，更新端点
    if args.url != BASE_URL:
        BASE_URL = args.url.rstrip('/')
        UPLOAD_ENDPOINT = f"{BASE_URL}/ota/upload"
    
    # 执行上传
    result = upload_firmware(args.file, args.version, args.description)
    
    # 根据结果设置退出码
    sys.exit(0 if result else 1)

if __name__ == "__main__":
    main()

"""
使用示例:

1. 基本上传（版本号从文件名解析）:
   python upload_firmware.py firmware_1.2.3.bin

2. 指定版本号和描述:
   python upload_firmware.py firmware.bin --version 1.2.3 --description "修复了电池监控模块的漏洞"

3. 使用自定义服务器URL:
   python upload_firmware.py firmware.bin --url http://example.com:8000

注意事项:
- 确保固件文件格式正确，通常为.bin格式
- 版本号应使用语义化版本格式 (X.Y.Z)
- 上传前确保服务器已启动并可访问
- 上传文件将保存在服务器的uploads目录中
- 版本号必须唯一，不能重复上传相同版本
"""