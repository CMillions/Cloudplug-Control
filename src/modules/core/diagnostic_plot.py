##
# @file diagnostic_plot.py
# @brief Defines the diagnostic plot widget.
#
# @section file_author Author
# - Created on 11/12/2021 by Connor DeCamp
# @section mod_history Modification History
##

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QVBoxLayout
import pyqtgraph as pg
from random import randint
import numpy as np

class DiagnosticPlot(pg.GraphicsLayoutWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.plot_item = self.addPlot(title="Test")
        self.plot_data_item = self.plot_item.plot([],
            symbolBrush=(255,255,255),symbolSize=5,symbolPen=None
        )

        self.parameter_values = []

        self.domain_limit = 10
        self.plot_item.setXRange(0, self.domain_limit)

        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_new_data)
        self.timer.start(1000)

    def handle_new_data(self):

        value = randint(-128, 128)

        self.parameter_values.append(value)

        num_vals = len(self.parameter_values)

        if num_vals > self.domain_limit:
            self.domain_limit = 2 * self.domain_limit
            self.plot_item.setXRange(0, self.domain_limit, padding=0)
            print('resized')

        formatted_data = np.array([range(num_vals), self.parameter_values])
        formatted_data = formatted_data.transpose()


        self.plot_data_item.setData(formatted_data)

        self.timer.start(1000)


if __name__ == '__main__':

    app = QApplication([])

    pg.setConfigOptions(antialias=False) # True seems to work as well

    win = DiagnosticPlot()
    win.show()
    win.resize(400,300) 
    win.raise_()
    app.exec_()
