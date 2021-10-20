##
# @file monitor_dialog.py
# @brief Defines the diagnostic monitoring window.
#
# @section file_author Author
# - Created on 10/18/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 10/19/2021 by Connor DeCamp
##

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from modules.core.monitor_dialog_autogen import Ui_Dialog

class MonitorDialog(QDialog, Ui_Dialog):

    timed_command = pyqtSignal(str)

    MESSAGE_INTERVAL_MSEC: int = 2000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Window is application modal - cannot do anything else until it's closed out.
        # This may not be the greatest solution
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("Monitor SFP Parameters")


        self.lineEdit.setReadOnly(True)
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_3.setReadOnly(True)

        # This is disgusting, but I want to set all of the line edits to be read only
        line_edits = [self.temperatureLineEdit, self.vccLineEdit, self.txBiasCurrentLineEdit,
        self.txPowerLineEdit, self.rxPowerLineEdit, self.laserTempLineEdit, self.tecCurrentLineEdit,
        self.tempHighAlarmLineEdit, self.tempLowAlarmLineEdit, self.vccHighAlarmLineEdit, self.vccLowAlarmLineEdit,
        self.txBiasHighAlarmLineEdit, self.txBiasLowAlarmLineEdit, self.txPowerHighAlarmLineEdit, self.txPowerLowAlarmLineEdit,
        self.rxPowerHighAlarmLineEdit, self.rxPowerLowAlarmLineEdit, self.laserTempHighAlarmLineEdit, self.laserTempLowAlarmLineEdit,
        self.tecCurrentHighAlarmLineEdit, self.tecCurrentLowAlarmLineEdit,
        self.tempHighWarnLineEdit, self.tempLowWarnLineEdit, self.vccHighWarnLineEdit, self.vccLowWarnLineEdit,
        self.txBiasHighWarnLineEdit, self.txBiasLowWarnLineEdit, self.txPowerHighWarnLineEdit, self.txPowerLowWarnLineEdit,
        self.rxPowerHighWarnLineEdit, self.rxPowerLowWarnLineEdit, self.laserTempHighWarnLineEdit, self.laserTempLowWarnLineEdit,
        self.tecCurrentHighWarnLineEdit, self.tecCurrentLowWarnLineEdit]

        for line_edit in line_edits:
            line_edit.setReadOnly(True)



        self.timer = QTimer()
        self.timer.timeout.connect(self._emit_command_restart_timer)

    def _emit_command_restart_timer(self):
        self.timed_command.emit("Diagnostic Monitor emitting event")
        self.startTimer()

    def startTimer(self):
        self.timer.start(self.MESSAGE_INTERVAL_MSEC)

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
