# Computer Network Lab 2 - ICMP Unicast/Multicast Implementation

## Task 1: Framework Code - COMPLETED ✓

The framework code in `cast_ping_simple.py` has been completed with the following implementations:

### Implemented Features:

#### 1. IP Address Validation
- **`validate_ip(ip)`**: Validates IP addresses and returns version (4 or 6)
- **`is_unicast_address(ip, ip_version)`**: Validates unicast address ranges
  - IPv4: 1.0.0.0 to 223.255.255.255
  - IPv6: 2000:: to 3FFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF
- **`is_multicast_address(ip, ip_version)`**: Validates multicast address ranges
  - IPv4: 224.0.0.0 to 239.255.255.255
  - IPv6: FF00::/8 prefix

#### 2. MAC Address Conversion
- **`ipv4_multicast_to_mac(ip)`**: Converts IPv4 multicast address to MAC
  - Uses 01:00:5E prefix + lower 23 bits of IP
- **`ipv6_multicast_to_mac(ip)`**: Converts IPv6 multicast address to MAC
  - Uses 33:33 prefix + lower 32 bits of IPv6

#### 3. ICMP/ICMPv6 Implementation
- **`calculate_checksum(data)`**: Calculates Internet checksum (RFC 1071)
- **`send_ipv4_unicast()`**: Sends ICMP Echo Request (Type=8, Code=0)
- **`send_ipv4_multicast()`**: Sends multicast ICMP Echo Request
- **`send_ipv6_unicast()`**: Sends ICMPv6 Echo Request (Type=128, Code=0) with IPv6 pseudo-header
- **`send_ipv6_multicast()`**: Sends multicast ICMPv6 Echo Request with IPv6 pseudo-header

---

## Task 2: Virtual Network Testing - NEXT STEPS

### Prerequisites:
1. **eNSP Software**: Install Huawei eNSP (Enterprise Network Simulation Platform)
2. **Administrator/Root Privileges**: Required to run the Python script (raw sockets)
3. **Dependencies**: Install psutil library
   ```bash
   pip install psutil
   ```

### Testing Steps:

### A. IPv4 Unicast Testing (10 pts)

1. **Build Virtual Network in eNSP**:
   - Create a network topology with multiple routers and PCs
   - Configure routing between subnets
   - Assign IPv4 addresses to all devices
   - Example topology: PC1 <-> Router1 <-> Router2 <-> PC2

2. **Add Cloud Device**:
   - Add a cloud device in eNSP
   - Connect the cloud device to the virtual network
   - Bind the cloud device to your physical network interface
   - This creates a bridge between virtual and real networks

3. **Run IPv4 Unicast Test**:
   ```bash
   # On your real machine (with sudo/admin privileges)
   sudo python3 cast_ping_simple.py <virtual_PC_IPv4_address> -s <your_source_IP> -c 4 -m unicast
   
   # Example:
   sudo python3 cast_ping_simple.py 192.168.1.100 -s 192.168.1.1 -c 4 -m unicast
   ```

4. **Expected Output**:
   ```
   Pinging 192.168.1.100 with 4 packets:
   Sent ICMPv4 Echo Request to 192.168.1.100 (Checksum: xxxx)- Packet 1
   Sent ICMPv4 Echo Request to 192.168.1.100 (Checksum: xxxx)- Packet 2
   ...
   ```

5. **Verify in eNSP**:
   - Use packet capture in eNSP to verify ICMP Echo Request packets are received
   - Check if ICMP Echo Reply packets are sent back
   - Verify routing tables on routers

### B. IPv4 Multicast Testing (10 pts)

1. **Configure Multicast in eNSP**:
   - Enable multicast routing on routers (PIM protocol)
   - Configure IGMP on PCs to join multicast groups
   - Example commands for Huawei routers:
     ```
     [Router] multicast routing-enable
     [Router-GigabitEthernet0/0/0] pim sm
     [Router-GigabitEthernet0/0/0] igmp enable
     ```

2. **Configure Multicast Group**:
   - On PCs in eNSP, join a multicast group (e.g., 224.1.1.1)
   - Configure static multicast routes if needed

3. **Run IPv4 Multicast Test**:
   ```bash
   # Your code acts as the multicast source
   sudo python3 cast_ping_simple.py 224.1.1.1 -s <your_source_IP> -c 4 -m multicast
   
   # Example:
   sudo python3 cast_ping_simple.py 224.1.1.1 -s 192.168.1.1 -c 4 -m multicast
   ```

4. **Expected Output**:
   ```
   Multicast MAC Address: 01:00:5e:01:01:01
   Pinging 224.1.1.1 with 4 packets:
   Sent ICMP Echo Request to 224.1.1.1 (MAC: 01:00:5e:01:01:01 - Checksum: xxxx) - Packet 1
   ...
   ```

5. **Verify Multicast Behavior**:
   - Check multicast forwarding table on routers
   - Verify packets are received by all group members
   - Use packet capture to confirm multicast MAC address
   - Check router statistics for multicast packet counts

### C. IPv6 Unicast Testing (10 pts)

1. **Configure IPv6 in eNSP**:
   - Enable IPv6 on all routers and PCs
   - Assign IPv6 global unicast addresses (2000::/3 range)
   - Configure IPv6 routing (OSPFv3 or static routes)
   - Example IPv6 addresses: 2001:db8:1::1, 2001:db8:2::1

2. **Run IPv6 Unicast Test**:
   ```bash
   sudo python3 cast_ping_simple.py 2001:db8:2::100 -s 2001:db8:1::1 -c 4 -m unicast
   ```

3. **Expected Output**:
   ```
   Pinging 2001:db8:2::100 with 4 packets:
   Sent ICMPv6 Echo Request to 2001:db8:2::100 (Checksum: xxxx)- Packet 1
   ...
   ```

4. **Verify in eNSP**:
   - Use packet capture to verify ICMPv6 packets
   - Check IPv6 routing tables
   - Verify ICMPv6 checksum includes pseudo-header

### D. IPv6 Multicast Testing (10 pts)

1. **Configure IPv6 Multicast**:
   - Enable IPv6 multicast routing on routers
   - **Note**: eNSP PCs don't support MLD (Multicast Listener Discovery)
   - **Workaround**: Configure router interfaces to simulate multicast members
   - Example multicast address: ff02::1:1 (link-local) or ff05::1:1 (site-local)

2. **Configure Router as Multicast Member**:
   ```
   [Router-GigabitEthernet0/0/0] ipv6 address 2001:db8:1::1/64
   [Router-GigabitEthernet0/0/0] ipv6 pim sm
   [Router] ipv6 multicast routing
   ```

3. **Run IPv6 Multicast Test**:
   ```bash
   sudo python3 cast_ping_simple.py ff02::1:1 -s 2001:db8:1::1 -c 4 -m multicast
   ```

4. **Expected Output**:
   ```
   Multicast MAC Address: 33:33:00:01:00:01
   Pinging ff02::1:1 with 4 packets:
   Sent ICMP Echo Request to ff02::1:1 (MAC: 33:33:00:01:00:01 - Checksum: xxxx) - Packet 1
   ...
   ```

5. **Verify IPv6 Multicast**:
   - Check multicast forwarding table
   - Verify multicast MAC address (33:33:XX:XX:XX:XX)
   - Monitor router statistics

---

## Usage Examples

### Basic Commands:

```bash
# IPv4 Unicast
sudo python3 cast_ping_simple.py 192.168.1.100 -m unicast -c 5

# IPv4 Multicast
sudo python3 cast_ping_simple.py 224.1.1.1 -m multicast -c 5

# IPv6 Unicast with source address
sudo python3 cast_ping_simple.py 2001:db8::1 -s 2001:db8::100 -m unicast -c 3

# IPv6 Multicast
sudo python3 cast_ping_simple.py ff02::1 -m multicast -c 3
```

### Error Handling Examples:

```bash
# Invalid IP address
$ python3 cast_ping_simple.py 256.1.2.3
Error: Invalid IP address 256.1.2.3

# Multicast address in unicast mode
$ python3 cast_ping_simple.py 224.1.1.1 -m unicast
Error: 224.1.1.1 is not a valid unicast address
IPv4 unicast addresses should be in range 1.0.0.0 to 223.255.255.255

# Unicast address in multicast mode
$ python3 cast_ping_simple.py 8.8.8.8 -m multicast
Error: 8.8.8.8 is not a valid multicast address
IPv4 multicast addresses should be in range 224.0.0.0 to 239.255.255.255
```

---

## Grading Checklist

### IPv4 Section (25 pts):
- [ ] **IPv4 Address Validation (5 pts)**: Program correctly validates IPv4 addresses
- [ ] **IPv4 Unicast Code (5 pts)**: ICMP Echo Request properly constructed with correct checksum
- [ ] **IPv4 Unicast Test (5 pts)**: Successfully ping virtual PC, receive ICMP Echo Reply
- [ ] **IPv4 Multicast Code (5 pts)**: Multicast MAC conversion and ICMP packets correct
- [ ] **IPv4 Multicast Test (5 pts)**: Packets reach multicast group members, verified in router stats

### IPv6 Section (25 pts):
- [ ] **IPv6 Address Validation (5 pts)**: Program correctly validates IPv6 addresses
- [ ] **IPv6 Unicast Code (5 pts)**: ICMPv6 with pseudo-header checksum correct
- [ ] **IPv6 Unicast Test (5 pts)**: Successfully ping virtual device, receive ICMPv6 Echo Reply
- [ ] **IPv6 Multicast Code (5 pts)**: Multicast MAC conversion and ICMPv6 packets correct
- [ ] **IPv6 Multicast Test (5 pts)**: Packets forwarded correctly, verified via router configuration

---

## Troubleshooting Tips

### Common Issues:

1. **Permission Denied**:
   - Run with `sudo` or administrator privileges
   - Raw sockets require elevated permissions

2. **Network Interface Not Found**:
   - Verify your source IP address is assigned to a network interface
   - Use `ip addr` (Linux) or `ipconfig` (Windows) to check

3. **No Response from Virtual Network**:
   - Verify cloud device is properly configured
   - Check routing tables in eNSP
   - Ensure firewall isn't blocking ICMP/ICMPv6

4. **Multicast Not Working**:
   - Verify multicast routing is enabled on all routers
   - Check IGMP/MLD configuration
   - Verify multicast group membership

5. **Checksum Errors**:
   - The checksums are calculated automatically
   - If packets are dropped, check network configuration, not the code

### Debugging Commands:

```bash
# Check network interfaces
ip addr show          # Linux
ipconfig /all         # Windows

# Test basic connectivity first
ping 192.168.1.100    # IPv4
ping6 2001:db8::1     # IPv6

# Capture packets (in eNSP or Wireshark)
# Verify ICMP type, code, and checksum fields
```

---

## Reference Materials

- **RFC 792**: Internet Control Message Protocol (ICMP)
- **RFC 4443**: Internet Control Message Protocol (ICMPv6)
- **RFC 1071**: Computing the Internet Checksum
- **Lab 9 Courseware**: Cloud device configuration (Part B)
- **Lab 10 Courseware**: 
  - Page 11: IPv4 multicast to MAC conversion
  - Page 30: IPv6 multicast to MAC conversion
  - Practice 2: IPv4 multicast configuration
  - Practice 3: IPv6 multicast configuration

---

## Files in This Repository

- **cast_ping_simple.py**: Complete implementation of ICMP/ICMPv6 unicast and multicast
- **CS305 2025 Fall Lab Assignment 2.pdf**: Original assignment document
- **README.md**: This file - setup and testing guide

---

## Contact

If you encounter issues during testing, refer to:
1. Lab courseware (Lab 9 and Lab 10)
2. eNSP documentation
3. RFC documents for protocol details

Good luck with your testing!
