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
```

### Java (Android) 示例

```java
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class FirmwareUpdateManager {
    private static final String BASE_URL = "http://localhost:8000";
    private static final String CURRENT_VERSION = "1.0.0";
    private UpdateListener listener;
    
    public interface UpdateListener {
        void onUpdateAvailable(FirmwareInfo firmwareInfo);
        void onNoUpdate();
        void onUpdateCheckFailed(String error);
        void onDownloadStart();
        void onDownloadProgress(int progress, long downloaded, long total);
        void onDownloadComplete(File firmwareFile);
        void onDownloadFailed(String error);
    }
    
    public void setUpdateListener(UpdateListener listener) {
        this.listener = listener;
    }
    
    public void checkForUpdates() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL(BASE_URL + "/ota/latest");
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    connection.setConnectTimeout(5000);
                    connection.setReadTimeout(10000);
                    
                    int responseCode = connection.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        // 解析JSON响应
                        StringBuilder response = new StringBuilder();
                        try (InputStream is = connection.getInputStream()) {
                            byte[] buffer = new byte[1024];
                            int bytesRead;
                            while ((bytesRead = is.read(buffer)) != -1) {
                                response.append(new String(buffer, 0, bytesRead));
                            }
                        }
                        
                        // 使用org.json库解析JSON
                        org.json.JSONObject jsonObject = new org.json.JSONObject(response.toString());
                        String latestVersion = jsonObject.getString("version");
                        String description = jsonObject.getString("description");
                        int id = jsonObject.getInt("id");
                        String filename = jsonObject.getString("filename");
                        String downloadUrl = jsonObject.getString("download_url");
                        
                        FirmwareInfo firmwareInfo = new FirmwareInfo(id, latestVersion, filename, description, downloadUrl);
                        
                        // 版本比较
                        if (isNewerVersion(latestVersion, CURRENT_VERSION)) {
                            if (listener != null) {
                                listener.onUpdateAvailable(firmwareInfo);
                            }
                        } else {
                            if (listener != null) {
                                listener.onNoUpdate();
                            }
                        }
                    } else {
                        if (listener != null) {
                            listener.onUpdateCheckFailed("服务器返回错误码: " + responseCode);
                        }
                    }
                } catch (Exception e) {
                    if (listener != null) {
                        listener.onUpdateCheckFailed("检查更新失败: " + e.getMessage());
                    }
                }
            }
        }).start();
    }
    
    public void downloadFirmware(final FirmwareInfo firmwareInfo, final File downloadDir) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                if (listener != null) {
                    listener.onDownloadStart();
                }
                
                try {
                    URL url = new URL(BASE_URL + firmwareInfo.downloadUrl);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    connection.setConnectTimeout(5000);
                    connection.setReadTimeout(10000);
                    connection.setDoInput(true);
                    
                    int responseCode = connection.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        long totalSize = connection.getContentLengthLong();
                        long downloadedSize = 0;
                        
                        File firmwareFile = new File(downloadDir, firmwareInfo.filename);
                        
                        try (InputStream is = connection.getInputStream();
                             FileOutputStream fos = new FileOutputStream(firmwareFile)) {
                            
                            byte[] buffer = new byte[4096];
                            int bytesRead;
                            
                            while ((bytesRead = is.read(buffer)) != -1) {
                                fos.write(buffer, 0, bytesRead);
                                downloadedSize += bytesRead;
                                
                                int progress = (int) ((downloadedSize * 100) / totalSize);
                                if (listener != null) {
                                    listener.onDownloadProgress(progress, downloadedSize, totalSize);
                                }
                            }
                        }
                        
                        if (listener != null) {
                            listener.onDownloadComplete(firmwareFile);
                        }
                    } else {
                        if (listener != null) {
                            listener.onDownloadFailed("下载失败，服务器返回: " + responseCode);
                        }
                    }
                } catch (Exception e) {
                    if (listener != null) {
                        listener.onDownloadFailed("下载失败: " + e.getMessage());
                    }
                }
            }
        }).start();
    }
    
    private boolean isNewerVersion(String newVersion, String currentVersion) {
        // 简单版本比较逻辑，实际应用中应使用更健壮的版本比较库
        String[] newParts = newVersion.split("\\.");
        String[] currentParts = currentVersion.split("\\.");
        
        int length = Math.max(newParts.length, currentParts.length);
        for (int i = 0; i < length; i++) {
            int newPart = i < newParts.length ? Integer.parseInt(newParts[i]) : 0;
            int currentPart = i < currentParts.length ? Integer.parseInt(currentParts[i]) : 0;
            
            if (newPart > currentPart) return true;
            if (newPart < currentPart) return false;
        }
        return false;
    }
    
    public static class FirmwareInfo {
        public final int id;
        public final String version;
        public final String filename;
        public final String description;
        public final String downloadUrl;
        
        public FirmwareInfo(int id, String version, String filename, String description, String downloadUrl) {
            this.id = id;
            this.version = version;
            this.filename = filename;
            this.description = description;
            this.downloadUrl = downloadUrl;
        }
    }
}
```

### Swift (iOS) 示例

```swift
import Foundation

class FirmwareUpdateManager {
    private let baseURL = "http://localhost:8000"
    private let currentVersion = "1.0.0"
    
    struct FirmwareInfo: Codable {
        let id: Int
        let version: String
        let filename: String
        let description: String
        let downloadUrl: String
    }
    
    func checkForUpdates(completion: @escaping (Result<FirmwareInfo?, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/ota/latest") else {
            completion(.failure(NSError(domain: "InvalidURL", code: -1, userInfo: [NSLocalizedDescriptionKey: "无效的URL"])))
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "NoData", code: -2, userInfo: [NSLocalizedDescriptionKey: "未返回数据"])))
                return
            }
            
            do {
                let firmwareInfo = try JSONDecoder().decode(FirmwareInfo.self, from: data)
                
                // 版本比较
                if self.isNewerVersion(firmwareInfo.version, than: self.currentVersion) {
                    completion(.success(firmwareInfo))
                } else {
                    completion(.success(nil))
                }
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    func downloadFirmware(_ firmwareInfo: FirmwareInfo, progressHandler: @escaping (Double) -> Void, completion: @escaping (Result<URL, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)\(firmwareInfo.downloadUrl)") else {
            completion(.failure(NSError(domain: "InvalidURL", code: -1, userInfo: [NSLocalizedDescriptionKey: "无效的URL"])))
            return
        }
        
        let task = URLSession.shared.downloadTask(with: url) { tempURL, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let tempURL = tempURL else {
                completion(.failure(NSError(domain: "NoDownloadURL", code: -3, userInfo: [NSLocalizedDescriptionKey: "下载失败，无临时URL"])))
                return
            }
            
            // 创建目标URL
            let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            let destinationURL = documentsURL.appendingPathComponent(firmwareInfo.filename)
            
            // 移除可能已存在的文件
            if FileManager.default.fileExists(atPath: destinationURL.path) {
                try? FileManager.default.removeItem(at: destinationURL)
            }
            
            // 移动文件到目标位置
            do {
                try FileManager.default.moveItem(at: tempURL, to: destinationURL)
                completion(.success(destinationURL))
            } catch {
                completion(.failure(error))
            }
        }
        
        // 设置进度处理器
        task.resume()
    }
    
    private func isNewerVersion(_ newVersion: String, than currentVersion: String) -> Bool {
        let newParts = newVersion.components(separatedBy: ".").compactMap { Int($0) }
        let currentParts = currentVersion.components(separatedBy: ".").compactMap { Int($0) }
        
        let count = max(newParts.count, currentParts.count)
        
        for i in 0..<count {
            let newVal = i < newParts.count ? newParts[i] : 0
            let currentVal = i < currentParts.count ? currentParts[i] : 0
            
            if newVal > currentVal {
                return true
            } else if newVal < currentVal {
                return false
            }
        }
        return false
    }
}
```

### JavaScript (Node.js) 示例

```javascript
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

class FirmwareUpdateManager {
    constructor(baseUrl = 'http://localhost:8000', currentVersion = '1.0.0') {
        this.baseUrl = baseUrl;
        this.currentVersion = currentVersion;
        this.isSecure = baseUrl.startsWith('https');
    }
    
    checkForUpdates() {
        return new Promise((resolve, reject) => {
            const url = new URL('/ota/latest', this.baseUrl);
            const client = this.isSecure ? https : http;
            
            const request = client.get(url, (response) => {
                if (response.statusCode !== 200) {
                    reject(new Error(`HTTP error! Status: ${response.statusCode}`));
                    return;
                }
                
                let data = '';
                response.on('data', (chunk) => {
                    data += chunk;
                });
                
                response.on('end', () => {
                    try {
                        const firmwareInfo = JSON.parse(data);
                        
                        // 版本比较
                        if (this.isNewerVersion(firmwareInfo.version, this.currentVersion)) {
                            resolve(firmwareInfo);
                        } else {
                            resolve(null);
                        }
                    } catch (error) {
                        reject(error);
                    }
                });
            });
            
            request.on('error', (error) => {
                reject(error);
            });
        });
    }
    
    downloadFirmware(firmwareInfo, downloadDir = '.') {
        return new Promise((resolve, reject) => {
            const url = new URL(firmwareInfo.download_url, this.baseUrl);
            const client = this.isSecure ? https : http;
            const filePath = path.join(downloadDir, firmwareInfo.filename);
            
            const file = fs.createWriteStream(filePath);
            
            const request = client.get(url, (response) => {
                if (response.statusCode !== 200) {
                    fs.unlink(filePath, () => {});
                    reject(new Error(`HTTP error! Status: ${response.statusCode}`));
                    return;
                }
                
                const totalSize = parseInt(response.headers['content-length'], 10) || 0;
                let downloadedSize = 0;
                
                response.on('data', (chunk) => {
                    downloadedSize += chunk.length;
                    file.write(chunk);
                    
                    // 计算下载进度
                    const progress = totalSize > 0 ? (downloadedSize / totalSize * 100).toFixed(1) : 'Unknown';
                    console.log(`Download progress: ${progress}%`);
                });
                
                response.on('end', () => {
                    file.end(() => {
                        console.log(`Firmware downloaded successfully to ${filePath}`);
                        resolve(filePath);
                    });
                });
            });
            
            request.on('error', (error) => {
                file.close(() => {
                    fs.unlink(filePath, () => {});
                    reject(error);
                });
            });
            
            file.on('error', (error) => {
                file.close(() => {
                    fs.unlink(filePath, () => {});
                    reject(error);
                });
            });
        });
    }
    
    isNewerVersion(newVersion, currentVersion) {
        const newParts = newVersion.split('.').map(Number);
        const currentParts = currentVersion.split('.').map(Number);
        
        for (let i = 0; i < Math.max(newParts.length, currentParts.length); i++) {
            const newVal = newParts[i] || 0;
            const currentVal = currentParts[i] || 0;
            
            if (newVal > currentVal) return true;
            if (newVal < currentVal) return false;
        }
        
        return false;
    }
}

// 使用示例
async function updateFirmware() {
    const updateManager = new FirmwareUpdateManager('http://localhost:8000', '1.0.0');
    
    try {
        console.log('Checking for updates...');
        const firmwareInfo = await updateManager.checkForUpdates();
        
        if (firmwareInfo) {
            console.log(`Found new version: ${firmwareInfo.version}`);
            console.log(`Description: ${firmwareInfo.description}`);
            console.log('Downloading firmware...');
            
            const filePath = await updateManager.downloadFirmware(firmwareInfo);
            console.log(`Firmware downloaded to: ${filePath}`);
            // 这里可以添加固件验证和安装的代码
        } else {
            console.log('No updates available. You have the latest version.');
        }
    } catch (error) {
        console.error('Error during firmware update:', error);
    }
}

// 运行更新检查
updateFirmware();
```

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