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
import logging
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import QAction, QHeaderView, QListWidget, \
    QMenu, QMenuBar, QTableWidgetItem, QDialog


from fpdf import FPDF

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
        self.menu_bar = QMenuBar()
        self.file_menu = QMenu("&File")
        self.menu_bar.addMenu(self.file_menu)
        self.layout().setMenuBar(self.menu_bar)
        #self.gridLayout.setMenuBar(self.menu_bar)

        self.menu_action_to_pdf = QAction("Export to PDF", self.file_menu)
        self.menu_action_to_pdf.triggered.connect(self._handle_export_to_pdf)
        self.file_menu.addAction(self.menu_action_to_pdf)

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
            scenario_name = data[3]
            list_of_values = [val for val in data[4::]]

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

    def _handle_export_to_pdf(self):
        '''!Try to export all data to PDF.

        @brief adapted code from http://www.fpdf.org/en/script/script3.php to work
        in Python.
        '''

        # Export memory tables in hex

        TABLE_COL_NAMES = [
            "--",
            "00", "01", "02", "03", "04", "05", "06", "07", 
            "08", "09", "0A", "0B", "0C", "0D", "0E", "0F"
        ]

        font = "Arial"

        pdf = FPDF("P", "in", "A4")
        pdf.add_page()
        pdf.set_font(font, 'B', 16.0)
        line_height = pdf.font_size * 2
        epw = pdf.w - 2*pdf.l_margin
        col_width = epw / len(TABLE_COL_NAMES)


        v_name = self.associated_sfp.get_vendor_name().strip()
        part_num = self.associated_sfp.get_vendor_part_number().strip()
        serial_num = self.associated_sfp.get_vendor_serial_number().strip()

        sfp_name_str = f'{v_name} | {part_num} | {serial_num}'

        pdf.cell(col_width * len(TABLE_COL_NAMES), line_height, f"Report for: {sfp_name_str}")
        pdf.ln(line_height)

        INFO_COL_NAMES = ["Page A0 Address", "# of Bytes", "Name", "Description", "Value"]
        col_width_page1 = epw / len(INFO_COL_NAMES)

        def render_table_header(col_names: List[str]):
            col_width = epw / len(col_names)
            pdf.set_font(font, "B", 10.0)
            for col_name in col_names:
                pdf.cell(col_width, line_height, col_name, border=1)
            pdf.ln(line_height)
            pdf.set_font(font, "", 10.0)

        #render_table_header(INFO_COL_NAMES)
        

        # Need to get text out of characteristics table

        NUM_COLUMNS = 5
        WIDTHS = [1.25, 1, 1.0, 1.5, int(epw) - 4.75]
        print(epw)
        col_width = epw / NUM_COLUMNS

        pdf.set_font(font, "B", 10.0)
        for i, col_name in enumerate(INFO_COL_NAMES):
            pdf.cell(WIDTHS[i], line_height, col_name, border=1)

        pdf.set_font(font, "", 10.0)
        pdf.ln(line_height)

        def num_lines(width: int, text: str):

            if width == 0:
                width = pdf.w - pdf.r_margin - pdf.get_x()

            max_width = (width - 2 * pdf.c_margin) * 1000 / pdf.font_size

            cw = pdf.current_font['cw']

            s = text.replace('\r', '')
            str_len = len(s)
            if str_len > 0 and s[str_len-1] == '\n':
                str_len -= 1

            sep = -1
            i = 0
            j = 0
            l = 0
            nl = 1

            while i < str_len:
                c = s[i]
                if c == '\n':
                    i += 1
                    sep = -1
                    j = i
                    l = 0
                    nl += 1
                    continue
                    
                if c == ' ':
                    sep = i

                l += cw[c]

                if l > max_width:
                    if sep == -1:
                        if i == j:
                            i += 1
                    else:
                        i = sep + 1
                        
                    sep = -1
                    j = i
                    l = 0
                    nl += 1
                else:
                    i += 1

            return nl

        def check_page_break(h: int):
            if pdf.get_y() + h > pdf.page_break_trigger:
                pdf.add_page(pdf.def_orientation)

        line_height = pdf.font_size * 2
        for row in range(self.tableWidget_2.rowCount()):

            text_in_row = []
            max_lines = 0
            for col in range(NUM_COLUMNS):
                s = self.tableWidget_2.item(row, col).text()
                text_in_row.append(s)

            max_lines = max([num_lines(WIDTHS[i], x) for i, x in enumerate(text_in_row)])
            h = max_lines * line_height

            check_page_break(h)

            for i, val in enumerate(text_in_row):
                x = pdf.get_x()
                y = pdf.get_y()

                pdf.rect(x, y, WIDTHS[i], h)
                pdf.multi_cell(WIDTHS[i], line_height, val, border=0, align='L')

                pdf.set_xy(x + WIDTHS[i], y)

            pdf.ln(h)






        pdf.add_page()
        pdf.set_font(font, "", 10.0)
        pdf.cell(col_width * len(TABLE_COL_NAMES), line_height, "Identification register values in hex (EEPROM location 0x50)")
        pdf.ln(line_height)

        render_table_header(TABLE_COL_NAMES)
        col_width = epw / len(TABLE_COL_NAMES)
        pdf.set_font(font, 'B', 10.0)
        pdf.cell(col_width, line_height, "0x00", border=1)
        pdf.set_font(font, '', 10.0)
        for i, val in enumerate(self.associated_sfp.page_a0):
            if i and i % 16 == 0:
                pdf.ln(line_height)
                pdf.set_font(font, "B", 10.0)
                pdf.cell(col_width, line_height, hex(i), border=1)
                pdf.set_font(font, "", 10.0)

            pdf.cell(col_width, line_height, hex(val).replace('0x', ''), border=1)


        pdf.add_page()
        pdf.set_font(font, "", 10.0)
        pdf.cell(
            col_width * len(TABLE_COL_NAMES), 
            line_height, 
            "Diagnostic register values in hex (EEPROM location 0x51)"
        )
        pdf.ln(line_height)
        render_table_header(TABLE_COL_NAMES)
        pdf.set_font(font, 'B', 10.0)
        
        pdf.cell(col_width, line_height, "0x00", border=1)
        pdf.set_font(font, '', 10.0)
        for i, val in enumerate(self.associated_sfp.page_a2):
            if i and i % 16 == 0:
                pdf.ln(line_height)
                pdf.set_font(font, "B", 10.0)
                pdf.cell(col_width, line_height, hex(i), border=1)
                pdf.set_font(font, "", 10.0)

            pdf.cell(col_width, line_height, hex(val).replace('0x', ''), border=1)

        pdf.output(f'{v_name}_{part_num}_{serial_num}_{time.asctime()}.pdf')

    ##
    # Overridden PyQT Methods
    ##
    def closeEvent(self, event):
        self.deleteLater()
        event.accept()
            
        
