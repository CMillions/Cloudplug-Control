# File:     network_threads.py
# Author:   Connor DeCamp
# Created:  08/25/2021
#
# This module contains functions and classes related to
# networking for the CloudPlugs.

from PyQt5.QtCore import QThread, pyqtSignal, QByteArray
from PyQt5.QtNetwork import QNetworkInterface, QUdpSocket, QHostAddress, QAbstractSocket
import time

from modules.network.message import Message, MessageCode

def get_LAN_ip_address() -> str:
    '''
    This method retrieves the host machines IP address on the local area network.
    '''
    # Gets the list of all addresses on the host machine
    ip_list = QNetworkInterface.allAddresses()

    # For each address in the list, check if it's an IPv4
    # address and not a loopback address
    for address in ip_list:
        if address.protocol() == QAbstractSocket.IPv4Protocol and not address.isLoopback():
            return address.toString()

    return None


def get_LAN_broadcast_address(local_ip_address: str) -> str:
    '''
    Gets the local area network broadcast IP address.
    '''
    # Get all listings of network interfaces on the host machine
    interface_list = QNetworkInterface.allInterfaces()

    # For each entry in each interface, we want to see if the ip
    # matches our local ip address. If it does, we return the
    # broadcast address of that
    for interface in interface_list:
        for entry in interface.addressEntries():
            if entry.ip().toString() == local_ip_address:
                return entry.broadcast().toString()

    return None


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
    # is a server and the software then client.

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