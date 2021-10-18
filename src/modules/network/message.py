from dataclasses import dataclass
import struct
from enum import Enum
from typing import List

class MessageCode(Enum):
    DISCOVER = 0

    # Docking Station Codes
    DOCK_DISCOVER_ACK           = 100
    CLONE_SFP_MEMORY            = 101
    CLONE_SFP_MEMORY_ERROR      = 102
    CLONE_SFP_MEMORY_SUCCESS    = 103
    REQUEST_SFP_PARAMETERS      = 104
    REQUEST_SFP_PARAMETERS_ACK  = 105

    # Cloudplug Codes
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
    code = MessageCode(code)
    sent_cmd = Message(code, str(data, 'utf-8').strip('\x00'))

    return sent_cmd

class MeasurementMessage:
    code: MessageCode
    data: List[int]

    def __init__(self, code=None, data=None):
        self.code = code
        self.data = data

    def to_network_message(self) -> bytes:
        return struct.pack('!H10B244s', self.code.value, *self.data, str.encode("0"))

    def __repr__(self):
        return f'{self.code},{self.data}'

def unpackMeasurementMessageBytes(raw_msg: bytes) -> MeasurementMessage:
    s = struct.unpack("!H10B244s", raw_msg)
    code = MessageCode(s[0])
    data = [int(val) for val in s[1:10 + 1]]

    sent_cmd = MeasurementMessage(code, data)

    return sent_cmd



    