# recipes_operations.py
# This module contains various operations related to recipes, including adding, updating, and deleting recipes,
# managing tags and foods associated with recipes, and retrieving recipe details, ingredients, steps, and nutrition information.
# It also includes methods to search for recipes based on different criteria.

import logging

class RecipeOperations:

    # Check if a recipe name exists in the database
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

    # Add a new recipe to the database
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

    # Add a tag to the recipe
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

    # Remove a tag from the recipe
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

    # Get all tags for a specific recipe
    @staticmethod
    def get_recipe_tags(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = """
                SELECT CT.TagId, CT.TagName
                FROM RecipeTags RT
                JOIN CustomTags CT ON RT.TagId = CT.TagId
                WHERE RT.RecipeId = ?
            """
            cursor.execute(query, (recipe_id,))
            results = cursor.fetchall()
            return [{'TagId': row[0], 'TagName': row[1]} for row in results]
            logging.debug(f"Retrieved tags for recipe {recipe_id}: {tags}")
            return tags
        except Exception as error:
            logging.error(f"Error getting recipe tags for recipe {recipe_id}: {error}")
            return []

    # Update nutrition information for a recipe
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

    # Update a recipe's details
    @staticmethod
    def update_recipe(connection, rec_id, servings=None, protein_id=None, notes=None):
        try:
            cursor = connection.cursor()

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

            update_query += " WHERE RecId = ?"
            update_params.append(rec_id)

            cursor.execute(update_query, update_params)
            connection.commit()
            return True
        except Exception as error:
            logging.error(f"Error while updating recipe: {error}")
            connection.rollback()
            return False

    # Delete a recipe from the database
    @staticmethod
    def delete_recipe(connection, rec_id):
        try:
            cursor = connection.cursor()

            # Delete Food associations
            cursor.execute("DELETE FROM RecipeFoods WHERE RecId = ?", (rec_id,))
            connection.commit()

            # Delete from Recipes table
            cursor.execute("DELETE FROM Recipes WHERE RecId = ?", (rec_id,))
            connection.commit()

            logging.info("Recipe deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting recipe: {error}")

    # Get all foods associated with a recipe
    @staticmethod
    def get_recipe_foods(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = """
                SELECT RF.FoodId, F.FoodName, SI.NoServe, SI.ServSize,
                        N.Calories, N.Carbs, N.Fat, N.Protein
                FROM RecipeFoods RF
                JOIN Foods F ON RF.FoodId = F.FoodId
                JOIN ServingInfo SI ON F.ServId = SI.ServId
                JOIN Nutrition N ON F.FoodId = N.FoodId
                WHERE RF.RecId = ?
            """
            logging.debug(f"Executing query: {query}")
            logging.debug(f"With recipe_id: {recipe_id}")
            cursor.execute(query, (recipe_id,))
            results = cursor.fetchall()
            logging.debug(f"Raw query results for recipe {recipe_id} foods: {results}")

            # Convert to list of dictionaries
            foods = [{
                'food_id': row[0],
                'name': row[1],
                'no_serve': row[2],
                'serv_size': row[3],
                'calories': row[4],
                'carbs': row[5],
                'fat': row[6],
                'protein': row[7]
            } for row in results]

            logging.debug(f"Processed recipe foods for recipe {recipe_id}: {foods}")
            return foods
        except Exception as error:
            logging.error(f"Error fetching recipe foods for recipe {recipe_id}: {error}", exc_info=True)
            return []

    # Add a food item to a recipe
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

    # Update a food item in a recipe
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
            logging.error(f"Error updating recipe_food: {error}", exc_info=True)
            connection.rollback()

    # Save the steps of a recipe
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

    # Populate the details of a recipe into the UI
    def populate_recipe_details(self, recipe_id):
        try:
            logging.debug(f"Loading and displaying recipe with ID: {recipe_id}")

            # Fetch recipe details
            recipe_info = RecipeOperations.get_recipe_info(self.database_manager.connection, recipe_id)
            if not recipe_info:
                raise ValueError("Recipe details not found")

            # Fetch recipe ingredients
            recipe_foods = RecipeOperations.get_recipe_foods(self.database_manager.connection, recipe_id)

            # Set current recipe ID
            self.current_rec_id = recipe_id
            logging.debug(f"Current recipe ID set to: {recipe_id}")

            # Update the UI fields with the fetched recipe details
            self.ui.recipeNameLineEdit.setText(recipe_info['name'])
            self.ui.noOfServingsLineEdit.setText(str(recipe_info['servings']))
            self.ui.recipeInstructionsTextEdit.setPlainText(recipe_info['instructions'])
            self.ui.recipeNotesTextEdit.setPlainText(recipe_info['notes'])

            # Update current recipe foods
            self.current_recipe_foods.clear()
            for food in recipe_foods:
                self.current_recipe_foods.append(food)
            logging.debug(f"Fetched ingredients for recipe {recipe_id}: {self.current_recipe_foods}")

            # Update the ingredients table
            self.update_recipe_ingredients_table()

            logging.info("Recipe page populated successfully.")
        except Exception as error:
            logging.error(f"Error loading recipe details: {error}", exc_info=True)

    # Get the main information about a recipe
    @staticmethod
    def get_recipe_info(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = """
                SELECT R.RecName, R.RecServings, R.RecInstructions, R.RecNotes, P.ProteinName
                FROM Recipes R
                LEFT JOIN Proteins P ON R.ProteinId = P.ProteinId
                WHERE RecId = ?
            """
            logging.debug(f"Executing query: {query}")
            logging.debug(f"With recipe_id: {recipe_id}")
            cursor.execute(query, (recipe_id,))
            result = cursor.fetchone()
            logging.debug(f"Query result for recipe {recipe_id} info: {result}")

            # Convert to dictionary
            if result:
                recipe_info = {
                    'name': result[0],
                    'servings': result[1],
                    'instructions': result[2],
                    'notes': result[3],
                    'protein_type': result[4] if result[4] else 'Not specified'
                }
                return recipe_info
            else:
                return None
        except Exception as error:
            logging.error(f"Error fetching recipe info for recipe {recipe_id}: {error}", exc_info=True)
            return None

    # Get all steps for a specific recipe
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
            return []

    # Update the instructions of a recipe
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

    # Calculate the total nutrition values for a recipe
    @staticmethod
    def get_recipe_total_nutrition(connection, recipe_id):
        try:
            cursor = connection.cursor()
            logging.debug(f"Executing nutrition calculation query for recipe ID: {recipe_id}")
            query = """
                SELECT
                    SUM(N.Calories) as TotalCalories,
                    SUM(N.Carbs) as TotalCarbs,
                    SUM(N.Fat) as TotalFat,
                    SUM(N.Protein) as TotalProtein
                FROM RecipeFoods RF
                JOIN Foods F ON RF.FoodId = F.FoodId
                JOIN Nutrition N ON F.FoodId = N.FoodId
                WHERE RF.RecId = ?
            """
            cursor.execute(query, (recipe_id,))
            results = cursor.fetchone()
            logging.debug(f"Nutrition query result for recipe {recipe_id}: {results}")
            return {
                'calories': round(results[0] or 0, 2),
                'carbs': round(results[1] or 0, 2),
                'fat': round(results[2] or 0, 2),
                'protein': round(results[3] or 0, 2),
            }
        except Exception as error:
            logging.error(f"Error calculating total nutrition for recipe: {error}")
            return {'calories': 0, 'carbs': 0, 'fat': 0, 'protein': 0}

    # Search for recipes based on various criteria
    @staticmethod
    def search_recipes(connection, category_index, search_text):
        try:
            cursor = connection.cursor()
            query = "SELECT DISTINCT R.RecId, R.RecName FROM Recipes R"
            params = []

            logging.debug(f"Search category index: {category_index}, search_text: '{search_text}'")

            if category_index == 4: # Recipe Name
                if search_text:
                    query += " WHERE R.RecName LIKE ?"
                    params.append(f"%{search_text}%")
            elif category_index == 0: # Calorie Range
                if search_text:
                    min_cal, max_cal = map(int, search_text.split('-'))
                    query += " WHERE R.RecCals >= ? AND R.RecCals <= ?"
                    params.extend([min_cal, max_cal])
            elif category_index == 2: # Macros
                if search_text:
                    carbs, protein, fat = map(lambda x: float(x) if x else 0, search_text.split(','))
                    query += " WHERE 1=1"
                    if carbs > 0:
                        query += " AND (R.RecCarbs <= ? OR R.RecCarbs IS NULL)"
                        params.append(carbs)
                    if protein > 0:
                        query += " AND (R.RecProtein <= ? OR R.RecProtein IS NULL)"
                        params.append(protein)
                    if fat > 0:
                        query += " AND (R.RecFat <= ? OR R.RecFat IS NULL)"
                        params.append(fat)
            elif category_index == 3: # Protein Type
                if search_text:
                    query += " WHERE R.ProteinId = ?"
                    params.append(search_text)
            elif category_index == 1: # Custom Tags
                if search_text:
                    query += """ JOIN RecipeTags RT on R.RecId = RT.RecipeId 
                                    JOIN CustomTags CT ON RT.TagId = CT.TagId
                                    WHERE CT.TagName = ?"""
                    params.append(search_text)

            logging.debug(f"Executing query: {query}")
            logging.debug(f"Query parameters: {params}")

            cursor.execute(query, params)
            results = cursor.fetchall()
            logging.debug(f"Search results: {results}")
            return results
        except Exception as error:
            logging.error(f"Error searching recipes: {error}")
            return []

    # Search recipes by protein type
    @staticmethod
    def search_recipes_by_protein_type(connection, protein_id):
        try:
            cursor = connection.cursor()
            query = "SELECT RecId, RecName FROM Recipes WHERE ProteinId = ?"
            cursor.execute(query, (protein_id,))
            results = cursor.fetchall()
            logging.debug(f"Search results by protein type: {results}")
            return results
        except Exception as error:
            logging.error(f"Error searching recipes by protein type: {error}")
            return []

    # Remove all tags from a recipe
    @staticmethod
    def remove_all_tags_from_recipe(connection, recipe_id):
        try:
            cursor = connection.cursor()
            query = "DELETE FROM RecipeTags WHERE RecipeId = ?"
            cursor.execute(query, (recipe_id,))
            connection.commit()
            logging.info(f"All tags removed from recipe {recipe_id}")
        except Exception as error:
            logging.error(f"Error removing all tags from recipe {recipe_id}: {error}")
            connection.rollback()

    # Remove a specific food from a recipe
    @staticmethod
    def remove_food_from_recipe(connection, recipe_id, food_id):
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM RecipeFoods WHERE RecId = ? AND FoodId = ?", (recipe_id, food_id))
            connection.commit()
            return cursor.rowcount > 0
        except Exception as error:
            logging.error(f"Error removing food from recipe: {error}", exc_info=True)
            return False

    @staticmethod
    def get_recipes_by_ids(connection, recipe_ids):
        try:
            with connection.cursor() as cursor:

                placeholders = ','.join('?' * len(recipe_ids))
                query = f"SELECT RecId, RecName FROM Recipes WHERE RecId IN ({placeholders})"
                cursor.execute(query, recipe_ids)
                return cursor.fetchall()
        except Exception as error:
            logging.error(f"Error getting recipes by IDs: {error}")
            return []