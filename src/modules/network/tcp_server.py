from typing import Union
import struct, time

from PyQt5.QtCore import QByteArray, QObject, pyqtSignal
from PyQt5.QtNetwork import QAbstractSocket, QHostAddress, QTcpServer, QTcpSocket

from modules.network.message import *
from modules.network.utility import *

class MyTCPServer(QObject):

    client_connected_signal = pyqtSignal(object)
    client_disconnected_signal = pyqtSignal(object)

    # Sends ONLY a number to the UI thread that
    # can handle updating things
    update_ui_signal = pyqtSignal(MessageCode)

    diagnostic_init_a0_signal = pyqtSignal(ReadRegisterMessage)
    diagnostic_init_a2_signal = pyqtSignal(ReadRegisterMessage)
    real_time_refresh_signal = pyqtSignal(ReadRegisterMessage)

    remote_io_error_signal = pyqtSignal(Message)

    # Emit messages to the main windows log
    log_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MyTCPServer, self).__init__(parent)
        self.server = None
        self.connected_dock_dict = {}
        self.connected_cloudplug_dict = {}

        self.expected_clients = 0

        

    def openSession(self):
                
        self.server = QTcpServer()
        self.HOST = get_LAN_ip_address()
        self.PORT = 20100

        if not self.server.listen(QHostAddress(self.HOST), self.PORT):
            raise Exception(f"Server failed to listen on {self.HOST}:{self.PORT}")
        
        self.log_signal.emit(f'TCP Server listening on {self.HOST}:{self.PORT}')

    def initDockConnection(self, sender_ip):
        self.connected_dock_dict[sender_ip] = None

        if self.server.hasPendingConnections():
            print("Trying to handle new dock connection")
            self.handleNewConnection()
        else:
            print("No pending connection, setting up to handle new connection")
            self.server.newConnection.connect(self.handleNewConnection)
            self.expected_clients += 1

            attempts = 10

            while attempts > 0:
                self.handleNewConnection()
                time.sleep(1)
                attempts -= 1

    def initCloudplugConnection(self, sender_ip):
        self.connected_cloudplug_dict[sender_ip] = None

        if self.server.hasPendingConnections():
            print("Trying to handle new cloudplug connection")
            self.handleNewConnection()
        else:
            print("No pending connection, setting up to handle new connection")
            self.server.newConnection.connect(self.handleNewConnection)
            self.expected_clients += 1

            attempts = 10

            while attempts > 0:
                self.handleNewConnection()
                time.sleep(1)
                attempts -= 1


    def handleNewConnection(self):
        '''
        Handles a pending connection in the connection queue for the TCP Server.
        '''
        client_connection = self.server.nextPendingConnection()
        client_ip = client_connection.peerAddress().toString()

        #print(f'{client_ip = }')

        if client_ip in self.connected_dock_dict:
            self.connected_dock_dict[client_ip] = client_connection
            self.client_connected_signal.emit((DeviceType.DOCKING_STATION, client_ip))
        elif client_ip in self.connected_cloudplug_dict:
            self.connected_cloudplug_dict[client_ip] = client_connection
            self.client_connected_signal.emit((DeviceType.CLOUDPLUG, client_ip))
        else:
            print(f"Unknown IP address: {client_ip}")
            return

        
        if self.expected_clients > 0:
            self.expected_clients -= 1

            if self.expected_clients == 0:
                self.server.newConnection.disconnect(self.handleNewConnection)

       

        #self.connected_socket_dict[client_ip] = client_connection
        #print(f'Incoming client connection from {client_ip}')
        
        # Set up the disconnected signal
        client_connection.disconnected.connect(self.handleClientDisconnect)
        client_connection.readyRead.connect(self.handleClientMessage)
        # client_connection.stateChanged.connect(self.handleClientStateChange) doesn't work...

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
        #print(f'{client_ip = }')

        if client_ip == '':
            print("Client ip was empty (''), searching")
            for key in self.connected_dock_dict:
                connection: QTcpSocket = self.connected_dock_dict[key]
                if connection is not None and connection.state() == QAbstractSocket.SocketState.UnconnectedState:
                    client_ip = key
                    print(f"Found DOCKING STATION with client ip: {client_ip}")
                    break
        
        if client_ip == '':
            for key in self.connected_cloudplug_dict:
                connection: QTcpSocket = self.connected_cloudplug_dict[key]
                if connection is not None and connection.state() == QAbstractSocket.SocketState.UnconnectedState:
                    client_ip = key
                    print(f"Found CLOUDPLUG with client ip: {client_ip}")
                    break

        if client_ip == '':
            print("Failed to find client ip")
            return
            

        self.log_signal.emit(f'Client at {client_ip} disconnected')
        #print(f'Client disconnected: {client.peerAddress().toString() = }')
        #print(f'There were {client.bytesAvailable()} bytes waiting to be processed')

        if client_ip in self.connected_dock_dict.keys():
            self.connected_dock_dict.pop(client_ip)
            self.client_disconnected_signal.emit((DeviceType.DOCKING_STATION, client_ip))
        
        if client_ip in self.connected_cloudplug_dict.keys():
            self.connected_cloudplug_dict.pop(client_ip)
            self.client_disconnected_signal.emit((DeviceType.CLOUDPLUG, client_ip))

        #client.close()

    def handleClientMessage(self):
        '''
        Handler for when a client sends a message
        '''
        client_socket: QTcpSocket = self.sender()
        client_ip = client_socket.peerAddress().toString()
        client_port = client_socket.peerPort()
        raw_msg = client_socket.readAll()
        
        code, *garbage = struct.unpack(f'!H{MESSAGE_BYTES - SIZEOF_H}x', raw_msg)
        sent_cmd = None

        read_register_acks = [MessageCode.DIAGNOSTIC_INIT_A0_ACK, MessageCode.DIAGNOSTIC_INIT_A2_ACK, MessageCode.REAL_TIME_REFRESH_ACK]

        if MessageCode(code) in read_register_acks:
            sent_cmd = bytesToReadRegisterMessage(raw_msg)
        else:
            sent_cmd = unpackRawBytes(raw_msg)

        #print(sent_cmd)
        #print(f'Client at {client_ip} sent a message: {sent_cmd}')
        self.log_signal.emit(f'Client at {client_ip} sent a message: {sent_cmd}')

        self.processClientMessage(client_ip, client_port, sent_cmd)

    def processClientMessage(self, ip: str, port: int, command: Union[Message, ReadRegisterMessage]):

        if command.code == MessageCode.CLONE_SFP_MEMORY_ERROR:
            self.log_signal.emit(f'ERROR from DOCKING STATION at {ip}:{port} said: {command.data_str}')
        elif command.code == MessageCode.CLONE_SFP_MEMORY_SUCCESS:
            self.update_ui_signal.emit(MessageCode.CLONE_SFP_MEMORY_SUCCESS)
        elif command.code == MessageCode.DIAGNOSTIC_INIT_A0_ACK:
            self.log_signal.emit(f'DOCKING STATION at {ip}:{port} successfully read vendor name, PN, diagnostic type')
            self.diagnostic_init_a0_signal.emit(command)
        elif command.code == MessageCode.DIAGNOSTIC_INIT_A2_ACK:
            self.log_signal.emit(f'DOCKING STATION at {ip}:{port} successfully read diagnostic information')
            self.diagnostic_init_a2_signal.emit(command)
        elif command.code == MessageCode.REAL_TIME_REFRESH_ACK:
            self.log_signal.emit(f'DOCKING STATION at {ip}:{port} successfully refreshed diagnostic info')
            self.real_time_refresh_signal.emit(command)
        elif command.code == MessageCode.I2C_ERROR:
            self.log_signal.emit(f'ERROR from DOCKING STATION at {ip}:{port} - said: {command.data_str}')
            self.remote_io_error_signal.emit(command)

    def sendCommandSignalHandler(self, ip_msg_tuple):
        ip = ip_msg_tuple[0]
        msg = ip_msg_tuple[1]

        #print('network_threads::send_command_from_ui')
        #print(f'Sending {msg} to {ip}')

        self.sendCommand(ip, msg)

    def sendCommand(self, destination_ip: str, command: Union[Message, ReadRegisterMessage]):
        '''
        This method sends a command to a destination IP address.
        '''
        destination_socket = None

        if destination_ip in self.connected_dock_dict:
            destination_socket: QTcpSocket = self.connected_dock_dict[destination_ip]
        elif destination_ip in self.connected_cloudplug_dict:
            destination_socket: QTcpSocket = self.connected_cloudplug_dict[destination_ip]
        else:
            print("Trying to send command to unknown IP")
            self.log_signal.emit(f"ERROR: Tried to send data to {destination_ip} which is an unknown destination.")
            return

        raw_command = command.to_network_message()
        
        qba = QByteArray(raw_command)
        destination_socket.write(qba)

    def _close_all_connections(self):
        
        for key in self.connected_dock_dict:
            if self.connected_dock_dict[key] is not None:
                sock: QTcpSocket = self.connected_dock_dict[key]
                sock.disconnectFromHost()
                sock.close()

        for key in self.connected_cloudplug_dict:
            if self.connected_cloudplug_dict[key] is not None:
                sock: QTcpSocket = self.connected_cloudplug_dict[key]

                sock.disconnectFromHost()
                sock.close()




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