import hashlib

# Protocol Constants as defined in the project brief
L2_TYPE_IPV4 = 0x0800
L3_PROTOCOL_UDP = 17
L4_TYPE_DATA = 0
L4_TYPE_ACK = 1

class Layer4Segment:
    """
    Transport Layer (UDP-like Segment with ACK support - rdt2.2)
    Responsible for port-based delivery, error detection (checksum), and segmentation logic.
    """
    def __init__(self, src_port, dst_port, segment_type, seq_num, data=""):
        self.src_port = src_port      # 2 bytes
        self.dst_port = dst_port      # 2 bytes
        self.type = segment_type      # 1 byte (0 = DATA, 1 = ACK)
        self.seq_num = seq_num        # 1 byte (0 or 1)
        self.data = data              # variable length application message (empty for ACK)
        
        # Calculate Length: 10 bytes of header + length of encoded data
        self.length = 10 + len(str(self.data).encode('utf-8')) # 2 bytes
        
        # 2 bytes for checksum, initialized to 0 before computation
        self.checksum = 0             
        
        # Automatically compute the checksum upon creation if it is a DATA segment
        if self.type == L4_TYPE_DATA:
            self.checksum = self.compute_checksum()

    def compute_checksum(self):
        """
        Computes a simple deterministic checksum for the segment.
        Combines header fields and data, creating an MD5 hash, 
        and returning an integer representation truncated to fit logical bounds.
        """
        segment_content = f"{self.src_port}{self.dst_port}{self.length}{self.type}{self.seq_num}{self.data}"
        hash_object = hashlib.md5(segment_content.encode('utf-8'))
        # Return a simple integer hash representing a 2-byte checksum
        return int(hash_object.hexdigest(), 16) % 65536 

    def verify_checksum(self):
        """
        Verifies if the stored checksum matches the currently computed checksum.
        Returns True if valid, False if corrupted.
        """
        return self.checksum == self.compute_checksum()

    def is_ack(self):
        """Helper to quickly identify ACK segments."""
        return self.type == L4_TYPE_ACK

    def __str__(self):
        """String representation required for the output logs."""
        type_str = "DATA" if self.type == L4_TYPE_DATA else "ACK"
        return f"({type_str}, seq={self.seq_num})"


class Layer3Packet:
    """
    Network Layer (IP-like Packet)
    Responsible for logical addressing and TTL handling.
    """
    def __init__(self, src_ip, dst_ip, ttl, payload):
        self.src_ip = src_ip          # 4 bytes
        self.dst_ip = dst_ip          # 4 bytes
        self.ttl = ttl                # 1 byte (Decremented at each router)
        self.protocol = L3_PROTOCOL_UDP  # 1 byte (17 indicates UDP payload)
        self.payload = payload        # variable (Layer 4 Segment)
        
        # Calculate Total Length: 12 bytes of header + payload length
        # Ensure payload has a 'length' attribute (which Layer4Segment does)
        payload_len = getattr(payload, 'length', 0)
        self.total_length = 12 + payload_len # 2 bytes

    def decrement_ttl(self):
        """Decrements the Time-To-Live value."""
        self.ttl -= 1
        
    def is_expired(self):
        """Checks if the packet should be dropped."""
        return self.ttl <= 0

    def __str__(self):
        """String representation required for the output logs."""
        return f"SRC_IP={self.src_ip}, DST_IP={self.dst_ip}, TTL={self.ttl}"


class Layer2Frame:
    """
    Data Link Layer (Ethernet-like Frame)
    Responsible for MAC addressing and local delivery.
    """
    def __init__(self, src_mac, dst_mac, payload):
        self.src_mac = src_mac        # 6 bytes
        self.dst_mac = dst_mac        # 6 bytes
        self.type = L2_TYPE_IPV4      # 2 bytes (0x0800 indicates IPv4 payload)
        self.payload = payload        # variable (Layer 3 Packet)

    def __str__(self):
        """String representation required for the output logs."""
        return f"SRC_MAC={self.src_mac}, DST_MAC={self.dst_mac}"
