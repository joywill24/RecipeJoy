# food_operations.py
import logging

class FoodOperations:

    @staticmethod
    def add_food_item(connection, food_name, no_serve, serv_size, calories, protein, carbs, fat):
        try:
            cursor = connection.cursor()

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
            return food_id
        except Exception as error:
            logging.error(f"Error adding food item: {error}")
            connection.rollback()
            return None

    @staticmethod
    def update_food_item(connection, food_id, new_food_name, new_no_serve, new_serv_size, new_calories, new_protein, new_carbs, new_fat):
        try:
            cursor = connection.cursor()

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
        except Exception as error:
            logging.error(f"Error updating food item: {error}")
            connection.rollback()
            raise

    @staticmethod
    def delete_food_item(connection, food_id):
        try:
            cursor = connection.cursor()

            # Delete from the Nutrition table
            cursor.execute("""
                DELETE FROM Nutrition
                WHERE FoodId = ?
                """,
                (food_id,))
            connection.commit()

            # Delete from the Foods table and retrieve the ServId
            cursor.execute("""
                DELETE FROM Foods
                OUTPUT DELETED.ServId
                WHERE FoodId = ?
                """,
                (food_id,))
            serve_id = cursor.fetchone()[0]
            connection.commit()

            # Delete from the ServingInfo table
            cursor.execute("""
                DELETE FROM ServingInfo
                WHERE ServId = ?
                """,
                (serve_id,))
            connection.commit()

            print ("Food item deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting food item: {error}")

    @staticmethod
    def get_measurements(connection):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT MeasId, MeasName FROM Measurements ORDER BY MeasName")
            return cursor.fetchall()
        except Exception as error:
            logging.error(f"Error while getting measurements: {error}")
            return []

    @staticmethod
    def search_foods(connection, search_term):
        cursor = connection.cursor()
        query = """
                SELECT F.FoodId, F.FoodName, S.NoServe, S.ServSize, 
                       N.Calories, N.Carbs, N.Fat, N.Protein
                FROM Foods F
                JOIN ServingInfo S ON F.ServId = S.ServId
                JOIN Nutrition N ON F.FoodId = N.FoodId
                WHERE F.FoodName LIKE ?
            """
        cursor.execute(query, (f'%{search_term}%',))
        return [Food(*row) for row in cursor.fetchall()]

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