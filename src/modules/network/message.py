from dataclasses import dataclass
import struct
from enum import Enum

class MessageCodes(Enum):
    DISCOVER = 0

@dataclass
class Message:
    code: int
    data: str

    def to_network_message(self):
        # Pack the message into 256 bytes in network byte ordering
        # ! - network byte ordering
        # H - unsigned short, 2 bytes by standard
        # 254s - 254 bytes (254 characters of a string)
        return struct.pack('!H254s', self.code, str.encode(self.data))

    