# File:     main.py
# Author:   Connor DeCamp
# Created:  07/08/2021
#
# Some parts taken from https://realpython.com/qt-designer-python/

# Standard imports
import sys
from typing import List

from PyQt5.QtWidgets import QApplication, QErrorMessage

# User defined imports
from modules.core.window import Window
from modules.network.sql_connection import SQLConnection


def main():

    # Create the Qt Application and an instance of the window class
    app = QApplication(sys.argv)
    main_window = Window()

    # Test a SQL connection with the database
    mydb = SQLConnection()

    # Populate table in GUI window with the SFP data
    mycursor = mydb.get_cursor()

    if mycursor is None:
        print('Error getting cursor from database')
        error_dialog = QErrorMessage()
        error_dialog.showMessage("Failed to connect to SFP database.")
        error_dialog.exec()
        return -1

    sql_command = 'SELECT * FROM sfp_info.sfp'
    main_window.appendToDebugLog(f'Executing SQL Command: {sql_command}')
    mycursor.execute(sql_command)    

    # Append data to sfp table in GUI
    for sfp_data in mycursor:
        main_window.appendToDebugLog(f'Adding {sfp_data} to the SFP table')
        main_window.appendRowInSFPTable(sfp_data)

    mydb.close()

    #for x in range(0x00, 0xFF + 1):
    #    sfp = SFP([x] * 256, [0] * 256)
    #    print(f'{hex(x)}\t{sfp.get_connector_type() = }'.format(x))

    main_window.setWindowTitle('CloudPlug Control')
    main_window.show()
    sys.exit(app.exec_())


    

if __name__ == '__main__':
    main()