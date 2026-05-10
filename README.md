# CITS3002: Mini Internet Protocol Stack Simulator

Authors: Damien Zhang (23669907) & Jules Van Melle-Park (23136223)

# Overview
This project is a logical Python simulation of a simplified three-tier network stack (Layers 2, 3, and 4). It demonstrates the encapsulation, routing, and reliable delivery of application data from Host A to Host B across a router (R1). 

The codebase is structured into four main components:
* `main.py`: The execution entry point that parses command-line arguments and mocks the physical connections.
* `devices.py`: Contains the `Host` and `Router` classes, implementing MAC learning, IP routing, and the rdt2.2 reliable data transfer protocol.
* `protocol.py`: Defines the header structures and dynamically calculates segment sizes, TTLs, and checksums.
* `config.py`: Stores the static network topology, including IP addresses, MAC addresses, and routing tables.

# Execution Instructions
This simulator requires Python 3 and uses only standard libraries. 

To run the simulation, execute `main.py` via the command line and pass the desired application message size (in bytes) as a single integer argument.

**Usage:**
python3 main.py <message_size_in_bytes>

**Example (10-byte payload):**
python3 main.py 10

**Example (1200-byte payload requiring segmentation):**
python3 main.py 1200