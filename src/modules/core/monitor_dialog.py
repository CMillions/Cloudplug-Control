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
from typing import Union
from PyQt5.QtWidgets import QDialog, QLineEdit
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

##
# Local Library Imports
##
from modules.core.monitor_dialog_autogen import Ui_Dialog
from modules.core.sfp import *

class DiagnosticMonitorDialog(QDialog, Ui_Dialog):

    ## Signal emitted when internal timer times out
    timed_command = pyqtSignal()

    ## Messaging interval in milliseconds
    MESSAGE_INTERVAL_MSEC = 1000

    ## SFP object to monitor diagnostics of
    associated_sfp = SFP([0]*256, [0]*256)
    
    ## IP address of associated docking station
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
        # Update the color of the text based on the value
        # compared to thresholds
        #
        # Red:         >= alarm high
        # Orange:      >= warning high
        # Green/black: > warning low
        # light blue:  > alarm low
        # dark blue:   <= alarm low
        temperature = sfp.get_temperature()
        self.temperatureLineEdit.setText(f'{temperature:.3f}')
        self._update_color_indicator(
            float(self.temperatureLineEdit.text()), 
            float(self.tempHighAlarmLineEdit.text()),
            float(self.tempHighWarnLineEdit.text()),
            float(self.tempLowWarnLineEdit.text()),
            float(self.tempLowAlarmLineEdit.text()),
            self.temperatureLineEdit
        )

        self.vccLineEdit.setText(f'{sfp.get_vcc() / Decimal(10000.0):.3f}')
        self._update_color_indicator(
            float(self.vccLineEdit.text()),
            float(self.vccHighAlarmLineEdit.text()),
            float(self.vccHighWarnLineEdit.text()),
            float(self.vccLowWarnLineEdit.text()),
            float(self.vccLowAlarmLineEdit.text()),
            self.vccLineEdit
        )

        self.txBiasCurrentLineEdit.setText(f'{sfp.get_tx_bias_current() * Decimal(2 * 10**-3):.3f}')
        self._update_color_indicator(
            float(self.txBiasCurrentLineEdit.text()),
            float(self.txBiasHighAlarmLineEdit.text()),
            float(self.txBiasHighWarnLineEdit.text()),
            float(self.txBiasLowWarnLineEdit.text()),
            float(self.txBiasLowAlarmLineEdit.text()),
            self.txBiasCurrentLineEdit
        )

        self.txPowerLineEdit.setText(f'{sfp.get_tx_power() * Decimal(0.1):.3f}')
        self._update_color_indicator(
            float(self.txPowerLineEdit.text()),
            float(self.txPowerHighAlarmLineEdit.text()),
            float(self.txPowerHighWarnLineEdit.text()),
            float(self.txPowerLowWarnLineEdit.text()),
            float(self.txPowerLowAlarmLineEdit.text()),
            self.txPowerLineEdit
        )

        self.rxPowerLineEdit.setText(f'{sfp.calculate_rx_power_uw() * Decimal(0.1):.3f}')
        self._update_color_indicator(
            float(self.rxPowerLineEdit.text()),
            float(self.rxPowerHighAlarmLineEdit.text()),
            float(self.rxPowerHighWarnLineEdit.text()),
            float(self.rxPowerLowWarnLineEdit.text()),
            float(self.rxPowerLowAlarmLineEdit.text())
        )

        #TODO - provide color coding for optional parameters
        if sfp.calibration_type == SFP.CalibrationType.INTERNAL:
            self.laserTempLineEdit.setText(f'{sfp.get_laser_temp_or_wavelength():.3f}')
            self.tecCurrentLineEdit.setText(f'{sfp.get_tec_current():.3f}')
        else:
            self.laserTempLineEdit.setText('Not supported')
            self.tecCurrentLineEdit.setText('Not supported')

        

        

    def _update_color_indicator(self, diagnostic_value: Union[Decimal, float], 
        alarm_high: Union[Decimal, float], warning_high: Union[Decimal, float], 
        warning_low: Union[Decimal, float], alarm_low: Union[Decimal, float], 
        line_edit: QLineEdit
    ):
        '''! Updates the color of real-time diagnostic values to visually indicate
        where they are compared to alarm and warning thresholds. Text color is
        RED for alarm high, YELLOW for warning high, BLACK for normal, LIGHT BLUE
        for warning low, and BLUE for alarm low.

        @param diagnostic_value The diagnostic value to be interpreted
        @param alarm_high The alarm high threshold
        @param warning_high The warning high threshold
        @param warning_low The warning low threshold
        @param alarm_low The alarm low threshold
        @param line_edit The QLineEdit object to be updated
        '''

        # Colors in qtStyleSheet format
        RED = 'rgb(255, 0, 0)'
        YELLOW = 'rgb(237, 212, 0)'
        BLACK = 'rgb(0, 0, 0)'
        LIGHT_BLUE = 'rgb(114, 159, 207)'
        BLUE = 'rgb(0, 0, 255)'

        if diagnostic_value >= alarm_high:
            line_edit.setStyleSheet(f'color: {RED}')
        elif diagnostic_value >= warning_high:
            line_edit.setStyleSheet(f'color: {YELLOW}')
        elif diagnostic_value > warning_low:
            line_edit.setStyleSheet(f'color: {BLACK}')
        elif diagnostic_value > alarm_low:
            line_edit.setStyleSheet(f'color: {LIGHT_BLUE}')
        else:
            line_edit.setStyleSheet(f'color: {BLUE}')

    def _emit_command_restart_timer(self):
        '''! Emits the timed_command signal and restarts the timer.'''
        self.timed_command.emit()
        self.start_timer()

    def start_timer(self):
        '''! Starts the window message timer.'''
        self.timer.start(self.MESSAGE_INTERVAL_MSEC)

    ##
    # PyQT overloaded function
    ##
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
