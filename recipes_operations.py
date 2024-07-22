# recipes_operations.py
import logging
from unittest import result


class RecipeOperations:

    @staticmethod
    def recipe_name_exists(connection, recipe_name):
        try:
            cursor = connection.cursor()
            query = "SELECT COUNT(*) FROM Recipes WHERE RecName = ?"
            cursor.execute(query, (recipe_name,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as error:
            logging.error(f"Error checking if recipe name exists: {error}")
            return False

    @staticmethod
    def add_recipe(connection, recipe_name, servings=1, instructions='', protein_id=None):
        try:
            cursor = connection.cursor()
            query = """
                    INSERT INTO Recipes (RecName, RecServings, RecInstructions, ProteinId) 
                    OUTPUT INSERTED.RecId 
                    VALUES (?, ?, ?, ?)
                    """
            cursor.execute(query, (recipe_name, servings, instructions, protein_id))
            rec_id = cursor.fetchone()[0]
            connection.commit()
            return rec_id
        except Exception as error:
            logging.error(f"Error adding recipe: {error}")
            connection.rollback()
            return None

    @staticmethod
    def add_tag_to_recipe(connection, recipe_id, tag_id):
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO RecipeTags (RecipeId, TagId) VALUES (?, ?)", (recipe_id, tag_id))
            connection.commit()
            return True
        except Exception as error:
            logging.error(f"Error adding tag to recipe: {error}")
            connection.rollback()
            return False

    @staticmethod
    def remove_tag_from_recipe(connection, recipe_id, tag_id):
        try:
            cursor = connection.cursor()
            query = "DELETE FROM RecipeTags WHERE RecipeId = ? AND TagId = ?"
            cursor.execute(query, (recipe_id, tag_id))
            connection.commit()
            return True
        except Exception as error:
            logging.error(f"Error removing tag from recipe: {error}")
            connection.rollback()
            return False

    @staticmethod
    def get_recipe_tags(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = """
                        SELECT CT.TagName
                        FROM RecipeTags RT
                        JOIN CustomTags CT ON RT.TagId = CT.TagId
                        WHERE RT.RecipeId = ?
                    """
            cursor.execute(query, (recipe_id,))
            results = cursor.fetchall()
            return [{'name': row[0]} for row in results]
        except Exception as error:
            logging.error(f"Error getting recipe tags: {error}")
            return []

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
    def update_recipe(connection, rec_id, servings=None, protein_id=None, notes=None):
        try:
            cursor = connection.cursor()

            # Prepare the update query and parameters
            update_query = "UPDATE Recipes SET "
            update_params = []

            if servings is not None:
                update_query += "RecServings = ?, "
                update_params.append(servings)
            if protein_id is not None:
                update_query += "ProteinId = ?, "
                update_params.append(protein_id)
            if notes is not None:
                update_query += "RecNotes = ?, "
                update_params.append(notes)

            # Remove the trailing comma and space
            update_query = update_query.rstrip(", ")

            # Add the WHERE clause
            update_query += " WHERE RecId = ?"
            update_params.append(rec_id)

            # Execute the update query
            cursor.execute(update_query, update_params)
            connection.commit()
            return True
        except Exception as error:
            logging.error(f"Error while updating recipe: {error}")
            connection.rollback()
            return False

    @staticmethod
    def delete_recipe(connection, rec_id):
        try:
            cursor = connection.cursor()

            # Delete Food associations
            cursor.execute("""
                DELETE FROM RecipeFoods
                WHERE RecId = ?
                """,
                (rec_id,))
            connection.commit()

            # Delete from Recipes table
            cursor.execute("""
                DELETE FROM Recipes
                WHERE RecId = ?
                """,
                (rec_id,))
            connection.commit()

            logging.info("Recipe deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting recipe: {error}")

    @staticmethod
    def get_recipe_foods(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = """
                SELECT F.FoodName, SI.NoServe, SI.ServSize
                FROM RecipeFoods RF
                JOIN Foods F ON RF.FoodId = F.FoodId
                JOIN ServingInfo SI ON F.ServId = SI.ServId
                WHERE RF.RecId = ?
                """
            cursor.execute(query, (recipe_id,))
            results = cursor.fetchall()
            return [{'name': row[0], 'amount': row[1], 'unit': row[2]} for row in results]
            logging.debug(f"Recipe foods for recipe {recipe_id}: {foods}")
            return foods
        except Exception as error:
            logging.error(f"Error getting recipe foods: {error}")
            return []

    @staticmethod
    def add_food_to_recipe(connection, recipe_id, food_id, no_serve, serv_size):
        try:
            cursor = connection.cursor()

            # Insert the serving info
            cursor.execute("""
                    INSERT INTO ServingInfo (NoServe, ServSize)
                    OUTPUT INSERTED.ServId
                    VALUES (?, ?)
                    """, (no_serve, serv_size))
            serv_id = cursor.fetchone()[0]

            # Update the Foods table with the new ServId
            cursor.execute("""
                    UPDATE Foods
                    SET ServId = ?
                    WHERE FoodId = ?
                    """, (serv_id, food_id))

            # Insert into RecipeFoods table
            cursor.execute("""
                INSERT INTO RecipeFoods (RecId, FoodId)
                VALUES (?, ?)
                """, (recipe_id, food_id))

            connection.commit()
            logging.info(f"Food (ID: {food_id}) added to recipe (ID: {recipe_id}) with new ServId: {serv_id}")
            return True
        except Exception as error:
            logging.error(f"Error adding food to recipe: {error}", exc_info=True)
            connection.rollback()
            return False

    @staticmethod
    def update_recipe_food(connection, rec_food_id, new_no_serve, new_serv_size):
        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE RecipeFoods
                SET NoServe = ?, ServSize = ?
                WHERE RecFoodId = ?
            """, (new_no_serve, new_serv_size, rec_food_id))
            connection.commit()
            logging.info(f"Food updated successfully. RecFoodId: {rec_food_id}")
        except Exception as error:
            logging.error(f"Error updating recipe_food: {error}")
            connection.rollback()

    @staticmethod
    def save_recipe_steps(connection, recipe_id, steps):
        try:
            cursor = connection.cursor()

            # Log the attempt to save steps
            logging.info(f"Attempting to save {len(steps)} steps for recipe ID: {recipe_id}")

            # Delete any existing steps for this recipe
            cursor.execute("DELETE FROM RecipeSteps WHERE RecId = ?", (recipe_id,))
            logging.debug(f"Deleted existing steps for recipe ID: {recipe_id}")

            # Insert new steps
            for index, step in enumerate(steps, start=1):
                cursor.execute("INSERT INTO RecipeSteps (RecId, StepNumber, StepDescription) VALUES (?, ?, ?)",
                               (recipe_id, index, step))
                logging.debug(f"Inserted step {index} for recipe ID: {recipe_id}")

            connection.commit()
            logging.info(f"Successfully saved {len(steps)} steps for recipe ID: {recipe_id}")
            return True
        except Exception as error:
            logging.error(f"Error saving recipe steps for recipe ID {recipe_id}: {error}", exc_info=True)
            connection.rollback()
            return False

    @staticmethod
    def get_recipe_details(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = """
                SELECT R.RecName, R.RecServings, R.RecInstructions, R.RecNotes,
                       R.RecCals, R.RecProtein, R.RecCarbs, R.RecFat,
                       P.ProteinName
                FROM Recipes R
                LEFT JOIN Proteins P ON R.ProteinId = P.ProteinId
                WHERE R.RecId = ?
            """
            cursor.execute(query, (recipe_id,))
            result = cursor.fetchone()

            if result:
                return {
                    'name': result[0],
                    'servings': result[1],
                    'instructions': result[2],
                    'notes': result[3],
                    'calories': result[4],
                    'protein': result[5],
                    'carbs': result[6],
                    'fat': result[7],
                    'protein_type': result[8]
                }
                logging.debug(f"Recipe details fetched for ID {recipe_id}: {recipe_details}")
                return recipe_details
            else:
                logging.error(f"No recipe found with ID: {recipe_id}")
                return None
        except Exception as error:
            logging.error(f"Error getting recipe details: {error}", exc_info=True)
            raise

    @staticmethod
    def get_recipe_steps(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = """
                    SELECT StepNumber, StepDescription
                    FROM RecipeSteps
                    WHERE RecId = ?
                    ORDER BY StepNumber
                """
            cursor.execute(query, (recipe_id,))
            results = cursor.fetchall()
            steps = [{'number': row[0], 'description': row[1]} for row in results]
            logging.debug(f"Recipe steps for recipe {recipe_id}: {steps}")
            return steps
        except Exception as error:
            logging.error(f"Error getting steps for recipe {recipe_id}: {error}")
            return[]

    @staticmethod
    def update_recipe_instructions(connection, recipe_id, instructions):
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE Recipes SET RecInstructions = ? WHERE RecId = ?", (instructions, recipe_id))
            connection.commit()
            logging.info(f"Recipe instructions updated successfully for RecId: {recipe_id}")
            return True
        except Exception as error:
            logging.error(f"Error updating recipe instructions: {error}")
            connection.rollback()
            return False

    @staticmethod
    def get_recipe_total_nutrition(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = """
                SELECT
                    SUM(N.Calories * RF.NoServe / SI.NoServe) as TotalCalories,
                    SUM(N.Carbs * RF.NoServe / SI.NoServe) as TotalCarbs,
                    SUM(N.Fat * RF.NoServe / SI.NoServe) as TotalFat,
                    SUM(N.Protein * RF.NoServe / SI.NoServe) as TotalProtein,
                FROM RecipeFoods RF
                JOIN Foods F ON RF.FoodId = F.FoodId
                JOIN Nutrition N ON F.FoodId = N.FoodId
                JOIN ServingInfo SI ON F.ServId = SI.ServId
                WHERE RF.RecId = ?
            """
            cursor.execute(query, (recipe_id,))
            results = cursor.fetchone()
            return {
                'calories': round(result[0] or 0, 2),
                'carbs': round(result[1] or 0, 2),
                'fat': round(results[2] or 0, 2),
                'protein': round(results[3] or 0, 2),
            }
        except Exception as error:
            logging.error(f"Error calculating total nutrition for recipe: {error}")
            return {'calories': 0, 'carbs': 0, 'fat': 0, 'protein': 0}