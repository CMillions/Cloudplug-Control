##
# @file sql_connection.py
# @brief Wrapper class for the MySQL connector library
# 
# @section file_author Author
# - Created on 08/19/2021 by Connor DeCamp
#
# Simple class that holds the mysql.connector object
# to access the a MySQL database. Code taken and modified
# from:
# https://thepythongeek.medium.com/organizing-db-connections-in-data-ingestion-python-projects-765cca7e809f
##

##
# Standard Imports
##
import os

##
# Third Party Library Imports
##
import mysql.connector
from dotenv import load_dotenv


class SQLConnection:
    '''! SQL connection wrapper class.
    '''

    def __init__(self):
        '''@brief Initializes the SQLConnection object with variables from a .env file.

        ! Reads the .env file located in the project directory to identify database
        login information.
        '''

        env_path = '../.env'
        load_dotenv(dotenv_path=env_path)

        self.connection = None
        self.cursor = None
        
        self.get_connection()

    def get_connection(self):
        ''' @brief Uses the .env file to read out the database information.
        '''
        
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        db_name = os.getenv('DB_NAME')
        
        try:
            #print(f'{db_host = }\t{db_user = }\t{db_pass = }')
            self.connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                database=db_name,
                connection_timeout=15
            )

            self.cursor = self.connection.cursor()

        except Exception as ex:
            print('Error')
            print(ex)
            self.connection = None
            self.cursor = None
            raise Exception(ex)

    def get_cursor(self):
        return self.connection.cursor()

    def close(self):
        if self.connection is not None:
            self.connection.close()

    def __del__(self):
        self.close()