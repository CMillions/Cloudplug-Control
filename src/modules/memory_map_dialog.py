# File:     main.py
# Author:   Connor DeCamp
# Created:  07/08/2021
#
# Window class to interact with the auto-generated gui.py file
# from QtDesigner. The signal connections will be defined
# in this file.

from gui import Ui_MainWindow
from PyQt5.QtWidgets import QAbstractScrollArea, QErrorMessage, \
                            QListWidgetItem, QTableWidgetItem, QMainWindow, QMenu, \
                            QDialog
from typing import Tuple

from memory_map_table import MemoryMapDialog_autogen

class MemoryMapTableWindow(QMainWindow, MemoryMapDialog_autogen):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)