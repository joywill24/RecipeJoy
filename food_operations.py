# food_operations.py
# This module provides operations for managing food items in a recipe application.
# It includes functionality to add, update, delete, and retrieve food items from the database,
# as well as search for food items.

import logging

logging.basicConfig(level=logging.DEBUG)

# Class to represent a food item
class Food:
    def __init__(self, food_id, name, no_serve, serv_size, calories, carbs, fat, protein):
        self.food_id = food_id
        self.name = name
        self.no_serve = no_serve
        self.serv_size = serv_size
        self.calories = calories
        self.carbs = carbs
        self.fat = fat
        self.protein = protein

class FoodOperations:

    # Add a new food item to the database
    @staticmethod
    def add_food_item(connection, food_name, no_serve, serv_size, calories, protein, carbs, fat):
        try:
            with connection.cursor() as cursor:
                # Insert serving info
                cursor.execute("INSERT INTO ServingInfo (NoServe, ServSize) OUTPUT INSERTED.ServId VALUES (?, ?)",
                                (no_serve, serv_size))
                serv_id = cursor.fetchone()[0]

                # Insert food
                cursor.execute("INSERT INTO Foods (ServId, FoodName) OUTPUT INSERTED.FoodId VALUES (?, ?)",
                                (serv_id, food_name))
                food_id = cursor.fetchone()[0]

                # Insert nutrition info
                cursor.execute("INSERT INTO Nutrition (FoodId, Calories, Protein, Carbs, Fat) VALUES (?, ?, ?, ?, ?)",
                                (food_id, calories, protein, carbs, fat))

                connection.commit()
                logging.info(f"Food item '{food_name}' added successfully with ID {food_id}")
                return food_id
        except Exception as error:
            logging.error(f"Error adding food item: {error}")
            connection.rollback()
            return None

    # Update an existing food item
    @staticmethod
    def update_food_item(connection, food_id, new_food_name, new_no_serve, new_serv_size, new_calories, new_protein, new_carbs, new_fat):
        try:
            with connection.cursor() as cursor:
                # Update the ServingInfo table
                cursor.execute("""
                    UPDATE ServingInfo
                    SET NoServe = ?, servsize = ?
                    WHERE ServId = (SELECT ServId FROM Foods WHERE FoodId = ?)
                    """,
                    (new_no_serve, new_serv_size, food_id))
                connection.commit()

                # Update the Foods table
                cursor.execute("""
                    UPDATE Foods
                    SET FoodName = ?
                    WHERE FoodId = ?
                    """,
                    (new_food_name, food_id))
                connection.commit()

                # Update the Nutrition table
                cursor.execute("""
                    UPDATE Nutrition
                    SET Calories = ?, Protein = ?, Carbs = ?, Fat = ?
                    WHERE FoodId = ?
                    """,
                    (new_calories, new_protein, new_carbs, new_fat, food_id))
                connection.commit()
                logging.info(f"Food item with ID {food_id} udpated successfully.")
                return True

        except Exception as error:
            logging.error(f"Error updating food item: {error}")
            connection.rollback()
            raise

    # Delete a food item
    @staticmethod
    def delete_food_item(connection, food_id):
        try:
            with connection.cursor() as cursor:
                # Delete from the Nutrition table
                cursor.execute("DELETE FROM Nutrition WHERE FoodId = ?", (food_id,))
                connection.commit()

                # Delete from the Foods table and retrieve the ServId
                cursor.execute("DELETE FROM Foods OUTPUT DELETED.ServId WHERE FoodId = ?", (food_id,))
                serve_id = cursor.fetchone()[0]
                connection.commit()

                # Delete from the ServingInfo table
                cursor.execute("DELETE FROM ServingInfo WHERE ServId = ?", (serve_id,))
                connection.commit()
                logging.info(f"Food item with ID {food_id} deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting food item: {error}")
            connection.rollback()

    # Retrieve measurements from the database
    @staticmethod
    def get_measurements(connection):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT MeasId, MeasName FROM Measurements ORDER BY MeasName")
                measurements =  cursor.fetchall()
                logging.info(f"Retrieved {len(measurements)} measurements.")
                return measurements
        except Exception as error:
            logging.error(f"Error while getting measurements: {error}")
            return []

    # Search for food items by name
    @staticmethod
    def search_foods(connection, search_term):
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT F.FoodId, F.FoodName, S.NoServe, S.ServSize, 
                            N.Calories, N.Carbs, N.Fat, N.Protein
                    FROM Foods F
                    JOIN ServingInfo S ON F.ServId = S.ServId
                    JOIN Nutrition N ON F.FoodId = N.FoodId
                    WHERE F.FoodName LIKE ?
                """
                cursor.execute(query, (f'%{search_term}%',))
                results = cursor.fetchall()
                logging.debug(f"Search results for term '{search_term}': {results}")
                return [Food(*row) for row in results]
        except Exception as error:
            logging.error(f"Error searching foods: {error}")
            return[]

    # Check for foods associated with recipes
    @staticmethod
    def check_food_associations(connection, food_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT RecId FROM RecipeFoods WHERE FoodId = ?", (food_id,))
                associated_recipes = cursor.fetchall()
                return [recipe[0] for recipe in associated_recipes]
        except Exception as error:
            logging.error(f"Error checking food associations: {error}")
            return []