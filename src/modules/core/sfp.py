##
# @file sfp.py
# @brief Module for interpreting the memory maps of SFP+ devices.
# @section file_author Author
# - Created by Connor DeCamp on 07/15/2021
# @section mod_history Modification History
# - Modified by Connor DeCamp on 07/19/2021
# - Modified by Connor DeCamp on 07/20/2021
# - Modified by Connor DeCamp on 07/27/2021
# - Modified by Connor DeCamp on 07/28/2021
# - Modified by Connor DeCamp on 07/29/2021
# - Modified by Connor DeCamp on 10/01/2021
# - Modified by Connor DeCamp on 10/18/2021
# - Modified by Connor DeCamp on 10/20/2021
# - Modified by Connor DeCamp on 10/27/2021
##

from typing import List
from modules.core.convert import *
from enum import Enum

class SFP:
    '''! Class used for interpreting EEPROM values of SFP+ modules.
    Has two lists of integers that represent the memory map
    of SFP/SFP+ modules. These are referred to by the I2C address of
    the memory, 0xA0 and 0xA2. These are sometimes referred to as 0x50 and 0x51,
    respective. The change is due to the 7-bit addressing supported by SFP+ modules.
    '''

    # Enumeration for SFP Diagnostic Monitoring types,
    # whether values are internally or externally calibrated
    class CalibrationType(Enum):
        '''! Enumeration for SFP+ calibration types. Modules can
        be either internally and externally calibrated.
        '''
        UNKNOWN = 0,
        INTERNAL = 1,
        EXTERNAL = 2

    ## Holds the data values from page 0xA0 of the SFP memory map
    page_a0 : List[int]

    ## Holds the data values from page 0xA2 of the SFP memory map
    page_a2 : List[int]

    ## Dictionary of memory pages
    memory_pages: dict

    ## Holds the calibration type of the module
    calibration_type: CalibrationType = CalibrationType.UNKNOWN

    def __init__(self, page_a0: List[int], page_a2: List[int]):
        '''! Initalizes the SFP module

        @param page_a0 Array of integers that hold the 0xA0 memory page of an SFP+ EEPROM
        @param page_a2 Array of integers that hold the 0xA2 memory page of an SFP+ EEPROM

        '''
        self.memory_pages = {}

        self.page_a0 = page_a0
        self.page_a2 = page_a2

        self.add_memory_page(0xA0, page_a0)
        self.add_memory_page(0xA2, page_a2)

        # Sets the calibration type flag for use in
        # the calculation functions

        EXTERNAL_CALIBRATION_FLAG = self.page_a0[92] & 0x20
        INTERNAL_CALIBRATION_FLAG = self.page_a0[92] & 0x10

        if EXTERNAL_CALIBRATION_FLAG:
            self.calibration_type = self.CalibrationType.INTERNAL
        elif INTERNAL_CALIBRATION_FLAG:
            self.calibration_type = self.CalibrationType.EXTERNAL
        else:
            print("WARNING: Invalid SFP calibration type. Is the memory valid?")

    def add_memory_page(self, page_code: int, page_values: List[int]) -> None:
        '''! Associates a hex value key with a list of integers that represent a memory page from SFP+ EEPROM.

            @param page_code An integer, may be given as hex
            @param page_values A list of integers that represent that page of EEPROM
        '''
        self.memory_pages[page_code] = page_values

    def get_page(self, page_number: int) -> List[int]:
        '''! Gets the requested page number from the memory pages dictionary

            @return The list of integers from the associated page number key
        '''
        return self.memory_pages[page_number]

    def get_page_a0(self) -> List[int]:
        return self.page_a0

    # From Table 5-1 and Table 4-1 from SFF 8024
    def get_identifier(self) -> str:
        '''
        Returns the type of transceiver the module has.
        Uses byte 0 of page 0xA0.
        '''
        # Use the id_code as an index into array
        # of strings for identifier type
        id_code = self.page_a0[0]

        result = [
                'Unknown or unspecified',
                'GBIC',
                'Module/connector soldered to motherboard',
                'SFP/SFP+/SFP28 and later',
                '300 pin XBI',
                'XENPAK',
                'XFP',
                'XFF',
                'XFP-E',
                'XPAK',
                'X2',
                'DWDM-SFP/SFP+ (not using SFF-8472)',
                'QSFP (INF-8438)',
                'QSFP+ or later with SFF-8636 or SFF-8436 management interface',
                'CXP or later',
                'Shielded Mini Multilane HD 4X',
                'Shielded Mini Multilane HD 8X',
                'QSFP28 or later with SFF-8636 management interface',
                'CXP2 (aka CXP28) or later',
                'CDFP (Style 1 / Style 2)',
                'Shielded Mini Multilane HD 4X Fanout Cable',
                'Shielded Mini Multilane HD 8X Fanout Cable',
                'CDFP (Style 3)',
                'microQSFP',
                'QSFP-DD Double Density 8X Pluggable Transceiver (INF-8628)',
                'QSFP 8X Pluggable Transceiver',
                'SFP-DD Double Density 2X Pluggable Transceiver',
                'DSFP Dual Small Form Factor Pluggable Transceiver',
                'x4 MiniLink/OcuLink',
                'x8 MiniLink',
                'QSFP+ or later with CMIS'
        ]

        if id_code <= 0x1E:
            return result[id_code]
        elif id_code <= 0x7F:
            return "Reserved"
        else:
            return "Vendor specific"

    # From Table 5-2
    def get_ext_identifier(self) -> str:
        
        possible = [
            "GBIC Definition not specified/not compliant with a defined MOD_DEF",
            "Compliant with MOD_DEF1",
            "Compliant with MOD_DEF2",
            "Compliant with MOD_DEF3",
            "Function defined by 2-wire interface ID only",
            "Compliant with MOD_DEF5",
            "Compliant with MOD_DEF6",
            "Compliant with MOD_DEF7"
        ]
        
        ext_id_code = self.page_a0[1]

        if ext_id_code <= 0x07:
            return possible[ext_id_code]
        else:
            return "Reserved"

    # From SFF-8024 Table 4-3
    def get_connector_type(self) -> str:
        code = self.page_a0[2]

        result = [
            'Unknown or unspecified',
            'SC (Subscriber Connector)',
            'Fibre Channel Style 1 copper connector',
            'Fibre Channel Style 2 copper connector',
            'BNC/TNC (Bayonet/Threaded Neill-Concelman)',
            'Fibre Channel coax headers',
            'Fibre Jack',
            'LC (Lucent Connector)',
            'MT-RJ (Mechanical Transfer - Registered Jack)',
            'MU (Multiple Optical)',
            'SG',
            'Optical Pigtail',
            'MPO 1x12 (Multifiber Parallel Optic)',
            'MPO 2x16']
        
        result2 = [
            'HSSDC II (High Speed Serial Data Connector)',
            'Copper Pigtail',
            'RJ45 (Registered Jack)',
            'No seperable connector',
            'MXC 2x16',
            'CS optical connector',
            'SN (previously Mini CS) optical connector',
            'MPO 2x12',
            'MPO 1x16',
        ]

        if code < 0x0E:
            return result[code]
        elif (code >= 0x0E and code <= 0x1F) or (code >= 0x29 and code <= 0x7F):
            return "Reserved"
        elif code > 0x1F and code < 0x29:
            print(f'{code - 0x20 = }')
            return result2[code - 0x20]
        else:
            return "Vendor specific"

    # See comments in method
    def get_transceiver_info(self) -> List[str]:
        """
        Returns the optical/electronic compatibility of the transceiver.
        """      
        # Starting at page 0xA0 byte 3, bytes 3-10 are used
        # to define the transceiver compliance

        # These arrays hold codes that represent the value for each
        # bit that is set in the corresponding byte. For example,
        # byte_three_codes[0] is the value we get when bit 0 of byte 3
        # is set, so if we had 0b00000001 we would add '1X Copper Passive'
        # to the transceiver type
        byte_three_codes = [
            '1X Copper Passive',
            '1X Copper Active',
            '1X LX',
            '1X SX',
            '10GBASE-SR',
            '10GBASE-LR',
            '10GBASE-LRM',
            '10GBASE-ER'
        ]

        byte_four_codes = [
            'OC-48 short reach',
            'OC-48 intermediate reach',
            'OC-48 long reach',
            'SONET reach specifier bit 2',
            'SONET reach specifier bit 1',
            'OC-192, short reach',
            'ESCON SMF, 1310nm Laser',
            'ESCON MMF, 1310nm LED'
        ]

        byte_five_codes = [ 
            'OC-3, short reach',
            'OC-3, single mode, intermediate reach',
            'OC-3, single mode, long reach',
            'Reserved',
            'OC-12, short reach',
            'OC-12, single mode, intermediate reach',
            'OC-12, single mode, long reach',
            'Reserved'
        ]

        byte_six_codes = [
            '1000BASE-SX',
            '1000BASE-LX',
            '1000BASE-CX',
            '1000BASE-T',
            '100BASE-LX/LX10',
            '100BASE-FX',
            'BASE_BX10',
            'BASE-PX',
        ]

        byte_seven_codes = [ 
            'Electrical inter-enclosure (EL)',
            'Longwave laser (LC)',
            'Shortwave laser, linear Rx (SA)',
            'medium distance (M)',
            'long distance (L)',
            'intermediate distance (I)',
            'short distance (S)',
            'very long distance (V)',
        ]

        byte_eight_codes = [
            'Reserved'
            'Reserved',
            'Passive Cable',
            'Active Cable',
            'Longwave laser (LL)',
            'Shortwave laser with OFC (SL)',
            'Shortwave laser w/o OFC (SN)',
            'Electrical intra-enclosure (EL)',
        ]


        byte_nine_codes = [
            'Single Mode (SM)'
            'Reserved',
            'Multimode, 50um (M5, M5E)',
            'Multimode, 62.5um (M6)',
            'Video Coax (TV)',
            'Miniature Coax (MI)',
            'Twisted Pair (TP)',
            'Twin Axial Pair (TW)',
        ]

        byte_ten_codes = [
            '100 MBytes/sec'
            'See byte 62 "Fibre Channel Speed 2"',
            '200 MBytes/sec',
            '3200 MBytes/sec',
            '400 MBytes/sec',
            '1600 MBytes/sec',
            '800 MBytes/sec',
            '1200 MBytes/sec',
        ]

        code_dict = {}
        code_dict[3] = byte_three_codes
        code_dict[4] = byte_four_codes
        code_dict[5] = byte_five_codes
        code_dict[6] = byte_six_codes
        code_dict[7] = byte_seven_codes
        code_dict[8] = byte_eight_codes
        code_dict[9] = byte_nine_codes
        code_dict[10] = byte_ten_codes

        compliant_with : List[str] = []


        # Mask starts at bit 7 and checks down to bit
        # 0. If any are true (!= 0) then we append the
        # corresponding id to the compliance list
        
        for byte in range(3, 11):
            mask = 0b10000000

            for i in range(7, -1, -1):            
                
                # If we take perform (byte AND mask) / mask, we will get either
                # zero or one

                if (self.page_a0[byte] & mask) // mask == 1:
                    compliant_with.append(code_dict[byte][i])

                mask = mask // 2

        return compliant_with

    def get_encoding(self) -> str:
        '''
        Returns the encoding method of the SFP. Values are
        from SFF-8024 Table 4-2. Uses byte 11 of page 0xA0
        '''

        encoding = [
            'Unspecified',
            '8B/10B',
            '4B/5B',
            'NRZ',
            'Manchester (8472) or SONET Scrambled (8436/8636)',
            'SONET Scrambled (8472) or 64B/66B (8436/8636)',
            '64B/66B (8472) or Manchester (8436/8636)',
            '256B/257B (transcoded FEC-enabled data)',
            'PAM4',
        ]

        code = self.page_a0[11]

        if code < 0x09:
            return encoding[code]
        else:
            return 'Reserved'

    def get_signaling_rate_nominal(self) -> int:
        '''
        Returns the nominal signaling rate in units of 100 MBaud.
        '''
        return self.page_a0[12]
    
    def get_rate_identifier(self) -> str:

        rates = [
            'Unspecified',
            'SFF-8079 (4/2/1G Rate_Select & AS0/AS1)',
            'SFF-8431 (8/4/2G Rx Rate_Select only)',
            'Unspecified',
            'SFF-8431 (8/4/2G Tx Rate_Select only)',
            'Unspecified',
            'SFF-8431 (8/4/2G Independent Rx & Tx Rate_Select)',
            'Unspecified',
            'FC-PI-5 (16/8/4G Independent Rx, Tx Rate_Select) High=16G only, Low=8G/4G',
            'Unspecified',
            'FC-PI-6 (32/16/8G Independent Rx, Tx Rate_Select) High=32G only, Low=16G/8G',
            'Unspecified',
            '10/8G Rx and Tx Rate_Select...',
            'Unspecified',
            'FC-PI-7 (64/32/16G Independent Rx, Tx Rate Select) High = 32GFC and 64GFC. Low = 16GFC',
            'Unspecified'
        ]

        code = self.page_a0[13]

        if code < 0x12:
            return rates[code]
        elif (code >= 0x12 and code <= 0x1F) or (code >= 0x21 and code <= 0xFF):
            return 'Reserved'
        elif code == 0x20:
            return 'Rate select based on PMDs as defined by 0xA0, byte 36 and 0xA2, byte 67'

    def get_smf_km_link_length(self) -> int:
        '''
        Link length supported for single-mode fiber, units of
        km, or copper cable attenuation in dB at 12.9 GHz
        '''
        return self.page_a0[14]

    def get_smf_link_length(self) -> int:
        '''
        Link length supported for single-mode fiber, units of
        100m, or copper cable attenuation in dB at 25.78 GHz
        '''
        return self.page_a0[15]

    def get_om2_link_length(self) -> int:
        '''
        Link length supported for 50um OM2 fiber
        '''
        return self.page_a0[16]

    def get_om1_link_length(self) -> int:
        '''
        Link length supported for 62.5um OM1 fiber
        '''
        return self.page_a0[17]

    def get_om4_link_length(self) -> int:
        '''
        Link length supported for 50um OM4 fiber in units of 10m,
        or length of copper/direct attach cable in units of m.
        '''
        return self.page_a0[18]

    def get_om3_link_length(self) -> int:
        '''
        Link length supported for 50um OM3 fiber, units of 10m.
        Alternatively, copper/direct attach cable multiplier and base value
        '''
        return self.page_a0[19]

    def get_vendor_name(self) -> str:
        '''
        Returns the vendor's name in ASCII.
        '''
        name = ""
        for num in self.page_a0[20:35 + 1]:
            name += chr(num)
        
        return name

    def get_transceiver2(self) -> str:
        '''
        Code for electronic or optical comatibility (Table 5-3). Also
        from SFF 8024 Table 4-4.
        '''

        codes = [
            'Unspecified',
            '100G AOC or 25GAUI C2M AOC. Providing a worst BER of 5 x 10^-5',
            '100GBASE-SR4 or 25GBASE-SR',
            '100GBASE-LR4 or 25GABSE-LR',
            '100GBASE-ER4 or 25GBASE-ER',
            '100GBASE-SR10',
            '100G CWDM4',
            '100G PSM4 Parallel SMF',
            '100G ACC or 25GAUI C2M ACC. Providing a worst BER of 5 x 10^-5',
            'Obsolete',
            'Reserved',
            '100GBASE-CR4, 25GBASE-CR CA-25G-L or 50GBASE-CR2 with RS (Clause91) FEC',
            '25GBASE-CR CA-25G-S or 50GBASE-CR2 with BASE_R (Clause 74 Fire code) FEC',
            '25GBASE-CR CA-25G-N or 50GBASE-CR2 with no FEC',
            '10 Mb/s Single Pair Ethernet (802.3cg, Clause 146/147, 1000m copper)',
            'Reserved',
            '40GBASE-ER4',
            '4 x 10GBASE-SR',
            '40G PSM4 Parallel SMF',
            'G959.1 profile P1I1-2D1 (10709 MBd, 2km, 1310 nm SM)',
            'G959.1 profile P1S1-2D2 (10709 MBd, 40km, 1550 nm SM)',
            'G959.1 profile P1L1-2D2 (10709 MBd, 80km, 1550 nm SM)',
            '10GBASE-T with SFI electrical interface',
            '100G CLR4',
            '100G AOC or 25GAUI C2M AOC. Providing a worst BER of 10^-12 or below',
            '100G ACC or 25GAUI C2M ACC. Providing a worst BER of 10^-12 or below',
            '100GE-DWDM2',
            '100G 1550nm WDM (4 wavelengths)',
            '10GBASE-T Short Reach (30 meters)',
            '5GBASE-T',
            '2.5GBASE-T',
            '40G SWDM4',
            '100G SWDM4', #0x20
            '100G PAM4 BiDi', #0x21
            '4WDM-10 MSA', # 0x22 - Note that the table in SFF-8024 is out of order
            '4WDM-20 MSA',
            '4WDM-40 MSA',
            '100GBASE-DR (Clause 140), CAUI-4 (no FEC)',
            '100G-FR or 100GBASE-FR1 (Clause 140), CAUI-4 (no FEC)',
            '100G-LR or 100GBASE-LR1 (Clause 140), CAUI-4 (no FEC)',
            '100GBASE-SR (P802.3db, Clause 167), CAUI-4 (no FEC)',
            '100GBASE-SR, 200GBASE-SR2 or 400GBASE-SR4 (P802.3db, Clause 167)'
            '100GBASE-FR1 (P802.3cu, Clause 140)',
            '100GBASE-LR1 (P802.3cu, Clause 140)',
            '100G-LR1-20 MSA, CAUI-4 (no FEC)',
            '100G-ER1-30 MSA, CAUI-4 (no FEC)',
            '100G-ER1-40 MSA, CAUI-4 (no FEC)', 
            '100G-LR1-20 MSA', #0x2F
            'ACC with 50GAUI, 100GAUI-2 or 200GAUI-4 C2M',
            'AOC with 50GAUI, 100GAUI-2 or 200GAUI-4 C2M',
            'ACC with 50GAUI, 100GAUI-2 or 200GAUI-4 C2M',
            'AOC with 50GAUI, 100GAUI-2 or 200GAUI-4 C2M',
            '100G-ER1-30 MSA', #0x34
            '100G-ER1-40 MSA',
            '100GBASE-VR, 200GBASE-VR2 or 400GBASE-VR4 (P802.3db, Clause 167)',
            '10GBASE-BR (Clause 158)',
            '25GBASE-BR (Clause 159)',
            '50GBASE-Br (Clause 160)',
            '100GBASE-VR (P802.3db, Clause 167), CAUI-4 (no FEC)',
            'Reserved',
            'Reserved',
            'Reserved',
            'Reserved',
            '100GBASE-CR1, 200GBASE-CR2 or 400GBASE-CR4 (P802.3ck, Clause 162)',
            '50GBASE-CR, 100GBASE-CR2, or 200GBASE-CR4',
            '50GBASE-SR, 100GBASE-SR2, or 200GBASE-SR4',
            '50GBASE-FR or 200GBASE-DR4',
            '200GBASE-FR4',
            '200G 1550nm PSM4',
            '50GBASE-LR',
            '200GBASE-LR4',
            '400GBASE-DR4 (802.3, Clause 124), 100GAUI-1 C2M (Annex 120G)',
            '400GBASE-FR4 (802.3cu, Clause 151)',
            '400GBASE-LR4-6 (802.3cu, Clause 151)',
            '50GBASE-ER (IEEE 802.3cn, Clause 139)',
            '400G-LR4-10',
            '400GBASE-ZR (802.3cw, Clause 156)',
        ]

        code = self.page_a0[36]

        if code < 0x4D:
            return codes[code]
        elif code >= 0x4D and code <= 0x7E:
            return "Reserved"
        elif code == 0x7F:
            return "256GFC-SW4 (FC-PI-7P)"
        elif code == 0x80:
            return "64GFC (FC-PI-7)"
        elif code == 0x81:
            return "128GFC (FC-PI-8)"
        else:
            return "Reserved"

    def get_vendor_oui(self) -> List[int]:
        '''
        Get's the SFP vendor IEEE company ID
        '''
        return self.page_a0[37:39 + 1]
    
    def get_vendor_part_number(self) -> str:
        '''
        Gets the part number provided by SFP vendor in ASCII.
        '''
        part_number = ''

        for val in self.page_a0[40:55 + 1]:
            part_number += chr(val)

        return part_number

    def get_vendor_revision_level(self) -> str:
        '''
        Gets the revision level for part number provided 
        by vendor in ASCII. Returns bytes [56,59]
        '''

        rev_level = ''

        for val in self.page_a0[56:59 + 1]:
            rev_level += chr(val)

        return rev_level
    
    def get_wavelength(self) -> int:
        '''
        Gets the laser wavelength (Passive/Active Cable Specification Compliance) in nm
        '''
        return self.page_a0[60] << 8 | self.page_a0[61]

    def get_fibre_channel_speed2(self) -> str:
        return f'{self.page_a0[62]}'

    def get_cc_base(self) -> str:
        return f'{hex(self.page_a0[63])}'

    
    def calculate_cc_base(self) -> int:
        
        # Returns the lower 8 bits of the sum of
        # bytes [0,62]. Array slicing doesn't
        # include the last value, so we add 1

        return 0xFF & sum(self.page_a0[0:62 + 1])

    # Extended ID Field getters
    def get_optional_tr_signals(self) -> str:
        '''
        Gets a list of optional transceiver signals that are
        implemented. From Table 8-3.
        '''
        # We have to examine each bit of bytes 64 and 65 from
        # page a0

        optional_signals = []

        byte_64 = self.page_a0[64]
        byte_65 = self.page_a0[65]

        if (byte_64 & 0x80):
            optional_signals.append("Reserved")
        
        if byte_64 & 0x40:
            optional_signals.append("Power Level 4 Required")
        else:
            optional_signals.append("Power Level 1,2, or 3")

        if byte_64 & 0x20:
            optional_signals.append('Power Level 3 or 4 requirement')
        else:
            optional_signals.append("Power level 1 or 2")
        
        if byte_64 & 0x10:
            optional_signals.append("Paging is implemened (byte 127d of 0xA2 used for page select)")
        
        if byte_64 & 0x08:
            optional_signals.append("SFP has internal retimer or CDR circuit")

        if byte_64 & 0x04:
            optional_signals.append("Cooled laser transmitter implemented")

        if byte_64 & 0x02:
            optional_signals.append("Power Level 2 required")
        else:
            optional_signals.append("Power level 1 (or unspecified)")

        if byte_64 & 0x01:
            optional_signals.append("Linear receiver output")
        else:
            optional_signals.append("Conventional limiting, PAM4 or unspecified receiver output")


        if byte_65 & 0x80:
            optional_signals.append("Receiver decision threshold (RDT) implemented")

        if byte_65 & 0x40:
            optional_signals.append("Transmitter wavelength/frequency is tunable in accordance with SFF-8690")

        if byte_65 & 0x20:
            optional_signals.append("RATE_SELECT functionality is implemented")

        if byte_65 & 0x10:
            optional_signals.append("TX_DISABLE is implemented and disables the high speed serial output")

        if byte_65 & 0x08:
            optional_signals.append("TX_FAULT is implemented")

        if byte_64 & 0x04:
            optional_signals.append("Loss of signal implemented, signal inverted from standard definition in SFP MSA")

        if byte_64 & 0x02:
            optional_signals.append("LOS implemented, behavior defined in SFF-8419 (called Rx_LOS)")

        if byte_64 & 0x01:
            optional_signals.append("Reserved")

        return optional_signals

    def get_max_signaling_rate_margin(self) -> str:
        '''
        Gets the upper signaling rate margin in units of %
        '''
        return f'{self.page_a0[66]} %'

    def get_min_signaling_rate_margin(self) -> str:
        '''
        Gets the lower signaling rate margin in units of %
        '''
        return f'{self.page_a0[67]} %'

    def get_vendor_serial_number(self) -> str:
        '''
        Gets the serial number provided by the vendor (ASCII)
        '''
        serial_number = ""
        for val in self.page_a0[68:83 + 1]:
            serial_number += chr(val)
        return serial_number

    def get_vendor_date_code(self) -> str:
        '''
        Gets the vendor's manufacturing date code (Table 8-4)
        '''

        # Not sure if this is correct. The standard says it's
        # all ASCII codes so it shouldn't matter. I'm just formatting it
        # nicely
        year = f'{chr(self.page_a0[84])}{chr(self.page_a0[85])}'
        month = f'{chr(self.page_a0[86])}{chr(self.page_a0[87])}'
        day = f'{chr(self.page_a0[88])}{chr(self.page_a0[89])}'

        extra_code = f'{chr(self.page_a0[90])}{chr(self.page_a0[91])}'

        date = f'{month}/{day}/{year}\t{extra_code}'
        return date

    def get_diagnostic_monitoring_type(self) -> str:
        '''
        Indicates which type of diagnostic monitoring is implemented (if any)
        in the transceiver (see Table 8-5).
        '''
        code = self.page_a0[92]

        compliant_with = []

        if code & 0x80:
            compliant_with.append('Reserved for legacy diagnostic implementations. SFP not compliant with SFF-8472!')
        
        if code & 0x40:
            compliant_with.append("Digital diagnostic monitoring implemented")

        if code & 0x20:
            compliant_with.append("Internally calibrated")
            self.calibration_type = self.CalibrationType.INTERNAL

        if code & 0x10:
            compliant_with.append("Externally calibrated")
            self.calibration_type = self.CalibrationType.EXTERNAL
        
        if code & 0x08:
            compliant_with.append("Received power measurement type: average power")
        else:
            compliant_with.append("Received power measurement type: OMA")

        if code & 0x04:
            compliant_with.append("Address change required")

        if code & 0x02 or code & 0x01:
            compliant_with.append("Reserved")

        return compliant_with

    def force_calibration_check(self):
        if self.page_a0[92] & 0x20:
            self.calibration_type = self.CalibrationType.INTERNAL

        if self.page_a0[92] & 0x10:
            self.calibration_type = self.CalibrationType.EXTERNAL

    def get_enhanced_options(self) -> str:
        '''
        Indicates which optional enhanced features are
        implemented (if any) in the transceiver (see Table 8-6).
        '''
        
        options = [
            'Optional Alarm/warning flags implemented for all monitored quantities', # bit 7
            'Optional soft TX_DISABLE control and monitoring implemented',
            'Optional soft TX_FAULT monitoring implemented',
            'Optional soft RX_LOS monitoring implemented',
            'Optional soft RATE_SELECT control and monitoring implemented',
            'Optional Application Select control implemented per SFF-8079',
            'Optional soft Rate Select control implemented per SFF-8431',
            'Reserved'
        ]

        code = self.page_a0[93]
        compliant_with = []

        mask = 0x80

        for i in range(8):
            if code & mask:
                compliant_with.append(options[i]) 

            mask = mask // 2

        return compliant_with

    def get_sff_8472_compliance(self) -> str:
        '''
        Indicates which revision of SFF-8472 the transceiver complies
        with (see Table 8-8).
        '''

        options = [
            '',
            'Rev 9.3',
            'Rev 9.5',
            'Rev 10.2',
            'Rev 10.4',
            'Rev 11.0',
            'Rev 11.3',
            'Rev 11.4',
            'Rev 12.3',
            'Rev 12.4'
        ]

        code = self.page_a0[94]

        if code <= 0x09:
            return options[code]
        else:
            return "Reserved as of SFF-8472 Rev 12.4"

    def get_cc_ext(self) -> str:
        '''
        Returns a hexadecimal string for the checksum
        over the extended ID fields of SFP memory page 0xA0.
        '''
        return f'{hex(self.page_a0[95])}'

    def calculate_cc_ext(self) -> int:
        '''
        Calculates the checksum CC_EXT over the extended ID
        fields by summing up the values. This returns an integer, not
        a hex string.
        '''
        # Just like CC_BASE, the low
        # order 8 bits of summing bytes
        # [64,94] inclusive is the checksum value

        return 0xFF & sum(self.page_a0[64:94 + 1])

    # Vendor Specific ID Fields

    def get_vendor_eeprom(self) -> str:
        '''
        Returns the vendor specific EEPROM data of page 0xA0.
        '''
        return f'{self.page_a0[96:127 + 1]}'

    def get_reserved_fields(self) -> str:
        '''
        In SFF-8472 R12.4, says bytes 122-255 are reserved,
        but assigned to SFF-8079. The mentioned standard does not have
        any information on these fields. Simply returns an ASCII string
        that contains the data.
        '''
        return f'{self.page_a0[128:255 + 1]}'

    def get_page_a2(self) -> List[int]:
        return self.page_a2

    #######################################
    #######    Alarm and Warning  #########
    #######    Threshold Methods  #########
    #######################################

    def _calibration_helper(self, msb_address: int, lsb_address: int) -> int:
        '''
        Returns uncalibrated data from module located at 
        addresses [msb, lsb] in page 0xA2. See Table 9-5 from SFF 8472
        '''
        return (self.page_a2[msb_address] << 8 | self.page_a2[lsb_address] & 0xFF)

    def get_temp_high_alarm(self) -> int:
        '''
        Gets the alarm threshold for module temperature
        being too high. This value is not calibrated.
        '''

        # MSB is at the lower address, so shift it left 8 bits
        # and OR it with the rest of the number
        b1 = self.page_a2[0]
        b0 = self.page_a2[1]
        return temperature_bytes_to_signed_twos_complement_decimal(b1, b0)

    def get_temp_low_alarm(self) -> int:
        '''
        Gets the alarm threshold for module temperature
        being too low. This value is not calibrated.
        '''
        print(f'{self.page_a2[2]}..{self.page_a2[3]}')
        return temperature_bytes_to_signed_twos_complement_decimal(self.page_a2[2], self.page_a2[3])
    
    def get_temp_high_warning(self) -> int:
        '''
        Gets the warning threshold for module temperature
        being too high. This value is not calibrated.
        '''

        return temperature_bytes_to_signed_twos_complement_decimal(self.page_a2[4], self.page_a2[5])

    def get_temp_low_warning(self) -> int:
        '''
        Gets the warning threshold for module temperature
        being too low. This value is not calibrated.
        '''

        return temperature_bytes_to_signed_twos_complement_decimal(self.page_a2[6], self.page_a2[7])

    def get_voltage_high_alarm(self) -> int:
        '''
        Gets the alarm threshold for module voltage
        being too high. This value is not calibrated.
        '''

        return self.page_a2[8] << 8 | self.page_a2[9]

    def get_voltage_low_alarm(self) -> int:
        '''
        Gets the alarm threshold for module voltage
        being too low. This value is not calibrated.
        '''

        return self.page_a2[10] << 8 | self.page_a2[11]

    def get_voltage_high_warning(self) -> int:
        '''
        Gets the warning threshold for module voltage
        being too high. This value is not calibrated.
        '''

        return self.page_a2[12] << 8 | self.page_a2[13]

    def get_voltage_low_warning(self) -> int:
        '''
        Gets the warning threshold for module voltage
        being too low. This value is not calibrated.
        '''

        return self.page_a2[14] << 8 | self.page_a2[15]

    def get_bias_high_alarm(self) -> int:
        '''
        Gets the alarm threshold for module bias
        current being too high. This value is not calibrated.
        '''

        return self.page_a2[16] << 8 | self.page_a2[17]

    def get_bias_low_alarm(self) -> int:
        '''
        Gets the alarm threshold for module bias
        current being too low. This value is not calibrated.
        '''

        return self.page_a2[18] << 8 | self.page_a2[19]

    def get_bias_high_warning(self) -> int:
        '''
        Gets the warning threshold for module bias
        current being too high. This value is not calibrated.
        '''

        return self._calibration_helper(20, 21)

    def get_bias_low_warning(self) -> int:
        '''
        Gets the warning threshold for module bias
        current being too low. This value is not calibrated.
        '''

        return self._calibration_helper(22, 23)

    def get_tx_power_high_alarm(self) -> int:
        '''
        Gets the alarm threshod for module transmitter
        power being too high. Uncalibrated.
        '''
        return self._calibration_helper(24, 25)

    def get_tx_power_low_alarm(self) -> int:
        '''
        Gets the alarm threshod for module transmitter
        power being too low. Uncalibrated.
        '''
        return self._calibration_helper(26, 27)
    
    def get_tx_power_high_warning(self) -> int:
        '''
        Gets the warning threshold for module transmitter
        power being too high. Uncalibrated.
        '''
        return self._calibration_helper(28, 29)

    def get_tx_power_low_warning(self) -> int:
        '''
        Gets the warning threshold for module transmitter
        power being too low. Uncalibrated.
        '''
        return self._calibration_helper(30, 31)

    def get_rx_power_high_alarm(self) -> int:
        '''
        Gets the alarm threshold for module receiver
        power being too high. Uncalibrated.
        '''
        return self._calibration_helper(32, 33)

    def get_rx_power_low_alarm(self) -> int:
        '''
        Gets the alarm threshold for module receiver
        power being too low. Uncalibrated.
        '''
        return self._calibration_helper(34, 35)
    
    def get_rx_power_high_warning(self) -> int:
        '''
        Gets the warning threshold for module receiver
        power being too high. Uncalibrated.
        '''
        return self._calibration_helper(36, 37)

    def get_rx_power_low_warning(self) -> int:
        '''
        Gets the warning threshold for module receiver
        power being too low. Uncalibrated.
        '''
        return self._calibration_helper(38, 39)

    def get_optional_laser_temp_high_alarm(self) -> int:
        '''
        Gets the high alarm threshold for the optional laser
        temperature. Uncalibrated
        '''
        return temperature_bytes_to_signed_twos_complement_decimal(self.page_a2[40], self.page_a2[41])

    def get_optional_laser_temp_low_alarm(self) -> int:
        '''
        Gets the low alarm threshold for the optional laser
        temperature. Uncalibrated
        '''
        return temperature_bytes_to_signed_twos_complement_decimal(self.page_a2[42], self.page_a2[43])
    
    def get_optional_laser_temp_high_warning(self) -> int:
        '''
        Gets the high warning threshold for the optional laser
        temperature. Uncalibrated.
        '''
        return temperature_bytes_to_signed_twos_complement_decimal(self.page_a2[44], self.page_a2[45])

    def get_optional_laser_temp_low_warning(self) -> int:
        '''
        Gets the low warning threshold for the optional laser
        temperature.
        '''
        return temperature_bytes_to_signed_twos_complement_decimal(self.page_a2[46], self.page_a2[47])
    
    def get_optional_tec_current_high_alarm(self) -> int:
        '''
        Gets the high alarm threshold for the optional TEC
        current.
        '''
        return bytes_to_tec_current(self.page_a2[48], self.page_a2[49])
    
    def get_optional_tec_current_low_alarm(self) -> int:
        '''
        Gets the low alarm threshold for the optional TEC
        current.
        '''
        return bytes_to_tec_current(self.page_a2[50], self.page_a2[51])
    
    def get_optional_tec_current_high_warning(self) -> int:
        '''
        Gets the high warning threshold for the optional TEC
        current. Uncalibrated.
        '''
        return bytes_to_tec_current(self.page_a2[52], self.page_a2[53])

    def get_optional_tec_current_low_warning(self) -> int:
        '''
        Gets the low warning threshold for the optional TEC
        current. Uncalibrated.
        '''
        return bytes_to_tec_current(self.page_a2[54], self.page_a2[55])
    
    #   Getters for External Calibration Constants
    #   RX Power uses IEEE 754 standard to represent
    #   floating point numbers.
        

    def _get_rx_pwr_4(self) -> int:
        '''
        Single precision floating point calibration data - Rx optical
        power. Bit 7 of byte 56 is MSB. Bit 0 of byte 59 is LSB. Rx_PWR(4)
        should be set to zero for 'internally calibrated' devices.
        '''
        return ieee754_to_decimal(
            self.page_a2[56], self.page_a2[57], 
            self.page_a2[58], self.page_a2[59]
        )

    def _get_rx_pwr_3(self) -> int:
        '''
        Single precision floating point calibration data - Rx optical
        power. Bit 7 of byte 60 is MSB. Bit 0 of byte 63 is LSB. Rx_PWR(3)
        should be set to zero for 'internally calibrated' devices.
        '''
        return ieee754_to_decimal(
            self.page_a2[60], self.page_a2[61],
            self.page_a2[62], self.page_a2[63]
        )

    def _get_rx_pwr_2(self) -> int:
        '''
        Single precision floating point calibration data - Rx optical
        power. Bit 7 of byte 64 is MSB. Bit 0 of byte 67 is LSB. Rx_PWR(2)
        should be set to zero for 'internally calibrated' devices.
        '''
        return ieee754_to_decimal(
            self.page_a2[64], self.page_a2[65],
            self.page_a2[66], self.page_a2[67]
        )

    def _get_rx_pwr_1(self) -> int:
        '''! Gets a scaling factor for the receiver power.
        @brief Single precision floating point calibration data - Rx optical
        power. Bit 7 of byte 68 is MSB. Bit 0 of byte 71 is LSB. Rx_PWR(1)
        should be set to zero for 'internally calibrated' devices.

        '''
        return ieee754_to_decimal(
            self.page_a2[68], self.page_a2[69],
            self.page_a2[70], self.page_a2[71]
        )

    def _get_rx_pwr_0(self) -> int:
        '''
        Single precision floating point calibration data - Rx optical
        power. Bit 7 of byte 72 is MSB. Bit 0 of byte 75 is LSB. Rx_PWR(0)
        should be set to zero for 'internally calibrated' devices.
        '''
        return ieee754_to_decimal(
            self.page_a2[72], self.page_a2[73],
            self.page_a2[74], self.page_a2[75]
        )

    def calculate_rx_power_uw(self) -> Decimal:
        '''! Calculates the receiver optical power in uW. 
        @brief Formula for external calibration is:
            Rx_PWR(4) * (read value) + 
            Rx_PWR(3) * (read value) + 
            Rx_PWR(2) * (read value) + 
            Rx_PWR(1) * (read value) + 
            Rx_PWR(0)
        '''

        msb = self.page_a2[104]
        lsb = self.page_a2[105]

        value = (msb << 8) | (lsb & 0xFF)

        # print(self.get_diagnostic_monitoring_type())

        if self.calibration_type == self.CalibrationType.INTERNAL:
            return Decimal(value)
        elif self.calibration_type == self.CalibrationType.EXTERNAL:
            return Decimal(self._get_rx_pwr_4() * value + self._get_rx_pwr_3() * value + \
                   self._get_rx_pwr_2() * value + self._get_rx_pwr_2() * value + \
                   self._get_rx_pwr_1() * value + self._get_rx_pwr_0())
        else:
            print("ERROR::SFP::calculate_rx_power() - Unknown calibration type")
            return -1



    def get_tx_i_slope(self) -> int:
        """! Get the slope for the transmitter current.
        @brief Fixed decimal (unsigned) calibration data, laser bias current.
        Bit 7 of byte 76 is MSB, bit 0 of byte 77 is LSB. Tx_I(slope)
        should be set to 1 for 'internally calibrated' devices.
        """
        return slope_bytes_to_unsigned_decimal(self.page_a2[76], self.page_a2[77])

    def get_tx_i_offset(self) -> int:
        '''
        Fixed decimal (signed two's complement) calibration data, laser bias
        current. Bit 7 of byte 78 is MSB, bit 0 of byte 79 is LSB.
        Tx_I(Offset) should be set to zero for "internally calibrated' devices.
        '''
        return offset_bytes_to_signed_twos_complement_int(self.page_a2[78], self.page_a2[79])

    def get_tx_pwr_slope(self) -> int:
        '''
        Fixed decimal (unsigned) calibration data, transmitter coupled
        output power. Bit 7 of byte 80 is MSB, bit 0 of byte 81 is LSB. Tx_PWR(slope)
        should be set to 1 for 'internally calibrated' devices.
        '''
        return slope_bytes_to_unsigned_decimal(self.page_a2[80], self.page_a2[81])

    def get_tx_pwr_offset(self) -> int:
        '''
        Fixed decimal (signed two's complement) calibration data, transmitter
        coupled output power. Bit 7 of byte 82 is MSB, bit 0 of byte 83 is LSB.
        Tx_PWR(Offset) should be set to zero for "internally calibrated" devices.
        '''
        return offset_bytes_to_signed_twos_complement_int(self.page_a2[82], self.page_a2[83])
    
    def get_temp_slope(self) -> int:
        '''
        Fixed decimal (unsigned) calibration data, internal module temperature.
        Bit 7 of byte 84 is MSB, bit 0 of byte 85 is LSB. T(Slope) should be set to
        1 for "internally calibrated" devices.
        '''
        return slope_bytes_to_unsigned_decimal(self.page_a2[84], self.page_a2[85])

    def get_temp_offset(self) -> int:
        '''
        Fixed decimal (signed two's complement) calibration data, internal module temperature.
        Bit 7 of byte 86 is MSB, bit 0 of byte 87 is LSB. T(Offset) should be set to
        0 for "internally calibrated" devices.
        '''
        return offset_bytes_to_signed_twos_complement_int(self.page_a2[86], self.page_a2[87])

    def get_voltage_slope(self) -> int:
        '''
        Fixed decimal (unsigned) calibration data, internal module supply voltage.
        Bit 7 of byte 88 is MSB, bit 0 of byte 89 is LSB. V(Slope) should be set to
        1 for "internally calibrated" devices.
        '''
        return slope_bytes_to_unsigned_decimal(self.page_a2[88], self.page_a2[89])

    def get_voltage_offset(self) -> int:
        '''
        Fixed decimal (signed two's complement) calibration data, internal module temperature.
        Bit 7 of byte 90 is MSB, bit 0 of byte 91 is LSB. V(Offset) should be set to
        0 for "internally calibrated" devices.
        '''
        return offset_bytes_to_signed_twos_complement_int(self.page_a2[90], self.page_a2[91])

    def get_reserved_a2_bytes(self) -> int:
        return f'{self.page_a2[92:94 + 1]}'

    def get_pagea2_checksum(self) -> str:
        return f'{hex(self.page_a2[95])}'

    def calculate_pagea2_checksum(self) -> int:
        '''
        Returns the low order 8 bits of the sum of
        bytes 0-94.
        '''
        return 0xFF & sum(self.page_a2[0:95])

    def get_temperature(self) -> Decimal:
        '''
        Returns the module temperature. Calibrated
        16-bit data.
        '''
        
        msb = self.page_a2[96]
        lsb = self.page_a2[97]

        converted_val = temperature_bytes_to_signed_twos_complement_decimal(msb, lsb)

        if self.calibration_type == self.CalibrationType.INTERNAL:
            return Decimal(converted_val)
        else:
            return Decimal(self.get_temp_slope()) * Decimal(converted_val) + Decimal(self.get_temp_offset())

    def get_vcc(self) -> Decimal:
        '''
        Returns the measured supply voltage in transceiver.
        '''

        slope = self.get_voltage_slope()
        offset = self.get_voltage_offset()

        return self._real_time_measurement_helper(98, 99, slope, offset)

    def get_tx_bias_current(self) -> Decimal:
        
        slope = self.get_tx_i_slope()
        offset = self.get_tx_i_offset()

        return self._real_time_measurement_helper(100, 101, slope, offset)

    def get_tx_power(self) -> Decimal:
        slope = self.get_tx_pwr_slope()
        offset = self.get_tx_pwr_offset()

        return self._real_time_measurement_helper(102, 103, slope, offset)

    def get_rx_power(self) -> Decimal:
        msb = self.page_a2[104]
        lsb = self.page_a2[105]

        value = self._calibration_helper(msb, lsb)

        if self.calibration_type == self.CalibrationType.INTERNAL:
            return Decimal(self.get_rx_pwr_0())
        elif self.calibration_type == self.CalibrationType.EXTERNAL:
            return Decimal(self.get_rx_pwr_4() * value + self.get_rx_pwr_3() * value + \
                   self.get_rx_pwr_2() * value + self.get_rx_pwr_1() * value + \
                   self.get_rx_pwr_0())
        else:
            print("ERROR:SFP::get_rx_pwr() - Unknown calibration type")

    def get_laser_temp_or_wavelength(self) -> float:
        msb = self.page_a2[106]
        lsb = self.page_a2[107]

        converted_val = temperature_bytes_to_signed_twos_complement_decimal(msb, lsb)

        if self.calibration_type == self.CalibrationType.INTERNAL:
            return Decimal(converted_val)
        else:
            return Decimal(self.get_temp_slope()) * Decimal(converted_val) + Decimal(self.get_temp_offset())

    def get_tec_current(self) -> float:
        msb = self.page_a2[108]
        lsb = self.page_a2[109]

        return bytes_to_tec_current(msb, lsb)

        

    def _real_time_measurement_helper(self, b1: int, b0: int, slope: float, offset: float) -> float:
        num = self._calibration_helper(b1, b0)

        if self.calibration_type == self.CalibrationType.INTERNAL:
            slope = 1.0
            offset = 0.0

        return Decimal(slope) * Decimal(num) + Decimal(offset)


    def __repr__(self):
        return f'{self.get_vendor_name()}-{self.get_vendor_part_number()}-{self.get_vendor_serial_number()}-{self.get_wavelength()}nm'

# END sfp.py