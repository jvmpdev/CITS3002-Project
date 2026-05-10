import sys
from config import *
from devices import Host, Router

def create_dummy_message(size):
    """
    Creates a simple text payload of the exact requested byte size.
    For simulation, we'll use a repeating character to easily verify size.
    """
    return "A" * size

def main():
    # get message size from args/read command line input
    if len(sys.argv) != 2:
        print("Usage: python main.py <message_size_in_bytes>")
        sys.exit(1)
    
    try:
        message_size = int(sys.argv[1])
        if message_size <= 0:
            raise ValueError
    except ValueError:
        print("Error: Message size must be a positive integer.")
        sys.exit(1)

    print(f"--- Starting Simulation: {message_size}-byte payload from Host A to Host B ---")

    # set up hosts and router
    host_a = Host("Host A", HOST_A_IP, HOST_A_MAC, ROUTING_TABLE_HOST_A, ARP_TABLE_HOST_A)
    host_b = Host("Host B", HOST_B_IP, HOST_B_MAC, ROUTING_TABLE_HOST_B, ARP_TABLE_HOST_B)
    
    router_r1 = Router(
        interfaces_config={
            "Interface 1": {"ip": ROUTER_R1_IFACE1_IP, "mac": ROUTER_R1_IFACE1_MAC, "arp_table": ARP_TABLE_R1_IFACE1},
            "Interface 2": {"ip": ROUTER_R1_IFACE2_IP, "mac": ROUTER_R1_IFACE2_MAC, "arp_table": ARP_TABLE_R1_IFACE2}
        },
        routing_table=ROUTING_TABLE_R1
    )

    # wire up the topology
    host_a.link = router_r1
    host_a.connected_interface = "Interface 1"  

    host_b.link = router_r1
    host_b.connected_interface = "Interface 2"

    router_r1.interfaces["Interface 1"]["link"] = host_a
    router_r1.interfaces["Interface 2"]["link"] = host_b

    # start transmission
    dummy_message = create_dummy_message(message_size)
    host_a.send_message(dummy_message, dest_ip=HOST_B_IP)

if __name__ == "__main__":
    main()
