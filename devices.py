from protocol import Layer2Frame, Layer3Packet, Layer4Segment
from config import *

class Host:
    def __init__(self, ip_address, mac_address, routing_table, arp_table):
        self.ip = ip_address
        self.mac = mac_address
        self.routing_table = routing_table
        self.arp_table = arp_table
        
        # L4 State Variables (STUDENT 1 / YOU)
        self.seq_num = 0  # For rdt2.2 alternating bit protocol
        self.waiting_for_ack = False

    # ========================================================
    # LAYER 4 - TRANSPORT & APPLICATION (STUDENT 1 / YOU)
    # ========================================================
    
    def send_message(self, message_string, dest_ip, dest_port=80):
        """
        Takes raw application string, segments it if > 500 bytes,
        creates Layer4Segments, and starts the rdt2.2 send loop.
        Calls self.send_to_layer3() for each segment.
        """
        pass 

    def receive_from_layer3(self, segment, src_ip):
        """
        Receives Layer4Segment from L3. 
        Verifies checksum. Handles ACKs (if sender) or DATA (if receiver).
        If valid DATA, prints message and sends ACK back via self.send_to_layer3().
        """
        pass

    def send_to_layer3(self, segment, dest_ip):
        """Helper to pass L4 segment down to Partner's L3."""
        pass


    # ========================================================
    # LAYER 3 & LAYER 2 - NETWORK & LINK (STUDENT 2 / PARTNER)
    # ========================================================

    def receive_from_layer4(self, segment, dest_ip):
        """
        Encapsulates segment into Layer3Packet.
        Performs routing table lookup to find next-hop IP.
        Calls self.send_to_layer2().
        """
        pass

    def receive_from_layer2(self, packet):
        """
        Checks if packet destination IP matches host IP.
        If yes, decapsulates and passes to self.receive_from_layer3().
        """
        pass

    def send_to_layer2(self, packet, next_hop_ip):
        """
        Looks up MAC address for next_hop_ip in ARP table.
        Encapsulates packet into Layer2Frame.
        Simulates sending over the wire.
        """
        pass

    def receive_frame(self, frame):
        """
        Physical entry point. Learns Source MAC.
        If Dest MAC matches host MAC, passes payload to self.receive_from_layer2().
        """
        pass


class Router:
    """
    STUDENT 2 / PARTNER ONLY
    Routers do not implement Layer 4, so this class is entirely Partner territory.
    """
    def __init__(self, interfaces_config):
        # Setup interfaces, IPs, MACs, and Routing/ARP tables
        pass

    def receive_frame(self, frame, interface_in):
        """
        Learns Source MAC on incoming interface.
        If frame is for this router, pass to self.process_packet().
        """
        pass

    def process_packet(self, packet):
        """
        Layer 3 logic. Decrements TTL. Drops if TTL <= 0.
        Reads Dest IP, does routing table lookup.
        Determines outgoing interface and next-hop IP.
        Passes to self.forward_frame().
        """
        pass

    def forward_frame(self, packet, interface_out, next_hop_ip):
        """
        Looks up MAC for next_hop_ip. 
        Creates new Layer2Frame with router's interface MAC as source.
        Simulates forwarding to next device.
        """
        pass
