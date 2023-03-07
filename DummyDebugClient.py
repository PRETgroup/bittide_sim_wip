import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(True)
sock.settimeout(None)
# Connect the socket to the port where the server is listening
server_address = ('localhost', 50000)
print('connecting to %s port %s' % server_address)
sock.connect(server_address)

while(True):
    # Send data
    message = (input('message>') + '\n').encode()
    first_name = message
    print('sending "%s"' % message)
    sock.send(message)

    while (True):
        data = ""
        nextchar = sock.recv(1).decode()
        while nextchar != '\n':
            data += nextchar
            nextchar= sock.recv(1).decode()
        print('received "%s"' % data)

        message = (input('message>') + '\n').encode()
        sock.send(message)