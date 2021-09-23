from dataclasses import dataclass
import struct
from enum import Enum

class MessageCode(Enum):
    DISCOVER = 0
    DOCK_DISCOVER_ACK = 100
    CLOUDPLUG_DISCOVER_ACK = 200

@dataclass
class Message:
    code: MessageCode
    data: str

    def to_network_message(self) -> bytes:
        # Pack the message into 256 bytes in network byte ordering
        # ! - network byte ordering
        # H - unsigned short, 2 bytes by standard
        # 254s - 254 bytes (254 characters of a string)
        return struct.pack('!H254s', self.code.value, str.encode(self.data))

def unpackRawBytes(raw_msg: bytes) -> Message:
    code, data = struct.unpack('!H254s', raw_msg)
    sent_cmd = Message(code, str(data, 'utf-8').strip('\x00'))

    return sent_cmd

    