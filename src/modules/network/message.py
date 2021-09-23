from dataclasses import dataclass
import struct
from enum import Enum

class MessageCode(Enum):
    DISCOVER = 0

@dataclass
class Message:
    code: MessageCode
    data: str

    def to_network_message(self):
        # Pack the message into 256 bytes in network byte ordering
        # ! - network byte ordering
        # H - unsigned short, 2 bytes by standard
        # 254s - 254 bytes (254 characters of a string)
        return struct.pack('!H254s', self.code.value, str.encode(self.data))

    