# 计算机网络实验2 - 使用说明（中文）

## ✅ 任务1：框架代码补全 - 已完成

所有框架代码已经补全，实现了以下功能：

### 已实现的功能：

1. **IP地址验证**
   - IPv4地址验证（单播范围：1.0.0.0 - 223.255.255.255）
   - IPv4组播地址验证（组播范围：224.0.0.0 - 239.255.255.255）
   - IPv6地址验证（单播范围：2000:: - 3FFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF）
   - IPv6组播地址验证（组播范围：FF00::/8）

2. **MAC地址转换**
   - IPv4组播地址转MAC地址（01:00:5E + 低23位）
   - IPv6组播地址转MAC地址（33:33 + 低32位）

3. **ICMP/ICMPv6实现**
   - ICMP校验和计算（RFC 1071）
   - IPv4单播ICMP回显请求（Type=8, Code=0）
   - IPv4组播ICMP回显请求
   - IPv6单播ICMPv6回显请求（Type=128, Code=0，包含伪首部）
   - IPv6组播ICMPv6回显请求（包含伪首部）

### 验证测试：

运行以下命令验证实现：
```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试脚本
python3 test_implementation.py
```

测试脚本会验证：
- ✓ IPv4地址验证
- ✓ IPv6地址验证  
- ✓ IPv4组播到MAC转换
- ✓ IPv6组播到MAC转换
- ✓ 校验和计算

---

## 📋 任务2：虚拟网络测试 - 你需要完成的工作

### 前置准备：

1. **安装eNSP软件**（华为企业网络模拟平台）
2. **管理员权限**：运行Python脚本需要管理员/root权限（使用原始套接字）
3. **安装依赖**：
   ```bash
   pip install psutil
   ```

---

### A. IPv4单播测试（10分）

**第1步：在eNSP中搭建虚拟网络**
- 创建包含多个路由器和PC的网络拓扑
- 配置子网间路由
- 为所有设备分配IPv4地址
- 示例拓扑：PC1 <-> 路由器1 <-> 路由器2 <-> PC2

**第2步：添加云设备**
- 在eNSP中添加云设备
- 将云设备连接到虚拟网络
- 绑定云设备到你的物理网卡
- 这样可以在虚拟网络和真实网络之间建立桥接

**第3步：运行IPv4单播测试**
```bash
# 在你的真实机器上（需要sudo/管理员权限）
sudo python3 cast_ping_simple.py <虚拟PC的IPv4地址> -s <你的源IP> -c 4 -m unicast

# 示例：
sudo python3 cast_ping_simple.py 192.168.1.100 -s 192.168.1.1 -c 4 -m unicast
```

**第4步：验证结果**
- 在eNSP中使用抓包查看ICMP回显请求包
- 检查是否收到ICMP回显应答包
- 验证路由器上的路由表

---

### B. IPv4组播测试（10分）

**第1步：配置组播**
- 在路由器上启用组播路由（PIM协议）
- 在PC上配置IGMP加入组播组
- 华为路由器示例命令：
```
[Router] multicast routing-enable
[Router-GigabitEthernet0/0/0] pim sm
[Router-GigabitEthernet0/0/0] igmp enable
```

**第2步：配置组播组**
- 让eNSP中的PC加入组播组（例如224.1.1.1）
- 如需要可配置静态组播路由

**第3步：运行IPv4组播测试**
```bash
# 你的代码作为组播源
sudo python3 cast_ping_simple.py 224.1.1.1 -s <你的源IP> -c 4 -m multicast

# 示例：
sudo python3 cast_ping_simple.py 224.1.1.1 -s 192.168.1.1 -c 4 -m multicast
```

**第4步：验证组播行为**
- 检查路由器上的组播转发表
- 验证所有组播组成员都收到了包
- 使用抓包确认组播MAC地址正确（01:00:5e:XX:XX:XX）
- 检查路由器统计信息中的组播包计数

---

### C. IPv6单播测试（10分）

**第1步：配置IPv6**
- 在所有路由器和PC上启用IPv6
- 分配IPv6全局单播地址（2000::/3范围）
- 配置IPv6路由（OSPFv3或静态路由）
- 示例IPv6地址：2001:db8:1::1, 2001:db8:2::1

**第2步：运行IPv6单播测试**
```bash
sudo python3 cast_ping_simple.py 2001:db8:2::100 -s 2001:db8:1::1 -c 4 -m unicast
```

**第3步：验证结果**
- 使用抓包验证ICMPv6包
- 检查IPv6路由表
- 验证ICMPv6校验和包含伪首部

---

### D. IPv6组播测试（10分）

**第1步：配置IPv6组播**
- 在路由器上启用IPv6组播路由
- **注意**：eNSP中的PC不支持MLD（组播监听者发现）
- **变通方法**：配置路由器接口模拟组播成员
- 示例组播地址：ff02::1:1（链路本地）或 ff05::1:1（站点本地）

**第2步：配置路由器作为组播成员**
```
[Router-GigabitEthernet0/0/0] ipv6 address 2001:db8:1::1/64
[Router-GigabitEthernet0/0/0] ipv6 pim sm
[Router] ipv6 multicast routing
```

**第3步：运行IPv6组播测试**
```bash
sudo python3 cast_ping_simple.py ff02::1:1 -s 2001:db8:1::1 -c 4 -m multicast
```

**第4步：验证IPv6组播**
- 检查组播转发表
- 验证组播MAC地址（33:33:XX:XX:XX:XX）
- 监控路由器统计信息

---

## 📝 使用示例

### 基本命令：

```bash
# IPv4单播
sudo python3 cast_ping_simple.py 192.168.1.100 -m unicast -c 5

# IPv4组播
sudo python3 cast_ping_simple.py 224.1.1.1 -m multicast -c 5

# IPv6单播（带源地址）
sudo python3 cast_ping_simple.py 2001:db8::1 -s 2001:db8::100 -m unicast -c 3

# IPv6组播
sudo python3 cast_ping_simple.py ff02::1 -m multicast -c 3
```

### 错误处理示例：

```bash
# 无效IP地址
$ python3 cast_ping_simple.py 256.1.2.3
错误：无效的IP地址 256.1.2.3

# 在单播模式下使用组播地址
$ python3 cast_ping_simple.py 224.1.1.1 -m unicast
错误：224.1.1.1 不是有效的单播地址
IPv4单播地址应在范围 1.0.0.0 到 223.255.255.255

# 在组播模式下使用单播地址
$ python3 cast_ping_simple.py 8.8.8.8 -m multicast
错误：8.8.8.8 不是有效的组播地址
IPv4组播地址应在范围 224.0.0.0 到 239.255.255.255
```

---

## ✅ 评分检查清单

### IPv4部分（25分）：
- [ ] **IPv4地址验证（5分）**：程序正确验证IPv4地址
- [ ] **IPv4单播代码（5分）**：ICMP回显请求构造正确，校验和正确
- [ ] **IPv4单播测试（5分）**：成功ping虚拟PC，收到ICMP回显应答
- [ ] **IPv4组播代码（5分）**：组播MAC转换和ICMP包正确
- [ ] **IPv4组播测试（5分）**：包到达组播组成员，路由器统计验证

### IPv6部分（25分）：
- [ ] **IPv6地址验证（5分）**：程序正确验证IPv6地址
- [ ] **IPv6单播代码（5分）**：带伪首部的ICMPv6校验和正确
- [ ] **IPv6单播测试（5分）**：成功ping虚拟设备，收到ICMPv6回显应答
- [ ] **IPv6组播代码（5分）**：组播MAC转换和ICMPv6包正确
- [ ] **IPv6组播测试（5分）**：包正确转发，路由器配置验证

---

## 🔧 故障排除

### 常见问题：

1. **权限被拒绝**
   - 使用`sudo`或管理员权限运行
   - 原始套接字需要提升的权限

2. **找不到网络接口**
   - 验证你的源IP地址已分配给网络接口
   - 使用`ip addr`（Linux）或`ipconfig`（Windows）检查

3. **虚拟网络无响应**
   - 验证云设备配置正确
   - 检查eNSP中的路由表
   - 确保防火墙没有阻止ICMP/ICMPv6

4. **组播不工作**
   - 验证所有路由器上已启用组播路由
   - 检查IGMP/MLD配置
   - 验证组播组成员资格

5. **校验和错误**
   - 校验和自动计算
   - 如果包被丢弃，检查网络配置，而不是代码

---

## 📚 参考资料

- **RFC 792**：Internet控制消息协议（ICMP）
- **RFC 4443**：Internet控制消息协议（ICMPv6）
- **RFC 1071**：计算Internet校验和
- **实验9课件**：云设备配置（B部分）
- **实验10课件**：
  - 第11页：IPv4组播到MAC转换
  - 第30页：IPv6组播到MAC转换
  - 练习2：IPv4组播配置
  - 练习3：IPv6组播配置

---

## 📁 仓库中的文件

- **cast_ping_simple.py**：ICMP/ICMPv6单播和组播的完整实现
- **test_implementation.py**：自动化测试脚本
- **requirements.txt**：Python依赖列表
- **README.md**：英文详细文档
- **README_CN.md**：本文件 - 中文使用指南
- **CS305 2025 Fall Lab Assignment 2.pdf**：原始作业文档

---

## 总结

**任务1（框架代码）已100%完成**。所有TODO标记的部分都已正确实现：
- ✅ IP地址验证
- ✅ 单播/组播地址检查
- ✅ 组播MAC地址转换
- ✅ ICMP/ICMPv6包构造
- ✅ 校验和计算

**你现在需要完成任务2**：
1. 在eNSP中搭建虚拟网络拓扑
2. 配置路由和组播
3. 使用提供的Python脚本进行测试
4. 验证结果并截图/记录用于报告

祝你测试顺利！如有问题，请参考：
1. 实验课件（实验9和实验10）
2. eNSP文档
3. RFC文档了解协议细节
