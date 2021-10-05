import sys
from typing import List
from collections import defaultdict
import struct

from PyQt5.QtCore import QByteArray, QObject, pyqtSignal
from PyQt5.QtNetwork import QAbstractSocket, QHostAddress, QTcpServer, QTcpSocket

from modules.network.message import Message, MessageCode
from modules.network.utility import *

class MyTCPServer(QObject):

    client_connected_signal = pyqtSignal(object)
    client_disconnected_signal = pyqtSignal(str)

    # Emit messages to the main windows log
    log_signal = pyqtSignal(object)

    # A list of all connected sockets
    connected_socket_list: List[QTcpSocket]

    # A dictionary of connected sockets, with the ip string
    # as the key and the socket object as the value
    connected_socket_dict: defaultdict

    def __init__(self, parent=None):
        super(MyTCPServer, self).__init__(parent)
        self.server = None
        self.connected_socket_list = []
        self.connected_socket_dict = defaultdict(None)

    def openSession(self):
                
        self.server = QTcpServer()
        self.HOST = get_LAN_ip_address()
        self.PORT = 20100
        
        self.server.newConnection.connect(self.handleNewConnection)

        if not self.server.listen(QHostAddress(self.HOST), self.PORT):
            raise Exception(f"Server failed to listen on {self.HOST}:{self.PORT}")
        
        self.log_signal.emit(f'TCP Server listening on {self.HOST}:{self.PORT}')

    def handleNewConnection(self):
        
        client_connection = self.server.nextPendingConnection()
        client_ip = client_connection.peerAddress().toString()

        self.connected_socket_dict[client_ip] = client_connection

        #self.textBrowser.append(f'Incoming client connection from {client_connection.peerAddress().toString()}')
        print(f'Incoming client connection from {client_ip}')
        
        # Set up the disconnected signal
        client_connection.disconnected.connect(self.handleClientDisconnect)
        client_connection.readyRead.connect(self.handleClientMessage)
        client_connection.stateChanged.connect(self.handleClientStateChange)

        self.client_connected_signal.emit(client_ip)
        self.log_signal.emit(f'Client connected from {client_ip}')

        # Add new client to the list of current connections
        #if client_connection not in self.connected_socket_list:
        #    self.connected_socket_list.append(client_connection)
        #    # Emit client IP as data
        #    print('Added socket to list')
        #    self.log_signal.emit(f'Client connected from {client_connection.peerAddress().toString()}')

    def handleClientDisconnect(self):
        # Technically bad design, but we need to know
        # which client disconnected
        client: QTcpSocket = self.sender()
        client_ip = client.peerAddress().toString()

        self.log_signal.emit(f'Client at {client.peerAddress().toString()} disconnected')
        print(f'Client disconnected {client.peerAddress().toString()}')
        print(f'There were {client.bytesAvailable()} bytes waiting to be processed')
        client.close()

        self.connected_socket_dict[client_ip] = None

        self.client_disconnected_signal.emit(client_ip)

        # Remove the first instance of a client with this IP address
        for sock in self.connected_socket_list:
            if sock.peerAddress().toString() == client.peerAddress().toString():
                self.connected_socket_list.remove(sock)

    def handleClientMessage(self):
        '''
        Handler for when a client sends a message
        '''
        client_socket: QTcpSocket = self.sender()
        raw_msg = client_socket.readAll()
        
        code, data = struct.unpack('!H254s', raw_msg)
        # Stripping \x00 may not be the best idea:
        # If the DATA part of the message must contain
        # zeros they would be removed...
        sent_cmd = Message(code, str(data, 'utf-8').strip('\x00'))

        print(sent_cmd)
        
        print(f'Client at {client_socket.peerAddress().toString()} sent a message: {sent_cmd}')
        self.log_signal.emit(f'Client at {client_socket.peerAddress().toString()} sent a message: {sent_cmd}')

    def handleClientStateChange(self, state):

        # Show that the connection has been made
        if state == QAbstractSocket.ConnectedState:
            self.log_signal.emit('Connection established')

    def sendCommand(self, destination_ip: str, code: MessageCode, msg: str):
        '''
        This method sends a command to a destination IP address.
        '''
        if not self.connected_socket_dict[destination_ip]:
            print("Trying to send command to unknown IP")
            self.log_signal.emit(f"ERROR: Tried to send data to {destination_ip} which is an unknown destination.")
            return

        destination_socket: QTcpSocket = self.connected_socket_dict[destination_ip]
        
        command = Message(code, msg)
        raw_command = command.to_network_message()
        
        qba = QByteArray(raw_command)
        destination_socket.write(qba)



'''
def main():

    app = QApplication(sys.argv)
    tcp_server = MyTCPServer()
    tcp_server.openSession()
    tcp_server.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
'''