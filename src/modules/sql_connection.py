# File:     sql_connection.py
# Author:   Connor DeCamp
# Created:  08/19/2021
#
# Simple class that holds the mysql.connector object
# to access the a MySQL database. Code taken and modified
# from:
# https://thepythongeek.medium.com/organizing-db-connections-in-data-ingestion-python-projects-765cca7e809f

import os
import mysql.connector
from dotenv import load_dotenv


class SQLConnection:

    def __init__(self):

        load_dotenv('.env')

        self.connection = None
        self.cursor = None
        
        self.get_connection()

    def get_connection(self):
        
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        db_name = os.getenv('DB_NAME')
        
        try:
            self.connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                database=db_name,
                connection_timeout=5
            )

            self.cursor = self.connection.cursor()

        except Exception as ex:
            print('Error')
            print(ex)
            self.connection = None
            self.cursor = None
            return

    def close(self):
        if self.connection is not None:
<<<<<<< HEAD
=======

>>>>>>> d9a3b59c76ab9b2170475ae0df9822f137e0cafb
            self.connection.close()

    def __del__(self):
        self.close()