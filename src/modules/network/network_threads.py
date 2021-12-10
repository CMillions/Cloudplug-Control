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
import logging
from typing import List

from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal, QByteArray
from PyQt5.QtNetwork import QUdpSocket, QHostAddress

from modules.network.message import MESSAGE_BYTES, Message, MessageCode, bytes_to_message
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
        self._TIMEOUT_MSEC = 2000

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
        #logging.debug('UDP Broadcast sent')

        # Restart the timer to infinitely do broadcast messages
        self._timer.start(self._TIMEOUT_MSEC)


    def cleanup(self):
        '''! This thread cleans up the worker object.
        @brief Stops the timer and closes the socket.
        '''
        self._timer.stop()
        self._sock.close()