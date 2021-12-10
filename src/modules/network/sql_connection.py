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
import logging

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

        self._connection = None
        self._cursor = None
        
        self.get_connection()

    def get_connection(self):
        '''! Gets a connection object to the database 
        @brief Uses a .env file to connect to a database
        '''
        
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        db_name = os.getenv('DB_NAME')
        
        try:
            #print(f'{db_host = }\t{db_user = }\t{db_pass = }')
            TIMEOUT_SEC = 5
            logging.debug(f"Trying to connect to database with timeout: {TIMEOUT_SEC} seconds")
            self._connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                database=db_name,
                connection_timeout=TIMEOUT_SEC,
                autocommit=True
            )
            logging.debug(f'Connected to db name: {db_name}')

            self._cursor = self._connection.cursor()

        except Exception as ex:
            logging.error(f'Error connecting to SFP database: {ex}')
            self._connection = None
            self._cursor = None
            raise Exception(ex)

    def get_cursor(self):
        return self._connection.cursor()

    def close(self):
        if self._connection is not None:
            self._connection.close()

            logging.debug("Closed connection to database")

    def __del__(self):
        self.close()