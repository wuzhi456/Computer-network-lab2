import socket
import struct
import argparse
import sys
import psutil
import time
import ipaddress

class PingTool:
    # Define constants
    IPv4 = 4
    IPv6 = 6

    def validate_ip(self, ip):
        """
        Validate IP address and return version
        
        Args:
            ip (str): IP address to validate
            
        Returns:
            int: IP version (4 or 6) or None if invalid
        """
        # Try IPv4 validation
        try:
            socket.inet_pton(socket.AF_INET, ip)
            return self.IPv4
        except socket.error:
            pass
        
        # Try IPv6 validation
        try:
            socket.inet_pton(socket.AF_INET6, ip)
            return self.IPv6
        except socket.error:
            pass
        
        return None


    def is_unicast_address(self, ip, ip_version):
        """
        Check if the IP address is an unicast address

        Args:
            ip (str): IP address to check
            ip_version (int): IP version (4 or 6)

        Returns:
            bool: True if it's an unicast address, False otherwise
        """
        if ip_version == self.IPv4:
            # IPv4 unicast range: 1.0.0.0 to 223.255.255.255
            octets = list(map(int, ip.split('.')))
            first_octet = octets[0]
            return 1 <= first_octet <= 223
        else:  # IPv6
            # IPv6 global unicast range: 2000:: to 3FFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF
            # Get the first hextet
            addr = ipaddress.IPv6Address(ip)
            addr_int = int(addr)
            # 2000::/3 range
            start = int(ipaddress.IPv6Address('2000::'))
            end = int(ipaddress.IPv6Address('3fff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'))
            return start <= addr_int <= end


    def is_multicast_address(self, ip, ip_version):
        """
        Check if the IP address is a multicast address
        
        Args:
            ip (str): IP address to check
            ip_version (int): IP version (4 or 6)
            
        Returns:
            bool: True if it's a multicast address, False otherwise
        """
        if ip_version == self.IPv4:
            # IPv4 multicast range: 224.0.0.0 to 239.255.255.255
            octets = list(map(int, ip.split('.')))
            first_octet = octets[0]
            return 224 <= first_octet <= 239
        else:  # IPv6
            # IPv6 multicast addresses start with FF00::/8 (first byte is 0xFF)
            addr = ipaddress.IPv6Address(ip)
            # Check if first byte is 0xFF
            return addr.packed[0] == 0xFF



    def ipv4_multicast_to_mac(self, ip):
        """
        Convert IPv4 multicast address to multicast MAC address
        
        Args:
            ip (str): IPv4 multicast address
            
        Returns:
            str: Multicast MAC address
            
        Raises:
            ValueError: If the IP is not a valid IPv4 multicast address
        """
        # Validate that it's a multicast address
        if not self.is_multicast_address(ip, self.IPv4):
            raise ValueError(f"{ip} is not a valid IPv4 multicast address")
        
        # IPv4 multicast MAC address conversion:
        # The MAC address starts with 01:00:5E
        # The lower 23 bits of the IP address are mapped to the lower 23 bits of the MAC address
        octets = list(map(int, ip.split('.')))
        
        # Get the lower 23 bits from the IP address
        # Second octet: only lower 7 bits (mask with 0x7F)
        # Third and fourth octets: all 8 bits
        mac_part1 = octets[1] & 0x7F  # Lower 7 bits of second octet
        mac_part2 = octets[2]          # Third octet
        mac_part3 = octets[3]          # Fourth octet
        
        # Format as MAC address
        mac = f"01:00:5e:{mac_part1:02x}:{mac_part2:02x}:{mac_part3:02x}"
        return mac


    def ipv6_multicast_to_mac(self, ip):
        """
        Convert IPv6 multicast address to multicast MAC address
        
        Args:
            ip (str): IPv6 multicast address
            
        Returns:
            str: Multicast MAC address
            
        Raises:
            ValueError: If the IP is not a valid IPv6 multicast address
        """
        # Validate that it's a multicast address
        if not self.is_multicast_address(ip, self.IPv6):
            raise ValueError(f"{ip} is not a valid IPv6 multicast address")
        
        # IPv6 multicast MAC address conversion:
        # The MAC address starts with 33:33
        # The lower 32 bits of the IPv6 address are mapped to the lower 32 bits of the MAC address
        addr = ipaddress.IPv6Address(ip)
        addr_bytes = addr.packed
        
        # Get the last 4 bytes (lower 32 bits) of the IPv6 address
        last_4_bytes = addr_bytes[-4:]
        
        # Format as MAC address: 33:33:XX:XX:XX:XX
        mac = f"33:33:{last_4_bytes[0]:02x}:{last_4_bytes[1]:02x}:{last_4_bytes[2]:02x}:{last_4_bytes[3]:02x}"
        return mac

    def get_interface_by_ip(self, target_ip):
        """
        Find network interface by IP address using psutil
        
        Args:
            target_ip (str): Target IP address
            
        Returns:
            str: Interface name or None if not found
        """
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and addr.address == target_ip:
                    return iface
        return None

    def create_raw_socket(self, ip_version, is_multicast=False):
        """
        Create raw socket
        
        Args:
            ip_version (int): IP version (4 or 6)
            is_multicast (bool): Whether it's for multicast communication
            
        Returns:
            socket: Raw socket object
        """
        try:
            if ip_version == self.IPv6:
                # Create IPv6 raw socket
                sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)
                # Allow IPv6 socket to receive its own multicast packets
                if is_multicast:
                    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, 1)
            else:
                # Create IPv4 raw socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                # Allow IPv4 socket to send multicast packets
                if is_multicast:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            return sock
        except PermissionError:
            print("Error: Administrator privileges required to create raw socket")
            sys.exit(1)
        except Exception as e:
            print(f"Error creating socket: {e}")
            sys.exit(1)

    def send_ipv4_unicast(self, src_addr, dst_addr, count):
        """
        Send IPv4 unicast ICMP echo request packets
        
        Args:
            src_addr (str): Source IP address
            dst_addr (str): Destination IP address
            count (int): Number of packets to send
        """
        try:
            sock = self.create_raw_socket(self.IPv4)
            if src_addr:
                sock.bind((src_addr, 0))
            for i in range(count):
                # Construct ICMP Echo Request packet
                # According to RFC 792, ICMP Echo Request:
                # Type = 8, Code = 0
                icmp_type = 8
                icmp_code = 0
                icmp_checksum = 0  # Will be calculated
                icmp_id = 1234  # Arbitrary ID
                # NOTE: please do not modify the value of 'icmp_seq',for the values of other fields, please specify them according to the Protocol.
                icmp_seq = i
                
                # Construct ICMP header (without checksum)
                # Format: Type (1 byte) + Code (1 byte) + Checksum (2 bytes) + ID (2 bytes) + Sequence (2 bytes)
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                
                # Add some data payload
                data = b'PingData'
                
                # Calculate checksum
                icmp_checksum = self.calculate_checksum(icmp_header + data)
                
                # Reconstruct ICMP header with checksum
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                
                # Send packet
                packet = icmp_header + data
                sock.sendto(packet, (dst_addr, 0))

                # Note: please do not remove print code, as it is used to validate the checksum of ICMP you calculated
                print(f"Sent ICMPv4 Echo Request to {dst_addr} (Checksum: {icmp_checksum:04x})- Packet {i + 1}")
                time.sleep(1)

            sock.close()
        except Exception as e:
            print(f"Error sending IPv4 unicast packets: {e}")
            import traceback
            traceback.print_exc()

    def send_ipv6_unicast(self, src_addr, dst_addr, count):
        """
        Send IPv6 unicast ICMPv6 echo request packets
        
        Args:
            src_addr (str): Source IP address
            dst_addr (str): Destination IP address
            count (int): Number of packets to send
        """
        try:
            sock = self.create_raw_socket(self.IPv6)
            if src_addr:
                sock.bind((src_addr, 0))
            
            for i in range(count):
                # Construct ICMPv6 Echo Request packet
                # According to RFC 4443, ICMPv6 Echo Request:
                # Type = 128, Code = 0
                icmp_type = 128
                icmp_code = 0
                icmp_checksum = 0  # Will be calculated
                icmp_id = 1234  # Arbitrary ID
                # NOTE: please do not modify the value of 'icmp_seq',for the values of other fields, please specify them according to the Protocol.
                icmp_seq = i

                # Construct ICMPv6 header (without checksum)
                # Format: Type (1 byte) + Code (1 byte) + Checksum (2 bytes) + ID (2 bytes) + Sequence (2 bytes)
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                
                # Add some data payload
                data = b'PingData'

                # For ICMPv6, checksum calculation includes IPv6 pseudo header
                src_ip = src_addr if src_addr else '::'
                
                # ICMPv6 packet length
                icmp_length = len(icmp_header) + len(data)
                
                # Create IPv6 pseudo header
                pseudo_header = self.create_ipv6_pseudo_header(src_ip, dst_addr, icmp_length)

                # Calculate checksum
                icmp_checksum = self.calculate_checksum(pseudo_header + icmp_header + data)

                # Reconstruct ICMP header with checksum
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                
                # Send packet
                packet = icmp_header + data
                sock.sendto(packet, (dst_addr, 0))

                # Note: please do not remove print code, as it is used to validate the checksum of ICMP you calculated
                print(f"Sent ICMPv6 Echo Request to {dst_addr} (Checksum: {icmp_checksum:04x})- Packet {i + 1}")
                time.sleep(1)

            sock.close()
        except Exception as e:
            print(f"Error sending IPv6 unicast packets: {e}")
            import traceback
            traceback.print_exc()

    def send_ipv4_multicast(self, src_addr, dst_addr, count):
        """
        Send IPv4 multicast ICMP echo request packets
        
        Args:
            src_addr (str): Source IP address
            dst_addr (str): Destination multicast IP address
            count (int): Number of packets to send
        """
        try:
            # Get multicast MAC address,and print it!
            # Note: You may don't need use the mac address to send multicast packets by socket,
            # but please do not remove print code, as it is used to validate the multicast MAC address you implemented
            multicast_mac = self.ipv4_multicast_to_mac(dst_addr)
            print(f"Multicast MAC Address: {multicast_mac}")
            
            # Get network interface
            iface = self.get_interface_by_ip(src_addr)
            if not iface:
                print(f"Warning: Could not find interface for IP {src_addr}")
            
            sock = self.create_raw_socket(self.IPv4, is_multicast=True)
            if src_addr:
                sock.bind((src_addr, 0))
            
            for i in range(count):
                # Construct ICMP Echo Request packet
                # According to RFC 792, ICMP Echo Request:
                # Type = 8, Code = 0
                icmp_type = 8
                icmp_code = 0
                icmp_checksum = 0  # Will be calculated
                icmp_id = 1234  # Arbitrary ID
                # NOTE: please do not modify the value of 'icmp_seq',for the values of other fields, please specify them according to the Protocol.
                icmp_seq = i

                # Construct ICMP header (without checksum)
                # Format: Type (1 byte) + Code (1 byte) + Checksum (2 bytes) + ID (2 bytes) + Sequence (2 bytes)
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                
                # Add some data payload
                data = b'PingData'
                
                # Calculate checksum
                icmp_checksum = self.calculate_checksum(icmp_header + data)

                # Reconstruct ICMP header with checksum
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                
                # Send packet
                packet = icmp_header + data
                sock.sendto(packet, (dst_addr, 0))

                # Note: please do not remove print code, as it is used to validate the checksum of ICMP you calculated
                print(f"Sent ICMP Echo Request to {dst_addr} (MAC: {multicast_mac} - Checksum: {icmp_checksum:04x}) - Packet {i+1}")
                time.sleep(1)
            sock.close()
        except Exception as e:
            print(f"Error sending IPv4 multicast packets: {e}")
            import traceback
            traceback.print_exc()

    def send_ipv6_multicast(self, src_addr, dst_addr, count):
        """
        Send IPv6 multicast ICMPv6 echo request packets
        
        Args:
            src_addr (str): Source IP address
            dst_addr (str): Destination multicast IP address
            count (int): Number of packets to send
        """
        try:
            # Get multicast MAC address,and print it!
            # Note: You may don't need use the mac address to send multicast packets by socket,
            # but please do not remove print code, as it is used to validate the multicast MAC address you implemented
            multicast_mac = self.ipv6_multicast_to_mac(dst_addr)
            print(f"Multicast MAC Address: {multicast_mac}")

            sock = self.create_raw_socket(self.IPv6, is_multicast=True)
            if src_addr:
                sock.bind((src_addr, 0))
            
            # Set IPv6 multicast hop limit
            try:
                sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 32)
            except Exception as e:
                print(f"Warning: Failed to set IPV6_MULTICAST_HOPS: {e}")
                # Try alternative method
                try:
                    sock.setsockopt(socket.SOL_IPV6, socket.IPV6_MULTICAST_HOPS, struct.pack('i', 32))
                except Exception as e2:
                    print(f"Warning: Alternative method also failed: {e2}")
            
            for i in range(count):
                # Construct ICMPv6 Echo Request packet
                # According to RFC 4443, ICMPv6 Echo Request:
                # Type = 128, Code = 0
                icmp_type = 128
                icmp_code = 0
                icmp_checksum = 0  # Will be calculated
                icmp_id = 1234  # Arbitrary ID
                # NOTE: please do not modify the value of 'icmp_seq',for the values of other fields, please specify them according to the Protocol.
                icmp_seq = i

                # Construct ICMPv6 header (without checksum)
                # Format: Type (1 byte) + Code (1 byte) + Checksum (2 bytes) + ID (2 bytes) + Sequence (2 bytes)
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                
                # Add some data payload
                data = b'PingData'

                # For ICMPv6, checksum calculation includes IPv6 pseudo header
                src_ip = src_addr if src_addr else '::'
                
                # ICMPv6 packet length
                icmp_length = len(icmp_header) + len(data)
                
                # Create IPv6 pseudo header
                pseudo_header = self.create_ipv6_pseudo_header(src_ip, dst_addr, icmp_length)

                # Calculate checksum
                icmp_checksum = self.calculate_checksum(pseudo_header + icmp_header + data)

                # Reconstruct ICMP header with checksum
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                
                # Send packet
                packet = icmp_header + data
                sock.sendto(packet, (dst_addr, 0))

                # Note: please do not remove print code, as it is used to validate the checksum of ICMP you calculated
                print(
                    f"Sent ICMP Echo Request to {dst_addr} (MAC: {multicast_mac} - Checksum: {icmp_checksum:04x}) - Packet {i + 1}")
                time.sleep(1)

            sock.close()
        except Exception as e:
            print(f"Error sending IPv6 multicast packets: {e}")
            import traceback
            traceback.print_exc()

    def calculate_checksum(self, data):
        """
        Calculate checksum of ICMP packet
        
        Args:
            data (bytes): Data（ICMP_HEADER+ICMP_DATA  OR  pseudo_header+ICMPv6_Header+ICMPv6_DATA） to calculate checksum for
            
        Returns:
            int: Calculated checksum
        """
        # Calculate Internet checksum (RFC 1071)
        # Sum all 16-bit words
        checksum = 0
        
        # Handle data in 16-bit chunks
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                # Combine two bytes into a 16-bit word (big-endian)
                word = (data[i] << 8) + data[i + 1]
            else:
                # If odd number of bytes, pad with zero
                word = data[i] << 8
            checksum += word
        
        # Add carry bits and fold to 16 bits
        while checksum >> 16:
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        
        # One's complement
        checksum = ~checksum & 0xFFFF
        
        return checksum

    def create_ipv6_pseudo_header(self, src_addr, dst_addr, upper_layer_packet_length, next_header=58):
        """
        Create IPv6 pseudo header for checksum calculation
        
        Args:
            src_addr (str): Source IPv6 address
            dst_addr (str): Destination IPv6 address
            upper_layer_packet_length (int): Length of upper layer packet (ICMPv6)
            next_header (int): Next header value (58 for ICMPv6)
            
        Returns:
            bytes: IPv6 pseudo header
        """
        # Convert addresses to binary
        src_bytes = ipaddress.IPv6Address(src_addr).packed
        dst_bytes = ipaddress.IPv6Address(dst_addr).packed
        
        # Construct pseudo header:
        # Source Address (16 bytes) + Destination Address (16 bytes) + 
        # Upper-Layer Packet Length (4 bytes) + Zero (3 bytes) + Next Header (1 byte)
        pseudo_header = src_bytes + dst_bytes + struct.pack('!I', upper_layer_packet_length) + struct.pack('!BBB', 0, 0, next_header)
        
        return pseudo_header



    def run(self, src_addr, dst_addr, count, mode):
        """
        Main run function
        
        Args:
            src_addr (str): Source IP address
            dst_addr (str): Destination IP address
            count (int): Number of packets to send
            mode (str): Send mode (unicast or multicast)
        """
        # Validate destination address
        ip_version = self.validate_ip(dst_addr)
        if ip_version is None:
            print(f"Error: Invalid IP address {dst_addr}")
            return

        # Validate source address (if provided)
        if src_addr:
            src_version = self.validate_ip(src_addr)
            if src_version is None:
                print(f"Error: Invalid source IP address {src_addr}")
                return
            if src_version != ip_version:
                print("Error: Source and destination IP versions must match")
                return

        # If multicast mode, validate multicast address
        if mode == "multicast":
            if not self.is_multicast_address(dst_addr, ip_version):
                print(f"Error: {dst_addr} is not a valid multicast address")
                if ip_version == self.IPv4:
                    print("IPv4 multicast addresses should be in range 224.0.0.0 to 239.255.255.255")
                else:
                    print("IPv6 multicast addresses should start with FF00::/8 prefix")
                return
        # If unicast mode, validate unicast address
        if mode == "unicast":
            if not self.is_unicast_address(dst_addr, ip_version):
                print(f"Error: {dst_addr} is not a valid unicast address")
                if ip_version == self.IPv4:
                    print("IPv4 unicast addresses should be in range 1.0.0.0 to 223.255.255.255")
                else:
                    print("IPv6 unicast addresses should within the range from 2000:: to 3FFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF")
                return

        print(f"Pinging {dst_addr} with {count} packets:")

        # Send packets based on address type and mode
        if ip_version == self.IPv4:
            if mode == "unicast":
                self.send_ipv4_unicast(src_addr, dst_addr, count)
            else:  # multicast
                self.send_ipv4_multicast(src_addr, dst_addr, count)
        else:  # IPv6
            if mode == "unicast":
                self.send_ipv6_unicast(src_addr, dst_addr, count)
            else:  # multicast
                self.send_ipv6_multicast(src_addr, dst_addr, count)


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description="Python Ping Tool with ICMP Multicast Support")
    parser.add_argument("destination", help="Destination IP address")
    parser.add_argument("-s", "--source", help="Source IP address", default="")
    parser.add_argument("-c", "--count", type=int, help="Number of packets to send", default=4)
    parser.add_argument("-m", "--mode", choices=["unicast", "multicast"],
                        help="Send mode (unicast or multicast)", default="unicast")

    args = parser.parse_args()

    # Create PingTool instance
    ping_tool = PingTool()
    # Run
    ping_tool.run(args.source, args.destination, args.count, args.mode)


if __name__ == "__main__":
    main()