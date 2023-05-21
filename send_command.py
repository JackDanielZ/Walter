import socket
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("message", type=str)

args = parser.parse_args()

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = '/tmp/walter_uds'
try:
    sock.connect(server_address)
except (socket.error, msg):
    print(msg)
    sys.exit(1)

try:
    # Send data
    sock.sendall(args.message.encode())
finally:
    sock.close()
