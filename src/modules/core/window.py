# File:     main.py
# Author:   Connor DeCamp
# Created:  07/08/2021
#
# Window class to interact with the auto-generated gui.py file
# from QtDesigner. The signal connections will be defined
# in this file.

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtWidgets import QAbstractScrollArea, QErrorMessage, \
                            QListWidgetItem, QPlainTextEdit, QTableWidgetItem, QMainWindow, QMenu, \
                            QDialog, QTextBrowser, QWidget

from modules.core.gui import Ui_MainWindow
from modules.core.memory_map_dialog import MemoryMapDialog
from modules.core.sfp import SFP

from modules.network.network_threads import BroadcastThread
from modules.network.sql_connection import SQLConnection

from random import randint
from typing import Tuple
import time

class Window(QMainWindow, Ui_MainWindow):

    db_connected: bool

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # User-defined setup methods
        self.connectSignalSlots()
        self.setupDatabase()

        # Allow columns to adjust to their contents
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        
        # TODO: remove later, just testing the table
        for i in range(3):
            self.listWidget.addItem(QListWidgetItem(f'Temp CloudPlug {i}'))


        self.appendToDebugLog('Starting device discovery thread')
        self.discovery_thread = BroadcastThread()
        self.discovery_thread.device_response.connect(self.handleClientDiscovery)
        self.discovery_thread.start()


    def connectSignalSlots(self):
        # Connect the 'Reprogram Cloudplugs' button to the correct callback
        self.reprogramButton.clicked.connect(self.cloudplug_reprogram_button_handler)

        self.tableWidget.doubleClicked.connect(self.display_sfp_memory_map)

    def setupDatabase(self):
        # Holds the database connection for the program
        self.db_connector = SQLConnection()
        
        # If the connection fails, update the state
        # of the connection in the main window
        if self.db_connector.connection is None:
            self.db_connected = False
        else:
            self.db_connected = True

    def display_sfp_memory_map(self, clicked_model_index):

        # The SFP the user double clicked from the table
        selected_row_in_table = clicked_model_index.row()

        selected_sfp_id = int(self.tableWidget.item(
            selected_row_in_table, 0
        ).text())

        # TODO: MOVE THIS OUT LATER

        mycursor = self.db_connector.cursor
        mycursor.execute(f"SELECT * FROM sfp_info.page_a0 WHERE id={selected_sfp_id};")

        page_a0 = []
        page_a2 = [0] * 256

        # should only be one result...
        for res in mycursor:
            for i in range(1, len(res)):
                page_a0.append(res[i] + randint(0, 255))

        sfp = SFP(page_a0, page_a2)

        # Create SFP object after reading from database

        memory_dialog = MemoryMapDialog(self)
        memory_dialog.initializeTableValues(sfp)
        memory_dialog.show()

    def appendRowInSFPTable(self, values: Tuple) -> None:

        ID = 0
        VENDOR_ID = 1
        VENDOR_PART_NUMBER = 2
        TRANSCEIVER_TYPE = 3

        rowPosition = self.tableWidget.rowCount()        
        self.tableWidget.insertRow(rowPosition)

        print(values)

        self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(values[ID])))
        self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(values[VENDOR_ID]))
        self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(values[VENDOR_PART_NUMBER]))
        self.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(values[TRANSCEIVER_TYPE]))

        self.tableWidget.resizeColumnsToContents()

    def cloudplug_reprogram_button_handler(self) -> None:
        """
        User presses this button to reprogram the selected cloudplugs with
        a single selected SFP/SFP+ persona.
        """

        # Check to see if the user has selected at least one cloudplug
        selected_cloudplugs = self.listWidget.selectedItems()
        print(f'User has selected {len(selected_cloudplugs)} cloudplugs')

        # If the user has not selected anything, show an error message and
        # return from this method
        if len(selected_cloudplugs) < 1:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("You must choose at least 1 CloudPlug!")
            error_dialog.exec()
            return

        selected_sfp_persona = self.tableWidget.selectionModel().selectedIndexes()

        if len(selected_sfp_persona) == 0:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("You must select an SFP from the table!")
            error_dialog.exec()
            return
        
        for model_index in selected_sfp_persona:
            print(f'{self.tableWidget.model().data(model_index) = }')


    def handleClientDiscovery(self, contents_ip_port_tuple: Tuple):
        raw_data:    bytes         = contents_ip_port_tuple[0]
        sender_ip:   QHostAddress  = contents_ip_port_tuple[1].toString()
        sender_port: int           = contents_ip_port_tuple[2]

        self.appendToDebugLog(f'Discovered device at {sender_ip}:{sender_port}')

    # Utility functions
    def appendToDebugLog(self, text: str):
        
        text_edit = self.logTab.findChild(QPlainTextEdit, 'plainTextEdit')

        if text_edit:
            formatted_time = time.strftime('%H:%M:%S', time.localtime())
            text_edit.appendPlainText(f'[{formatted_time}]: {text}')

    