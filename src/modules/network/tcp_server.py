##
# @file tcp_server.py
# @brief Defines the TCPServer class.
#
# @section file_author Author
# - Created on 08/16/21 by Connor DeCamp
#
##

from typing import Union
import struct, time

from PyQt5.QtCore import QByteArray, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QAbstractSocket, QHostAddress, QTcpServer, QTcpSocket

from modules.network.message import *
from modules.network.utility import *

class TCPServer(QObject):

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
        super(TCPServer, self).__init__(parent)
        self.server = None
        self.connected_dock_dict = {}
        self.connected_cloudplug_dict = {}

        self.expected_clients = 0


    def open_session(self):
                
        self.server = QTcpServer()
        self.HOST = get_LAN_ip_address()
        self.PORT = 20100

        if not self.server.listen(QHostAddress(self.HOST), self.PORT):
            print(f"Server failed to listen on {self.HOST}:{self.PORT}")
            return

        self.log_signal.emit(f'TCP Server listening on {self.HOST}:{self.PORT}')

    def init_dock_connection(self, sender_ip):
        self.connected_dock_dict[sender_ip] = None

        if self.server.hasPendingConnections():
            print("Trying to handle new dock connection")
            self.handle_new_connection()
        else:
            print("No pending connection, setting up to handle new connection")
            self.server.newConnection.connect(self.handle_new_connection)
            self.expected_clients += 1

            attempts = 10

            while attempts > 0:
                self.handle_new_connection()
                time.sleep(1)
                attempts -= 1

    def init_cloudplug_connection(self, sender_ip):
        self.connected_cloudplug_dict[sender_ip] = None

        if self.server.hasPendingConnections():
            print("Trying to handle new cloudplug connection")
            self.handle_new_connection()
        else:
            print("No pending connection, setting up to handle new connection")
            self.server.newConnection.connect(self.handle_new_connection)
            self.expected_clients += 1

            attempts = 10

            while attempts > 0:
                self.handle_new_connection()
                time.sleep(1)
                attempts -= 1


    def handle_new_connection(self):
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
                self.server.newConnection.disconnect(self.handle_new_connection)

       

        #self.connected_socket_dict[client_ip] = client_connection
        #print(f'Incoming client connection from {client_ip}')
        
        # Set up the disconnected signal
        client_connection.disconnected.connect(self.handle_client_disconnect)
        client_connection.readyRead.connect(self.handle_client_message)
        # client_connection.stateChanged.connect(self.handleClientStateChange) doesn't work...

        self.log_signal.emit(f'Client connected from {client_ip}')

        # Add new client to the list of current connections
        #if client_connection not in self.connected_socket_list:
        #    self.connected_socket_list.append(client_connection)
        #    # Emit client IP as data
        #    print('Added socket to list')
        #    self.log_signal.emit(f'Client connected from {client_connection.peerAddress().toString()}')

    def handle_client_disconnect(self):
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

    def handle_client_message(self):
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
            sent_cmd = bytes_to_read_register_message(raw_msg)
        else:
            sent_cmd = bytes_to_message(raw_msg)

        #print(sent_cmd)
        #print(f'Client at {client_ip} sent a message: {sent_cmd}')
        self.log_signal.emit(f'Client at {client_ip} sent a message: {sent_cmd}')

        self.process_client_message(client_ip, client_port, sent_cmd)

    def process_client_message(self, ip: str, port: int, command: Union[Message, ReadRegisterMessage]):

        if command.code == MessageCode.CLONE_SFP_MEMORY_ERROR:
            self.log_signal.emit(f'ERROR from DOCKING STATION at {ip}:{port} - said: {command.data_str}')
            self.update_ui_signal.emit(MessageCode.CLONE_SFP_MEMORY_ERROR)
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

    def handle_send_command_signal(self, ip_msg_tuple):
        ip = ip_msg_tuple[0]
        msg = ip_msg_tuple[1]

        #print('network_threads::send_command_from_ui')
        #print(f'Sending {msg} to {ip}')

        self.send_command(ip, msg)

    def send_command(self, destination_ip: str, command: Union[Message, ReadRegisterMessage]):
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

        raw_command = command.to_bytes()
        
        qba = QByteArray(raw_command)
        destination_socket.write(qba)

    @pyqtSlot()
    def _close_all_connections(self):
        '''! Closes all socket connections on the TCP
        server. Meant to be a pyqt slot.
        '''
        for key in self.connected_dock_dict:
            if self.connected_dock_dict[key] is not None:
                sock: QTcpSocket = self.connected_dock_dict[key]
                try:
                    sock.close()
                    self.connected_dock_dict.pop(key)
                except Exception as ex:
                    print(ex)

        for key in self.connected_cloudplug_dict:
            if self.connected_cloudplug_dict[key] is not None:
                sock: QTcpSocket = self.connected_cloudplug_dict[key]
                try:
                    sock.close()
                    self.connected_cloudplug_dict.pop(key)
                except Exception as ex:
                    print(ex)
                    




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