##
# @file convert.py
# @brief Provides methods to convert individual bytes to different formats.
#
# @section file_author Author
# - Created on 07/29/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 07/29/2021 by Connor DeCamp 
#
# See SFF-8472 for tables that determine what each
# value means in the memory map.
##

from decimal import *

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
