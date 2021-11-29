##
# @file convert.py
# @brief Provides methods to convert individual bytes to different formats.
#
# @section file_author Author
# - Created on 07/29/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 07/29/2021 by Connor DeCamp
# - Modified on 09/13/2021 by Connor DeCamp
# - Modified on 10/14/2021 by Connor DeCamp
# - Modified on 11/04/2021 by Connor DeCamp 
#
# See SFF-8472 for tables that determine what each
# value means in the memory map.
##

from decimal import *
from typing import List
import binary_fractions
from binary_fractions import binary

def ieee754_to_decimal(b3: int, b2: int, b1: int, b0: int) -> Decimal:
    '''! Takes 4 bytes in IEEE 754 floating point format and converts it into a floating point
    number as per the IEEE 754 specification. The MSB (bit 31) is the sign bit,
    bits 2-9 are the exponent, and the rest belong to the mantissa.

    S = sign
    E = Exponent
    M = Mantissa
    
    (Byte, Contents, Significance)
    (b3,     SEEEEEEE,       most)
    (b2,     EMMMMMMM,    second most)
    (b1,     MMMMMMMM,    second least)
    (b0,     MMMMMMMM,       least)

    @param b3 Most significant byte
    @param b2 Second most significant byte
    @param b1 Second least significant byte
    @param b0 Least significant byte
    @return A signed floating point value
    '''

    # Put bytes into array to make it easier to
    # convert into binary string
    bytelist = [b3, b2, b1, b0]
    s = ""
    for b in bytelist:
        s += format(b, '08b')        # Format each number in binary

    sign = int(s[0:1])               # Sign is the first bit
    exponent = int(s[1:9], 2) - 127  # Exponent is the next 8 bits, subtract 127 to unbias it
    mantissa_str = s[9:32]           # Mantissa (fraction) is the rest of the number (1.M)
    mantissa_int = Decimal('1')      # Begin converting mantissa bits into fraction
    power = -1                       # We need 1.M, so first power is 2^(-1) * bit and decreases from there

    for bit in mantissa_str:
        mantissa_int += Decimal(str(int(bit) * (2 ** power)))
        power -= 1
    

    result = Decimal(pow(-1, int(sign))) * Decimal(pow(2, exponent)) * mantissa_int # (-1)^sign * 2^(exponent) * 1.M
    
    return result

def slope_bytes_to_unsigned_decimal(b1: int, b0: int) -> Decimal:
    '''!Takes in 2 bytes, formatted as b1.b0 and returns the
    unsigned decimal equivalent.

    @param b1 Most significant byte
    @param b0 Least significant byte
    '''
    b1 &= 0xFF
    b0 &= 0xFF

    b1_weights = [128, 64, 32, 16, 8, 4, 2, 1]
    b0_weights = [1/2.0, 1/4.0, 1/8.0, 1/16.0, 1/32.0, 1/64.0, 1/128.0, 1/256.0]

    ans = 0
    mask = 0x80
    i = 0
    while mask > 0:
        if b1 & mask:
            ans += b1_weights[i]
        if b0 & mask:
            ans += b0_weights[i]
        mask = mask >> 1
        i += 1

    return ans

def temperature_bytes_to_signed_twos_complement_decimal(b1: int, b0: int) -> float:
    '''! Takes in 2 bytes, formatted as b1.b0 and returns the
    signed two's complement decimal equivalent.

    @param b1 Most significant byte
    @param b0 Least significant byte
    
    @return A float in the range [-127.996, +127.996]
    '''
    b1 &= 0xFF
    b0 &= 0xFF

    b1_weights = [64, 32, 16, 8, 4, 2, 1]
    b0_weights = [1/2.0, 1/4.0, 1/8.0, 1/16.0, 1/32.0, 1/64.0, 1/128.0, 1/256.0]

    sign = ((b1 & 0x80) >> 7)
    ans = 0

    # Start with 0b0100 0000 since the
    # first bit is the sign
    b1_mask = 0x40
    i = 0
    while b1_mask > 0:
        if b1 & b1_mask:
            ans += b1_weights[i]
        b1_mask = b1_mask >> 1
        i += 1

    b0_mask = 0x80
    i = 0
    while b0_mask > 0:
        if b0 & b0_mask:
            ans += b0_weights[i]
        
        b0_mask = b0_mask >> 1
        i += 1

    if sign == 1:
        ans = ans - 128

    return ans

def offset_bytes_to_signed_twos_complement_int(b1: int, b0: int) -> int:
    '''! Converts two bytes formatted as b1 b0 in signed twos complement and
    converts them to an integer.

    @param b1 Most significant byte
    @param b0 Least significant byte

    @return An integer in the range [-32768, +32767]
    '''
    b1 &= 0xFF
    b0 &= 0xFF

    ans = 0x0000
    ans += (b1 << 8) | b0
    sign = (ans & 0x8000) >> 15

    if sign == 1:
        ans = ans - 65536

    return ans


def bytes_to_tec_current(b1: int, b0: int) -> float:
    '''! Converts bytes that represent TEC current to the actual
    TEC current value.

    @param b1 Most significant byte
    @param b0 Least significant byte
    @return A value in the range [-3276.8, 3276.7]
    '''

    return offset_bytes_to_signed_twos_complement_int(b1, b0) / 10.0


def unsigned_decimal_to_bytes(number: Decimal) -> List[int]:
    '''!Converts a number in the range [0, 255.9961]
    into two bytes, b1.b0.

    @param number The number to be converted
    @return A list containing the two bytes [b1, b0]
    '''

    if number < 0 or number > 255.9961:
        raise ValueError("Invalid number received")

    b = str(binary_fractions.Binary(number))
    b = b.strip("0b")
    b = b.split('.')
    
    b1 = int(b[0][0:8],base=2)
    b0 = int(b[1][0:8],base=2)

    return [b1, b0]


def float_to_signed_twos_complement_bytes(number: float) -> List[int]:
    '''!Converts a number in the range [-127.996, 127.996]
    into two bytes, b1.b0 using signed two's complement.

    @param number The floating point value to be converted
    @return A list containing the two bytes [b1, b0]
    '''

    MIN = -127.99609375
    MAX = 127.99609375

    if number < MIN or number > MAX:
        raise ValueError(f"Number must be in range [{MIN}, {MAX}]")

    bin_str = str(binary_fractions.TwosComplement(number))
    bin_str = bin_str.split('.')


    if len(bin_str) < 2:
        bin_str.append('00000000')

    pad_b1 = 0
    pad_b0 = 0

    if len(bin_str[0]) < 8:
        pad_b1 = 8 - len(bin_str[0])

    if len(bin_str[1]) < 8:
        pad_b0 = 8 - len(bin_str[1])

    pad_char = "0"

    if number < 0:
        pad_char = "1"

    for i in range(pad_b1):
        bin_str[0] = pad_char + bin_str[0]    

    for i in range(pad_b0):
        bin_str[1] += "0"


    b1 = int(bin_str[0][0:8], base=2)
    b0 = int(bin_str[1][0:8], base=2)

    return [b1, b0]

def float_to_unsigned_decimal_bytes(number: float) -> List[int]:
    '''! Converts a number in the range [0, 65535] to
    a sixteen bit unsigned decimal representation b1b0.

    @param number The floating point number to convert
    @return A list [b1, b0] of bytes that when formatted as b1b0 is the binary
    representation of the input number.
    '''

    if number < 0 or number > 65535:
        raise ValueError(f'{number} is not in the range [0, 65535]')


    b1 = int(number) >> 8 & 0xFF
    b0 = int(number) & 0x00FF

    return [b1, b0]

if __name__ == '__main__':
    b1, b0 = float_to_unsigned_decimal_bytes(7020.1)

    b1,b0 = float_to_signed_twos_complement_bytes(-4.2)

    #print(b1, b0)


    #print(binary_fractions.TwosComplement(-4.2))
    #print(temperature_bytes_to_signed_twos_complement_decimal(251, 204))