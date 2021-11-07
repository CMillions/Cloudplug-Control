##
# @file test_conversions.py
# @brief Unit tests for the convert module.
#
# @section file_author Author
# - Created on 10/21/21 by Connor DeCamp
##

import os
import sys
import unittest


from decimal import Decimal

# This is here to make the import work when ran from the main folder
# in VSCode
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')


from modules.core.convert import bytes_to_tec_current, float_to_signed_twos_complement_bytes, float_to_unsigned_decimal_bytes
from modules.core.convert import offset_bytes_to_signed_twos_complement_int
from modules.core.convert import slope_bytes_to_unsigned_decimal
from modules.core.convert import temperature_bytes_to_signed_twos_complement_decimal
from modules.core.convert import ieee754_to_decimal

class TestConvertMethods(unittest.TestCase):
    '''! Defines the unit tests for the convert package.'''

    def test_slope_bytes_to_unsigned_decimal(self):
        '''! Tests the method slope_bytes_to_unsigned_decimal()'''
        DELTA = 0.004

        self.assertEqual(0.0, slope_bytes_to_unsigned_decimal(0x00, 0x00))
        self.assertAlmostEqual(0.0039, slope_bytes_to_unsigned_decimal(0x00, 0x01), delta=DELTA)
        self.assertAlmostEqual(1.0, slope_bytes_to_unsigned_decimal(0x01, 0x00), delta=DELTA)
        self.assertAlmostEqual(1.0313, slope_bytes_to_unsigned_decimal(0x01, 0x08), delta=DELTA)
        self.assertAlmostEqual(1.9961, slope_bytes_to_unsigned_decimal(0x01, 0xFF), delta=DELTA)
        self.assertEqual(2.0, slope_bytes_to_unsigned_decimal(0x02, 0x00))
        self.assertAlmostEqual(255.9921, slope_bytes_to_unsigned_decimal(0xFF, 0xFE), delta=DELTA)
        self.assertAlmostEqual(255.9961, slope_bytes_to_unsigned_decimal(0xFF, 0xFF), delta=DELTA)


    def test_temperature_bytes_to_signed_twos_complement_decimal(self):
        '''! Tests the method temperature_bytes_to_signed_twos_complement_decimal()'''

        # The numbers here are expected to range from [-127.996, +127.996]
        # It is calculated using two 1-byte words, b1 and b0
        # ====D==== ====C====
        # 1111 1111.1111 1111
        #
        # The MSB (D7) is the sign bit
        #
        #
        # The bit weights for D are then
        # Sign 128 64 32 16 8 4 2 1
        #
        # For byte C
        # 1/2  1/4  1/8  1/16  1/32  1/64  1/128  1/258

        # The maximum granularity of the measurements
        # for temperature (16 bit signed twos complement)
        DELTA = 0.004

        self.assertEqual(0.0, temperature_bytes_to_signed_twos_complement_decimal(0x00, 0x00))
        self.assertEqual(127.0, temperature_bytes_to_signed_twos_complement_decimal(0x7F, 0x00))
        self.assertEqual(0.5, temperature_bytes_to_signed_twos_complement_decimal(0x00, 0x80))
        self.assertAlmostEqual(127.997, temperature_bytes_to_signed_twos_complement_decimal(0x7F, 0xFF), delta=DELTA)
        self.assertEqual(125.0, temperature_bytes_to_signed_twos_complement_decimal(0x7D, 0x00))
        self.assertEqual(25.0, temperature_bytes_to_signed_twos_complement_decimal(0x19, 0x00))
        self.assertAlmostEqual(1.004, temperature_bytes_to_signed_twos_complement_decimal(0x01, 0x01), delta=DELTA)
        self.assertEqual(1.0, temperature_bytes_to_signed_twos_complement_decimal(0x01, 0x00))
        self.assertAlmostEqual(0.996, temperature_bytes_to_signed_twos_complement_decimal(0x00, 0xFF), delta=DELTA)
        self.assertAlmostEqual(0.004, temperature_bytes_to_signed_twos_complement_decimal(0x00, 0x01), delta=DELTA)
        self.assertAlmostEqual(-0.004, temperature_bytes_to_signed_twos_complement_decimal(0xFF, 0xFF), delta=DELTA)
        self.assertEqual(-1.0, temperature_bytes_to_signed_twos_complement_decimal(0xFF, 0x00))
        self.assertEqual(-25.0, temperature_bytes_to_signed_twos_complement_decimal(0xE7, 0x00))
        self.assertEqual(-40.0, temperature_bytes_to_signed_twos_complement_decimal(0xD8, 0x00))
        self.assertAlmostEqual(-127.996, temperature_bytes_to_signed_twos_complement_decimal(0x80, 0x01), delta=DELTA)

    def test_offset_bytes_to_signed_twos_complement_int(self):
        '''! Tests the method offset_bytes_to_signed_twos_complement_int()'''

        self.assertEqual(32767, offset_bytes_to_signed_twos_complement_int(0x7F, 0xFF))
        self.assertEqual(3, offset_bytes_to_signed_twos_complement_int(0x00, 0x03))
        self.assertEqual(2, offset_bytes_to_signed_twos_complement_int(0x00, 0x02))
        self.assertEqual(1, offset_bytes_to_signed_twos_complement_int(0x00, 0x01))
        self.assertEqual(0, offset_bytes_to_signed_twos_complement_int(0x00, 0x00))
        self.assertEqual(-1, offset_bytes_to_signed_twos_complement_int(0xFF, 0xFF))
        self.assertEqual(-2, offset_bytes_to_signed_twos_complement_int(0xFF, 0xFE))
        self.assertEqual(-3, offset_bytes_to_signed_twos_complement_int(0xFF, 0xFD))
        self.assertEqual(-32768, offset_bytes_to_signed_twos_complement_int(0x80, 0x00))

    def test_bytes_to_tec_current(self):
        '''! Tests the method bytes_to_tec_current()'''

        DELTA = 0.1

        self.assertAlmostEqual(3276.7, bytes_to_tec_current(0x7F, 0xFF), delta=DELTA)
        self.assertAlmostEqual(3200.0, bytes_to_tec_current(0x7D, 0x00), delta=DELTA)
        self.assertAlmostEqual(640.0, bytes_to_tec_current(0x19, 0x00), delta=DELTA)
        self.assertAlmostEqual(25.7, bytes_to_tec_current(0x01, 0x01), delta=DELTA)
        self.assertAlmostEqual(25.6, bytes_to_tec_current(0x01, 0x00), delta=DELTA)
        self.assertAlmostEqual(25.5, bytes_to_tec_current(0x00, 0xFF), delta=DELTA)
        self.assertAlmostEqual(0.1, bytes_to_tec_current(0x00, 0x01), delta=DELTA)
        self.assertAlmostEqual(0.0, bytes_to_tec_current(0x00, 0x00), delta=DELTA)
        self.assertAlmostEqual(-0.1, bytes_to_tec_current(0xFF, 0xFF), delta=DELTA)
        self.assertAlmostEqual(-25.6, bytes_to_tec_current(0xFF, 0x00), delta=DELTA)
        self.assertAlmostEqual(-640.0, bytes_to_tec_current(0xE7, 0x00), delta=DELTA)
        self.assertAlmostEqual(-1024.0, bytes_to_tec_current(0xD8, 0x00), delta=DELTA)
        self.assertAlmostEqual(-3276.7, bytes_to_tec_current(0x80, 0x01), delta=DELTA)
        self.assertAlmostEqual(-3276.8, bytes_to_tec_current(0x80, 0x00), delta=DELTA)

    def test_ieee_754_to_decimal(self):
        '''! Tests the method ieee_754_to_decimal()'''
        
        DELTA = 0.1
        self.assertAlmostEqual(Decimal(1.02), ieee754_to_decimal(0x3F, 0x82, 0x8F, 0x5C), delta=DELTA)
        self.assertAlmostEqual(Decimal(589302.2), ieee754_to_decimal(0x49, 0x0F, 0xDF, 0x63), delta=DELTA)
        self.assertAlmostEqual(Decimal(-2004.12304), ieee754_to_decimal(0xC4, 0xFa, 0x83, 0xF0), delta=DELTA)
        self.assertAlmostEqual(Decimal(-0.000001), ieee754_to_decimal(0xB5, 0x86, 0x37, 0xBD), delta=DELTA)
        self.assertAlmostEqual(Decimal(44444.44444), ieee754_to_decimal(0x47, 0x2D, 0x9C, 0x72), delta=DELTA)

    def test_float_to_signed_twos_complement_bytes(self):
        
        DELTA = 1/256.0

        i = -127.996

        while i < 128:
            b1,b0 = float_to_signed_twos_complement_bytes(i)
            re_converted = temperature_bytes_to_signed_twos_complement_decimal(b1, b0)
            self.assertAlmostEqual(i, re_converted, delta=DELTA)
            i += 1

if __name__ == '__main__':
    unittest.main()
        
