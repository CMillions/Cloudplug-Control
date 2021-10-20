## 
# @file window.py
# @brief Defines the main window for the application.
#
# @section file_author Author
# - Created on 07/08/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 10/19/2021 by Connor DeCamp
##
from struct import unpack
import PyQt5

from PyQt5 import QtCore
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtWidgets import QAbstractScrollArea, QErrorMessage, QListWidget, \
                            QListWidgetItem, QPlainTextEdit, QTableWidget, QTableWidgetItem, QMainWindow, QMenu, \
                            QDialog, QTextBrowser, QWidget
from modules.core.monitor_dialog import MonitorDialog

from modules.core.window_autogen import Ui_MainWindow
from modules.core.memory_map_dialog import MemoryMapDialog
from modules.core.sfp import SFP

from modules.network.message import MessageCode, Message, unpackRawBytes
from modules.network.network_threads import BroadcastThread, TcpServerThread
from modules.network.sql_connection import SQLConnection

from random import randint
from typing import Tuple
import time

from modules.network.utility import DeviceType

class Window(QMainWindow, Ui_MainWindow):

    db_connected: bool

    send_command_signal = QtCore.pyqtSignal(object)

    kill_signal = QtCore.pyqtSignal(int)

    dock_discover_signal = QtCore.pyqtSignal(str)
    cloudplug_discover_signal = QtCore.pyqtSignal(str)

    dockingStationList: QListWidget

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # User-defined setup methods
        self.connectSignalSlots()

        # Allow columns to adjust to their contents
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.verticalHeader().setVisible(False)

        # TODO: remove later, just testing the table
        #for i in range(3):
        #    self.listWidget.addItem(QListWidgetItem(f'Temp CloudPlug {i}'))


        self.appendToDebugLog('Starting device discovery thread')
        discovery_thread = BroadcastThread()
        discovery_thread.device_response.connect(self.handleUdpClientMessage)

        self.kill_signal.connect(discovery_thread.main_window_close_event_handler)

        discovery_thread.start()

        self.appendToDebugLog('Starting TCP server thread')
        self.tcp_server_thread = TcpServerThread()
        

        # It's a lot to type, so use a temp variable to access the tcp_server of the thread
        # to connect slots
        self.tcp_server_thread.client_connected_signal.connect(self.tcpClientConnectHandler)
        self.tcp_server_thread.client_disconnected_signal.connect(self.tcpClientDisconnectHandler)
        self.tcp_server_thread.update_ui_signal.connect(self.updateUiSignalHandler)
        self.tcp_server_thread.log_signal.connect(self.appendToDebugLog)

        self.dock_discover_signal.connect(self.tcp_server_thread.initDockConnection)
        self.cloudplug_discover_signal.connect(self.tcp_server_thread.initCloudplugConnection)

        self.send_command_signal.connect(self.tcp_server_thread.send_command_from_ui)
        self.kill_signal.connect(self.tcp_server_thread.main_window_close_event_handler)

        self.tcp_server_thread.start()


        self.diagnostic_monitor_dialog = MonitorDialog(self)
        self.diagnostic_monitor_dialog.timed_command.connect(self.appendToDebugLog)

    def connectSignalSlots(self):
        # Connect the 'Reprogram Cloudplugs' button to the correct callback
        self.reprogramButton.clicked.connect(self._test_func)

        self.tableWidget.doubleClicked.connect(self.display_sfp_memory_map)

        self.readSfpMemoryButton.clicked.connect(self.clone_sfp_memory_button_handler)

        self.monitorSfpButton.clicked.connect(self.display_monitor_dialog)

    def display_sfp_memory_map(self, clicked_model_index):

        # The SFP the user double clicked from the table
        selected_row_in_table = clicked_model_index.row()

        selected_sfp_id = int(self.tableWidget.item(
            selected_row_in_table, 0
        ).text())


        mydb = SQLConnection()
        mycursor = mydb.get_cursor()
        mycursor.execute(f"SELECT * FROM sfp_info.page_a0 WHERE id={selected_sfp_id};")

        page_a0 = []
        page_a2 = [0] * 256

        # should only be one result...
        for res in mycursor:
            for i in range(1, len(res)):
                page_a0.append(res[i])

        mydb.close()

        sfp = SFP(page_a0, page_a2)

        print(format(sfp.calculate_cc_base(), '02X'))
        print(sfp.get_cc_base())

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


    def handleUdpClientMessage(self, contents_ip_port_tuple: Tuple):
        '''
        Handles the message from a UDP client. 
        '''
        raw_data:    bytes         = contents_ip_port_tuple[0]
        sender_ip:   QHostAddress  = contents_ip_port_tuple[1].toString()
        sender_port: int           = contents_ip_port_tuple[2]

        # DEBUG message
        # self.appendToDebugLog(f'Discovered device at {sender_ip}:{sender_port}')        
        # print(raw_data)

        received_message = unpackRawBytes(raw_data)

        self.appendToDebugLog(received_message)

        if MessageCode(received_message.code) == MessageCode.DOCK_DISCOVER_ACK:
            self.appendToDebugLog(f"Discovered DOCKING STATION at {sender_ip}:{sender_port}")
            print(f"Emitting DOCK {sender_ip}")
            self.dock_discover_signal.emit(sender_ip)
        elif MessageCode(received_message.code) == MessageCode.CLOUDPLUG_DISCOVER_ACK:
            self.appendToDebugLog(f"Discovered CLOUDPLUG at {sender_ip}:{sender_port}")
            print(f"Emitting CLOUDPLUG {sender_ip}")
            self.cloudplug_discover_signal.emit(sender_ip)
        else:
            self.appendToDebugLog(f"Unknown data from {sender_ip}:{sender_port}")

    def clone_sfp_memory_button_handler(self):
        '''
        Method that handles when the "Clone SFP Memory" button is
        clicked.
        '''

        selected_item_in_dock_tab = self.dockingStationList.selectedItems()

        for ip in selected_item_in_dock_tab:
            
            # The IP address is placed as text in the list
            ip = ip.text()

            # The message code is to clone the SFP memory
            code = MessageCode.CLONE_SFP_MEMORY
            # The text of the message doesn't matter for this message
            msg = 'read the memory please and thanks'

            # The server needs to know the IP address of the client
            # and what to send to it. The only way to emit this as a
            # signal is to make it into a tuple
            msg_tuple = (ip, Message(code, msg))

            # Emits the signal with the data as the msg_tuple
            # This signal is caught by the TcpServer thread
            self.send_command_signal.emit(msg_tuple)
            

    def tcpClientConnectHandler(self, data: object):
        self.appendToDebugLog(f"Successful TCP connection from {data}")

        device_type = data[0]
        device_ip = data[1]

        if device_type == DeviceType.DOCKING_STATION:
            self.dockingStationList.addItem(QListWidgetItem(device_ip))
        elif device_type == DeviceType.CLOUDPLUG:
            self.listWidget.addItem(QListWidgetItem(device_ip))

    def tcpClientDisconnectHandler(self, data: str):
        # For each item in the list of docking stations, find its
        # row and remove it from that list.
        
        print(f"Trying to remove data from {data}")

        device_type = data[0]
        device_ip = data[1]

        if device_type == DeviceType.DOCKING_STATION:
            for item in self.dockingStationList.findItems(device_ip, QtCore.Qt.MatchExactly):
                row_of_item = self.dockingStationList.row(item)
                self.dockingStationList.takeItem(row_of_item) # removeListItem didn't work
        elif device_type == DeviceType.CLOUDPLUG:
            for item in self.listWidget.findItems(device_ip, QtCore.Qt.MatchExactly):
                row_of_item = self.listWidget.row(item)
                self.listWidget.takeItem(row_of_item)


    def updateUiSignalHandler(self, code: MessageCode):
        
        if code == MessageCode.CLONE_SFP_MEMORY_SUCCESS:
            self.appendToDebugLog("A docking station successfully, cloned SFP memory")
            self._refreshSfpTable()

    def _refreshSfpTable(self):
        sql_statement = "SELECT * FROM sfp"
        self.appendToDebugLog(f"Executing SQL STATEMENT: {sql_statement}")
        
        db = SQLConnection()

        cursor = db.get_cursor()
        cursor.execute(sql_statement)

        self.tableWidget.setRowCount(0)

        for data_tuple in cursor:
            print(data_tuple)
            self.appendRowInSFPTable(data_tuple)

        db.close()

    # Utility functions

    def closeEvent(self, event):
        print("Closing the window")

        self.kill_signal.emit(-1)
        event.accept()
        

    def _test_func(self):
        selected_item_in_dock_tab = self.dockingStationList.selectedItems()

        for ip in selected_item_in_dock_tab:
            
            # The IP address is what's stored in the list
            ip = ip.text()

            code = MessageCode.REQUEST_SFP_PARAMETERS
            # The text of the message doesn't matter for this message
            msg = 'Read parameters'

            # The server needs to know the IP address of the client
            # and what to send to it. The only way to emit this as a
            # signal is to make it into a tuple
            msg_tuple = (ip, Message(code, msg))

            # Emits the signal with the data as the msg_tuple
            # This signal is caught by the TcpServer thread
            self.send_command_signal.emit(msg_tuple)
        
    def display_monitor_dialog(self):

        selected_items = self.dockingStationList.selectedItems()

        self.diagnostic_monitor_dialog.show()

        if len(selected_items) != 1:
            temp = QErrorMessage()
            if len(selected_items) > 1:
                temp.showMessage("You can only choose 1 Docking Station!")
            else:
                temp.showMessage("No Docking Stations are available!")

            temp.exec()
            temp.deleteLater()
        else:
            self.diagnostic_monitor_dialog.startTimer()
            self.diagnostic_monitor_dialog.show()

    def appendToDebugLog(self, text: str):
        
        text_edit = self.logTab.findChild(QPlainTextEdit, 'plainTextEdit')

        if text_edit:
            formatted_time = time.strftime('%H:%M:%S', time.localtime())
            text_edit.appendPlainText(f'[{formatted_time}]: {text}')

    