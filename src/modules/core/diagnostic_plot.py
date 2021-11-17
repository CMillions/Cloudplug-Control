##
# @file diagnostic_plot.py
# @brief Defines the diagnostic plot widget.
#
# @section file_author Author
# - Created on 11/12/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 11/15/2021 by Connor DeCamp
##

##
# Standard imports
##
from random import randint
from enum import Enum


##
# Third party library imports
##
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QVBoxLayout
import pyqtgraph as pg

class DiagnosticPlot(pg.GraphicsLayoutWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setBackground('w')

        self.temperature_plot = self.addPlot(row=0, col=0, title="Temperature")
        self.temperature_plot_data = self.temperature_plot.plot([],
            symbolBrush=(0,0,0),
            symbolSize=5,
            symbolPen=None
        )

        self.vcc_plot = self.addPlot(row=0, col=1, title="VCC")
        self.vcc_plot_data = self.vcc_plot.plot([],
            symbolBrush=(0,0,0),
            symbolSize=5,
            symbolPen=None
        )

        self.tx_bias_plot = self.addPlot(row=0, col=2, title="TX Bias Current")
        self.tx_bias_plot_data = self.tx_bias_plot.plot([],
            symbolBrush=(0,0,0),
            symbolSize=5,
            symbolPen=None
        )

        self.rx_power_plot = self.addPlot(row=1, col=0, title="RX Power")
        self.rx_power_plot_data = self.rx_power_plot.plot([],
            symbolBrush=(0,0,0),
            symbolSize=5,
            symbolPen=None
        )

        self.tx_power_plot = self.addPlot(row=1, col=1, title="TX Power")
        self.tx_power_plot_data = self.tx_power_plot.plot([],
            symbolBrush=(0,0,0),
            symbolSize=5,
            symbolPen=None
        )

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

        self.temperature_plot.setYRange(-128, 128)
        self.vcc_plot.setYRange(-128, 128)
        self.tx_bias_plot.setYRange(-128, 128)
        self.rx_power_plot.setYRange(-128, 128)
        self.tx_power_plot.setYRange(-128, 128)




        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_new_data)
        self.timer.start(1000)

    def handle_new_data(self):

        temp = [randint(30, 40) for i in range(5)]
        value1, value2, value3, value4, value5 = temp

        self.temperature_values.append(value1)
        self.vcc_values.append(value2)
        self.tx_bias_values.append(value3)
        self.rx_power_values.append(value4)
        self.tx_power_values.append(value5)

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

    win = DiagnosticPlot()
    win.show()
    win.raise_()
    app.exec_()
