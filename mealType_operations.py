# mealType_operations.py
import logging

class MealTypeOperations:
    @staticmethod
    def add_meal_type(connection, meal_type_name):
        try:
            cursor = connection.cursor()

            # Insert a record into the MealType table
            cursor.execute("""
                INSERT INTO MealType (MealTypeName)
                VALUES (?)
                """,
                (meal_type_name))
            connection.commit()

            # Retrieve the generated MealTypeId
            cursor.execute("SELECT @@IDENTITY AS MealTypeId")
            meal_type_id = cursor.fetchone()[0]

            print("Meal type added successfully.")
            return meal_type_id
        except Exception as error:
            logging.error(f"Error while adding meal type: {error}")
            return None

    @staticmethod
    def update_meal_type(connection, meal_type_id, new_meal_type_name):
        try:
            cursor = connection.cursor()

            # Update the MealType table
            cursor.execute("""
                UPDATE MealType
                SET MealTypeName = ?
                WHERE MealTypeId = ?
                """,
                (new_meal_type_name, meal_type_id))
            connection.commit()

            print("Meal type updated successfully.")
        except Exception as error:
            logging.error(f"Error while updating meal type: {error}")

    @staticmethod
    def delete_meal_type(connection, meal_type_id):
        try:
            cursor = connection.cursor()

            # Delete from MealType table
            cursor.execute("""
                DELETE FROM MealType
                WHERE MealTypeId = ?
                """,
                (meal_type_id,))
            connection.commit()

            print("Meal type deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting meal type: {error}")