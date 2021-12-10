##
# @file monitor_dialog.py
# @brief Defines the diagnostic monitoring window.
#
# @section file_author Author
# - Created on 10/18/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 10/19/2021 by Connor DeCamp
# - Modified on 10/20/2021 by Connor DeCamp
# - Modified on 10/21/2021 by Connor DeCamp
##

import logging
from PyQt5.QtCore import pyqtSignal

##
# Third Party Library Imports
##
from PyQt5.QtWidgets import QDialog, QErrorMessage, QTableWidgetItem

##
# Local Library Imports
##
from modules.network.sql_connection import SQLConnection

from modules.core.run_stress_dialog_autogen import Ui_Dialog
from modules.core.sfp import *

class RunStressDialog(QDialog, Ui_Dialog):

    command_signal = pyqtSignal(int)

    def __init__(self, sfp_id: int, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.send_run_command)

        conn = SQLConnection()
        cursor = conn.get_cursor()

        cursor.execute(f'SELECT * FROM stress_scenarios where sfp_id={sfp_id}')

        stress_scenarios_list = []
        for res in cursor:
            stress_scenarios_list.append(res)

        conn.close()

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
        self.tableWidget.setRowCount(0)
        for data in stress_scenarios_list:
            stress_id = data[0]
            scenario_name = data[3]
            list_of_values = [val for val in data[4::]]

            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)
            self.tableWidget.setItem(row_count, 0, QTableWidgetItem(str(stress_id)))
            self.tableWidget.setItem(row_count, 1, QTableWidgetItem(str(scenario_name)))
            self.tableWidget.setItem(row_count, 2, QTableWidgetItem(repr(list_of_values)))

        self.tableWidget.resizeColumnsToContents()



    def send_run_command(self):

        # Check to see if user selected stress recording
        selected_stress_recordings = self.tableWidget.selectionModel().selectedIndexes()

        if len(selected_stress_recordings) == 0:
            error = QErrorMessage()
            error.showMessage('You must select a stress recording!')
            error.exec()
            return

        stress_id = int(selected_stress_recordings[0].data())

        self.command_signal.emit(stress_id)
        