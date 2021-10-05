# File:     network_threads.py
# Author:   Connor DeCamp
# Created:  08/25/2021
#
# This module contains functions and classes related to
# networking for the CloudPlugs.

import time
from typing import List

from PyQt5.QtCore import QThread, pyqtSignal, QByteArray
from PyQt5.QtNetwork import QUdpSocket, QHostAddress

from modules.network.message import Message, MessageCode
from modules.network.tcp_server import MyTCPServer
from modules.network.utility import *


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
        '''
        This thread will not stop until the application is
        killed. Binds a UDP socket to the host machine LAN IP address
        and a port (not important). Loops forever, occasionally broadcasting
        packets to all devices on LAN. CloudPlugs and Docking Stations will
        understand this message and can respond. On a message response, this
        thread emits a signal which is connected to the main thread.
        '''
        local_ip_str = get_LAN_ip_address()
        broadcast_ip_str = get_LAN_broadcast_address(local_ip_str)

        port = 20100

        bind_addr = QHostAddress(local_ip_str)
        broadcast_addr = QHostAddress(broadcast_ip_str)

        print(f'Broadcast IP: {broadcast_ip_str = }')

        udp_socket = QUdpSocket()
        udp_socket.bind(bind_addr, port)

        discover_msg = Message(MessageCode.DISCOVER, 'DISCOVER')
        raw_bytes = discover_msg.to_network_message()

        byte_array = QByteArray()
        byte_array.append(raw_bytes)

        PACKET_SIZE = len(raw_bytes)

        while True:
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


class TcpServerThread(QThread):
    '''
    A thread that houses the TCP Server used to communicate with
    CloudPlugs and Docking Stations.
    '''
    tcp_server = MyTCPServer()

    client_connected_signal = pyqtSignal(object)
    client_disconnected_signal = pyqtSignal(object)
    
    log_signal = pyqtSignal(object)

    ## Starts an infinite loop to handle TCP connections and message processing.
    # @param self The self object pointer
    def run(self):
        '''
        Starts an infinite loop to handle TCP connections and
        message processing.

        @param self Self pointer object
        @returns nothing
        '''

        
        self.tcp_server.openSession()

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
        msg= ip_msg_tuple[1]

        print('network_threads::send_command_from_ui')
        print(f'Sending {msg} to {ip}')

        self.tcp_server.sendCommand(ip, msg.code, msg.data)