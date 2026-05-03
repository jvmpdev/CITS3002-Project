from config import ETHER_TYPE_IPV4, PROTOCOL_UDP

class Layer4Segment:
    """
    Transport Layer (UDP-like Segment with ACK support)
    Header Size: 10 bytes
    """
    def __init__(self, src_port, dst_port, segment_type, seq_num, data=""):
        self.src_port = src_port      # 2 bytes[cite: 1]
        self.dst_port = dst_port      # 2 bytes[cite: 1]
        self.type = segment_type      # 1 byte (0 = DATA, 1 = ACK)[cite: 1]
        self.seq_num = seq_num        # 1 byte[cite: 1]
        self.data = data              # variable (application message)[cite: 1]
        self.checksum = 0             # 2 bytes (computed later)[cite: 1]
        
        # Calculate simulated length: 10 byte header + data length[cite: 1]
        self.length = 10 + (len(data.encode('utf-8')) if data else 0) # 2 bytes[cite: 1]

    def set_checksum(self, checksum_value):
        self.checksum = checksum_value

    def __str__(self):
        # Useful for generating the required console logs
        type_str = "DATA" if self.type == 0 else "ACK"
        return f"({type_str}, seq={self.seq_num})"


class Layer3Packet:
    """
    Network Layer (IP-like Packet)
    Header Size: 12 bytes
    """
    def __init__(self, src_ip, dst_ip, ttl, payload):
        self.src_ip = src_ip          # 4 bytes[cite: 1]
        self.dst_ip = dst_ip          # 4 bytes[cite: 1]
        self.ttl = ttl                # 1 byte[cite: 1]
        self.protocol = PROTOCOL_UDP  # 1 byte (17 indicates UDP)[cite: 1]
        self.payload = payload        # variable (Layer 4 Segment)[cite: 1]
        
        # Calculate total length: 12 byte header + payload length[cite: 1]
        self.total_length = 12 + payload.length # 2 bytes[cite: 1]

    def decrement_ttl(self):
        self.ttl -= 1

    def __str__(self):
        return f"SRC_IP={self.src_ip}, DST_IP={self.dst_ip}, TTL={self.ttl}"


class Layer2Frame:
    """
    Data Link Layer (Ethernet-like Frame)
    Header Size: 14 bytes
    """
    def __init__(self, src_mac, dst_mac, payload):
        self.src_mac = src_mac        # 6 bytes[cite: 1]
        self.dst_mac = dst_mac        # 6 bytes[cite: 1]
        self.type = ETHER_TYPE_IPV4   # 2 bytes (0x0800 indicates IPv4)[cite: 1]
        self.payload = payload        # variable (Layer 3 Packet)[cite: 1]

    def __str__(self):
        return f"SRC_MAC={self.src_mac}, DST_MAC={self.dst_mac}"
