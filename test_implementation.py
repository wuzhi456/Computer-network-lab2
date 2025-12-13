#!/usr/bin/env python3
"""
Test script to validate the ICMP/ICMPv6 implementation
This script tests all validation and conversion functions
"""

from cast_ping_simple import PingTool
import struct

def test_ipv4_validation():
    """Test IPv4 address validation"""
    print("\n" + "="*60)
    print("Testing IPv4 Address Validation")
    print("="*60)
    
    pt = PingTool()
    
    # Test valid unicast addresses
    unicast_valid = ['8.8.8.8', '1.0.0.0', '223.255.255.255', '192.168.1.1']
    print("\nValid IPv4 Unicast Addresses:")
    for ip in unicast_valid:
        version = pt.validate_ip(ip)
        is_unicast = pt.is_unicast_address(ip, version)
        print(f"  {ip:20} - Version: {version}, Is Unicast: {is_unicast}")
        assert version == 4, f"{ip} should be IPv4"
        assert is_unicast, f"{ip} should be unicast"
    
    # Test valid multicast addresses
    multicast_valid = ['224.0.0.0', '224.1.1.1', '239.255.255.255']
    print("\nValid IPv4 Multicast Addresses:")
    for ip in multicast_valid:
        version = pt.validate_ip(ip)
        is_multicast = pt.is_multicast_address(ip, version)
        print(f"  {ip:20} - Version: {version}, Is Multicast: {is_multicast}")
        assert version == 4, f"{ip} should be IPv4"
        assert is_multicast, f"{ip} should be multicast"
    
    # Test invalid addresses
    invalid = ['256.1.1.1', '1.2.3', '1.2.3.4.5']
    print("\nInvalid IPv4 Addresses:")
    for ip in invalid:
        version = pt.validate_ip(ip)
        print(f"  {ip:20} - Version: {version}")
        assert version is None, f"{ip} should be invalid"
    
    print("\n✓ IPv4 validation tests passed!")

def test_ipv6_validation():
    """Test IPv6 address validation"""
    print("\n" + "="*60)
    print("Testing IPv6 Address Validation")
    print("="*60)
    
    pt = PingTool()
    
    # Test valid unicast addresses
    unicast_valid = ['2001:db8::1', '2000::', '3fff:ffff:ffff:ffff:ffff:ffff:ffff:ffff']
    print("\nValid IPv6 Unicast Addresses:")
    for ip in unicast_valid:
        version = pt.validate_ip(ip)
        is_unicast = pt.is_unicast_address(ip, version)
        print(f"  {ip:45} - Version: {version}, Is Unicast: {is_unicast}")
        assert version == 6, f"{ip} should be IPv6"
        assert is_unicast, f"{ip} should be unicast"
    
    # Test valid multicast addresses
    multicast_valid = ['ff00::', 'ff02::1', 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff']
    print("\nValid IPv6 Multicast Addresses:")
    for ip in multicast_valid:
        version = pt.validate_ip(ip)
        is_multicast = pt.is_multicast_address(ip, version)
        print(f"  {ip:45} - Version: {version}, Is Multicast: {is_multicast}")
        assert version == 6, f"{ip} should be IPv6"
        assert is_multicast, f"{ip} should be multicast"
    
    # Test link-local and loopback (not in unicast range per requirements)
    other_v6 = ['fe80::1', '::1', 'fc00::1']
    print("\nOther IPv6 Addresses (link-local, loopback, ULA):")
    for ip in other_v6:
        version = pt.validate_ip(ip)
        is_unicast = pt.is_unicast_address(ip, version)
        is_multicast = pt.is_multicast_address(ip, version)
        print(f"  {ip:45} - Valid IPv6: {version==6}, Unicast: {is_unicast}, Multicast: {is_multicast}")
        assert version == 6, f"{ip} should be valid IPv6"
    
    print("\n✓ IPv6 validation tests passed!")

def test_ipv4_mac_conversion():
    """Test IPv4 multicast to MAC conversion"""
    print("\n" + "="*60)
    print("Testing IPv4 Multicast to MAC Conversion")
    print("="*60)
    
    pt = PingTool()
    
    test_cases = [
        ('224.0.0.1', '01:00:5e:00:00:01'),
        ('224.1.1.1', '01:00:5e:01:01:01'),
        ('239.255.1.1', '01:00:5e:7f:01:01'),
        ('225.128.64.32', '01:00:5e:00:40:20'),
        ('224.0.1.1', '01:00:5e:00:01:01'),
    ]
    
    print("\nIPv4 Multicast -> MAC Conversions:")
    for ip, expected_mac in test_cases:
        mac = pt.ipv4_multicast_to_mac(ip)
        print(f"  {ip:20} -> {mac:20} (Expected: {expected_mac})")
        assert mac == expected_mac, f"MAC mismatch for {ip}: got {mac}, expected {expected_mac}"
    
    # Test error handling
    print("\nTesting error handling for non-multicast addresses:")
    try:
        pt.ipv4_multicast_to_mac('8.8.8.8')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"  ✓ Correctly raised error: {e}")
    
    print("\n✓ IPv4 MAC conversion tests passed!")

def test_ipv6_mac_conversion():
    """Test IPv6 multicast to MAC conversion"""
    print("\n" + "="*60)
    print("Testing IPv6 Multicast to MAC Conversion")
    print("="*60)
    
    pt = PingTool()
    
    test_cases = [
        ('ff02::1', '33:33:00:00:00:01'),
        ('ff02::2', '33:33:00:00:00:02'),
        ('ff05::1:3', '33:33:00:01:00:03'),
        ('ff02::1:ff00:1', '33:33:ff:00:00:01'),
        ('ff02::1:ff00:0', '33:33:ff:00:00:00'),
    ]
    
    print("\nIPv6 Multicast -> MAC Conversions:")
    for ip, expected_mac in test_cases:
        mac = pt.ipv6_multicast_to_mac(ip)
        print(f"  {ip:30} -> {mac:20} (Expected: {expected_mac})")
        assert mac == expected_mac, f"MAC mismatch for {ip}: got {mac}, expected {expected_mac}"
    
    # Test error handling
    print("\nTesting error handling for non-multicast addresses:")
    try:
        pt.ipv6_multicast_to_mac('2001:db8::1')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"  ✓ Correctly raised error: {e}")
    
    print("\n✓ IPv6 MAC conversion tests passed!")

def test_checksum():
    """Test checksum calculation"""
    print("\n" + "="*60)
    print("Testing Checksum Calculation")
    print("="*60)
    
    pt = PingTool()
    
    # Test case 1: ICMP Echo Request
    print("\nTest 1: ICMP Echo Request")
    icmp_header = struct.pack('!BBHHH', 8, 0, 0, 1234, 0)
    data = b'PingData'
    checksum = pt.calculate_checksum(icmp_header + data)
    print(f"  Checksum: 0x{checksum:04x}")
    
    # Verify: checksum of packet with embedded checksum should be 0
    icmp_with_checksum = struct.pack('!BBHHH', 8, 0, checksum, 1234, 0)
    verify = pt.calculate_checksum(icmp_with_checksum + data)
    print(f"  Verification: 0x{verify:04x} (should be 0x0000)")
    assert verify == 0, f"Checksum verification failed: {verify:04x}"
    
    # Test case 2: Known test vector from RFC 1071
    print("\nTest 2: RFC 1071 Example")
    test_data = b'\x00\x01\xf2\x03\xf4\xf5\xf6\xf7'
    checksum = pt.calculate_checksum(test_data)
    print(f"  Input: {test_data.hex()}")
    print(f"  Checksum: 0x{checksum:04x}")
    # The correct checksum for this data is 0x220d
    expected = 0x220d
    assert checksum == expected, f"Checksum mismatch: got 0x{checksum:04x}, expected 0x{expected:04x}"
    
    print("\n✓ Checksum tests passed!")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ICMP/ICMPv6 Implementation Validation Test Suite")
    print("="*60)
    
    try:
        test_ipv4_validation()
        test_ipv6_validation()
        test_ipv4_mac_conversion()
        test_ipv6_mac_conversion()
        test_checksum()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        print("\nThe implementation is correct and ready for testing with eNSP.")
        print("Refer to README.md for instructions on Task 2 (Virtual Network Testing).")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
