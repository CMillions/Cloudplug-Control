##
# @file diagnostic_plot.py
# @brief Defines the diagnostic plot widget.
#
# @section file_author Author
# - Created on 11/12/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 11/15/2021 by Connor DeCamp
# - Modified on 11/23/2021 by Connor DeCamp
##

##
# Standard imports
##
from collections import namedtuple

##
# Third party library imports
##
import numpy as np
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QWidget
from PyQt5.QtCore import Qt
import pyqtgraph as pg

##
# Named Tuple for diagnostic data that
# needs to be plotted
##
DiagnosticData = namedtuple(
    "DiagnosticData",
    "temperature, vcc, tx_bias, tx_power, \
    rx_power, laser_temperature, tec_current"
)

class DiagnosticPlotWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QGridLayout()

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self.setWindowTitle("Diagnostic Plots")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.temperature_plot, self.temperature_plot_data = self._create_plot(
            "Module Temperature",
            "Time (sec)",
            "Degrees (C)"
        )

        self.vcc_plot, self.vcc_plot_data = self._create_plot(
            "VCC",
            "Time (sec)",
            "Voltage (V)"
        )

        self.tx_bias_plot, self.tx_bias_plot_data = self._create_plot(
            "TX Bias Current",
            "Time (sec)",
            "Current (mA)"
        )

        self.tx_power_plot, self.tx_power_plot_data = self._create_plot(
            "TX Power",
            "Time (sec)",
            "Power (uW)"
        )

        self.rx_power_plot, self.rx_power_plot_data = self._create_plot(
            "RX Power",
            "Time (sec)",
            "Power (uW)"
        )

        self.main_layout.addWidget(self.temperature_plot, 0, 0)
        self.main_layout.addWidget(self.vcc_plot, 0, 2)
        self.main_layout.addWidget(self.tx_bias_plot, 0, 4)
        self.main_layout.addWidget(self.tx_power_plot, 2, 0)
        self.main_layout.addWidget(self.rx_power_plot, 2, 2)


        self.hline = QFrame(self)
        self.hline.setFrameShape(QFrame.HLine)
        #self.hline.setFrameShadow(QFrame.Sunken)

        self.vline = QFrame(self)
        self.vline.setFrameShape(QFrame.VLine)

        self.vline2 = QFrame(self)
        self.vline2.setFrameShape(QFrame.VLine)

        self.main_layout.addWidget(self.hline, 1, 0, 1, 5)
        self.main_layout.addWidget(self.vline, 0, 1, 3, 1)
        self.main_layout.addWidget(self.vline2, 0, 3, 3, 1)
        self.setLayout(self.main_layout)

        self.temperature_values = []
        self.vcc_values = []
        self.tx_bias_values = []
        self.rx_power_values = []
        self.tx_power_values= []

        self.domain_limit = 30
        self.temperature_plot.setXRange(0, self.domain_limit)
        self.vcc_plot.setXRange(0, self.domain_limit)
        self.tx_bias_plot.setXRange(0, self.domain_limit)
        self.rx_power_plot.setXRange(0, self.domain_limit)
        self.tx_power_plot.setXRange(0, self.domain_limit)

        ##
        # Plot ranges change
        ##
        # Temperature expects [-127.996, 127.996] C
        # VCC is [0, 6.5535] V
        # Tx_Bias is [0, 131] mA
        # TX_PWR is [0, 6.5535] mW
        # RX_PWR is [0, 6.5535] mW
        #
        ##
        # Optional plot ranges
        ##
        # Laser Temp is [-127.996, 127.996] C
        #    ^ This could also be wavelength
        #
        # TEC current is [-3276.8, 3276.8] mA
        ##

        self.temperature_plot.setYRange(-128, 128)
        self.vcc_plot.setYRange(0, 7)
        self.tx_bias_plot.setYRange(0, 135)
        self.rx_power_plot.setYRange(0, 7)
        self.tx_power_plot.setYRange(0, 7)

    def _create_plot(self, title: str, x_label: str, y_label:str) -> pg.PlotWidget:
        '''! Creates a PlotWidget object for specific use in this module.
        
        @param title The title of the plot
        @param x_label The label for the x-axis
        @param y_label The label for the y-axis
        @return A tuple containing the plot object and the plot data object
        '''
        plot = pg.PlotWidget(title=title, left=y_label, bottom=x_label)
        plot.showGrid(x=True, y=True)
        plot_data = plot.plot(
            [],
            symbolBrush=(0,0,0),
            symbolSize=5,
            symbolPen=None
        )

        plot.getViewBox().setBorder(
            pg.mkPen({
                'color': '#000000',
                'width': 2
            })
        )

        return plot, plot_data

    def handle_new_data(self, data: DiagnosticData):

        self.temperature_values.append(data.temperature)
        self.vcc_values.append(data.vcc)
        self.tx_bias_values.append(data.tx_bias)
        self.rx_power_values.append(data.rx_power)
        self.tx_power_values.append(data.tx_power)

        num_vals = len(self.temperature_values)

        if num_vals > self.domain_limit:
            self.domain_limit += 30
            self.temperature_plot.setXRange(0, self.domain_limit, padding=0)
            self.vcc_plot.setXRange(0, self.domain_limit, padding=0)
            self.tx_bias_plot.setXRange(0, self.domain_limit, padding=0)
            self.rx_power_plot.setXRange(0, self.domain_limit, padding=0)
            self.tx_power_plot.setXRange(0, self.domain_limit, padding=0)

        formatted_data = np.array([range(num_vals), self.temperature_values])
        formatted_data = formatted_data.transpose()
        self.temperature_plot_data.setData(formatted_data)

        formatted_data = np.array([range(num_vals), self.vcc_values])
        formatted_data = formatted_data.transpose()
        self.vcc_plot_data.setData(formatted_data)

        formatted_data = np.array([range(num_vals), self.tx_bias_values])
        formatted_data = formatted_data.transpose()
        self.tx_bias_plot_data.setData(formatted_data)

        formatted_data = np.array([range(num_vals), self.rx_power_values])
        formatted_data = formatted_data.transpose()
        self.rx_power_plot_data.setData(formatted_data)

        formatted_data = np.array([range(num_vals), self.tx_power_values])
        formatted_data = formatted_data.transpose()
        self.tx_power_plot_data.setData(formatted_data)

        self.timer.start(1000)


if __name__ == '__main__':

    app = QApplication([])

    pg.setConfigOptions(antialias=False) # True seems to work as well

    w = DiagnosticPlotWidget()
    w.show()
    
    
    app.exec_()
