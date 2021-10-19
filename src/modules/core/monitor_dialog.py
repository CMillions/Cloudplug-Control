

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

        self.temperatureLineEdit.setReadOnly(True)
        self.vccLineEdit.setReadOnly(True)
        self.txBiasCurrentLineEdit.setReadOnly(True)
        self.txPowerLineEdit.setReadOnly(True)
        self.rxPowerLineEdit.setReadOnly(True)
        self.laserTempLineEdit.setReadOnly(True)
        self.tecCurrentLineEdit.setReadOnly(True)


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
