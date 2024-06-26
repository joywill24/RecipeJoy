# food_operations.py
import uuid
import logging

class FoodOperations:
    @staticmethod
    def add_food_item(connection, food_name, no_serve, serv_size, calories, protein, carbs, fat):
        try:
            cursor = connection.cursor()

            # Generate unique identifiers
            serv_id = uuid.uuid4()
            food_id = uuid.uuid4()
            nut_id = uuid.uuid4()

            # Insert a record into the ServingInfo table
            cursor.execute("""
                INSERT INTO ServingInfo (ServId, NoServe, servsize)
                VALUES (?, ?, ?)
                """,
                (serv_id, no_serve, serv_size)
            )
            connection.commit()

            # Retrieve the generated ServId
            cursor.execute("SELECT ServId FROM ServingInfo WHERE ServId = ?", (serv_id,))
            serve_id = cursor.fetchone()[0]

            #Insert a record into the Foods table
            cursor.execute("""
                INSERT INTO Foods (FoodId, ServId, FoodName)
                VALUES (?, ?, ?)
                """,
                (food_id, serve_id, food_name)
            )
            connection.commit()

            # Retrieve the generated FoodId
            cursor.execute("SELECT FoodId FROM Foods WHERE FoodId = ?", (food_id,))
            food_id = cursor.fetchone()[0]

            # Insert record into the Nutrition table
            cursor.execute("""
                INSERT INTO Nutrition (NutId, FoodId, Calories, Protein, Carbs, Fat)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nut_id, food_id, calories, protein, carbs, fat)
            )
            connection.commit()

            print("Food item added successfully.")
            return food_id
        except Exception as error:
            logging.error(f"Error while adding food item: {error}")
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
                (new_no_serve, new_serv_size, food_id)
            )
            connection.commit()

            # Update the Foods table
            cursor.execute("""
                UPDATE Foods
                SET FoodName = ?
                WHERE FoodId = ?
                """,
                (new_food_name, food_id)
            )
            connection.commit()

            # Update the Nutrition table
            cursor.execute("""
                UPDATE Nutrition
                SET Calories = ?, Protein = ?, Carbs = ?, Fat = ?
                WHERE FoodId = ?
                """,
                (new_calories, new_protein, new_carbs, new_fat, food_id)
            )
            connection.commit()

            print("Food item updated successfully.")
        except Exception as error:
            logging.error(f"Error while updating food item: {error}")

    @staticmethod
    def delete_food_item(connection, food_id):
        try:
            cursor = connection.cursor()

            # Delete from the Nutrition table
            cursor.execute("""
                DELETE FROM Nutrition
                WHERE FoodId = ?
                """,
                (food_id,)
            )
            connection.commit()

            # Delete from the Foods table and retrieve the ServId
            cursor.execute("""
                DELETE FROM Foods
                OUTPUT DELETED.ServId
                WHERE FoodId = ?
                """,
                (food_id,)
            )
            serve_id = cursor.fetchone()[0]
            connection.commit()

            # Delete from the ServingInfo table
            cursor.execute("""
                DELETE FROM ServingInfo
                WHERE ServId = ?
                """,
                (serve_id,)
            )
            connection.commit()

            print ("Food item deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting food item: {error}")