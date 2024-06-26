# recipe_operations.py
import uuid
import logging

class RecipeOperations:
    @staticmethod
    def add_recipe(connection, rec_name, rec_servings, food_ids, protein_id, tag_id, meal_type_id, rec_instructions, rec_notes):
        try:
            cursor = connection.cursor()

            # Generate unique identifier for the RecId
            rec_id = uuid.uuid4()

            # Insert a record into the Recipes table with default values for nutritional fields
            cursor.execute("""
                INSERT INTO Recipes (RecId, RecName, RecServings, ProteinId, TagId, MealTypeId, RecInstructions, RecNotes, RecCals, RecProtein, RecCarbs, RecFat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (rec_id, rec_name, rec_servings, protein_id, tag_id, meal_type_id, rec_instructions, rec_notes, 0, 0, 0, 0)
            )
            connection.commit()

            # Add FoodId associations in RecipeFoods table
            for food_id in food_ids:
                cursor.execute("""
                    INSERT INTO RecipeFoods (RecId, FoodId)
                    VALUES (?, ?)
                    """,
                    (rec_id, food_id)
                )
            connection.commit()

            # Update nutritional totals based on the included foods
            RecipeOperations.update_recipe_nutrition(connection, rec_id)

            print("Recipe added successfully.")
            return rec_id
        except Exception as error:
            logging.error(f"Error while adding recipe: {error}")
            return None

    @staticmethod
    def update_recipe_nutrition(connection, rec_id):
        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Recipes
                SET RecCals = (SELECT SUM(Calories) FROM Nutrition WHERE FoodId IN (SELECT FoodId FROM RecipeFoods WHERE RecId = ?)),
                    RecProtein = (SELECT SUM(Protein) FROM Nutrition WHERE FoodId IN (SELECT FoodId FROM RecipeFoods WHERE RecId = ?)),
                    RecCarbs = (SELECT SUM(Carbs) FROM Nutrition WHERE FoodId IN (SELECT FoodId FROM RecipeFoods WHERE RecId = ?)),
                    RecFat = (SELECT SUM(Fat) FROM Nutrition WHERE FoodId IN (SELECT FoodId FROM RecipeFoods WHERE RecId = ?))
                WHERE RecId = ?
            """, (rec_id, rec_id, rec_id, rec_id, rec_id))
            connection.commit()
        except Exception as error:
            logging.error(f"Error while updating recipe nutrition: {error}")

    @staticmethod
    def update_recipe(connection, rec_id, new_rec_name, new_rec_servings, new_rec_instructions, new_rec_notes, new_food_ids):
        try:
            cursor = connection.cursor()

            # Update the Recipes table
            cursor.execute("""
                UPDATE Recipes
                SET RecName = ?, RecServings = ?, RecInstructions = ?, RecNotes = ?
                WHERE RecId = ?
                """,
                (new_rec_name, new_rec_servings, new_rec_instructions, new_rec_notes, rec_id)
            )
            connection.commit()

            # Delete existing FoodId associations
            cursor.execute("""
                DELETE FROM RecipeFoods
                WHERE RecId = ?
                """,
                (rec_id,)
            )
            connection.commit()

            # Add new FoodId associations
            for food_id in new_food_ids:
                cursor.execute("""
                    INSERT INTO RecipeFoods (RecId, FoodId)
                    VALUES (?, ?)
                    """,
                    (rec_id, food_id)
                )
            connection.commit()

            # Update nutritional totals based on the included foods
            RecipeOperations.update_recipe_nutrition(connection, rec_id)

            print("Recipe updated successfully.")
        except Exception as error:
            logging.error(f"Error while updating recipe: {error}")

    @staticmethod
    def delete_recipe(connection, rec_id):
        try:
            cursor = connection.cursor()

            # Delete Food associations
            cursor.execute("""
                DELETE FROM RecipeFoods
                WHERE RecId = ?
                """,
                (rec_id,)
            )
            connection.commit()

            # Delete from Recipes table
            cursor.execute("""
                DELETE FROM Recipes
                WHERE RecId = ?
                """,
                (rec_id,)
            )
            connection.commit()

            print("Recipe deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting recipe: {error}")