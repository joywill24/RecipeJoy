# database.py
# Manages database connection.

import pyodbc
import logging

class DatabaseManager:
    def __init__(self):
        self.connection = None

    def connect_to_database(self):
        try:
            # Establish a connection to the SQL Server database
            self.connection = pyodbc.connect(
                "Driver={SQL Server};"
                "Server=localhost\SQLEXPRESS;"
                "Database=RecipeJoy;"
                "Trusted_Connection=True;"
            )
            print("Connected to database successfully.")
            return True
        except pyodbc.Error as error:
            logging.error(f"Error while connecting to SQL Server: {error}")
            return False

    def close_connection(self):
        if self.connection:
            self.connection.close()