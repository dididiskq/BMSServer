---
name: "self_ble"
description: "BMS BLE协议解析封装工具。Invoke when working with BMS Modbus protocol, parsing BLE frames, or communicating with battery management systems."
---

# Self BLE - BMS Modbus协议工具

本skill提供BMS（电池管理系统）基于Modbus协议的BLE通信功能，包括报文解析、封装、CRC校验等核心功能。

## 协议概述

该协议基于Modbus RTU协议，用于与BMS设备进行通信。支持读取设备状态、电压电流数据、温度信息等，以及写入配置参数。

## 帧格式

```
| 子节点地址 | 功能代码 | 数据 | CRC校验 |
| 1字节     | 1字节   | N字节 | 2字节   |
```

- **CRC校验**: CRC低字节在前，CRC高字节在后

## 功能码

| 功能码 | 说明 |
|--------|------|
| 0x03   | 读取保持寄存器 |
| 0x10   | 写入多个保持寄存器 |

## 寄存器地址映射

### Table1 - 设备信息寄存器（只读）

| 地址偏移 | 数据类型 | 单位 | 说明 |
|----------|----------|------|------|
| 0x0000 | Uint16 | K | MOS温度1 |
| 0x0001 | Uint16 | K | 电池温度1 |
| 0x0002 | Uint16 | K | 电池温度2 |
| 0x0003 | Uint16 | K | 电池温度3 |
| 0x0004 | Uint32 | mV | 电池组总电压 |
| 0x0006 | Int32 | mA | 电池组总电流（正充电/负放电） |
| 0x0008 | Uint32 | mAh | 剩余容量RC |
| 0x000A | Uint32 | - | 平衡状态BalStatus |
| 0x000C | Uint32 | - | AFE状态 |
| 0x000E | Uint16 | - | 报警状态 |
| 0x000F | Uint16 | - | 电池状态PackStatus |
| 0x0010 | Uint16 | 10mV | 二次电压 |
| 0x0011 | Int16 | 10mA | 二次电流 |
| 0x0012 | Uint16 | K | 二次温度 |
| 0x0013 | Uint16 | - | 固件版本（高8位主版本/低8位次版本） |
| 0x0014 | Uint16 | % | 健康百分比SOH（高8位）/电量百分比RSOC（低8位） |
| 0x0015 | Uint16 | - | RTC年月 |
| 0x0016 | Uint16 | - | RTC日时 |
| 0x0017 | Uint16 | - | RTC分秒 |
| 0x0018 | Uint16 | - | 电池组串数/电池类型 |
| 0x0019 | Uint16 | - | AFE代号/客户代号 |
| 0x001A | Uint16 | - | 循环次数 |
| 0x001B | Uint16 | 10mAh | 满充容量FCC |
| 0x001C | Uint16 | 10mAh | 设计容量DC |
| 0x001D | Uint16 | h | 最大未充电间隔时间 |
| 0x001E | Uint16 | h | 最近未充电间隔时间 |
| 0x001F | Uint16 | - | 功能开关配置寄存器 |
| 0x0020-0x003F | Uint16 | mV | 第1-32节电池电压 |

**AFE状态位定义（1表示置位）**:
- bit0:过压, bit1:欠压, bit2:放电过流1, bit3:放电过流2
- bit4:充电过流, bit5:短路, bit6:断线, bit7:低压禁充
- bit8:充电低温, bit9:充电高温, bit10:放电低温, bit11:放电高温
- bit16:放电MOS状态, bit17:充电MOS状态, bit18:硬件放电, bit19:硬件充电
- bit20:PRO状态, bit21:CTLD状态, bit22:PD状态, bit23:均衡状态

**报警状态位定义（1表示置位）**:
- bit0:超高压报警, bit1:超低压报警, bit2:防拆卸报警
- bit3:电压采集线断线, bit4:温度采集线断线, bit5:AFE通讯失效
- bit6:电池组压差过大

**电池状态位定义（1表示置位）**:
- bit0:零电流已校准, bit1:电流已校准, bit2:强制开启放电
- bit3:强制关闭放电, bit4:强制开启充电, bit5:强制关闭充电
- bit8:满充电标志, bit10:允许容量更新, bit11:放电标志
- bit12:充电标志, bit13:AFE配置失败, bit14:允许放电, bit15:正版固件

### Table2 - 设备信息寄存器（可读写）

| 地址偏移 | 数据类型 | 单位 | 说明 |
|----------|----------|------|------|
| 0x0200 | Uint16 | - | 电池组串数CellNumber |
| 0x0201 | Uint16 | - | 电池类型CellType（0:磷酸铁锂 1:三元 2:钛酸锂 3:钠电池） |
| 0x0202 | Uint16 | - | 模拟前端代号AFE Number |
| 0x0203 | Uint16 | - | 客户代号Customer Number |
| 0x0204 | Uint16 | - | 硬件版本 |
| 0x0205 | Uint16 | - | 开关配置寄存器FunctionConfig |
| 0x0206 | Uint16 | s | 休眠延时SleepDelay |
| 0x0207 | Uint16 | s | 关机延时ShutDownDelay |
| 0x0208 | Uint16 | 10mV | 额定充电电压（5460表示54.6V） |
| 0x0209 | Int16 | 10mA | 额定充电电流（200表示2.0A） |
| 0x020A | Uint16 | mV | 满充电压(单节) |
| 0x020B | Int16 | mA | 满充电流 |
| 0x020C | Uint16 | s | 满充延时 |
| 0x020D | Int16 | mA | 零电流显示阈值 |
| 0x020E | float | mΩ | 采样电阻值SampleRValue |
| 0x020F | Uint16 | mV | 过充保护电压OV（单节） |
| 0x0210 | Uint16 | mV | 过充恢复电压OVR（单节） |
| 0x0211 | Uint16 | ms | 过充延时OVT |
| 0x0212 | Uint16 | mV | 低压禁充电电压VL0V |
| 0x0213 | Uint16 | mV | 均衡启动电压VOB（单节） |
| 0x0214 | Uint16 | mV | 均衡启动阈值BALD |
| 0x0215 | Uint16 | ms | 均衡延时BALT |
| 0x0216 | Uint16 | mV | 过放保护电压UV（单节） |
| 0x0217 | Uint16 | mV | 过放恢复电压UVR（单节） |
| 0x0218 | Uint16 | ms | 过放延时UVT |
| 0x0219 | Uint16 | A | 放电过流1保护电流OCD1 |
| 0x021A | Uint16 | ms | 放电过流1延时OCD1T |
| 0x021B | Uint16 | A | 放电过流2保护电流OCD2 |
| 0x021C | Uint16 | ms | 放电过流2延时OCD2T |
| 0x021D | Uint16 | A | 短路保护电流 |
| 0x021E | Uint16 | μs | 短路保护延时SCT |
| 0x021F | Uint16 | A | 充电过流保护电流OCC |
| 0x0220 | Uint16 | ms | 充电过流延时OCCT |
| 0x0221 | Int16 | ℃ | 充电高温保护OTC |
| 0x0222 | Int16 | ℃ | 充电高温恢复OTCR |
| 0x0223 | Int16 | ℃ | 充电低温保护UTC |
| 0x0224 | Int16 | ℃ | 充电低温恢复UTCR |
| 0x0225 | Int16 | ℃ | 放电高温保护OTD |
| 0x0226 | Int16 | ℃ | 放电高温恢复OTDR |
| 0x0227 | Int16 | ℃ | 放电低温保护UTD |
| 0x0228 | Int16 | ℃ | 放电低温恢复UTDR |
| 0x0229 | Int16 | ℃ | MOS放电高温保护MOTD |
| 0x022A | Int16 | ℃ | MOS放电高温恢复MOTDR |
| 0x022B | string | - | 电池SN[12] |
| 0x0233 | string | - | 制造厂家Manufacturer[8] |
| 0x0237 | string | - | 制造厂商型号ManufacturerModel[24] |
| 0x023F | string | - | 客户名称CustomerName[8] |
| 0x0243 | string | - | 客户型号CustomerModel[24] |
| 0x0257 | string | - | 生产日期MNFDate[8] |

### Table3 - 内部动态记录参数

| 地址偏移 | 数据类型 | 单位 | 说明 |
|----------|----------|------|------|
| 0x0300 | Uint16 | - | 设计循环次数 |
| 0x0301 | Uint16 | - | 循环次数Cyclecount |
| 0x0302 | Uint32 | mAh | 满充容量FCC |
| 0x0304 | Uint32 | mAh | 设计容量DC |
| 0x0306 | Uint16 | h | 最大未充电间隔时间 |
| 0x0307 | Uint16 | h | 最近未充电间隔时间 |
| 0x0308 | string | - | BT码BT[32] |
| 0x0328-0x035F | Uint32 | - | 第1-24个保护时间 |
| 0x0360-0x0397 | Uint32 | - | 第1-24个保护事件 |

## CRC校验算法

使用Modbus CRC16校验，多项式0xA001。

```python
def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF
```

## 报文封装示例

### 读取电池电量（寄存器0x0014，1个寄存器）

**请求报文**:
```
16 03 00 14 00 01 35 F6
```
- 16: 从机地址
- 03: 功能码
- 00 14: 起始地址
- 00 01: 寄存器数量
- 35 F6: CRC校验

**响应报文**:
```
16 03 00 14 02 00 02 CA C7
```
- 16: 从机地址
- 03: 功能码
- 00 14: 起始地址
- 02: 返回字节数
- 00 02: 健康SOH=0%, 电量RSOC=2%
- CA C7: CRC校验

### 写入电池组串数（寄存器0x0200，写入值0x0010）

**请求报文**:
```
16 10 02 00 00 01 02 00 10 C4 5E
```
- 16: 从机地址
- 10: 功能码
- 02 00: 起始地址
- 00 01: 寄存器数量
- 02: 字节数
- 00 10: 数据（电池组串数=16）
- C4 5E: CRC校验

**响应报文**:
```
16 10 02 00 00 01 18 BC
```
- 16: 从机地址
- 10: 功能码
- 02 00: 起始地址
- 00 01: 写入数量
- 18 BC: CRC校验

## 使用场景

1. **读取BMS状态**: 读取电池电压、电流、温度、SOC、SOH等实时数据
2. **配置BMS参数**: 设置电池组串数、电池类型、保护阈值等
3. **监控报警状态**: 获取过压、欠压、过流、温度异常等报警信息
4. **读取历史数据**: 获取保护事件记录、循环次数等历史数据
5. **固件版本查询**: 获取BMS固件版本信息

## 数据类型说明

- **Uint16**: 无符号16位整数
- **Int16**: 有符号16位整数
- **Uint32**: 无符号32位整数
- **Int32**: 有符号32位整数
- **float**: 32位浮点数
- **string**: ASCII字符串

## 注意事项

1. 所有多字节数据采用大端序（Big-Endian）存储
2. 温度单位开尔文(K)需要转换为摄氏度: °C = K - 273.15
3. 电流正数表示充电，负数表示放电
4. 字符串字段需要根据指定长度进行解析
5. CRC校验必须正确，否则设备不会响应
