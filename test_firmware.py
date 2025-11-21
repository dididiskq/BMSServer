#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试固件生成和上传演示脚本

此脚本用于生成一个测试固件文件，然后调用upload_firmware.py上传到服务器。
"""

import os
import sys
import subprocess
import tempfile
import time
from upload_firmware import upload_firmware
def generate_test_firmware(output_path, size_kb=10):
    """
    生成一个测试固件文件
    
    Args:
        output_path: 输出文件路径
        size_kb: 文件大小（KB）
        
    Returns:
        str: 生成的文件路径
    """
    print(f"生成测试固件文件: {output_path} (大小: {size_kb} KB)")
    
    # 创建指定大小的文件，填充测试数据
    with open(output_path, 'wb') as f:
        # 生成一些模拟的固件数据
        header = b'BMSFIRMWARE\x00'  # 模拟固件头
        f.write(header)
        
        # 计算还需要写入的字节数
        remaining_bytes = size_kb * 1024 - len(header)
        
        # 写入剩余数据
        chunk_size = 8192
        chunk = b'\xAA' * chunk_size  # 填充数据
        
        while remaining_bytes > 0:
            write_size = min(chunk_size, remaining_bytes)
            f.write(chunk[:write_size])
            remaining_bytes -= write_size
    
    print(f"测试固件文件生成完成: {os.path.getsize(output_path)/1024:.2f} KB")
    return output_path

def run_upload_script(firmware_path, version, description):
    """
    运行上传脚本
    
    Args:
        firmware_path: 固件文件路径
        version: 固件版本
        description: 固件描述
        
    Returns:
        bool: 上传是否成功
    """
    # 获取上传脚本的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    upload_script = os.path.join(script_dir, 'upload_firmware.py')
    
    if not os.path.exists(upload_script):
        print(f"错误: 找不到上传脚本 '{upload_script}'")
        return False
    
    # 构建命令行参数
    cmd = [sys.executable, upload_script, firmware_path, 
           '--version', version, '--description', description]
    
    print(f"\n执行上传命令: {' '.join(cmd)}")
    
    try:
        # 执行上传脚本
        result = subprocess.run(cmd, check=False, text=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        # 打印输出
        print("\n上传脚本输出:")
        print(result.stdout)
        
        # 检查退出码
        if result.returncode == 0:
            print("\n上传成功!")
            return True
        else:
            print(f"\n上传失败，退出码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"执行上传脚本时出错: {str(e)}")
        return False

def main():
    """
    主函数
    """
    print("BMS服务器固件上传测试演示\n")
    
    # 生成版本号（使用当前时间，确保唯一性）
    timestamp = time.strftime("%Y%m%d_%H%M")
    version = f"1.2.{timestamp}"
    
    # 创建临时文件或使用固定名称
    temp_file = os.path.join(os.path.dirname(__file__), f"test_firmware_{version}.bin")
    
    try:
        # 生成测试固件文件
        firmware_path = generate_test_firmware(temp_file, size_kb=5)
        
        # 定义上传描述
        description = f"测试固件版本 {version}，用于演示上传功能"
        
        # 上传固件
        success = run_upload_script(firmware_path, version, description)
        
        # 总结
        if success:
            print("\n固件上传演示完成!")
            print(f"固件文件: {firmware_path}")
            print(f"版本: {version}")
        else:
            print("\n固件上传演示失败，请检查错误信息")
            
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"演示过程中出错: {str(e)}")
    finally:
        # 可选：清理临时文件
        # if os.path.exists(temp_file):
        #     os.remove(temp_file)
        #     print(f"清理临时文件: {temp_file}")
        pass

if __name__ == "__main__":
    main()

"""
使用说明:

1. 确保服务器已启动并运行在默认地址 (http://localhost:8000)
2. 运行此脚本: python test_firmware.py
3. 脚本会自动:
   - 生成一个测试固件文件
   - 调用upload_firmware.py上传固件
   - 显示上传结果

可以通过修改size_kb参数来调整测试固件文件的大小。
"""