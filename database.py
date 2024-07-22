# database.py
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
                "Server=Laptop-YOGA\SQLEXPRESS;"
                "Database=RecipeJoy;"
                "Trusted_Connection=yes;"
            )
            print("Connected to database successfully.")
            return True
        except pyodbc.Error as error:
            logging.error(f"Error while connecting to SQL Server: {error}")
            return False

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def add_example_data(self):
        try:
            if self.connection is None:
                self.connect_to_database()

            # Example meal type data
            meal_type_name = "Breakfast"

            # Add a new meal type and get meal_type_id
            meal_type_id = add_meal_type(self.connection, meal_type_name)
            if meal_type_id is None:
                print("Failed to add meal type.")
                return False

            return True
        except Exception as error:
            logging.error(f"Error adding example data: {error}")
            return False

    def get_search_categories(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT CategoryName FROM SearchCategories")
            categories = cursor.fetchall()
            return [category[0] for category in categories]
        except Exception as error:
            logging.error(f"Error getting search categories: {error}")
            return[]

    def insert_search_category(self, category_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO SearchCategories (CategoryId, CategoryName)
                VALUES (NEWID(), ?)
            """, (category_name,))
            self.connection.commit()
            print("Search category inserted successfully.")
        except Exception as error:
            logging.error(f"Error inserting search category: {error}")

    def recipe_name_exists(self, recipe_name):
        cursor = self.connection.cursor()
        query = "SELECT COUNT(*) FROM Recipes WHERE RecName = ?"
        cursor.execute(query, (recipe_name,))
        count = cursor.fetchone()[0]
        return count > 0