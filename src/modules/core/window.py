## 
# @file window.py
# @brief Defines the main window for the application.
#
# @section file_author Author
# - Created on 07/08/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 10/19/2021 by Connor DeCamp
# - Modified on 10/21/2021 by Connor DeCamp
# - Modified on 11/04/2021 by Connor DeCamp
##

##
# Standard Imports
##
import time
from typing import Tuple
import logging

##
# Third Party Library Imports
##
from PyQt5 import QtCore
from PyQt5.QtWidgets import QAbstractScrollArea, QErrorMessage,\
                            QListWidgetItem, QPlainTextEdit,\
                            QTableWidgetItem, QMainWindow

##
# Local Library Imports
## 

from modules.core.sfp import SFP
from modules.core.monitor_dialog import DiagnosticMonitorDialog
from modules.core.window_autogen import Ui_MainWindow
from modules.core.memory_map_dialog import MemoryMapDialog

from modules.network.message import MessageCode, Message
from modules.network.message import ReadRegisterMessage, bytes_to_message
from modules.network.network_threads import BroadcastWorker
from modules.network.sql_connection import SQLConnection
from modules.network.tcp_server import TCPServer
from modules.network.utility import DeviceType

class Window(QMainWindow, Ui_MainWindow):
    '''! Defines the main window of the application.'''    

    ## Signal that is sent to network threads to force socket close
    kill_signal = QtCore.pyqtSignal(int)

    ## Signal used to send network commands across threads
    send_command_signal = QtCore.pyqtSignal(object)

    ## Signal for when a docking station is discovered
    dock_discover_signal = QtCore.pyqtSignal(str)

    ## Signal for when a cloudplug is discovered
    cloudplug_discover_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # User-defined setup methods
        self.connect_signal_slots()

        # Allow columns to adjust to their contents
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.verticalHeader().setVisible(False)

        self.append_to_debug_log('Starting UDP device discovery thread')
        self.udp_thread = QtCore.QThread()
        self.worker = BroadcastWorker()
        self.worker.moveToThread(self.udp_thread)

        self.worker.device_response.connect(self.handle_udp_client_message)
        self.udp_thread.started.connect(self.worker.on_thread_start)
        self.kill_signal.connect(self.worker.cleanup)
        self.udp_thread.start()

        #udp_thread = BroadcastThread()
        #udp_thread.device_response.connect(self.handleUdpClientMessage)
        #self.kill_signal.connect(udp_thread.main_window_close_event_handler)
        #udp_thread.start()

        
        
        self.append_to_debug_log('Starting TCP server thread')
        self.tcp_thread = QtCore.QThread()
        self.tcp_server = TCPServer()
        self.tcp_server.moveToThread(self.tcp_thread)
        self.tcp_server.client_connected_signal.connect(self.handle_tcp_client_connect)
        self.tcp_server.client_disconnected_signal.connect(self.handle_tcp_client_disconnect)
        self.tcp_server.update_ui_signal.connect(self.handle_update_ui_signal)
        self.tcp_server.log_signal.connect(self.append_to_debug_log)

        self.tcp_server.diagnostic_init_a0_signal.connect(self.handle_init_diagnostic_a0)
        self.tcp_server.diagnostic_init_a2_signal.connect(self.handle_init_diagnostic_a2)
        self.tcp_server.real_time_refresh_signal.connect(self.handle_real_time_refresh)
        self.tcp_server.remote_io_error_signal.connect(self.handle_remote_io_error)

        self.dock_discover_signal.connect(self.tcp_server.init_dock_connection)
        self.cloudplug_discover_signal.connect(self.tcp_server.init_cloudplug_connection)
        self.send_command_signal.connect(self.tcp_server.handle_send_command_signal)
        self.kill_signal.connect(self.tcp_server._close_all_connections)
        
        self.tcp_thread.started.connect(self.tcp_server.open_session)
        self.tcp_thread.start()

        # This code was commented out in favor of the above code.
        # There is no more need for a class that subclasses the QThread
        # object. Instead, it's moved to a thread that we own.

        #TODO: Think about removing this commented out code
        # It's a lot to type, so use a temp variable to access the tcp_server of the thread
        # to connect slots
        # self.tcp_server_thread = TcpServerThread()
        #self.tcp_server_thread.client_connected_signal.connect(self.tcpClientConnectHandler)
        #self.tcp_server_thread.client_disconnected_signal.connect(self.tcpClientDisconnectHandler)
        #self.tcp_server_thread.update_ui_signal.connect(self.updateUiSignalHandler)
        #self.tcp_server_thread.log_signal.connect(self.appendToDebugLog)
        #self.tcp_server_thread.diagnostic_init_a0_signal.connect(self.handle_init_diagnostic_a0)
        #self.tcp_server_thread.diagnostic_init_a2_signal.connect(self.handle_init_diagnostic_a2)
        #self.tcp_server_thread.real_time_refresh_signal.connect(self.handle_real_time_refresh)
        #self.tcp_server_thread.remote_io_error_signal.connect(self.handle_remote_io_error)

        #self.dock_discover_signal.connect(self.tcp_server_thread.initDockConnection)
        #self.cloudplug_discover_signal.connect(self.tcp_server_thread.initCloudplugConnection)

        #self.send_command_signal.connect(self.tcp_server_thread.send_command_from_ui)
        #self.kill_signal.connect(self.tcp_server_thread.main_window_close_event_handler)

        #self.tcp_server_thread.start()
        
        ## The diagnostic monitoring window object
        self.diagnostic_monitor_dialog = DiagnosticMonitorDialog(self)
        self.diagnostic_monitor_dialog.timed_command.connect(self.handle_diagnostic_timer_timeout)
        
        # Populate the table when the application opens
        try:
            self._refresh_sfp_table()
        except Exception as ex:
            logging.error(f'{ex}')
            error_dialog = QErrorMessage()
            error_dialog.showMessage(f'{ex}')
            error_dialog.exec()
            self.kill_signal.emit(-1)
            time.sleep(2)
            raise ex

    def connect_signal_slots(self):
        # Connect the 'Reprogram Cloudplugs' button to the correct callback
        self.reprogramButton.clicked.connect(self.cloudplug_reprogram_button_handler)
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

        # Get the page_a0 values from the cursor
        for res in mycursor:
            for i in range(1, len(res)):
                page_a0.append(res[i])

        mycursor.execute(f"SELECT * FROM sfp_info.page_a2 WHERE id={selected_sfp_id};")

        page_a2 = []

        # Get the page_a2 values from the cursor
        for res in mycursor:
            for i in range(1, len(res)):
                page_a2.append(res[i])

        mydb.close()

        sfp = SFP(page_a0, page_a2)

        # Compare checksum values
        #print(format(sfp.calculate_cc_base(), '02X'))
        #print(sfp.get_cc_base())

        # Create SFP object after reading from database

        memory_dialog = MemoryMapDialog(self)
        memory_dialog.initialize_table_values(sfp)
        memory_dialog.refresh_stress_scenario_table(selected_sfp_id)
        memory_dialog.show()

    def append_row_to_sfp_table(self, id_memory_map_tuple: Tuple) -> None:
        '''! Appends an entry to the SFP table shown on the main screen
        of the application. The page 0xA0 identifying information is
        used to determine vendor name, part number, serial number, etc.
        
        @param id_memory_map_tuple A tuple consisting of the SFP ID from the database
        and the information page (0xA0) memory map values.
        '''
        self.append_to_debug_log(f'Adding SFP with ID {id_memory_map_tuple[0]} to SFP table')

        ID = 0
        temp_sfp = SFP(id_memory_map_tuple[1:], [0]*256)

        rowPosition = self.tableWidget.rowCount()        
        self.tableWidget.insertRow(rowPosition)

        self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(id_memory_map_tuple[ID])))
        self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(temp_sfp.get_vendor_name()))
        self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(temp_sfp.get_vendor_part_number()))
        self.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(temp_sfp.get_vendor_serial_number()))
        self.tableWidget.setItem(rowPosition, 4, QTableWidgetItem(temp_sfp.get_connector_type()))
        self.tableWidget.setItem(rowPosition, 5, QTableWidgetItem(str(temp_sfp.get_wavelength())))


        self.tableWidget.resizeColumnsToContents()

    def cloudplug_reprogram_button_handler(self) -> None:
        """! User presses this button to reprogram the selected cloudplugs with
        a single selected SFP/SFP+ persona.
        """

        # Check to see if the user has selected at least one cloudplug
        selected_cloudplugs = self.listWidget.selectedItems()
        logging.debug(f'User has selected {len(selected_cloudplugs)} cloudplugs')

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

        sfp_id = int(selected_sfp_persona[0].data())


        msg_code = MessageCode.REPGORAM_CLOUDPLUG
        data_to_send = [sfp_id]
        msg = ReadRegisterMessage(msg_code, '', 0x00, data_to_send)

        # For each selected cloudplug, send the command
        for ip in selected_cloudplugs:
            cloudplug_ip = ip.text()
            msg_tuple = (cloudplug_ip, msg)
            self.send_command_signal.emit(msg_tuple)

    def handle_udp_client_message(self, contents_ip_port_tuple: Tuple):
        '''! Handles the message from a UDP client.'''
        raw_data = contents_ip_port_tuple[0]
        sender_ip = contents_ip_port_tuple[1].toString()
        sender_port = contents_ip_port_tuple[2]

        # DEBUG message
        # self.appendToDebugLog(f'Discovered device at {sender_ip}:{sender_port}')        
        # print(raw_data)

        received_message = bytes_to_message(raw_data)

        self.append_to_debug_log(received_message)

        if MessageCode(received_message.code) == MessageCode.DOCK_DISCOVER_ACK:
            self.append_to_debug_log(f"Discovered DOCKING STATION at {sender_ip}:{sender_port}")
            logging.debug(f"Emitting DOCK {sender_ip}")
            self.dock_discover_signal.emit(sender_ip)
        elif MessageCode(received_message.code) == MessageCode.CLOUDPLUG_DISCOVER_ACK:
            self.append_to_debug_log(f"Discovered CLOUDPLUG at {sender_ip}:{sender_port}")
            logging.debug(f"Emitting CLOUDPLUG {sender_ip}")
            self.cloudplug_discover_signal.emit(sender_ip)
        else:
            self.append_to_debug_log(f"Unknown data from {sender_ip}:{sender_port}")

    def clone_sfp_memory_button_handler(self):
        '''! Method that handles when the "Clone SFP Memory" button is
        clicked.
        '''

        selected_item_in_dock_tab = self.dockingStationList.selectedItems()

        # Disable the button until succesful read OR error
        self.readSfpMemoryButton.setEnabled(False)
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
            

    def handle_tcp_client_connect(self, data: DeviceType):
        '''! Handles when a TCP client connects.'''
        self.append_to_debug_log(f"Successful TCP connection from {data}")

        device_type = data[0]
        device_ip = data[1]

        if device_type == DeviceType.DOCKING_STATION:
            self.dockingStationList.addItem(QListWidgetItem(device_ip))
        elif device_type == DeviceType.CLOUDPLUG:
            self.listWidget.addItem(QListWidgetItem(device_ip))

    def handle_tcp_client_disconnect(self, data: DeviceType):
        '''!Handles when a TCP client disconnects.
        
        @param data The DeviceType object to be removed from the software.
        '''
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


    def handle_update_ui_signal(self, code: MessageCode):
        '''!Handles the update_ui_signal emitted from the
        TCP server.

        @param code The MessageCode enumerated value to be processed
        '''
        if code == MessageCode.CLONE_SFP_MEMORY_SUCCESS:
            self.append_to_debug_log("A docking station successfully, cloned SFP memory")
            self.readSfpMemoryButton.setEnabled(True)
            self._refresh_sfp_table()
        elif code == MessageCode.CLONE_SFP_MEMORY_ERROR:
            self.append_to_debug_log("A docking station had an error reading SFP memory.")
            self.readSfpMemoryButton.setEnabled(True)

    def _refresh_sfp_table(self):
        '''! Refreshes the SFP table on the main screen.

        @brief Accesses the SFP database to refresh all of the available
        personas.
        '''
        sql_statement = "SELECT * FROM page_a0"
        self.append_to_debug_log(f"Executing SQL STATEMENT: {sql_statement}")
        
        db = SQLConnection()

        cursor = db.get_cursor()
        cursor.execute(sql_statement)

        self.tableWidget.setRowCount(0)

        for data_tuple in cursor:
            self.append_row_to_sfp_table(data_tuple)

        db.close()
    
        
    def display_monitor_dialog(self):
        '''! Function to display the diagnostic monitoring dialog.

        @brief If the user has selected a connected Docking Station,
        it opens a diagnostic monitoring dialog that allows the user
        to see the diagnostics of the SFP module.
        '''
        selected_items = self.dockingStationList.selectedItems()
        
        if len(selected_items) != 1:
            error_msg = QErrorMessage()
            if len(selected_items) > 1:
                error_msg.showMessage("You can only choose 1 Docking Station!")
            else:
                error_msg.showMessage("No Docking Stations are available!")

            error_msg.exec()
            error_msg.deleteLater()
        else:
            selected_item = selected_items[0]
            # We need to read a lot of values from the SFP before
            # we start doing diagnostic monitoring
            # Initially, we need to read:
            #   - Vendor name (16 bytes)
            #   - Part number (16 bytes)
            #   - Diagnostic Monitoring Type (1 byte)
            #   - ALL of the alarm and warning thresholds (40 or 56 bytes)

            # So we are expecting at least 73 and at most
            # 89 bytes back from the docking station

            dock_ip = selected_item.text()
            self.diagnostic_monitor_dialog.dock_ip = dock_ip

            page_a0_registers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                                 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                                 92]
            msg = ReadRegisterMessage(MessageCode.DIAGNOSTIC_INIT_A0, "", 0x50, page_a0_registers)
            self.send_command_signal.emit((dock_ip, msg))

            page_a2_registers = [i for i in range(91 + 1)]
            page_a2_registers += [i for i in range(96, 109 + 1)]
            msg = ReadRegisterMessage(MessageCode.DIAGNOSTIC_INIT_A2, "", 0x51, page_a2_registers)
            self.send_command_signal.emit((dock_ip, msg))

            self.diagnostic_monitor_dialog.start_timer()
            self.diagnostic_monitor_dialog.show()

    def handle_init_diagnostic_a0(self, cmd: ReadRegisterMessage):
        '''! Handles updating identifying information from the SFP inserted
        in the docking station. This is so the user knows what SFP
        is being monitored.

        @param cmd The ReadRegisterMessage object received from the TCP Server.
        '''
        sfp_ptr = self.diagnostic_monitor_dialog.associated_sfp

        i = 0
        for val in cmd.register_numbers[0:16]:
            sfp_ptr.page_a0[20 + i] = val
            i += 1

        i = 0        
        for val in cmd.register_numbers[16:32]:
            sfp_ptr.page_a0[40 + i] = val
            i += 1

        diagnostic_int = cmd.register_numbers[len(cmd.register_numbers) - 1]
        sfp_ptr.page_a0[92] = diagnostic_int
        sfp_ptr.force_calibration_check()

        calibration_str = ""
        if sfp_ptr.calibration_type == SFP.CalibrationType.INTERNAL:
            calibration_str = "Internally Calibrated"
        elif sfp_ptr.calibration_type == SFP.CalibrationType.EXTERNAL:
            calibration_str = "Externally Calibrated"

        self.diagnostic_monitor_dialog.lineEdit.setText(sfp_ptr.get_vendor_name())
        self.diagnostic_monitor_dialog.lineEdit_2.setText(sfp_ptr.get_vendor_part_number())
        self.diagnostic_monitor_dialog.lineEdit_3.setText(calibration_str)
        


    def handle_init_diagnostic_a2(self, cmd: ReadRegisterMessage):
        '''! Handles the diagnostic information from page 0xA2 of the
        SFP memory map. This page contains the diagnostic alarms/warnings
        and calibration constants.

        @param cmd The ReadRegisterMessage that was received from the TCP Server.
        '''
        m = self.diagnostic_monitor_dialog
        sfp_ptr = m.associated_sfp

        for i in range(91 + 1):
            sfp_ptr.page_a2[i] = cmd.register_numbers[i]

        for i in range(96, 109 + 1):
            sfp_ptr.page_a2[i] = cmd.register_numbers[i - 4]

        self.diagnostic_monitor_dialog.update_alarm_warning_tab()
        self.diagnostic_monitor_dialog.update_real_time_tab()

    def handle_diagnostic_timer_timeout(self):
        '''! Handles the diagnostic monitoring timeout. Sends a message to the
        respective docking station that requests the updated A/D values.
        '''
        # Send a refresh real-time diagnostics message
        code = MessageCode.REAL_TIME_REFRESH
        page_num = 0x51
        # All the register numbers for diagnostic information
        registers = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109]

        command = ReadRegisterMessage(code, "", page_num, registers)
        self.send_command_signal.emit((self.diagnostic_monitor_dialog.dock_ip, command))

    def handle_real_time_refresh(self, cmd: ReadRegisterMessage):
        '''! Handles the refreshing of diagnostic data from the
        a docking station.

        @param cmd The ReadRegisterMessage object that contains the updated
        A/D values.
        '''
        # Expecting data from registers [96, 109] in page 0x51 (aka 0xA2)
        sfp_ptr = self.diagnostic_monitor_dialog.associated_sfp
        sfp_ptr.force_calibration_check()

        for i in range(96, 109 + 1):
            sfp_ptr.page_a2[i] = cmd.register_numbers[i - 96]

        self.diagnostic_monitor_dialog.update_real_time_tab()

    def handle_remote_io_error(self, cmd: Message):
        '''! Handles when a device responds with 'Remote IO Error'.
        @param cmd The message object that was sent
        '''
        self.append_to_debug_log(cmd)
        self.diagnostic_monitor_dialog.close()

    ##
    # Utility functions
    #
    # You cannot rename closeEvent(), its a pyQT function.
    ##
    def closeEvent(self, event):
        '''! Handles the closeEvent when the user presses the red X.
        This is an reimplemented PyQT function to modify the behavior
        of the closeEvent slot.
        '''
        logging.debug("Closing the window")
        self.kill_signal.emit(-1)
        self.tcp_thread.exit()
        logging.debug("Killed TCP thread")
        self.udp_thread.exit()
        logging.debug("Killed UDP thread")
        event.accept()

    def append_to_debug_log(self, text: str):
        '''! Allows timestamped debug messages to be added to a text log.

            @param text The text to be added to the debug log.
        '''
        logging.debug(text)
        # Select the text-edit widget on the debug tab
        text_edit = self.logTab.findChild(QPlainTextEdit, 'plainTextEdit')

        # If we find it
        if text_edit:
            # Format the local time into HH:MM:SS and append to the debug log
            formatted_time = time.strftime('%H:%M:%S', time.localtime())
            text_edit.appendPlainText(f'[{formatted_time}]: {text}')




    