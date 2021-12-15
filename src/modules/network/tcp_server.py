##
# @file tcp_server.py
# @brief Defines the TCPServer class.
#
# @section file_author Author
# - Created on 08/16/21 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 12/03/21 by Connor DeCamp
#
# I left off re-doing the connection management by making a wrapper
# around the socket. Thinking it would be better to use a dictionary
# inside the TCP server instead of searching a list every time.
##

import struct
import logging
from typing import Union
from collections import defaultdict

from PyQt5.QtCore import QByteArray, QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QAbstractSocket, QHostAddress, QTcpServer, QTcpSocket

from modules.network.message import *
from modules.network.utility import *

class DeviceConnection:
    '''! Defines an object for Device Connections.
    '''
    def __init__(self, device_type: DeviceType, ip_address: str):

        self.type = device_type
        self.ip = ip_address
        self.socket_ptr = None

        self._timeout_timer = QTimer()
        self._TIMEOUT_MSEC = 5000
    
    def set_socket_ptr(self, socket_ptr: QTcpSocket):
        self.socket_ptr = socket_ptr

    def disable_timeout(self):
        self._timeout_timer.stop()

    def restart_timer(self):
        self._timeout_timer.start(self._TIMEOUT_MSEC)


class KeepaliveTimer(QObject):

    ip_timeout_signal = pyqtSignal(str)


    def __init__(self, ip):
        super().__init__()

        self.ip = ip

        self.kill_timer = QTimer()
        self._timeout_msec = 5000

        self.kill_timer.timeout.connect(
            lambda: self.ip_timeout_signal.emit(self.ip)
        )

    def restart_timer(self):
        self.kill_timer.start(self._timeout_msec)

    def stop_timer(self):
        self.kill_timer.stop()



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

    def handle_key_error(self):
        return None

    def open_session(self):
                
        self.connected_dock_dict = {}
        self.connected_cloudplug_dict = {}
        self.timers = {}

        self.connected_devices = defaultdict(self.handle_key_error)

        # Every 2.5 seconds send out
        # heartbeat signal to all sockets
        # Each socket has 5 seconds to reply unless
        # it was commanded to read SFP memory, write
        # CloudPlug persona
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.send_heartbeats)
        self.heartbeat_timer.start(2500)

        self.server = QTcpServer()
        self.HOST = get_LAN_ip_address()
        self.PORT = 20100

        if not self.server.listen(QHostAddress(self.HOST), self.PORT):
            logging.error(f"Server failed to listen on {self.HOST}:{self.PORT}")
            return

        self.server.newConnection.connect(self.handle_new_connection)

        self.log_signal.emit(f'TCP Server listening on {self.HOST}:{self.PORT}')

    def handle_new_connection(self):
        '''
        Handles a pending connection in the connection queue for the TCP Server.
        '''
        client_connection = self.server.nextPendingConnection()

        if client_connection:
            client_ip = client_connection.peerAddress().toString()
        else:
            raise RuntimeError("No pending connection")

        #logging.debug(f'{client_ip = }')

        # Set up signals
        client_connection.disconnected.connect(self.handle_client_disconnect)
        client_connection.readyRead.connect(self.handle_client_message)
        client_connection.stateChanged.connect(lambda s: self.log_signal.emit(f"state change to {s}"))
        client_connection.error.connect(lambda s: self.log_signal.emit(f"Error: {s}"))

        self.connected_devices[client_ip] = DeviceConnection(DeviceType.UNKNOWN, client_ip)
        self.connected_devices[client_ip].set_socket_ptr(client_connection)

        msg = Message(MessageCode.IDENTIFY_DEVICE, "Identify")
        self.send_command(client_ip, msg)

        self.log_signal.emit(f'Client connected from {client_ip}, asking to ID')

    def handle_client_timeout(self, ip_str : str):

        self.log_signal.emit(f"Client at {ip_str} timed out")

    def handle_client_disconnect(self):
        # Technically bad design, but we need to know
        # which client disconnected
        client: QTcpSocket = self.sender()
        
        client_ip = client.peerAddress().toString()
        logging.debug("Client trying to disconnect")

        # If the client disconnects and we don't have the IP,
        # we need to search all of the devices to find the
        # socket in the 'Unconnected' state
        if client_ip == '':
            print("Client ip was empty (''), searching")

            for device in self.connected_devices:
                condition = device.socket_ptr.state() is QAbstractSocket.SocketState.UnconnectedState
                if device.socket_ptr and condition:
                    dev_type = None
                    if device.type is DeviceType.CLOUDPLUG:
                        dev_type = "CloudPlug"
                    elif device.type is DeviceType.DOCKING_STATION:
                        dev_type = "Docking Station"

                    logging.debug(f"Disconnecting {dev_type} with client ip: {device.ip}")
                    self.client_disconnected_signal.emit(device)
                    self.connected_devices.pop(client_ip)
                    break
        else:
            # We know the IP of the client that disconnected,
            # so remove it fro the dictionary

            device = self.connected_devices[client_ip]
            dev_type = None
            if device.type is DeviceType.CLOUDPLUG:
                dev_type = "CloudPlug"
            elif device.type is DeviceType.DOCKING_STATION:
                dev_type = "Docking Station"

            logging.debug(f"Disconnecting {dev_type} with client ip: {client_ip}")
            self.client_disconnected_signal.emit(device)
            self.connected_devices.pop(client_ip)

    def handle_client_message(self):
        '''
        Handler for when a client sends a message
        '''
        client_socket: QTcpSocket = self.sender()
        client_ip = client_socket.peerAddress().toString()
        client_port = client_socket.peerPort()
        raw_msg = client_socket.readAll()
        
        # We need the message code to determine how to process
        # the rest of the message
        code, *garbage = struct.unpack(f'!H{MESSAGE_BYTES - SIZEOF_H}x', raw_msg)
        command = None

        # If the message code is one of these, we
        # process it differently
        read_register_acks = [
            MessageCode.DIAGNOSTIC_INIT_A0_ACK, 
            MessageCode.DIAGNOSTIC_INIT_A2_ACK, 
            MessageCode.REAL_TIME_REFRESH_ACK
        ]

        if MessageCode(code) in read_register_acks:
            command = bytes_to_read_register_message(raw_msg)
        else:
            command = bytes_to_message(raw_msg)
        
        # Don't print heartbeat messages, helps avoid
        # spamming the debug console
        if command.code != MessageCode.HEARTBEAT:
            self.log_signal.emit(f'Client at {client_ip} sent a message: {command}')

        if command.code == MessageCode.DOCK_DISCOVER_ACK:
            device = self.connected_devices[client_ip]
            device.type = DeviceType.DOCKING_STATION
            self.client_connected_signal.emit(device)
        elif command.code == MessageCode.CLOUDPLUG_DISCOVER_ACK:
            device = self.connected_devices[client_ip]
            device.type = DeviceType.CLOUDPLUG
            self.client_connected_signal.emit(device)
        if command.code == MessageCode.CLONE_SFP_MEMORY_ERROR:
            self.log_signal.emit(
                f'ERROR from DOCKING STATION at {client_ip}:{client_port} - \
                said: {command.data_str}'
            )
            self.update_ui_signal.emit(MessageCode.CLONE_SFP_MEMORY_ERROR)
        elif command.code == MessageCode.CLONE_SFP_MEMORY_SUCCESS:
            self.update_ui_signal.emit(MessageCode.CLONE_SFP_MEMORY_SUCCESS)
        elif command.code == MessageCode.DIAGNOSTIC_INIT_A0_ACK:
            self.log_signal.emit(f'DOCKING STATION at {client_ip}:{client_port} successfully read vendor name, PN, diagnostic type')
            self.diagnostic_init_a0_signal.emit(command)
        elif command.code == MessageCode.DIAGNOSTIC_INIT_A2_ACK:
            self.log_signal.emit(f'DOCKING STATION at {client_ip}:{client_port} successfully read diagnostic information')
            self.diagnostic_init_a2_signal.emit(command)
        elif command.code == MessageCode.REAL_TIME_REFRESH_ACK:
            self.log_signal.emit(f'DOCKING STATION at {client_ip}:{client_port} successfully refreshed diagnostic info')
            self.real_time_refresh_signal.emit(command)
        elif command.code == MessageCode.I2C_ERROR:
            self.log_signal.emit(f'ERROR from DOCKING STATION at {client_ip}:{client_port} - said: {command.data_str}')
            self.remote_io_error_signal.emit(command)
        elif command.code == MessageCode.REPROGRAM_SUCCESS:
            self.log_signal.emit(f'Successfully reprogrammed CloudPlug')
            self.update_ui_signal.emit(MessageCode.REPROGRAM_SUCCESS)
        elif command.code == MessageCode.REPROGRAM_FAIL:
            self.log_signal.emit(f'Failed to reprogram CloudPlug')
            self.update_ui_signal.emit(MessageCode.REPROGRAM_FAIL)
        elif command.code == MessageCode.STRESS_FAIL:
            self.log_signal.emit('Failed to run stress scenario!')
            self.update_ui_signal.emit(MessageCode.STRESS_FAIL)
        elif command.code == MessageCode.STRESS_START:
            self.log_signal.emit('Beginning stress scenario, monitor your network switch!')
            self.update_ui_signal.emit(MessageCode.STRESS_START)


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
        destination_socket = self.connected_devices[destination_ip].socket_ptr

        if destination_socket:
            raw_command = command.to_bytes()

            #self.timers[destination_ip].stop_timer()
            qba = QByteArray(raw_command)
            destination_socket.write(qba)
        else:
            logging.error("Tried to send command to invalid device!")

    def send_heartbeats(self):
        ##
        #
        ##
        for ip_sock in self.connected_cloudplug_dict.items():
            sock: QTcpSocket = ip_sock[1]
            msg = Message(MessageCode.HEARTBEAT, "hello")
            
            if sock:
                sock.write(QByteArray(msg.to_bytes()))

        self.heartbeat_timer.start(2500)

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