# File:     main.py
# Author:   Connor DeCamp
# Created:  07/08/2021
#
# Some parts taken from https://realpython.com/qt-designer-python/

# Standard imports
from random import randint
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTableWidgetItem
from PyQt5.uic import loadUi
import mysql.connector

from typing import List

# User defined imports
from modules.window import Window
from modules.sfp import SFP
from modules.sql_connection import SQLConnection

def main():

    # Create the Qt Application and an instance of the window class
    app = QApplication(sys.argv)
    win = Window()

    mydb = win.db_connection

    if mydb is None:
        print('Error when connecting to MySQL databse')
        return -1

    # Populate table in GUI window with the SFP data
    mycursor = mydb.cursor

    if mycursor is None:
        print('Error getting cursor from database')
        return -1

    mycursor.execute("SELECT * FROM sfp")

    # Append data to sfp table in GUI
    for sfp_data in mycursor:
        win.appendRowInSFPTable(sfp_data)


    #for x in range(0x00, 0xFF + 1):
    #    sfp = SFP([x] * 256, [0] * 256)
    #    print(f'{hex(x)}\t{sfp.get_connector_type() = }'.format(x))

    win.setWindowTitle('CloudPlug Control')
    win.show()
    sys.exit(app.exec_())


    

if __name__ == '__main__':
    main()