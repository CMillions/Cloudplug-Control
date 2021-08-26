from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
import time

def get_local_ip_address() -> str:
    
    # Gets the list of all addresses on the host machine
    ip_list = QNetworkInterface.allAddresses()

    # For each address in the list, check if it's an IPv4
    # address and not a loopback address
    for address in ip_list:
        if address.protocol() == QAbstractSocket.IPv4Protocol and not address.isLoopback():
            return address.toString()

    return None


def get_local_broadcast_address(local_ip_address: str) -> str:

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

    # Has a tuple of 3 objects: (message contents in binary, QHostAddress object, port as an integer)
    device_response = pyqtSignal(object)

    def run(self):

        local_ip_str = get_local_ip_address()
        broadcast_ip_str = get_local_broadcast_address(local_ip_str)
        port = 7755

        bind_addr = QHostAddress(local_ip_str)
        broadcast_addr = QHostAddress(broadcast_ip_str)

        udp_socket = QUdpSocket()
        udp_socket.bind(bind_addr, port)

        byte_array = QByteArray()
        byte_array.append('DISCOVER')

        PACKET_SIZE = 255

        while True:
            # Write discovery message
            udp_socket.writeDatagram(byte_array, broadcast_addr, port)

            while udp_socket.hasPendingDatagrams():
                msg_tuple = udp_socket.readDatagram(PACKET_SIZE)

                binary_contents = msg_tuple[0]
                sender_ip_addr = msg_tuple[1].toString()

                if sender_ip_addr == local_ip_str:
                    break

                sender_port = msg_tuple[2]

                print(f'BroadcastThread:: {binary_contents}\t{sender_ip_addr}\t{sender_port}')

                # Emit response as a signal
                self.device_response.emit(msg_tuple)

            time.sleep(5)