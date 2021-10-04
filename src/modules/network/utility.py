## @package utility
# Provides simple network utility functions.

from PyQt5.QtNetwork import QNetworkInterface, QAbstractSocket

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