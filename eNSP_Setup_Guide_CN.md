# eNSP 虚拟网络搭建详细指南

## 目录
1. [环境准备](#环境准备)
2. [测试1：IPv4单播通信](#测试1ipv4单播通信)
3. [测试2：IPv4组播通信](#测试2ipv4组播通信)
4. [测试3：IPv6单播通信](#测试3ipv6单播通信)
5. [测试4：IPv6组播通信](#测试4ipv6组播通信)
6. [故障排除](#故障排除)

---

## 环境准备

### 软件要求
- **eNSP V1.3.00.100** 或更高版本
- **VirtualBox** (eNSP依赖)
- **WinPcap** 或 **Npcap** (抓包工具)
- **Python 3.x** (用于运行测试脚本)

### 安装步骤
1. 安装VirtualBox
2. 安装eNSP
3. 在eNSP中注册设备（AR路由器、交换机等）
4. 配置WinPcap/Npcap用于抓包

---

## 测试1：IPv4单播通信

### 拓扑结构

```
[你的真实PC] --- [Cloud1] --- [AR1] --- [AR2] --- [PC1]
  192.168.1.1      桥接      .1   .2   .1   .2    192.168.2.10
                            192.168.1.0/24  192.168.2.0/24
```

### 第一步：创建拓扑

1. **打开eNSP**，创建新拓扑

2. **添加设备**：
   - 从设备列表拖拽 **2个AR路由器** (例如：AR2220)
   - 拖拽 **1个PC**
   - 拖拽 **1个Cloud** (云设备)

3. **连接设备**：
   - Cloud1 的 Ethernet1 连接到 AR1 的 GigabitEthernet0/0/0
   - AR1 的 GigabitEthernet0/0/1 连接到 AR2 的 GigabitEthernet0/0/0
   - AR2 的 GigabitEthernet0/0/1 连接到 PC1

4. **配置Cloud设备**：
   - 右键点击 Cloud1 → 配置
   - 在 "端口映射" 选项卡中，将 Ethernet1 绑定到你的真实网卡（选择你正在使用的网络适配器）
   - 点击确定

### 第二步：配置AR1路由器

启动AR1，在CLI中输入以下命令：

```bash
<Huawei> system-view
[Huawei] sysname AR1
[AR1] interface GigabitEthernet 0/0/0
[AR1-GigabitEthernet0/0/0] ip address 192.168.1.2 24
[AR1-GigabitEthernet0/0/0] quit

[AR1] interface GigabitEthernet 0/0/1
[AR1-GigabitEthernet0/0/1] ip address 10.0.0.1 24
[AR1-GigabitEthernet0/0/1] quit

# 配置静态路由到PC1所在网段
[AR1] ip route-static 192.168.2.0 24 10.0.0.2

# 保存配置
[AR1] quit
<AR1> save
The current configuration will be written to the device. Are you sure? [Y/N]: y
```

### 第三步：配置AR2路由器

启动AR2，在CLI中输入以下命令：

```bash
<Huawei> system-view
[Huawei] sysname AR2
[AR2] interface GigabitEthernet 0/0/0
[AR2-GigabitEthernet0/0/0] ip address 10.0.0.2 24
[AR2-GigabitEthernet0/0/0] quit

[AR2] interface GigabitEthernet 0/0/1
[AR2-GigabitEthernet0/0/1] ip address 192.168.2.1 24
[AR2-GigabitEthernet0/0/1] quit

# 配置静态路由回真实网络
[AR2] ip route-static 192.168.1.0 24 10.0.0.1

# 保存配置
[AR2] quit
<AR2> save
```

### 第四步：配置PC1

1. 右键点击PC1 → 配置
2. 设置IP地址：
   - IP地址：`192.168.2.10`
   - 子网掩码：`255.255.255.0`
   - 网关：`192.168.2.1`

### 第五步：配置你的真实PC

在你的真实PC上配置IP地址（Windows/Linux）：

**Windows:**
```cmd
# 打开网络适配器设置，为绑定到Cloud的网卡设置：
IP地址：192.168.1.1
子网掩码：255.255.255.0
网关：192.168.1.2
```

**Linux:**
```bash
sudo ip addr add 192.168.1.1/24 dev eth0  # 替换eth0为你的网卡名
sudo ip route add 192.168.2.0/24 via 192.168.1.2
```

### 第六步：测试连通性

在真实PC上测试：

```bash
# 测试到AR1
ping 192.168.1.2

# 测试到AR2
ping 10.0.0.2

# 测试到PC1
ping 192.168.2.10
```

### 第七步：运行Python脚本测试

```bash
# 在你的真实PC上运行
sudo python3 cast_ping_simple.py 192.168.2.10 -s 192.168.1.1 -c 4 -m unicast
```

### 期待效果

**控制台输出：**
```
Pinging 192.168.2.10 with 4 packets:
Sent ICMPv4 Echo Request to 192.168.2.10 (Checksum: xxxx)- Packet 1
Sent ICMPv4 Echo Request to 192.168.2.10 (Checksum: xxxx)- Packet 2
Sent ICMPv4 Echo Request to 192.168.2.10 (Checksum: xxxx)- Packet 3
Sent ICMPv4 Echo Request to 192.168.2.10 (Checksum: xxxx)- Packet 4
```

**在eNSP中验证：**
1. 在AR1或AR2的接口上启动抓包（右键接口 → 数据抓包）
2. 观察ICMP Echo Request包
3. 在PC1上也应该能看到ICMP包到达
4. 可能会收到ICMP Echo Reply（取决于PC1的配置）

---

## 测试2：IPv4组播通信

### 拓扑结构

```
[你的真实PC] --- [Cloud1] --- [AR1] --- [AR2] --- [PC1]
  192.168.1.1      桥接      .2    .1   .1   .2    192.168.2.10
                          (组播源)        (组播成员)
```

### 第一步：在测试1的基础上继续配置

### 第二步：在AR1上启用组播

```bash
<AR1> system-view

# 全局启用组播路由
[AR1] multicast routing-enable

# 在连接云设备的接口上配置PIM
[AR1] interface GigabitEthernet 0/0/0
[AR1-GigabitEthernet0/0/0] pim sm
[AR1-GigabitEthernet0/0/0] igmp enable
[AR1-GigabitEthernet0/0/0] quit

# 在连接AR2的接口上配置PIM
[AR1] interface GigabitEthernet 0/0/1
[AR1-GigabitEthernet0/0/1] pim sm
[AR1-GigabitEthernet0/0/1] quit

# 配置静态RP（汇聚点）
[AR1] pim
[AR1-pim] static-rp 192.168.1.2
[AR1-pim] quit

# 保存配置
[AR1] quit
<AR1> save
```

### 第三步：在AR2上启用组播

```bash
<AR2> system-view

# 全局启用组播路由
[AR2] multicast routing-enable

# 在连接AR1的接口上配置PIM
[AR2] interface GigabitEthernet 0/0/0
[AR2-GigabitEthernet0/0/0] pim sm
[AR2-GigabitEthernet0/0/0] quit

# 在连接PC的接口上配置PIM和IGMP
[AR2] interface GigabitEthernet 0/0/1
[AR2-GigabitEthernet0/0/1] pim sm
[AR2-GigabitEthernet0/0/1] igmp enable
[AR2-GigabitEthernet0/0/1] quit

# 配置静态RP（使用相同的RP地址）
[AR2] pim
[AR2-pim] static-rp 192.168.1.2
[AR2-pim] quit

# 保存配置
[AR2] quit
<AR2> save
```

### 第四步：配置PC1加入组播组

在PC1上：

```bash
# 打开PC1的命令行
# 加入组播组 224.1.1.1
# 注意：eNSP的PC可能不完全支持IGMP，可以用以下替代方法
```

**替代方法：在AR2上手动配置组播组成员**

```bash
<AR2> system-view
[AR2] interface GigabitEthernet 0/0/1
[AR2-GigabitEthernet0/0/1] igmp static-group 224.1.1.1
[AR2-GigabitEthernet0/0/1] quit
[AR2] quit
<AR2> save
```

### 第五步：验证组播配置

在AR1上检查组播路由表：

```bash
<AR1> display pim routing-table
<AR1> display igmp group
```

在AR2上检查：

```bash
<AR2> display pim routing-table
<AR2> display igmp group
```

### 第六步：运行Python脚本测试

```bash
# 在你的真实PC上运行
sudo python3 cast_ping_simple.py 224.1.1.1 -s 192.168.1.1 -c 4 -m multicast
```

### 期待效果

**控制台输出：**
```
Multicast MAC Address: 01:00:5e:01:01:01
Pinging 224.1.1.1 with 4 packets:
Sent ICMP Echo Request to 224.1.1.1 (MAC: 01:00:5e:01:01:01 - Checksum: xxxx) - Packet 1
Sent ICMP Echo Request to 224.1.1.1 (MAC: 01:00:5e:01:01:01 - Checksum: xxxx) - Packet 2
Sent ICMP Echo Request to 224.1.1.1 (MAC: 01:00:5e:01:01:01 - Checksum: xxxx) - Packet 3
Sent ICMP Echo Request to 224.1.1.1 (MAC: 01:00:5e:01:01:01 - Checksum: xxxx) - Packet 4
```

**验证方法：**
1. 在AR1上启动接口抓包，观察组播包
2. 检查组播MAC地址是否为 `01:00:5e:01:01:01`
3. 在AR2上查看组播统计：
   ```bash
   <AR2> display pim statistics
   <AR2> display multicast forwarding-table
   ```
4. 组播包应该从AR1转发到AR2，再到达PC1所在的网段

---

## 测试3：IPv6单播通信

### 拓扑结构

```
[你的真实PC] --- [Cloud1] --- [AR1] --- [AR2] --- [PC1]
2001:db8:1::1    桥接      ::2   ::1  ::1   ::2  2001:db8:2::10
                        2001:db8:1::/64   2001:db8:2::/64
```

### 第一步：清除IPv4配置或使用新拓扑

可以继续使用测试1的拓扑，同时配置IPv6。

### 第二步：配置AR1的IPv6

```bash
<AR1> system-view

# 全局启用IPv6
[AR1] ipv6

# 配置连接云设备的接口
[AR1] interface GigabitEthernet 0/0/0
[AR1-GigabitEthernet0/0/0] ipv6 enable
[AR1-GigabitEthernet0/0/0] ipv6 address 2001:db8:1::2/64
[AR1-GigabitEthernet0/0/0] quit

# 配置连接AR2的接口
[AR1] interface GigabitEthernet 0/0/1
[AR1-GigabitEthernet0/0/1] ipv6 enable
[AR1-GigabitEthernet0/0/1] ipv6 address 2001:db8:10::1/64
[AR1-GigabitEthernet0/0/1] quit

# 配置静态路由
[AR1] ipv6 route-static 2001:db8:2:: 64 2001:db8:10::2

# 保存配置
[AR1] quit
<AR1> save
```

### 第三步：配置AR2的IPv6

```bash
<AR2> system-view

# 全局启用IPv6
[AR2] ipv6

# 配置连接AR1的接口
[AR2] interface GigabitEthernet 0/0/0
[AR2-GigabitEthernet0/0/0] ipv6 enable
[AR2-GigabitEthernet0/0/0] ipv6 address 2001:db8:10::2/64
[AR2-GigabitEthernet0/0/0] quit

# 配置连接PC的接口
[AR2] interface GigabitEthernet 0/0/1
[AR2-GigabitEthernet0/0/1] ipv6 enable
[AR2-GigabitEthernet0/0/1] ipv6 address 2001:db8:2::1/64
[AR2-GigabitEthernet0/0/1] quit

# 配置静态路由
[AR2] ipv6 route-static 2001:db8:1:: 64 2001:db8:10::1

# 保存配置
[AR2] quit
<AR2> save
```

### 第四步：配置PC1的IPv6

**注意：eNSP的PC对IPv6支持有限，可以用AR2的接口IP作为测试目标**

或者，如果PC支持IPv6：
- IPv6地址：`2001:db8:2::10/64`
- 网关：`2001:db8:2::1`

### 第五步：配置真实PC的IPv6

**Windows:**
```cmd
# 使用PowerShell（管理员权限）
netsh interface ipv6 add address "你的网卡名" 2001:db8:1::1/64
netsh interface ipv6 add route 2001:db8:2::/64 "你的网卡名" 2001:db8:1::2
```

**Linux:**
```bash
sudo ip -6 addr add 2001:db8:1::1/64 dev eth0
sudo ip -6 route add 2001:db8:2::/64 via 2001:db8:1::2
```

### 第六步：测试IPv6连通性

```bash
# 测试到AR1
ping6 2001:db8:1::2

# 测试到AR2
ping6 2001:db8:10::2

# 测试到PC1（或AR2的另一个接口）
ping6 2001:db8:2::1
```

### 第七步：运行Python脚本测试

```bash
# 测试到AR2的接口（因为PC可能不支持IPv6）
sudo python3 cast_ping_simple.py 2001:db8:2::1 -s 2001:db8:1::1 -c 4 -m unicast

# 或者如果PC支持IPv6
sudo python3 cast_ping_simple.py 2001:db8:2::10 -s 2001:db8:1::1 -c 4 -m unicast
```

### 期待效果

**控制台输出：**
```
Pinging 2001:db8:2::1 with 4 packets:
Sent ICMPv6 Echo Request to 2001:db8:2::1 (Checksum: xxxx)- Packet 1
Sent ICMPv6 Echo Request to 2001:db8:2::1 (Checksum: xxxx)- Packet 2
Sent ICMPv6 Echo Request to 2001:db8:2::1 (Checksum: xxxx)- Packet 3
Sent ICMPv6 Echo Request to 2001:db8:2::1 (Checksum: xxxx)- Packet 4
```

**验证：**
1. 在路由器接口上抓包，观察ICMPv6包
2. 验证ICMPv6类型为128（Echo Request）
3. 检查IPv6路由表：
   ```bash
   <AR1> display ipv6 routing-table
   ```

---

## 测试4：IPv6组播通信

### 拓扑结构

使用测试3的拓扑，在其基础上配置IPv6组播。

### 第一步：在AR1上启用IPv6组播

```bash
<AR1> system-view

# 全局启用IPv6组播路由
[AR1] multicast ipv6 routing-enable

# 在连接云设备的接口上配置
[AR1] interface GigabitEthernet 0/0/0
[AR1-GigabitEthernet0/0/0] pim ipv6 sm
[AR1-GigabitEthernet0/0/0] mld enable
[AR1-GigabitEthernet0/0/0] quit

# 在连接AR2的接口上配置
[AR1] interface GigabitEthernet 0/0/1
[AR1-GigabitEthernet0/0/1] pim ipv6 sm
[AR1-GigabitEthernet0/0/1] quit

# 配置IPv6 PIM静态RP
[AR1] pim ipv6
[AR1-pim-ipv6] static-rp 2001:db8:1::2
[AR1-pim-ipv6] quit

# 保存配置
[AR1] quit
<AR1> save
```

### 第二步：在AR2上启用IPv6组播

```bash
<AR2> system-view

# 全局启用IPv6组播路由
[AR2] multicast ipv6 routing-enable

# 在连接AR1的接口上配置
[AR2] interface GigabitEthernet 0/0/0
[AR2-GigabitEthernet0/0/0] pim ipv6 sm
[AR2-GigabitEthernet0/0/0] quit

# 在连接PC的接口上配置（模拟组播成员）
[AR2] interface GigabitEthernet 0/0/1
[AR2-GigabitEthernet0/0/1] pim ipv6 sm
[AR2-GigabitEthernet0/0/1] mld enable
# 手动加入组播组（因为PC不支持MLD）
[AR2-GigabitEthernet0/0/1] mld static-group ff05::1:1
[AR2-GigabitEthernet0/0/1] quit

# 配置IPv6 PIM静态RP
[AR2] pim ipv6
[AR2-pim-ipv6] static-rp 2001:db8:1::2
[AR2-pim-ipv6] quit

# 保存配置
[AR2] quit
<AR2> save
```

### 第三步：验证IPv6组播配置

在AR1上：

```bash
<AR1> display pim ipv6 routing-table
<AR1> display mld group
```

在AR2上：

```bash
<AR2> display pim ipv6 routing-table
<AR2> display mld group
```

应该能看到组播组 `ff05::1:1` 的信息。

### 第四步：运行Python脚本测试

```bash
# 使用站点本地组播地址
sudo python3 cast_ping_simple.py ff05::1:1 -s 2001:db8:1::1 -c 4 -m multicast

# 或使用链路本地组播地址（范围更小）
sudo python3 cast_ping_simple.py ff02::1 -s 2001:db8:1::1 -c 4 -m multicast
```

### 期待效果

**控制台输出：**
```
Multicast MAC Address: 33:33:00:01:00:01
Pinging ff05::1:1 with 4 packets:
Sent ICMP Echo Request to ff05::1:1 (MAC: 33:33:00:01:00:01 - Checksum: xxxx) - Packet 1
Sent ICMP Echo Request to ff05::1:1 (MAC: 33:33:00:01:00:01 - Checksum: xxxx) - Packet 2
Sent ICMP Echo Request to ff05::1:1 (MAC: 33:33:00:01:00:01 - Checksum: xxxx) - Packet 3
Sent ICMP Echo Request to ff05::1:1 (MAC: 33:33:00:01:00:01 - Checksum: xxxx) - Packet 4
```

**验证方法：**
1. 在AR1接口上抓包，观察IPv6组播包
2. 验证目标MAC地址为 `33:33:00:01:00:01`
3. 检查组播转发表：
   ```bash
   <AR2> display multicast ipv6 forwarding-table
   <AR2> display pim ipv6 statistics
   ```
4. 在AR2的统计信息中应该能看到接收到的组播包

---

## 故障排除

### 问题1：无法ping通虚拟网络

**可能原因：**
- 路由配置错误
- 接口未启用
- 防火墙阻止

**解决方法：**
```bash
# 检查接口状态
<AR1> display ip interface brief
<AR1> display interface GigabitEthernet 0/0/0

# 检查路由表
<AR1> display ip routing-table

# 确保接口没有shutdown
[AR1] interface GigabitEthernet 0/0/0
[AR1-GigabitEthernet0/0/0] undo shutdown
```

### 问题2：Cloud设备无法通信

**可能原因：**
- 网卡绑定错误
- 真实PC的IP配置错误
- 防火墙阻止

**解决方法：**
1. 重新配置Cloud设备，选择正确的网卡
2. 确保真实PC的IP在正确的网段
3. 临时关闭防火墙测试：
   ```bash
   # Windows
   netsh advfirewall set allprofiles state off
   
   # Linux
   sudo ufw disable
   ```

### 问题3：组播不工作

**可能原因：**
- PIM未启用
- RP配置错误
- IGMP/MLD未配置

**解决方法：**
```bash
# 检查组播路由是否启用
<AR1> display current-configuration | include multicast

# 检查PIM接口
<AR1> display pim interface

# 检查组播路由表
<AR1> display pim routing-table

# 重启组播协议
[AR1] undo multicast routing-enable
[AR1] multicast routing-enable
```

### 问题4：Python脚本权限错误

**错误信息：** `PermissionError: Operation not permitted`

**解决方法：**
```bash
# 使用sudo运行
sudo python3 cast_ping_simple.py <destination> -m <mode>

# Linux: 给Python添加cap_net_raw权限（可选）
sudo setcap cap_net_raw+ep $(which python3)
```

### 问题5：IPv6地址配置失败

**可能原因：**
- 系统不支持IPv6
- IPv6未启用

**解决方法：**
```bash
# Windows: 确保IPv6已启用
netsh interface ipv6 show interface

# Linux: 启用IPv6
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=0
```

### 问题6：抓包看不到数据

**可能原因：**
- 抓包位置选择错误
- 过滤器设置问题

**解决方法：**
1. 在靠近源的接口抓包（例如AR1的GE0/0/0）
2. 不要使用过滤器，先看所有流量
3. 确保接口有流量通过：
   ```bash
   <AR1> display interface GigabitEthernet 0/0/0
   # 查看 Input/Output packets 计数
   ```

---

## 测试检查清单

### IPv4单播 (10分)
- [ ] 拓扑搭建完成
- [ ] 所有设备IP配置正确
- [ ] 路由表配置正确
- [ ] 可以从真实PC ping通虚拟PC
- [ ] Python脚本成功发送ICMP Echo Request
- [ ] 抓包验证ICMP包格式正确
- [ ] 校验和正确

### IPv4组播 (10分)
- [ ] 组播路由启用
- [ ] PIM配置在所有路由器上
- [ ] RP配置正确
- [ ] IGMP启用并配置静态组
- [ ] Python脚本输出正确的MAC地址
- [ ] 组播包被正确转发
- [ ] 组播统计信息显示接收到的包

### IPv6单播 (10分)
- [ ] IPv6地址配置正确
- [ ] IPv6路由表配置正确
- [ ] 可以ping6通虚拟网络
- [ ] Python脚本成功发送ICMPv6 Echo Request
- [ ] 抓包验证ICMPv6包格式正确
- [ ] 伪首部校验和正确

### IPv6组播 (10分)
- [ ] IPv6组播路由启用
- [ ] PIM IPv6配置在所有路由器上
- [ ] IPv6 RP配置正确
- [ ] MLD启用并配置静态组
- [ ] Python脚本输出正确的IPv6组播MAC地址
- [ ] IPv6组播包被正确转发
- [ ] 组播统计信息显示接收到的包

---

## 提交报告建议

### 必须包含的内容：
1. **拓扑截图**：显示完整的网络拓扑
2. **配置文件**：每个设备的完整配置
3. **测试截图**：
   - Python脚本运行输出
   - ping/ping6测试结果
   - 路由表显示
   - 组播路由表和统计信息
4. **抓包截图**：
   - ICMP/ICMPv6包详细信息
   - 显示类型、代码、校验和
   - 组播包的MAC地址
5. **验证结果**：说明测试是否成功，遇到什么问题以及如何解决

### 评分要点：
- 拓扑搭建正确性（10%）
- 配置完整性和正确性（20%）
- 测试成功与否（40%）
- 抓包分析（20%）
- 问题分析和解决（10%）

---

## 附录：常用命令快速参考

### 路由器基本命令
```bash
# 进入系统视图
system-view

# 配置接口IP
interface GigabitEthernet 0/0/0
ip address 192.168.1.1 24

# 配置IPv6
ipv6
ipv6 address 2001:db8::1/64

# 查看路由表
display ip routing-table
display ipv6 routing-table

# 查看接口状态
display ip interface brief
display ipv6 interface brief

# 保存配置
save

# 查看当前配置
display current-configuration
```

### 组播相关命令
```bash
# IPv4组播
multicast routing-enable
pim sm
igmp enable
igmp static-group 224.1.1.1
display pim routing-table
display igmp group

# IPv6组播
multicast ipv6 routing-enable
pim ipv6 sm
mld enable
mld static-group ff05::1:1
display pim ipv6 routing-table
display mld group
```

### 故障诊断命令
```bash
# ping测试
ping 192.168.1.1
ping ipv6 2001:db8::1

# tracert跟踪路由
tracert 192.168.1.1

# 查看接口详细信息
display interface GigabitEthernet 0/0/0

# 查看ARP表
display arp

# 查看IPv6邻居
display ipv6 neighbors

# 调试命令（慎用）
debugging ip icmp
debugging ipv6 icmp
undo debugging all
```

---

**祝测试顺利！如有问题，请参考本文档的故障排除部分。**
