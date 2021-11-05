## 
# @file main.py
# @brief Main driver for the software.
#
# Some parts taken from https://realpython.com/qt-designer-python/
#
# @section file_author Author
# - Created on 07/08/2021 by Connor DeCamp
# @section mod_history Modification History
# - Modified on 07/10/2021
# - Modified on 07/11/2021
# - Modified on 07/14/2021
# - Modified on 08/03/2021
# - Modified on 10/19/2021
# - Modified on 10/21/2021 by Connor DeCamp
# - Modified on 10/24/2021 by Connor DeCamp
##

##
# Standard Library Imports
##
import sys


##
# Third Party Library Imports
##
from PyQt5.QtWidgets import QApplication

##
# User defined imports
##
from modules.core.window import Window

APPLICATION_NAME = "CloudPlug Control"
APPLICATION_DISPLAY_NAME = "CloudPlug Control"
APPLICATION_VERSION = "0.2"

def main():

    # Create the Qt Application and an instance of the window class
    app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationDisplayName(APPLICATION_DISPLAY_NAME)
    app.setApplicationVersion(APPLICATION_VERSION)

    main_window = Window()
    main_window.setWindowTitle('CloudPlug Control')
    main_window.show()

    sys.exit(app.exec_())

    

if __name__ == '__main__':
    main()