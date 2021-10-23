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

##
# Third Party Library Imports
##
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

##
# Local Library Imports
##
from modules.core.monitor_dialog_autogen import Ui_Dialog
from modules.core.sfp import *

class DiagnosticMonitorDialog(QDialog, Ui_Dialog):

    timed_command = pyqtSignal()

    MESSAGE_INTERVAL_MSEC: int = 1000

    associated_sfp = SFP([0]*256, [0]*256)

    dock_ip = ""

    def __init__(self, parent=None):
        '''! Initilazes the Diagnostic Monitoring Dialgo
        '''
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

    def update_alarm_warning_tab(self):
        
        sfp_ptr = self.associated_sfp

        self.tempHighAlarmLineEdit.setText(f'{sfp_ptr.get_temp_high_alarm():.3f}')
        self.tempLowAlarmLineEdit.setText(f'{sfp_ptr.get_temp_low_alarm():.3f}')
        self.tempHighWarnLineEdit.setText(f'{sfp_ptr.get_temp_high_warning():.3f}')
        self.tempLowWarnLineEdit.setText(f'{sfp_ptr.get_temp_low_warning():.3f}')

        # Voltage is measured in 100 uV, or 100 * 10^-6 = 10^-4 = 10000.0 
        # if we want it in Volts
        self.vccHighAlarmLineEdit.setText(f'{sfp_ptr.get_voltage_high_alarm() / 10000.0:.3f}')
        self.vccLowAlarmLineEdit.setText(f'{sfp_ptr.get_voltage_low_alarm() / 10000.0:.3f}')
        self.vccHighWarnLineEdit.setText(f'{sfp_ptr.get_voltage_high_warning() / 10000.0:.3f}')
        self.vccLowWarnLineEdit.setText(f'{sfp_ptr.get_voltage_low_warning() / 10000.0:.3f}')

        # LSB is 2 uA, or 2*10**-6
        # If we want milli, multiply by 10^3
        self.txBiasHighAlarmLineEdit.setText(f'{sfp_ptr.get_bias_high_alarm() * 2*10**-3:.3f}')
        self.txBiasLowAlarmLineEdit.setText(f'{sfp_ptr.get_bias_low_alarm()*2*10**-3:.3f}')
        self.txBiasHighWarnLineEdit.setText(f'{sfp_ptr.get_bias_high_warning()*2*10**-3:.3f}')
        self.txBiasLowWarnLineEdit.setText(f'{sfp_ptr.get_bias_low_warning()*2*10**-3:.3f}')

        # LSB is 0.1uW
        self.txPowerHighAlarmLineEdit.setText(f'{sfp_ptr.get_tx_power_high_alarm() * 0.1:.3f}')
        self.txPowerLowAlarmLineEdit.setText(f'{sfp_ptr.get_tx_power_low_alarm() * 0.1:.3f}')
        self.txPowerHighWarnLineEdit.setText(f'{sfp_ptr.get_tx_power_high_warning() * 0.1:.3f}')
        self.txPowerLowWarnLineEdit.setText(f'{sfp_ptr.get_tx_power_low_warning() * 0.1:.3f}')

        # LSB is 0.1uW
        self.rxPowerHighAlarmLineEdit.setText(f'{sfp_ptr.get_rx_power_high_alarm() * 0.1:.3f}')
        self.rxPowerLowAlarmLineEdit.setText(f'{sfp_ptr.get_rx_power_low_alarm() * 0.1:.3f}')
        self.rxPowerHighWarnLineEdit.setText(f'{sfp_ptr.get_rx_power_high_warning() * 0.1:.3f}')
        self.rxPowerLowWarnLineEdit.setText(f'{sfp_ptr.get_rx_power_low_warning() * 0.1:.3f}')

        self.laserTempHighAlarmLineEdit.setText(f'{sfp_ptr.get_optional_laser_temp_high_alarm():.3f}')
        self.laserTempLowAlarmLineEdit.setText(f'{sfp_ptr.get_optional_laser_temp_low_alarm():.3f}')
        self.laserTempHighWarnLineEdit.setText(f'{sfp_ptr.get_optional_laser_temp_high_warning():.3f}')
        self.laserTempLowWarnLineEdit.setText(f'{sfp_ptr.get_optional_laser_temp_low_warning():.3f}')

        self.tecCurrentHighAlarmLineEdit.setText(f'{sfp_ptr.get_optional_tec_current_high_alarm():.3f}')
        self.tecCurrentLowAlarmLineEdit.setText(f'{sfp_ptr.get_optional_tec_current_low_alarm():.3f}')
        self.tecCurrentHighWarnLineEdit.setText(f'{sfp_ptr.get_optional_tec_current_high_warning():.3f}')
        self.tecCurrentLowWarnLineEdit.setText(f'{sfp_ptr.get_optional_laser_temp_low_warning():.3f}')

    def update_real_time_tab(self):
        sfp = self.associated_sfp
        self.temperatureLineEdit.setText(f'{sfp.get_temperature():.3f}')
        self.vccLineEdit.setText(f'{sfp.get_vcc() / Decimal(10000.0):.3f}')
        self.txBiasCurrentLineEdit.setText(f'{sfp.get_tx_bias_current() * Decimal(2 * 10**-3):.3f}')
        self.txPowerLineEdit.setText(f'{sfp.get_tx_power() * Decimal(0.1):.3f}')
        self.rxPowerLineEdit.setText(f'{sfp.calculate_rx_power_uw() * Decimal(0.1):.3f}')

        self.laserTempLineEdit.setText(f'{sfp.get_laser_temp_or_wavelength():.3f}')
        self.tecCurrentLineEdit.setText(f'{sfp.get_tec_current():.3f}')

    def _emit_command_restart_timer(self):
        self.timed_command.emit()
        print(f'{self.associated_sfp.page_a2[96:98]}')
        self.start_timer()

    def start_timer(self):
        self.timer.start(self.MESSAGE_INTERVAL_MSEC)

    ##
    # PyQT overloaded function
    ##
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
