from protocol import Layer2Frame, Layer3Packet, Layer4Segment
from config import *

class Host:
    def __init__(self, name, ip_address, mac_address, routing_table, arp_table):
        self.name = name  # Store the name (e.g., "Host A")
        self.ip = ip_address
        self.mac = mac_address
        self.routing_table = routing_table
        self.arp_table = arp_table
        self.mac_table = {}
        self.link = None
        
        # L4 State Variables
        self.seq_num = 0 
        self.waiting_for_ack = False
    
    def _route(self, dst_ip: str):
        dst_int = self._ip_to_int(dst_ip)
        for (network, prefix_len, next_hop, interface) in self.routing_table:
            mask    = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF
            net_int = self._ip_to_int(network)
            if (dst_int & mask) == (net_int & mask):
                resolved = dst_ip if next_hop is None else next_hop
                return resolved, interface
        raise Exception(f"{self.name}: Layer 3: No route to {dst_ip}")
    
    def _ip_to_int(self, ip: str) -> int:
        parts = [int(x) for x in ip.split(".")]
        return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

    # ========================================================
    # LAYER 4 - TRANSPORT & APPLICATION (Damien)
    # ========================================================
    
    def send_message(self, message_string, dest_ip, dest_port=80):
        """
        Takes raw application string, segments it if > 500 bytes,
        creates Layer4Segments, and starts the rdt2.2 send loop.
        """
        MAX_PAYLOAD_SIZE = 500
        
        # Log the receipt from the Application Layer
        print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(message_string)}")

        # 1. Segment the data
        segments_data = []
        for i in range(0, len(message_string), MAX_PAYLOAD_SIZE):
            chunk = message_string[i:i + MAX_PAYLOAD_SIZE]
            segments_data.append(chunk)
            
        # 2. rdt2.2 Send Loop
        for chunk in segments_data:
            print(f"{self.name}: Layer 4: Checksum computed")
            
            # Step 2a: Create the Layer4Segment (segment_type 0 = DATA)
            segment = Layer4Segment(src_port=5000, dst_port=dest_port, segment_type=0, seq_num=self.seq_num, data=chunk)
            
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={self.seq_num}) (encapsulation)")
            
            # Step 2b: Send and wait for ACK
            self.waiting_for_ack = True
            while self.waiting_for_ack:
                print(f"{self.name}: Layer 4: Segment sent to Network Layer")
                self.send_to_layer3(segment, dest_ip)
                
            # Step 2c: Flip the alternating bit (0 becomes 1, 1 becomes 0)
            self.seq_num = 1 - self.seq_num

    def receive_from_layer3(self, segment, src_ip):
        """
        Receives Layer4Segment from L3. 
        Verifies checksum. Handles ACKs (if sender) or DATA (if receiver).
        """
        print(f"{self.name}: Layer 4: Segment received from Network Layer")
        
        # 1. Verify Checksum
        if not segment.verify_checksum():
            print(f"{self.name}: Layer 4: Segment discarded due to checksum error")
            # In rdt2.2, if receiver gets corrupt DATA, they resend the previous ACK
            # If sender gets corrupt ACK, they do nothing, and the loop will retransmit
            if segment.type == 0: 
                # Resend previous ACK
                prev_ack_seq = 1 - self.seq_num
                ack_segment = Layer4Segment(src_port=80, dst_port=5000, segment_type=1, seq_num=prev_ack_seq)
                self.send_to_layer3(ack_segment, src_ip)
            return
            
        print(f"{self.name}: Layer 4: Checksum verified")

        # 2. Handle incoming ACK (Sender Side)
        if segment.type == 1: 
            print(f"{self.name}: Layer 4: ACK received: seq={segment.seq_num}")
            if segment.seq_num == self.seq_num:
                self.waiting_for_ack = False # Breaks the while loop!
            else:
                print(f"{self.name}: Layer 4: Incorrect ACK received, retransmitting...")
                
        # 3. Handle incoming DATA (Receiver Side)
        elif segment.type == 0: 
            if segment.seq_num == self.seq_num:
                print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")
                # Advance receiver's expected sequence number
                self.seq_num = 1 - self.seq_num 
            else:
                # Duplicate segment detected (ACK was likely lost)
                pass

            # Always send an ACK for the sequence number we just received
            ack_segment = Layer4Segment(src_port=80, dst_port=5000, segment_type=1, seq_num=segment.seq_num)
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={segment.seq_num})")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")
            
            # Send it down to Layer 3 to travel back to the sender
            self.send_to_layer3(ack_segment, src_ip)

    def send_to_layer3(self, segment, dest_ip):
        """
        Helper to pass L4 segment down to Partner's L3.
        This bridges your Transport layer with your partner's Network layer.
        """
        self.receive_from_layer4(segment, dest_ip)

    # ========================================================
    # LAYER 3 & LAYER 2 - NETWORK & LINK (Jules)
    # ========================================================

    def receive_from_layer4(self, segment, dest_ip):
        src_ip = self.ip
        print(f"{self.name}: Layer 3: Segment received from Transport Layer: "
            f"SRC_IP={src_ip}, DST_IP={dest_ip}, TTL={DEFAULT_TTL}")

        packet = Layer3Packet(src_ip, dest_ip, DEFAULT_TTL, segment)

        print(f"{self.name}: Layer 3: Destination IP read: {dest_ip}")
        print(f"{self.name}: Layer 3: Routing table lookup performed")

        next_hop, interface = self._route(dest_ip)

        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop}")
        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        self.send_to_layer2(packet, next_hop)


    def receive_from_layer2(self, packet):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        if packet.dst_ip == self.ip:
            print(f"{self.name}: Layer 3: Packet identified as local delivery")
            print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")
            self.receive_from_layer3(packet.payload, packet.src_ip)

    def send_to_layer2(self, packet, next_hop_ip):
        dst_mac = self.arp_table.get(next_hop_ip)
        if dst_mac is None:
            raise Exception(f"{self.name}: Layer 2: No ARP entry for {next_hop_ip}")

        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}")

        frame = Layer2Frame(self.mac, dst_mac, packet)
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame sent")

        self.link.receive_frame(frame, self.connected_interface)

    def receive_frame(self, frame):
        interface = "eth0"
        print(f"{self.name}: Layer 2: Frame received")
        if frame.src_mac not in self.mac_table:
            self.mac_table[frame.src_mac] = interface
            print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")

        if frame.dst_mac == self.mac:
            print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
            self.receive_from_layer2(frame.payload)
        else:
            print(f"{self.name}: Layer 2: Frame not for this host — dropping")


class Router:
    def __init__(self, interfaces_config, routing_table):
        self.interfaces    = interfaces_config 
        self.routing_table = routing_table
        self.mac_tables    = {iface: {} for iface in interfaces_config} 

    def receive_frame(self, frame, interface_in):
        print(f"Router R1: Layer 2: Frame received on {interface_in}")
        src_mac = frame.src_mac
        if src_mac not in self.mac_tables[interface_in]:
            self.mac_tables[interface_in][src_mac] = interface_in
            print(f"Router R1: Layer 2: Source MAC learned: {src_mac} on {interface_in}")

        my_mac = self.interfaces[interface_in]["mac"]
        if frame.dst_mac == my_mac:
            print(f"Router R1: Layer 2: Packet delivered to Network Layer")
            self.process_packet(frame.payload)
        else:
            print(f"Router R1: Layer 2: Frame not for this router — dropping")

    def process_packet(self, packet):
        print(f"Router R1: Layer 3: Packet received from Data Link Layer: "
              f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"Router R1: Layer 3: Destination IP read: {packet.dst_ip}")

        old_ttl = packet.ttl
        packet.decrement_ttl()
        print(f"Router R1: Layer 3: TTL decremented: {old_ttl} → {packet.ttl}")

        if packet.is_expired():
            print(f"Router R1: Layer 3: TTL expired — packet dropped")
            return

        print(f"Router R1: Layer 3: Routing table lookup performed")
        next_hop, interface_out = self._route(packet.dst_ip)
        print(f"Router R1: Layer 3: Next-hop IP determined: {next_hop}")
        print(f"Router R1: Layer 3: Outgoing interface selected ({interface_out})")

        self.forward_frame(packet, interface_out, next_hop)

    def forward_frame(self, packet, interface_out, next_hop_ip):
        iface     = self.interfaces[interface_out]
        src_mac   = iface["mac"]
        dst_mac   = iface["arp_table"].get(next_hop_ip)
        if dst_mac is None:
            raise Exception(f"Router R1: Layer 2: No ARP entry for {next_hop_ip}")

        print(f"Router R1: Layer 3: Packet forwarded to Data Link Layer")
        print(f"Router R1: Layer 2: Packet received from Network Layer")
        print(f"Router R1: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}")

        frame = Layer2Frame(src_mac, dst_mac, packet)
        print(f"Router R1: Layer 2: Frame created: SRC_MAC={src_mac}, DST_MAC={dst_mac}")
        print(f"Router R1: Layer 2: Frame forwarded on {interface_out}")

        iface["link"].receive_frame(frame)

    def _route(self, dst_ip: str):
        dst_int = self._ip_to_int(dst_ip)
        for (network, prefix_len, next_hop, interface) in self.routing_table:
            mask    = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF
            net_int = self._ip_to_int(network)
            if (dst_int & mask) == (net_int & mask):
                resolved = dst_ip if next_hop is None else next_hop
                return resolved, interface
        raise Exception(f"Router R1: Layer 3: No route to {dst_ip}")

    def _ip_to_int(self, ip: str) -> int:
        parts = [int(x) for x in ip.split(".")]
        return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]
