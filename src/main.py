# File:     main.py
# Author:   Connor DeCamp
# Created:  07/08/2021
#
# Some parts taken from https://realpython.com/qt-designer-python/

# Standard imports
from random import randint
import sys
from PyQt5.QtWidgets import QApplication, QErrorMessage
from PyQt5.uic import loadUi

from typing import List

# User defined imports
from modules.window import Window
from modules.sfp import SFP
from modules.sql_connection import SQLConnection

def main():

    # Create the Qt Application and an instance of the window class
    app = QApplication(sys.argv)
    main_window = Window()

    if not main_window.db_connected:
        print('Error when connecting to MySQL databse')
        error_dialog = QErrorMessage()
        error_dialog.showMessage("Failed to connect to SFP database.")
        error_dialog.exec()
        return -1

    # Window() class has a sql connection to the databases
    mydb = main_window.db_connector

    # Populate table in GUI window with the SFP data
    mycursor = mydb.cursor

    if mycursor is None:
        print('Error getting cursor from database')
        error_dialog = QErrorMessage()
        error_dialog.showMessage("Failed to connect to SFP database.")
        error_dialog.exec()
        return -1

    mycursor.execute("SELECT * FROM sfp")

    # Append data to sfp table in GUI
    for sfp_data in mycursor:
        main_window.appendRowInSFPTable(sfp_data)


    #for x in range(0x00, 0xFF + 1):
    #    sfp = SFP([x] * 256, [0] * 256)
    #    print(f'{hex(x)}\t{sfp.get_connector_type() = }'.format(x))

    main_window.setWindowTitle('CloudPlug Control')
    main_window.show()
    sys.exit(app.exec_())


    

if __name__ == '__main__':
    main()