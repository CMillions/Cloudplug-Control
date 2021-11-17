##
# @file network_threads.py
# @brief Provides threads for network code.
#
# @section file_author Author
# - Created on 08/25/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified a lot 
# - Modified by Connor DeCamp on 10/21/21
#
##

import time
from typing import List

from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal, QByteArray
from PyQt5.QtNetwork import QUdpSocket, QHostAddress

from modules.network.message import MESSAGE_BYTES, Message, MessageCode
from modules.network.tcp_server import TCPServer
from modules.network.utility import *

class BroadcastWorker(QObject):
    '''! Worker object that sends out UDP broadcast packets.
    
    @brief Uses QTimer to signal a timeout event every __TIMEOUT_MSEC
    milliseconds. When the timeout event occurs, it signals the do_broadcast()
    slot.

    '''
    # This signal is emitted when a UDP response is received
    device_response = pyqtSignal(object)

    

    def on_thread_start(self):
        '''! Called when the thread starts.

        @brief Creates a UDP socket and binds it to the machine's local IP 
        address on port 20100. Also finds and saves the LAN broadcast address.
        '''
        local_ip_str = get_LAN_ip_address()
        broadcast_ip_str = get_LAN_broadcast_address(local_ip_str)

        self._sock = QUdpSocket()
        self._port = 20100
        self._bind_address = QHostAddress(local_ip_str)
        self._broadcast_address = QHostAddress(broadcast_ip_str)

        self._sock.bind(self._bind_address, self._port)

        # The amount of time in msec before the timer times out
        self._TIMEOUT_MSEC = 1000

        self._timer = QTimer()
        self._timer.timeout.connect(self.do_broadcast)
        self._timer.start(self._TIMEOUT_MSEC)
        

    def do_broadcast(self):
        '''! Sends a broadcast packet on the local network.

        @brief Writes a UDP broadcast on the local network and checks to see if there are
        any responses to it. If there is a response from another device, it emits the
        device_response signal with the message contents.
        '''
        msg = Message(MessageCode.DISCOVER, "DISCOVER")

        self._sock.writeDatagram(QByteArray(msg.to_bytes()), self._broadcast_address, self._port)
        while self._sock.hasPendingDatagrams():
            msg_tuple = self._sock.readDatagram(MESSAGE_BYTES)

            binary_contents = msg_tuple[0]
            sender_ip_addr = msg_tuple[1].toString()
            sender_port = msg_tuple[2]

            # If the sender's IP address is not our local address
            if sender_ip_addr != self._bind_address.toString():
                self.device_response.emit(msg_tuple)

        # Restart the timer to infinitely do broadcast messages
        self._timer.start(self._TIMEOUT_MSEC)

    def cleanup(self):
        '''! This thread cleans up the worker object.
        @brief Stops the timer and closes the socket.
        '''
        self._timer.stop()
        self._sock.close()

class BroadcastThread(QThread):
    '''
    Provides a way to discover CloudPlugs and Docking Stations on LAN. It does
    so by finding the host machine's LAN broadcast IP address and continuously 
    broadcasts a DISCOVER message on it. It awaits responses from devices that 
    understand what to do with that message.
    '''

    # Perhaps a better way of doing this is to have the server listen
    # for incoming messages that the cloudplugs and docking stations
    # broadcast... does it really matter though?
    #
    # If the software is acting as a server and each cloudplug/dock as 
    # a client, it would make more sense for the clients to connect to
    # the server. The clients try can each broadcast to discover the
    # 'server', which then initiates a connection with them.

    # In this way, our 'server' is trying to discover 'clients' and start
    # connections with them. It's almost like each cloudplug/docking station
    # is a server and the software is a client.

    # Has a tuple of 3 objects: 
    # (message contents in binary, QHostAddress object, port as an integer)
    device_response = pyqtSignal(object)

    def run(self):
        '''! Infinite loop that broadcasts UDP packets.
        @brief This thread will not stop until the application is
        killed. Binds a UDP socket to the host machine LAN IP address
        and a port (not important). Loops forever, occasionally broadcasting
        packets to all devices on LAN. CloudPlugs and Docking Stations will
        understand this message and can respond. On a message response, this
        thread emits a signal which is connected to the main thread.
        '''
        self.running = True

        local_ip_str = get_LAN_ip_address()
        broadcast_ip_str = get_LAN_broadcast_address(local_ip_str)

        port = 20100

        bind_addr = QHostAddress(local_ip_str)
        broadcast_addr = QHostAddress(broadcast_ip_str)

        #print(f'Broadcast IP: {broadcast_ip_str = }')

        udp_socket = QUdpSocket()
        udp_socket.bind(bind_addr, port)

        discover_msg = Message(MessageCode.DISCOVER, 'DISCOVER')
        raw_bytes = discover_msg.to_bytes()

        byte_array = QByteArray()
        byte_array.append(raw_bytes)

        PACKET_SIZE = len(raw_bytes)
        
        while self.running:
            # Write discovery message
            # print('Trying to write discovery message')
            udp_socket.writeDatagram(byte_array, broadcast_addr, port)
            while udp_socket.hasPendingDatagrams():
                msg_tuple = udp_socket.readDatagram(PACKET_SIZE)

                # Unpack the tuple to obtain the
                # message, sender IP address, and the port
                binary_contents = msg_tuple[0]
                sender_ip_addr = msg_tuple[1].toString()
                sender_port = msg_tuple[2]

                # Since the message is broadcast to all machines
                # on LAN, we don't want to do anything if the
                # recipient is the host machine

                # print(f'{local_ip_str = }\t{sender_ip_addr = }')

                if sender_ip_addr == local_ip_str:
                    break
                
                # Print response to the console
                # print(f'BroadcastThread:: {binary_contents}\t{sender_ip_addr}\t{sender_port}')

                # Emit response as a signal that can be received by
                # the main UI thread
                self.device_response.emit(msg_tuple)

            time.sleep(1)

        udp_socket.close()
        self.quit()

    def main_window_close_event_handler(self):
        self.running = False

class TcpServerThread(QThread):
    '''
    A thread that houses the TCP Server used to communicate with
    CloudPlugs and Docking Stations.
    '''

    client_connected_signal = pyqtSignal(object)
    client_disconnected_signal = pyqtSignal(object)

    # Sends ONLY a number to the UI thread that
    # can handle updating things
    update_ui_signal = pyqtSignal(MessageCode)

    # Emit messages to the main windows log
    log_signal = pyqtSignal(object)

    diagnostic_init_a0_signal = pyqtSignal(object)
    diagnostic_init_a2_signal = pyqtSignal(object)
    real_time_refresh_signal = pyqtSignal(object)
    remote_io_error_signal = pyqtSignal(object)

    ## Starts an infinite loop to handle TCP connections and message processing.
    # @param self The self object pointer
    def run(self):
        '''
        Starts an infinite loop to handle TCP connections and
        message processing.

        @param self Self pointer object
        @returns nothing
        '''

        self.tcp_server = TCPServer()

        self.tcp_server.client_connected_signal.connect(self.emit_client_connected_signal)
        self.tcp_server.client_disconnected_signal.connect(self.emit_client_disconnected_signal)
        self.tcp_server.update_ui_signal.connect(self.emit_update_ui_signal)
        self.tcp_server.log_signal.connect(self.emit_log_signal)

        self.tcp_server.diagnostic_init_a0_signal.connect(lambda cmd: self.diagnostic_init_a0_signal.emit(cmd))
        self.tcp_server.diagnostic_init_a2_signal.connect(lambda cmd: self.diagnostic_init_a2_signal.emit(cmd))
        self.tcp_server.real_time_refresh_signal.connect(lambda cmd: self.real_time_refresh_signal.emit(cmd))
        self.tcp_server.remote_io_error_signal.connect(lambda cmd: self.remote_io_error_signal.emit(cmd))

        self.tcp_server.open_session()

        # Qt documentation says this shouldn't be needed
        # but this makes the thread stay alive, therefore
        # the server can have an event loop
        self.exec()


    def send_command_from_ui(self, ip_msg_tuple):
        '''
        This function is used to send commands from the user interface.
        For example, when a user tries to read SFP memory, that user selects
        a docking station and then pressed the "Read SFP Memory" button.

        The event of clicking that button is connected to this function, which
        then calls the tcp_server::sendCommmand method
        '''
        ip = ip_msg_tuple[0]
        msg = ip_msg_tuple[1]

        #print('network_threads::send_command_from_ui')
        #print(f'Sending {msg} to {ip}')
       
        self.tcp_server.send_command(ip, msg)

    def init_dock_connection(self, ip: str):
        self.tcp_server.init_dock_connection(ip)

    def init_cloudplug_connection(self, ip: str):
        self.tcp_server.init_cloudplug_connection(ip)

    def emit_client_connected_signal(self, data: object):
        self.client_connected_signal.emit(data)

    def emit_client_disconnected_signal(self, data: object):
        self.client_disconnected_signal.emit(data)

    def emit_update_ui_signal(self, code: MessageCode):
        self.update_ui_signal.emit(code)

    def emit_log_signal(self, data: object):
        self.log_signal.emit(data)


    def main_window_close_event_handler(self):
        self.tcp_server._close_all_connections()
        self.quit()