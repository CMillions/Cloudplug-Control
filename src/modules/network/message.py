##
# @file message.py
# @brief Message codes for the CloudPlug network protocol.
#
# @section file_author Author
# - Created on 08/25/20
# @section mod_history Modification History
##


from dataclasses import dataclass
import struct
from enum import Enum
from typing import List

##
# @brief Codes for updating the user interface. Mostly used
#        for the diagnostic monitoring window since data has
#        to be exchanged over the network.
#
##

class MessageCode(Enum):
    DISCOVER = 0

    # Docking Station Codes
    DOCK_DISCOVER_ACK           = 100
    CLONE_SFP_MEMORY            = 101
    CLONE_SFP_MEMORY_ERROR      = 102
    CLONE_SFP_MEMORY_SUCCESS    = 103
    READ_SFP_REGISTERS          = 125
    READ_SFP_REGISTERS_ACK      = 126
    DIAGNOSTIC_INIT_A0          = 127
    DIAGNOSTIC_INIT_A0_ACK      = 128
    DIAGNOSTIC_INIT_A2          = 129
    DIAGNOSTIC_INIT_A2_ACK      = 130
    REAL_TIME_REFRESH           = 131
    REAL_TIME_REFRESH_ACK       = 132

    I2C_ERROR                   = 150


    # Cloudplug Codes
    CLOUDPLUG_DISCOVER_ACK = 200


MESSAGE_BYTES = 256
SIZEOF_H = 2

@dataclass
class Message:
    code: MessageCode
    data_str: str

    def to_network_message(self) -> bytes:
        # Pack the message into 256 bytes in network byte ordering
        # ! - network byte ordering
        # H - unsigned short, 2 bytes by standard
        # 254s - 254 bytes (254 characters of a string)
        return struct.pack(
            f'!H{MESSAGE_BYTES - SIZEOF_H}s', 
            self.code.value, 
            str.encode(self.data_str)
        )

def bytesToMessage(raw_msg: bytes) -> Message:
    code, data = struct.unpack(f'!H{MESSAGE_BYTES - SIZEOF_H}s', raw_msg)
    code = MessageCode(code)
    sent_cmd = Message(code, str(data, 'utf-8').strip('\x00'))

    return sent_cmd

@dataclass
class ReadRegisterMessage(Message):
    page_number:      int
    register_numbers: List[int]

    def to_network_message(self) -> bytes:
        '''! Converts an object of type ReadRegisterMessage into a bytes 
        object. The format string is dynamic, but packs 3 short integers
        (H) in network byte order, then the number of registers requested to
        read bytes (B), then the rest pad bytes (X). The maximum amount
        of bytes in a packet is 256.
        
        @return The class message packed into bytes
        '''
        num_registers_to_request = len(self.register_numbers)
        format_str = f"\!HHH{num_registers_to_request}B\{MESSAGE_BYTES - 3 * SIZEOF_H - num_registers_to_request}x"

        return struct.pack(
            format_str, 
            self.code.value, 
            self.page_number, 
            num_registers_to_request, 
            *self.register_numbers
        )

def bytesToReadRegisterMessage(raw_msg: bytes) -> ReadRegisterMessage:
    int_code, page_num, arr_len, *garbage = struct.unpack(f"!HHH{MESSAGE_BYTES - 3 * SIZEOF_H}x", raw_msg)
    format_str = f"!HHH{arr_len}B{MESSAGE_BYTES - 3 * SIZEOF_H - arr_len}x"
    int_code, page_num, arr_len, *data = struct.unpack(format_str, raw_msg)

    code = MessageCode(int_code)

    return ReadRegisterMessage(code, "", page_num, data)