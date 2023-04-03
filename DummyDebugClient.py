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
    tick_count = -1
    for line in sys.stdin:
        message = line.replace('\\n', '\n')
        for fragment in message.split('\n'):
            if (fragment == ''): break
            fragment = (fragment + '\n').encode()
            print('Tick %d send: "%s"' % (tick_count,fragment))
            
            sock.send(fragment)
            data = ""
            nextchar = sock.recv(1).decode()
            while nextchar != '\n':
                data += nextchar
                nextchar= sock.recv(1).decode()
            print('Tick %d receive: "%s"' % (tick_count,data))
            tick_count += 1