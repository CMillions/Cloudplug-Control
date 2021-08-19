# https://thepythongeek.medium.com/organizing-db-connections-in-data-ingestion-python-projects-765cca7e809f

import os
import mysql.connector
from dotenv import load_dotenv


load_dotenv('.env')

class SQLConnection:

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.get_connection()

    def get_connection(self):
        
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        db_name = os.getenv('DB_NAME')
        
        self.connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )

        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def __del__(self):
        self.close()