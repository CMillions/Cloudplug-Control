##
# @file test_sfp_methods.py
# @brief Unit tests for the methods of the SFP class.
#
##

import unittest
import sys, os, time

# This is here to make the import work when ran from the main folder
# in VSCode
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from modules.core.sfp import SFP

class TestSFPMethods(unittest.TestCase):
    '''
    Tests the methods from the SFP module. The data used is from a Menara Networks SFP.

    Menara Networks 10GBASE-SR SFP+, 850nm 300m I-temp, 5SR0P2U-0850, S/N: NG5F23535
    '''
    def setUp(self):
        '''
        Creates an SFP object using memory values from the Menara Networks 10GBASE-SR SFP+,
        850nm 300m I-temp, 5SR0P2U-0850, S/N: NG5F23535
        '''
        a0_list = [3,4,7,16,0,0,0,0,0,6,0,6,103,0,0,0,8,2,0,30,77,69,78,65,82,65,32,78,69,84,87,79,82,75,83,32,0,0,0,0,53,83,82,48,80,50,85,45,48,56,53,48,32,32,32,32,65,32,32,32,3,82,0,123,0,26,0,0,78,71,53,70,50,51,53,51,53,32,32,32,32,32,32,32,49,54,49,48,49,50,32,32,104,240,3,210,0,0,17,121,242,178,32,182,249,51,27,119,111,227,226,82,152,4,109,0,0,0,0,0,0,0,0,0,213,212,199,223,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255]
        a2_list = [90,0,216,0,85,0,221,0,140,159,117,48,136,184,121,23,29,76,1,244,25,100,3,232,43,212,7,70,39,16,9,40,43,212,2,133,39,16,3,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,63,128,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,45,22,229,128,28,12,55,21,230,0,1,0,0,0,0,2,0,0,64,0,0,0,64,0,0,0,0,0,0,0,0,0,0,67,79,85,73,65,77,51,67,65,66,49,48,45,50,52,49,53,45,48,51,86,48,51,32,1,0,70,0,0,0,0,193,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,170,170,83,70,80,45,49,48,71,45,83,82,32,32,32,32,32,32,32,32,32,32,49,51,0,0,0,0,0,0,0,0,0,52,21,26,32,36,42,48,32,48,0,0,0,0,0,0,0,0,0,0,0,0,0,29,0,0,0,0,0,0,0,0,73,35]
        self.sfp = SFP(a0_list, a2_list)

    def test_get_identifier(self):
        test_value = self.sfp.get_identifier()
        expected_value = 'SFP/SFP+/SFP28 and later'
        
        self.assertEqual(test_value, expected_value)

    def test_get_ext_identifier(self):
        test_value = self.sfp.get_ext_identifier()
        expected_value = 'Function defined by 2-wire interface ID only'

        self.assertEqual(test_value, expected_value)

    def test_get_connector_type(self):
        test_value = self.sfp.get_connector_type()
        expected_value = 'LC (Lucent Connector)'
        
        self.assertEqual(test_value, expected_value)

    def test_get_transceiver_info(self):
        
        #Tests the get_transceiver_info() method
        test_transceiver_info = self.sfp.get_transceiver_info()
        
        expected_transceiver_info = ['10GBASE-SR', 'Multimode, 62.5um (M6)', 'Multimode, 50um (M5, M5E)']

        self.assertEqual(test_transceiver_info, expected_transceiver_info)

    def test_get_encoding(self):
        test_value = self.sfp.get_encoding()
        expected_value = '64B/66B (8472) or Manchester (8436/8636)'
        self.assertEqual(test_value, expected_value)

    def test_get_signaling_rate_nominal(self):
        
        # Tests the get_signaling_rate_nominal() method. Units are in
        # 100 MBaud
        
        test_value = self.sfp.get_signaling_rate_nominal()
        expected_value = 103

        self.assertEqual(test_value, expected_value)

    def test_get_rate_identifier(self):
        '''
        '''
        test_value = self.sfp.get_rate_identifier()
        expected_value = 'Unspecified'

        self.assertEqual(test_value, expected_value)

    def test_get_smf_link_length(self):
        
        #Tests the get_smf_link_length() method.
        
        #The tested method returns the link length supported for 
        #single-mode fiber, units of 100m, or copper cable 
        #attenuation in dB at 25.78 GHz. I don't know how
        #to tell which one it is.
        
        test_value = self.sfp.get_smf_link_length()
        expected_value = 0

        self.assertEqual(test_value, expected_value)

    def test_get_om2_link_length(self):
        test_value = self.sfp.get_om2_link_length()
        expected_value = 8

        self.assertEqual(test_value, expected_value)

    def test_get_om1_link_length(self):
        test_value = self.sfp.get_om1_link_length()
        expected_value = 2

        self.assertEqual(test_value, expected_value)

    def test_get_om4_link_length(self):
        test_value = self.sfp.get_om4_link_length()
        expected_value = 0

        self.assertEqual(test_value, expected_value)

    def test_get_om3_link_length(self):
        test_value = self.sfp.get_om3_link_length()
        expected_value = 30

        self.assertEqual(test_value, expected_value)

    def test_get_vendor_name(self):
        # Testing that bytes [20,36] of page A0 are correct
        # Note that this means the name must be 16 characters long
        test_vendor_name = self.sfp.get_vendor_name()
        expected_vendor_name = 'MENARA NETWORKS '
        self.assertEqual(test_vendor_name, expected_vendor_name)

    def test_get_transceiver2(self):
        test_value = self.sfp.get_transceiver2()
        expected_value = 'Unspecified'

        self.assertEqual(test_value, expected_value)

    def test_get_vendor_oui(self):
        test_value = self.sfp.get_vendor_oui()
        expected_value = [0, 0, 0]

        self.assertEqual(test_value, expected_value)

    def test_get_vendor_part_number(self):
        test_value = self.sfp.get_vendor_part_number()
        # Note that the expected value is 16 characters, which
        # is why there are spaces at the end of the string
        expected_value = '5SR0P2U-0850    '

        self.assertEqual(test_value, expected_value)

    def test_get_vendor_revision_level(self):
        test_value = self.sfp.get_vendor_revision_level()
        # The revision level field is 4 bytes (4 characters) which
        # is why there are extra spaces at the end of the expected
        # value
        expected_value = 'A   '

        self.assertEqual(test_value, expected_value)

    def test_get_wavelength(self):
        test_value = self.sfp.get_wavelength()
        expected_value = 850
        
        self.assertEqual(test_value, expected_value)

def print_sfp_memory(sfp: SFP):
    for i in range(256):
        print(chr(sfp.page_a0[i]), end='')

        if i and i % 16 == 0:
            print()


if __name__ == '__main__':

    log_file = './log_file.txt'
    with open(log_file, 'w') as file:

        now = time.localtime()
        
        date_str = f'Tests ran on {now.tm_mon:02}/{now.tm_mday:02}/{now.tm_year:02} at {now.tm_hour:02}:{now.tm_min:02}\n'
        separator_str = '{s:{c}^{n}}'.format(s='=', c='=',n=len(date_str) - 1) + '\n\n'

        file.write(date_str)
        file.write(separator_str)

        runner = unittest.TextTestRunner(file, descriptions=True, verbosity=2)
        unittest.main(testRunner = runner)
