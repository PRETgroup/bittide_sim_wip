import socket
import ast

class ControlServer:
    def __init__(self, port):
        # Create a UDP socket
        self.sock = socket.socket()         # Create a socket object
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = "0.0.0.0" # Get local machine name
        self.sock.bind((host, port))        # Bind to the port
        self.sock.listen(5)                 # Now wait for client connection.
        self.connections = {}
        print('Server started on ' + str(host) + ":" + str(port))

    def handle_fsm_connections (self, node_names):
        remaining_connection_names = node_names.copy()
        while len(remaining_connection_names) > 0:
            print('Waiting for following FSM clients:' + str(remaining_connection_names))
            print('...')
            clientSock, address = self.sock.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            data = ""
            nextchar = clientSock.recv(1).decode()
            while nextchar != '\n':
                data += nextchar
                nextchar = clientSock.recv(1).decode()
                
        
            print('Client has self-identified as machine ' + data)
            try:
                remaining_connection_names.pop(remaining_connection_names.index(data))
                self.connections[data] = clientSock
            except:
                print("Did not find this node name")
        print("All machines connected....beginning")

    def send_to_client(self, nodename : str, val : str):
        message = (val + "\n").encode()
        self.connections[nodename].send(message)

    def receive_from_client(self, nodename : str) -> list[str]:
        data = ""
        nextchar = self.connections[nodename].recv(1).decode()
        while nextchar != '\n':
            data += nextchar
            nextchar = self.connections[nodename].recv(1).decode()

        return ast.literal_eval(data)


    def run_node_tick(self, nodename : str, input_signals : list[str]) -> list[str]:
        self.send_to_client(nodename, str(input_signals))
        return self.receive_from_client(nodename)
             