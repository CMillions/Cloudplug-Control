# File:     main.py
# Author:   Connor DeCamp
# Created:  08/04/2021
#
# Custom Dialog class to display memory map values in a
# hex table.

from PyQt5.QtWidgets import QAbstractScrollArea, QErrorMessage, QHeaderView, \
                            QListWidgetItem, QTableWidgetItem, QMainWindow, QMenu, \
                            QDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from modules.core.memory_map_dialog_autogen import Ui_Dialog
from modules.core.sfp import SFP
from enum import Enum
from typing import List

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

        self.comboBox.activated[str].connect(self.changeTableDisplayMode)
        self.comboBox_2.activated[str].connect(self.changeMemoryPage)

        self.selected_memory_page = 0xA0

    def initializeTableValues(self, sfp_to_show: SFP):
        
        self.associated_sfp = sfp_to_show

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

    def changeTableDisplayMode(self, selection: str):

        if selection == 'Hex' and self.selected_display_mode != self.DisplayType.HEX:
            self.selected_display_mode = self.DisplayType.HEX
        elif selection == 'Decimal' and self.selected_display_mode != self.DisplayType.DECIMAL:
            self.selected_display_mode = self.DisplayType.DECIMAL
        elif selection == 'ASCII' and self.selected_display_mode != self.DisplayType.ASCII:
            self.selected_display_mode = self.DisplayType.ASCII
        else:
            return


        self.tableWidget.setUpdatesEnabled(False)
        self.updateTable()
        self.tableWidget.setUpdatesEnabled(True)

    def updateTable(self):

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

    def changeMemoryPage(self, selection: str):
        self.selected_memory_page = int(selection, base=16)
        self.updateTable()


            
        
