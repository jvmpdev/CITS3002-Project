# IP addresses
HOST_A_IP = "10.0.1.10"
HOST_B_IP = "10.0.2.20"
ROUTER_R1_IFACE1_IP = "10.0.1.1"
ROUTER_R1_IFACE2_IP = "10.0.2.1"

# MAC addresses
HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"
ROUTER_R1_IFACE1_MAC = "BB:BB:BB:BB:BB:BB"
ROUTER_R1_IFACE2_MAC = "CC:CC:CC:CC:CC:CC"

# Subnets
SUBNET_1 = ("10.0.1.0", 24)
SUBNET_2 = ("10.0.2.0", 24)

# Layer 2 constants
ETHER_TYPE_IPV4 = 0x0800

# Layer 3 constants
DEFAULT_TTL = 100
PROTOCOL_UDP = 17

# Layer 4 constants
DEFAULT_SRC_PORT = 5000
DEFAULT_DST_PORT = 80
SEGMENT_TYPE_DATA = 0
SEGMENT_TYPE_ACK = 1

# Routing tables
# format: destination network: (network, prefix length, next hop ip, outgoing interface)

ROUTING_TABLE_HOST_A = [
    ("10.0.1.0", 24, None, "eth0"),           # directly connected
    ("0.0.0.0",  0,  ROUTER_R1_IFACE1_IP, "eth0"),  # default route via R1
]

ROUTING_TABLE_HOST_B = [
    ("10.0.2.0", 24, None, "eth0"),           # directly connected
    ("0.0.0.0",  0,  ROUTER_R1_IFACE2_IP, "eth0"),  # default route via R1
]

ROUTING_TABLE_R1 = [
    ("10.0.1.0", 24, None,    "iface1"),  # directly connected
    ("10.0.2.0", 24, None,    "iface2"),  # directly connected
]

ARP_TABLE_HOST_A = {
    ROUTER_R1_IFACE1_IP: ROUTER_R1_IFACE1_MAC,
}

ARP_TABLE_HOST_B = {
    ROUTER_R1_IFACE2_IP: ROUTER_R1_IFACE2_MAC,
}

ARP_TABLE_R1_IFACE1 = {
    HOST_A_IP: HOST_A_MAC,
}

ARP_TABLE_R1_IFACE2 = {
    HOST_B_IP: HOST_B_MAC,
}