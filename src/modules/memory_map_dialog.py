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
from typing import Tuple

from modules.memory_map_dialog_autogen import Ui_Dialog
from modules.sfp import SFP

class MemoryMapDialog(QDialog, Ui_Dialog):
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

    def initializeTableValues(self, sfp_to_show: SFP):
        
        for i in range(256):
            row = i // 16
            col = i % 16

            item_to_add = QTableWidgetItem(f'{sfp_to_show.page_a0[i] : 02X}')
            item_to_add.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.tableWidget.setItem(row, col, item_to_add)