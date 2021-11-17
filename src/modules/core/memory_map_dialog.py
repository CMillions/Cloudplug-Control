##
# @file memory_map_dialog.py
# @brief Defines the memory map window. Displays memory map
#        values in a hex table and shows a characteristics tab
#        that is dynamically populated.
#
# @section file_author Author
# - Created on 08/04/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 11/04/2021 by Connor DeCamp
##

from enum import Enum
from typing import List

from PyQt5.QtWidgets import QHeaderView, QListWidget, QTableWidgetItem, QDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from modules.core.memory_map_dialog_autogen import Ui_Dialog
from modules.core.create_stress_scenario_dialog import CreateStressScenarioDialog
from modules.core.sfp import SFP

from modules.network.sql_connection import SQLConnection


class MemoryMapDialog(QDialog, Ui_Dialog):

    class DisplayType(Enum):
        HEX = 0,
        DECIMAL = 1,
        ASCII = 2

    # selected_display_mode is the one the user wants to switch to
    selected_display_mode : DisplayType = DisplayType.HEX

    # Current display mode is the type that is being currently displayed
    current_display_mode : DisplayType = DisplayType.HEX

    associated_sfp: SFP
    selected_memory_page: int

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Window is application modal - cannot do anything else until it's closed out.
        # This may not be the greatest solution
        # self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("Memory Map Information")

        # Get header of table widget and resize each column
        # to fit its contents
        header = self.tableWidget.horizontalHeader()

        for i in range(16):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        self.comboBox.activated[str].connect(self.change_table_display_mode)
        self.comboBox_2.activated[str].connect(self.change_memory_page)

        self.selected_memory_page = 0xA0

        

        # Whenever a section in the table is resized we also want
        # to resize the rows (allows for text wrapping)
        header = self.tableWidget_2.horizontalHeader()

        #header.sectionResized.connect(self.tableWidget_2.resizeRowsToContents)

        ##
        # Connect button slots
        ##

        self.addStressButton.clicked.connect(self._handle_add_stress_button_clicked)
        
        


    def initialize_table_values(self, sfp_to_show: SFP):
        '''! Initializes the characteristic table values.
        
        @param sfp_to_show The SFP object to display information about.
        '''
        self.associated_sfp = sfp_to_show

        self.setWindowTitle(self.associated_sfp.get_vendor_name() + 
            " " + self.associated_sfp.get_vendor_part_number() + 
            " " + self.associated_sfp.get_vendor_serial_number()
        )

        # Loop from [0, 255] and display memory map
        # values in hex by default
        for i in range(256):
            row = i // 16
            col = i % 16

            val_to_show = sfp_to_show.page_a0[i]
            
            item_to_add = QTableWidgetItem(format(val_to_show, '02X'))
            item_to_add.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_to_add.setFont(QFont('Ubuntu', 8))

            self.tableWidget.setItem(row, col, item_to_add)
        
        # Fill in the values on the characteristics page
        self.generate_characteristics_table()

    def refresh_stress_scenario_table(self, sfp_id: int):
        '''!Given a list of stress scenario tuples from the
        database, fills out the table in this dialog.
        
        '''
        self.selected_sfp_id = sfp_id

        sql_conn = SQLConnection()
        cursor = sql_conn.get_cursor()

        cursor.execute(f'SELECT * FROM stress_scenarios where sfp_id={self.selected_sfp_id}')

        stress_scenarios_list = []
        for res in cursor:
            stress_scenarios_list.append(res)

        sql_conn.close()

        ##
        # Database is formatted as
        #
        # Name         Column Number
        # --------------------------
        # stress_id         0
        # sfp_id            1
        # scenario_name     2
        # values           3-22
        ##
        self.tableWidget_3.setRowCount(0)
        for data in stress_scenarios_list:
            scenario_name = data[2]
            list_of_values = [val for val in data[3::]]

            row_count = self.tableWidget_3.rowCount()
            self.tableWidget_3.insertRow(row_count)
            self.tableWidget_3.setItem(row_count, 0, QTableWidgetItem(str(scenario_name)))
            self.tableWidget_3.setItem(row_count, 1, QTableWidgetItem(repr(list_of_values)))

        self.tableWidget_3.resizeColumnsToContents()

    def change_table_display_mode(self, selection: str):

        if selection == 'Hex' and self.selected_display_mode != self.DisplayType.HEX:
            self.selected_display_mode = self.DisplayType.HEX
        elif selection == 'Decimal' and self.selected_display_mode != self.DisplayType.DECIMAL:
            self.selected_display_mode = self.DisplayType.DECIMAL
        elif selection == 'ASCII' and self.selected_display_mode != self.DisplayType.ASCII:
            self.selected_display_mode = self.DisplayType.ASCII
        else:
            return


        self.tableWidget.setUpdatesEnabled(False)
        self.update_table()
        self.tableWidget.setUpdatesEnabled(True)

    def update_table(self):

        memory_to_display = self.associated_sfp.memory_pages[self.selected_memory_page]

        for i in range(256):
            row = i // 16
            col = i % 16

            if self.selected_display_mode == self.DisplayType.HEX:
                self.tableWidget.item(row, col).setText(
                    format(memory_to_display[i], '02X')
                )
            elif self.selected_display_mode == self.DisplayType.DECIMAL:
                self.tableWidget.item(row, col).setText(
                    f'{memory_to_display[i]}'
                )
            elif self.selected_display_mode == self.DisplayType.ASCII:
                self.tableWidget.item(row, col).setText(
                    chr(memory_to_display[i])
                )
            else:
                raise Exception("ERROR:memory_map_dialog.py::Unknown display type for memory table.")

    def change_memory_page(self, selection: str):
        self.selected_memory_page = int(selection, base=16)
        self.update_table()


    # Functions for Characteristics tab

    def generate_characteristics_table(self):
        '''
        Fills in the characteristics of the SFP module associated
        with the memory page being shown. The table fields come from
        SFF 8472 Rev 12.4 and are typed exactly.
        '''
        self.tableWidget_2: QListWidget

        data_to_add = self.associated_sfp.get_identifier()
        self.tableWidget_2.item(0, 4).setText(str(data_to_add))

        data_to_add = self.associated_sfp.get_ext_identifier()
        self.tableWidget_2.item(1, 4).setText(str(data_to_add))

        data_to_add = self.associated_sfp.get_connector_type()
        self.tableWidget_2.item(2, 4).setText(str(data_to_add))

        data_to_add = self.associated_sfp.get_transceiver_info()
        self.tableWidget_2.item(3, 4).setText(str(data_to_add))

        data_to_add = self.associated_sfp.get_encoding()
        self.tableWidget_2.item(4, 4).setText(str(data_to_add))

        self.tableWidget_2.item(5, 4).setText(str(self.associated_sfp.get_signaling_rate_nominal()))
        self.tableWidget_2.item(6, 4).setText(str(self.associated_sfp.get_rate_identifier()))
        self.tableWidget_2.item(7, 4).setText(str(self.associated_sfp.get_smf_km_link_length()))
        self.tableWidget_2.item(8, 4).setText(str(self.associated_sfp.get_smf_link_length()))
        self.tableWidget_2.item(9, 4).setText(str(self.associated_sfp.get_om2_link_length()))
        self.tableWidget_2.item(10, 4).setText(str(self.associated_sfp.get_om1_link_length()))
        self.tableWidget_2.item(11, 4).setText(str(self.associated_sfp.get_om4_link_length()))
        self.tableWidget_2.item(12, 4).setText(str(self.associated_sfp.get_om3_link_length()))
        self.tableWidget_2.item(13, 4).setText(str(self.associated_sfp.get_vendor_name()))
        self.tableWidget_2.item(14, 4).setText(str(self.associated_sfp.get_transceiver2()))
        self.tableWidget_2.item(15, 4).setText(str(self.associated_sfp.get_vendor_oui()))
        self.tableWidget_2.item(16, 4).setText(str(self.associated_sfp.get_vendor_part_number()))
        self.tableWidget_2.item(17, 4).setText(str(self.associated_sfp.get_vendor_revision_level()))
        self.tableWidget_2.item(18, 4).setText(str(self.associated_sfp.get_wavelength()))
        self.tableWidget_2.item(19, 4).setText(str(self.associated_sfp.get_fibre_channel_speed2()))
        self.tableWidget_2.item(20, 4).setText(str(self.associated_sfp.get_cc_base()))
        self.tableWidget_2.item(21, 4).setText(str(self.associated_sfp.get_optional_tr_signals()))
        self.tableWidget_2.item(22, 4).setText(str(self.associated_sfp.get_max_signaling_rate_margin()))
        self.tableWidget_2.item(23, 4).setText(str(self.associated_sfp.get_min_signaling_rate_margin()))
        self.tableWidget_2.item(24, 4).setText(str(self.associated_sfp.get_vendor_serial_number()))
        self.tableWidget_2.item(25, 4).setText(str(self.associated_sfp.get_vendor_date_code()))
        self.tableWidget_2.item(26, 4).setText(str(self.associated_sfp.get_diagnostic_monitoring_type()))
        self.tableWidget_2.item(27, 4).setText(str(self.associated_sfp.get_enhanced_options()))
        self.tableWidget_2.item(28, 4).setText(str(self.associated_sfp.get_sff_8472_compliance()))
        self.tableWidget_2.item(29, 4).setText(str(self.associated_sfp.get_cc_ext()))
        self.tableWidget_2.item(30, 4).setText(str(self.associated_sfp.get_vendor_eeprom()))
        self.tableWidget_2.item(31, 4).setText(str(self.associated_sfp.get_reserved_fields()))
        

        self.tableWidget_2.setColumnWidth(0, 100)
        self.tableWidget_2.setColumnWidth(1, 100)
        self.tableWidget_2.setColumnWidth(2, 200)
        self.tableWidget_2.setColumnWidth(3, 200)
        self.tableWidget_2.setColumnWidth(4, 300)

        self.tableWidget_2.resizeRowsToContents()

    ##
    # Button Handlers
    ##

    def _handle_add_stress_button_clicked(self):

        self.stress_dialog = CreateStressScenarioDialog(self, self.selected_sfp_id)
        self.stress_dialog.refresh_stress_signal.connect(self.refresh_stress_scenario_table)
        self.stress_dialog.show()

        print('handler')



    ##
    # Overriden PyQT Methods
    ##
    def closeEvent(self, event):
        self.deleteLater()
        event.accept()
            
        
