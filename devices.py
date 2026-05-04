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
        """
        MAX_PAYLOAD_SIZE = 500
        
        # Log the receipt from the Application Layer
        print(f"Host {self.ip[-2:]}: Layer 4: Data received from Application Layer. Data size = {len(message_string)}")

        # 1. Segment the data
        segments_data = []
        for i in range(0, len(message_string), MAX_PAYLOAD_SIZE):
            chunk = message_string[i:i + MAX_PAYLOAD_SIZE]
            segments_data.append(chunk)
            
        # Temporary print statement to test the chunking
        for index, chunk in enumerate(segments_data):
            print(f"DEBUG - Created chunk {index + 1} of size: {len(chunk)}")
            
        # 2. rdt2.2 Send Loop
        for chunk in segments_data:
            print(f"Host {self.ip[-2:]}: Layer 4: Checksum computed")
            
            # Step 2a: Create the Layer4Segment (segment_type 0 = DATA)
            segment = Layer4Segment(src_port=5000, dst_port=dest_port, segment_type=0, seq_num=self.seq_num, data=chunk)
            
            print(f"Host {self.ip[-2:]}: Layer 4: Segment created by adding transport layer header (DATA, seq={self.seq_num}) (encapsulation)")
            
            # Step 2b: Send and wait for ACK
            self.waiting_for_ack = True
            while self.waiting_for_ack:
                print(f"Host {self.ip[-2:]}: Layer 4: Segment sent to Network Layer")
                self.send_to_layer3(segment, dest_ip)
                
                # --- SAFETY BREAK FOR INDEPENDENT TESTING ---
                # Remove these two lines once your partner finishes Layer 3!
                print(f"DEBUG: Simulating successful ACK receipt to prevent infinite loop.")
                self.waiting_for_ack = False 
                # --------------------------------------------
                
            # Step 2c: Flip the alternating bit (0 becomes 1, 1 becomes 0)
            self.seq_num = 1 - self.seq_num

    def receive_from_layer3(self, segment, src_ip):
        """
        Receives Layer4Segment from L3. 
        Verifies checksum. Handles ACKs (if sender) or DATA (if receiver).
        """
        print(f"Host {self.ip[-2:]}: Layer 4: Segment received from Network Layer")
        
        # 1. Verify Checksum[cite: 1]
        if not segment.verify_checksum():
            print(f"Host {self.ip[-2:]}: Layer 4: Segment discarded due to checksum error")
            # In rdt2.2, if receiver gets corrupt DATA, they resend the previous ACK[cite: 1].
            # If sender gets corrupt ACK, they do nothing, and the loop will retransmit[cite: 1].
            if segment.type == 0: 
                # Resend previous ACK
                prev_ack_seq = 1 - self.seq_num
                ack_segment = Layer4Segment(src_port=80, dst_port=5000, segment_type=1, seq_num=prev_ack_seq)
                self.send_to_layer3(ack_segment, src_ip)
            return
            
        print(f"Host {self.ip[-2:]}: Layer 4: Checksum verified")

        # 2. Handle incoming ACK (Sender Side)[cite: 1]
        if segment.type == 1: 
            print(f"Host {self.ip[-2:]}: Layer 4: ACK received: seq={segment.seq_num}")
            if segment.seq_num == self.seq_num:
                self.waiting_for_ack = False # Breaks the while loop!
            else:
                print(f"Host {self.ip[-2:]}: Layer 4: Incorrect ACK received, retransmitting...")
                
        # 3. Handle incoming DATA (Receiver Side)[cite: 1]
        elif segment.type == 0: 
            if segment.seq_num == self.seq_num:
                print(f"Host {self.ip[-2:]}: Layer 4: DATA segment delivered to Application Layer. Data size = {len(segment.data)}")
                # Advance receiver's expected sequence number
                self.seq_num = 1 - self.seq_num 
            else:
                # Duplicate segment detected (ACK was likely lost)
                pass

            # Always send an ACK for the sequence number we just received
            ack_segment = Layer4Segment(src_port=80, dst_port=5000, segment_type=1, seq_num=segment.seq_num)
            print(f"Host {self.ip[-2:]}: Layer 4: Segment created by adding transport layer header (ACK, seq={segment.seq_num})")
            print(f"Host {self.ip[-2:]}: Layer 4: Segment sent to Network Layer")
            
            # Send it down to Layer 3 to travel back to the sender
            self.send_to_layer3(ack_segment, src_ip)
            
    def send_to_layer3(self, segment, dest_ip):
        """
        Helper to pass L4 segment down to Partner's L3.
        This bridges your Transport layer with your partner's Network layer.
        """
        self.receive_from_layer4(segment, dest_ip)

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
    def __init__(self, interfaces_config, routing_table):
        self.interfaces = interfaces_config
        self.routing_table = routing_table

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
