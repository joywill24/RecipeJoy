# ui_operations.py
import logging
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QInputDialog, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import pyqtSignal
from UI_Files.ui_mainwindow import Ui_MainWindow
from database import DatabaseManager
from customTags_operations import CustomTagOperations
from food_operations import FoodOperations
from proteins_operations import ProteinOperations
from recipes_operations import RecipeOperations
from pyodbc import Error as PyodbcError

logging.basicConfig(level=logging.DEBUG)

class CustomButton(QPushButton):
    clicked_with_row = pyqtSignal(int)

    def __init__(self, text, row):
        super().__init__(text)
        self.row = row
        self.clicked.connect(self.emit_with_row)

    def emit_with_row(self):
        self.clicked_with_row.emit(self.row)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize the UI and home page
        logging.debug("Initializing MainWindow")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.current_recipe_id = None
        self.ui.newRecipeNameLabel.setVisible(False)
        self.ui.addFoodsButton.setVisible(False)
        self.current_recipe_foods = []
        self.temp_recipe_data = {}

        # Database and custom operations setup
        self.database_manager = DatabaseManager()
        if not self.database_manager.connect_to_database():
            logging.error("Failed to connect to the database")
            return

        logging.info("Database connected successfully")

        # Initialize operations that depend on the database
        self.custom_tag_operations = CustomTagOperations()
        self.food_operations = FoodOperations()
        self.protein_operations = ProteinOperations()
        self.recipes_operations = RecipeOperations()

        self.setup_connections()
        self.connectUI()
        self.show()

        self.populate_protein_combo_box()

    def setup_connections(self):
        button_style = "background-color: rgb(139, 196, 190);"
        self.ui.submitButton.clicked.connect(self.handle_recipe_name_submission)
        self.ui.addFoodsButton.clicked.connect(self.navigate_to_add_foods_page)
        self.ui.ingredientSearchButton.clicked.connect(self.search_foods)
        self.ui.saveButton_5.clicked.connect(self.save_steps_and_continue)
        self.ui.addStepButton.clicked.connect(self.add_step_to_recipe)

        self.ui.stackedWidget.currentChanged.connect(self.on_stacked_widget_changed)

        # Menu Actions
        self.home_action = QtWidgets.QAction("Home", self)
        self.ui.menuHome.addAction(self.home_action)
        self.home_action.triggered.connect(self.navigate_to_home_page)
        self.ui.actionCustom_Tags.triggered.connect(self.on_action_custom_tags_triggered)
        self.ui.actionFood_and_Nutrition_Info.triggered.connect(self.navigate_to_food_and_nutrition_info_page)
        self.ui.actionProtein_Types.triggered.connect(self.navigate_to_protein_types_page)

    def connectUI(self):
        # Navigation and action buttons
        self.ui.findArecipeButton.clicked.connect(self.navigate_to_find_recipe_page)
        self.ui.returnTohomeButton.clicked.connect(self.navigate_to_home_page)
        self.ui.submitArecipeButton.clicked.connect(self.navigate_to_submit_recipe_page)
        self.ui.addNewFoodItemButton.clicked.connect(self.navigate_to_add_new_food_page)
        self.ui.searchButton.clicked.connect(self.search_and_populate_foods_list)
        self.ui.addNewTagButton.clicked.connect(self.add_new_tag)
        self.ui.searchButton.clicked.connect(self.execute_recipe_search)
        self.ui.returnTohomeButton_2.clicked.connect(self.navigate_to_home_page)
        self.ui.saveButton_3.clicked.connect(self.save_food_and_return_to_manage)
        self.ui.returnTohomeButton_3.clicked.connect(self.navigate_to_home_page)
        self.ui.returnTohomeButton_4.clicked.connect(self.navigate_to_home_page)
        self.ui.addNewProteinTypeButton.clicked.connect(self.add_new_protein_type)
        self.ui.saveButton_4.clicked.connect(self.navigate_to_add_steps_page)
        self.ui.saveButton_5.clicked.connect(self.save_steps_and_continue)
        self.ui.saveButton_6.clicked.connect(self.save_and_show_recipe)
        self.ui.saveButton_7.clicked.connect(self.save_food_and_return_to_add_foods)

    def navigate_to_home_page(self):
        logging.debug("Navigating to the Home page.")
        self.ui.stackedWidget.setCurrentIndex(0)
        logging.debug("Current index set to 0")

    def navigate_to_find_recipe_page(self):
        logging.debug("Navigating to the Find Recipe page.")
        self.ui.stackedWidget.setCurrentIndex(1)
        logging.debug("Current index set to 1")

    def navigate_to_submit_recipe_page(self):
        logging.debug("Navigating to the Submit Recipe page.")
        self.ui.stackedWidget.setCurrentIndex(3 )
        logging.debug("Current index set to 3")

    def navigate_to_add_foods_page(self):
        logging.debug("Navigating to the Add Foods to Recipe page.")
        self.ui.stackedWidget.setCurrentIndex(4)
        logging.debug("Current index set to 4")
        self.update_recipe_ingredients_table()

    def navigate_to_add_steps_page(self):
        logging.debug("Navigating to the Add Steps to Recipe page.")
        self.ui.stackedWidget.setCurrentIndex(5)
        logging.debug("Current index set to 5")

    def navigate_to_finish_recipe_info_page(self):
        logging.debug("Navigating to the Finish Recipe Info page.")
        self.ui.stackedWidget.setCurrentIndex(6)
        self.populate_protein_combo_box()
        self.populate_tags_list()
        logging.debug("Current index set to 6")

    def on_action_custom_tags_triggered(self):
        logging.debug("Navigating to the Custom Tags page.")
        self.ui.stackedWidget.setCurrentIndex(7)
        logging.debug("Current index set to 7")
        self.populate_tags_table()

    def navigate_to_food_and_nutrition_info_page(self):
        logging.debug("Navigating to the Food and Nutrition Info page.")
        self.ui.stackedWidget.setCurrentIndex(8)
        logging.debug("Current index set to 8")
        self.populate_foods_table()

    def navigate_to_add_new_food_page(self):
        try:
            logging.debug("Navigating to the Manage Foods and Nutrition Information page.")
            self.ui.stackedWidget.setCurrentIndex(9)
            logging.debug("Current index set to 9")
            self.clear_food_input_fields()
            self.populate_size_combobox()
            if hasattr(self, 'current_editing_food_id'):
                del self.current_editing_food_id
        except Exception as error:
            logging.error(f"Error navigating to the Manage Foods and Nutrition Information page: {str(error)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(error)}")

    def navigate_to_edit_existing_food_page(self, food_details, food_id):
        try:
            logging.debug(f"Navigating to edit existing food page for food ID: {food_id}")
            self.ui.stackedWidget.setCurrentIndex(10)

            # Check if food_details has the expected number of elements
            if len(food_details) !=7:
                raise ValueError(f"Unexpected number of food details: {len(food_details)}")

            self.ui.foodNameLine.setText(str(food_details[0]))
            self.ui.quantityDoubleSpinBox.setValue(float(food_details[1]))

            # Populate the sizeComboBox with measurements from the database
            self.populate_size_combobox()

            # Set the text for the sizeComboBox
            current_size = str(food_details[2])
            index = self.ui.sizeComboBox.findText(current_size)
            if index >=0:
                self.ui.sizeComboBox.setCurrentIndex(index)
            else:
                # If the current size is not in the list, add it and select it
                self.ui.sizeComboBox.addItem(current_size)
                self.ui.sizeComboBox.setCurrentText(current_size)

            self.ui.caloriesLineEdit.setText(str(food_details[3]))
            self.ui.carbsLine.setText(str(food_details[4]))
            self.ui.fatLine.setText(str(food_details[5]))
            self.ui.proteinLine.setText(str(food_details[6]))

            self.current_editing_food_id = food_id
            logging.debug("Existing food details populated successfully")
        except Exception as error:
            logging.error(f"Error navigating to edit existing food page: {str(error)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(error)}")

    def navigate_to_edit_food_page(self, new_food_name=None):
        self.previous_page_index = self.ui.stackedWidget.currentIndex()
        self.ui.stackedWidget.setCurrentIndex(9)
        if new_food_name:
            self.ui.foodNameLine.setText(new_food_name)
        self.populate_size_combobox()

    def navigate_to_protein_types_page(self):
        logging.debug("Navigating to the Protein Types page.")
        self.ui.stackedWidget.setCurrentIndex(10)
        logging.debug("Current index set to 10")
        self.populate_protein_types_table()

    def save_new_food(self):
        try:
            food_name = self.ui.foodNameLine.text().strip()
            no_serve = self.ui.quantityDoubleSpinBox.value()
            serv_size = self.ui.sizeComboBox.currentText()
            calories = int(self.ui.caloriesLineEdit.text())
            carbs = int(self.ui.carbsLineEdit.text())
            fat = int(self.ui.fatLine.text())
            protein = int(self.ui.proteinLineEdit.text())

            food_id = FoodOperations.add_food_item(
                self.database_manager.connection,
                food_name, no_serve, serv_size, calories, protein, carbs, fat
            )

            if food_id:
                QMessageBox.information(self, "Success", f"Food item '{food_name}' added successfully.")
                self.ui.stackedWidget.setCurrentIndex(self.previous_page_index)
                self.search_foods()
            else:
                QMessageBox.warning(self, "Error", "Failed to add food item.")
        except Exception as error:
            logging.error(f"Error saving new food: {error}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def save_food_item(self):
        try:
            food_name = self.ui.foodNameLine.text().strip()
            no_serve = self.ui.quantityDoubleSpinBox.value()
            serv_size = self.ui.sizeComboBox.currentText()
            calories = int(self.ui.caloriesLineEdit.text())
            carbs = int(self.ui.carbsLine.text())
            fat = int(self.ui.fatLine.text())
            protein = int(self.ui.proteinLine.text())

            if hasattr(self, 'current_editing_food_id'):
                FoodOperations.update_food_item(
                    self.database_manager.connection,
                    self.current_editing_food_id, food_name, no_serve, serv_size, calories, protein, carbs, fat
                )
                message = f"Food item '{food_name}' updated successfully."
            else:
                food_id = FoodOperations.add_food_item(
                    self.database_manager.connection,
                    food_name, no_serve, serv_size, calories, protein, carbs, fat
                )
                message = f"Food item '{food_name}' added successfully."

            QMessageBox.information(self, "Success", message)
            self.navigate_to_food_and_nutrition_info_page()

            if hasattr(self, 'current_editing_food_id'):
                del self.current_editing_food_id

        except Exception as error:
            logging.error(f"Error saving new food: {error}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def clear_food_input_fields(self):
        self.ui.foodNameLine.clear()
        self.ui.quantityDoubleSpinBox.setValue(0)
        self.ui.sizeComboBox.setCurrentIndex(0)
        self.ui.caloriesLineEdit.clear()
        self.ui.carbsLine.clear()
        self.ui.fatLine.clear()
        self.ui.proteinLine.clear()

    def add_new_tag(self):
        tag_name = self.ui.newTagNameLine.text().strip()
        if tag_name:
            tag_id = self.custom_tag_operations.add_tag(self.database_manager.connection, tag_name)
            if tag_id is not None:
                logging.info(f"Tag added with ID: {tag_id}")
                self.populate_tags_table()
                self.ui.newTagNameLine.clear()
                QMessageBox.information(self, "Success", f"Tag '{tag_name}' added successfully with ID {tag_id}.")
            else:
                logging.error("Failed to add tag.  It may already exist.")
                QMessageBox.warning(self, "Error", f"Failed to add tag '{tag_name}'. It may already exist.")
        else:
            logging.error("Tag name cannot be empty.")
            QMessageBox.warning(self, "Error", "Tag name cannot be empty.")

    def add_tag_to_current_recipe(self, tag_id):
        if RecipeOperations.add_tag_to_recipe(self.database_manager.connection, self.current_recipe_id, tag_id):
            logging.debug(f"Tag added to recipe successfully")
            self.update_recipe_tags_display()
        else:
            QMessageBox.warning(self, "Error", "Failed to add tag to the recipe")

    def update_recipe_tags_display(self):
        tags = RecipeOperations.get_recipe_tags(self.database_manager.connection, self.current_recipe_id)

        self.ui.tagsTableWidget.setRowCount(0)  # Clear the existing rows

        for tag in tags:
            row_position = self.ui.tagsTableWidget.rowCount()
            self.ui.tagsTableWidget.insertRow(row_position)

            tag_name_item = QTableWidgetItem(tag[1])
            self.ui.tagsTableWidget.setItem(row_position, 0, tag_name_item)

            remove_button = QPushButton("Remove")
            remove_button.setStyleSheet("background-color: rgb(139, 196, 190);")
            remove_button.clicked.connect(lambda _, t_id=tag[0]: self.remove_tag_from_recipe(t_id))
            self.ui.tagsTableWidget.setCellWidget(row_position, 1, remove_button)

    def remove_tag_from_recipe(self, tag_id):
        try:
            RecipeOperations.remove_tag_from_recipe(self.database_manager.connection, self.current_recipe_id, tag_id)
            logging.info(f"Tag ID {tag_id} removed from recipe successfully.")
            self.update_recipe_tags_display()  # Refresh the tags display
        except Exception as error:
            logging.error(f"Error removing tag from recipe: {error}")
            QMessageBox.warning(self, "Error", f"Failed to remove tag from recipe: {str(error)}")

    def on_stacked_widget_changed(self, index):
        if index == 5:
            self.populate_tags_table()

    def populate_tags_table(self):
        try:
            logging.debug("Populating Tags table.")
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT TagId, TagName FROM CustomTags ORDER BY TagName")
            tags = cursor.fetchall()
            self.ui.tagsTableWidget.setRowCount(0)
            for tag_id, tag_name in tags:
                self.add_tag_to_table(tag_name, tag_id)
            logging.info("Tags table populated successfully.")
        except Exception as error:
            logging.error(f"Error populating tags table: {error}")
            QMessageBox.warning(self, "Error", f"Error populating tags table: {str(error)}")

    def add_tag_to_table(self, tag_name, tag_id):
        row_position = self.ui.tagsTableWidget.rowCount()
        self.ui.tagsTableWidget.insertRow(row_position)
        tag_item = QTableWidgetItem(tag_name)
        self.ui.tagsTableWidget.setItem(row_position, 0, tag_item)

        # Adding edit and remove buttons
        button_style = "background-color: rgb(139, 196, 190);"
        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet(button_style)
        remove_button = QPushButton("Remove")
        remove_button.setStyleSheet(button_style)

        # Connecting signals to pass the current tag_id
        edit_button.clicked.connect(lambda _, id=tag_id: self.edit_tag(id))
        remove_button.clicked.connect(lambda _, id=tag_id: self.remove_tag(id))

        self.ui.tagsTableWidget.setCellWidget(row_position, 1, edit_button)
        self.ui.tagsTableWidget.setCellWidget(row_position, 2, remove_button)

    def edit_tag(self, tag_id):
        logging.info(f"Editing tag ID: {tag_id}")
        current_tag_name = self.find_current_tag_name(tag_id)
        new_tag_name, ok = QInputDialog.getText(self, "Edit Tag", "Enter the new tag name:", text=current_tag_name)
        if ok and new_tag_name:
            try:
                self.custom_tag_operations.update_tag(self.database_manager.connection, tag_id, new_tag_name)
                logging.info(f"Tag updated successfully.")
                self.populate_tags_table()
                QMessageBox.information(self, "Success", "Tag updated successfully.")
            except Exception as error:
                logging.error(f"Error updating tag: {error}")
                QMessageBox.warning(self,"Error", f"Error updating tag: {str(error)}")

    def remove_tag(self, tag_id):
        confirm = QMessageBox.question(self, "Confirm Removal", "Are you sure you want to remove this tag?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.custom_tag_operations.delete_tag(self.database_manager.connection, tag_id)
                logging.info(f"Tag removed successfully.")
                self.populate_tags_table()
            except Exception as error:
                logging.error(f"Error removing tag: {error}")
                QMessageBox.warning(self, "Error", f"Error removing tag: {str(error)}")

    def find_current_tag_name(self, tag_id):
        cursor = self.database_manager.connection.cursor()
        cursor.execute("SELECT TagName FROM CustomTags WHERE TagId = ?", (tag_id,))
        result = cursor.fetchone()
        return result[0] if result else ""

    def populate_tags_list(self):
        try:
            tags = self.custom_tag_operations.get_all_tags(self.database_manager.connection)
            self.ui.tagsListWidget.clear()
            for tag_id, tag_name in tags:
                item = QtWidgets.QListWidgetItem(tag_name)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setData(QtCore.Qt.UserRole, tag_id)
                self.ui.tagsListWidget.addItem(item)

            logging.info("Tags list populated successfully.")
        except Exception as error:
            logging.error(f"Error populating tags list: {error}")
            QMessageBox.warning(self, "Error", f"Failed to load tags: {str(error)}")

    def get_selected_tags(self):
        selected_tags = []
        for index in range(self.ui.tagsListWidget.count()):
            item = self.ui.tagsListWidget.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                tag_id = item.data(QtCore.Qt.UserRole)
                tag_name = item.text()
                selected_tags.append((tag_id, tag_name))
        return selected_tags

    def save_recipe_tags(self):
        if hasattr(self, 'current_recipe_id'):
            selected_tags = self.get_selected_tags()
            for tag_id, _ in selected_tags:
                try:
                    RecipeOperations.add_tag_to_recipe(self.database_manager.connection, self.current_recipe_id, tag_id)
                except Exception as error:
                    logging.error(f"Error adding tag {tag_id} to recipe {self.current_recipe_id}: {error}")
            QMessageBox.information(self, "Success", "Tags added to recipe successfully.")
        else:
            logging.error("No current recipe ID found when trying to save tags")
            QMessageBox.warning(self, "Error", "No active recipe found. Please create a recipe first.")

    def save_and_show_recipe(self):
        try:
            logging.info("Starting save_and_show_recipe")
            # Get values from UI
            new_servings = int(self.ui.noOfServingsLine.text())
            new_protein_id = self.ui.proteinComboBox.currentData()
            new_recipe_notes = self.ui.notesTextEdit.toPlainText()

            logging.debug(f"New servings: {new_servings}, New protein ID: {new_protein_id}")
            logging.debug(f"Current recipe ID: {self.current_recipe_id}")

            # Update the recipe
            success = RecipeOperations.update_recipe(
                self.database_manager.connection,
                self.current_recipe_id,
                servings=new_servings,
                protein_id=new_protein_id,
                notes=new_recipe_notes
            )

            logging.debug(f"Recipe update success: {success}")

            if success:
                logging.info("Recipe updated successfully.")
                # Save tags
                self.save_recipe_tags()
                QMessageBox.information(self, "Success", "Recipe saved successfully!")

                # Populate the recipe page with the new information
                logging.debug(f"Populating recipe page for recipe ID: {self.current_recipe_id}")
                self.populate_recipe_page(self.current_recipe_id)

                # Navigate to the recipe page
                logging.debug(f"Current stacked widget index before switch: {self.ui.stackedWidget.currentIndex()}")
                self.ui.stackedWidget.setCurrentIndex(2)
                logging.debug(f"Current stacked widget index after switch: {self.ui.stackedWidget.currentIndex()}")
            else:
                logging.warning("Failed to save recipe")
                QMessageBox.warning(self, "Error", "Failed to save recipe. Please try again.")

        except Exception as error:
            logging.error(f"Error saving and showing recipe: {error}")
            QMessageBox.critical(self, "Error", f"An error occurred while saving and showing the recipe: {str(error)}")

    def populate_recipe_page(self, recipe_id):
        try:
            logging.info(f"Populating recipe page for recipe ID: {recipe_id}")

            # Verify that self.current_recipe_id is set correctly
            logging.debug(f"Current recipe ID: {self.current_recipe_id}")
            if self.current_recipe_id != recipe_id:
                logging.warning(f"Mismatch between current_recipe_id ({self.current_recipe_id}) and passed recipe_id ({recipe_id})")

            # Fetch recipe details
            recipe = RecipeOperations.get_recipe_details(self.database_manager.connection, recipe_id)
            logging.debug(f"Recipe details: {recipe}")

            if recipe is None:
                logging.warning(f"No recipe found with ID: {recipe_id}")
                QMessageBox.warning(self, "Error", f"No recipe found with ID: {recipe_id}")
                return

            # Populate recipe name
            self.ui.recipeNameLabel.setText(recipe['name'])
            logging.debug(f"Set recipe name: {recipe['name']}")

            # Populate serving size
            self.ui.servingSizeLine.setText(str(recipe['servings']))
            logging.debug(f"Set serving size: {recipe['servings']}")

            # Populate ingredients
            ingredients = RecipeOperations.get_recipe_foods(self.database_manager.connection, recipe_id)
            self.ui.ingredientsTable.clear()
            for ingredient in ingredients:
                item = QtWidgets.QListWidgetItem(f"{ingredient['name']} - {ingredient['amount']} {ingredient['unit']}")
                self.ui.ingredientsTable.addItem(item)
            logging.debug(f"Populated ingredients: {len(ingredients)} items")

            # Populate steps
            steps = RecipeOperations.get_recipe_steps(self.database_manager.connection, recipe_id)
            self.ui.stepsTable.clear()
            for step in steps:
                item = QtWidgets.QListWidgetItem(f"{step['number']}. {step['description']}")
                self.ui.stepsTable.addItem(item)
            logging.debug(f"Populated steps: {len(steps)} items")

            # Populate notes tab
            self.ui.notesTextEdit_2.setPlainText(recipe['notes'])

            # Calculate and populate nutrition tab
            total_nutrition = RecipeOperations.get_recipe_total_nutrition(self.database_manager.connection, recipe_id)
            self.ui.nutritionTable.setRowCount(1)
            self.ui.nutritionTable.setColumnCount(4)
            self.ui.nutritionTable.setHorizontalHeaderLabels(["Calories", "Carbs (g)", "Fat (g)", "Protein (g)"])
            self.ui.nutritionTable.setItem(0, 0, QtWidgets.QTableWidgetItem(str(total_nutrition['calories'])))
            self.ui.nutritionTable.setItem(0, 1, QtWidgets.QTableWidgetItem(str(total_nutrition['carbs'])))
            self.ui.nutritionTable.setItem(0, 2, QtWidgets.QTableWidgetItem(str(total_nutrition['fat'])))
            self.ui.nutritionTable.setItem(0, 3, QtWidgets.QTableWidgetItem(str(total_nutrition['protein'])))

            # Populate tags tab
            self.ui.tagsListWidget_2.clear()
            tags = RecipeOperations.get_recipe_tags(self.database_manager.connection, recipe_id)
            for tag in tags:
                self.ui.tagsListWidget_2.addItem(tag['name'])

            logging.info("Recipe page populated successfully")

            self.ui.recipePage.update()
            QtWidgets.QApplication.processEvents()

            logging.info("Forced UI update after populating the recipe page")

        except Exception as error:
            logging.error(f"Error populating recipe page: {error}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while loading the recipe: {str(error)}")

    def execute_recipe_search(self):
        category = self.ui.searchCategoryComboBox.currentText()
        criteria = self.ui.searchCriteriaLineEdit.text()
        try:
            self.fetch_recipes_by_criteria(category, criteria)
        except Exception as error:
            logging.error(f"Error performing serach: {error}")
            QMessageBox.warning(self, "Error", f"Error performing search: {str(error)}")

    def fetch_recipes_by_criteria(self, category, criteria):
        logging.debug(f"Fetching recipes by criteria: Category - {category}, Criteria - {criteria}")
        try:
            cursor = self.database_manager.connection.cursor()
            query_map = {
                "Recipe Name": ("SELECT * FROM Recipes WHERE RecName LIKE ?", ("%" + criteria + "%",)),
                "Calorie Range": ("SELECT * FROM Recipes WHERE RecCals BETWEEN ? AND ?", tuple(map(int, criteria.split("-")))),
                "Macros": ("""SELECT * FROM Recipes
                                WHERE RecProtein BETWEEN ? AND ?
                                AND RecCarbs BETWEEN ? AND ?
                                AND RecFat BETWEEN ? AND ?""", tuple(map(int, criteria.split(',')))),
                "Meal Type": ("SELECT * FROM Recipes WHERE MealTypeId IN (SELECT MealTypeId FROM MealType WHERE MealTypeName = ?)",
                (criteria,)),
                "Protein Type": ("SELECT * FROM Recipes WHERE ProteinId IN (SELECT ProteinId FROM Proteins WHERE ProteinName = ?)",
                (criteria,)),
                "Custom Tags": ("SELECT * FROM Recipes WHERE TagId IN (SELECT TagId FROM CustomTags WHERE TagName = ?)",
                (criteria,))
            }
            query, params = query_map(category, (None, None))
            if query is None:
                raise ValueError(f"Invalid category: {category}")

            cursor.execute(query, params)
            results = cursor.fetchall()
            self.populate_results_table(results)
            logging.info("Recipe search executed nad results populated successfully.")
        except Exception as error:
            logging.error(f"Error fetching recipes: {error}")
            raise

    def populate_results_table(self, results):
        logging.debug("Populating results table with search results.")
        self.ui.resultsTableWidget.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.ui.resultsTableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.resultsTableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        logging.info("Results table populated successfully.")

    def onSearchCategoryChanged(self, index):
        logging.debug(f"Search category changed to index {index}")
        self.ui.searchCriteriaLineEdit.hide()
        self.ui.minCalLineEdit.hide()
        self.ui.maxCalLineEdit.hide()
        self.ui.fatLineEdit.hide()
        self.ui.carbsLineEdit.hide()
        self.ui.proteinLineEdit.hide()
        if index == 0:  # Recipe Name
            self.ui.searchCriteriaLineEdit.show()
        elif index == 1:  # Calorie Range
            self.ui.minCalLineEdit.show()
            self.ui.maxCalLineEdit.show()
        elif index == 2:  # Macros
            self.ui.fatLineEdit.show()
            self.ui.carbsLineEdit.show()
            self.ui.proteinLineEdit.show()
        elif index == 3:  # Meal Type
            self.ui.searchCriteriaLineEdit.show()
        elif index == 4:  # Protein Type
            self.ui.searchCriteriaLineEdit.show()
        elif index == 5:  # Custom Tags
            self.ui.searchCriteriaLineEdit.show()
        logging.debug("UI updated based on selected search category.")

    def populate_search_categories(self):
        logging.debug("Populating search categories.")
        try:
            categories = self.database_manager.get_search_categories()
            self.ui.searchCategoryComboBox.clear()
            self.ui.searchCategoryComboBox.addItems(categories)
            logging.info("Search categories populated successfully.")
        except Exception as error:
            logging.error(f"Error populating search categories: {error}")
            QMessageBox.warning(self, "Database Error", f"Error loading search categories: {str(error)}")

    def add_new_search_category(self):
        category_name = self.ui.newCategoryLineEdit.text().strip()
        if category_name:
            try:
                self.database_manager.insert_search_category(category_name)
                self.populate_search_categories()
                QMessageBox.information(self, "Category Added", f"Category '{category_name}' added successfully.")
                self.ui.newCategoryLineEdit.clear()
            except Exception as error:
                logging.error(f"Error adding new search category: {error}")
                QMessageBox.warning(self, "Error", f"Failed to add new category: {str(error)}")
        else:
            logging.warning("Search category name input was empty.")
            QMessageBox.warning(self, "Error", "Category name cannot be empty.")

    def search_and_populate_foods_list(self):
        food_name = self.ui.findIngredientSearch.text()
        # Call the method in food_operations.py to search for foods
        try:
            foods = self.food_operations.search_foods(self.database_manager.connection, food_name)
            self.update_foods_list_table(foods)
        except Exception as error:
            logging.error(f"Error searching and populating foods list: {error}")
            QMessageBox.warning(self, "Error", f"Failed to search foods: {str(error)}")

    def update_foods_list_table(self, foods):
        logging.debug("Updating foods list table.")
        self.ui.FoodsList.setRowCount(0)
        for row, food in enumerate(foods):
            self.ui.FoodsList.insertRow(row)
            self.ui.FoodsList.setItem(row, 0, QTableWidgetItem(food.FoodName))
            select_button = QPushButton("Select")
            select_button.clicked.connect(lambda checked, food=food: self.handle_food_selection(food))
            self.ui.FoodsList.setCellWidget(row, 1, select_button)
        logging.info("Foods list table updated successfully.")

    def handle_food_selection(self, food):
        logging.debug(f"Food selected: {food.FoodName}")
        self.selected_food = food
        self.ui.numberOfServingsInput.show()
        self.ui.servingSizeInput.show()
        self.ui.newFoodAddButton.show()

    def handle_recipe_name_submission(self):
        try:
            logging.debug("handle_recipe_name_submission called")
            recipe_name = self.ui.recipeNamefield.text().strip()
            logging.debug(f"Recipe name: {recipe_name}")
            if recipe_name:
                logging.debug("Checking if recipe name exists.")
                if not RecipeOperations.recipe_name_exists(self.database_manager.connection, recipe_name):
                    selected_protein_id = self.ui.proteinComboBox.currentData() if hasattr(self.ui, 'proteinComboBox') else None

                    self.current_recipe_id = RecipeOperations.add_recipe(
                        self.database_manager.connection,
                        recipe_name,
                        servings=1,
                        instructions='',
                        protein_id=selected_protein_id
                    )
                    if self.current_recipe_id:
                        self.ui.newRecipeNameLabel.setText(f"New Recipe: {recipe_name}")
                        self.ui.newRecipeNameLabel.setVisible(True)
                        self.ui.addFoodsButton.setVisible(True)
                        self.ui.addFoodsButton.setEnabled(True)
                        QMessageBox.information(self, "Success", f"Recipe '{recipe_name}' added successfully.  Next, add foods to this recipe.")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to add the recipe.  Please try again.")
                else:
                    logging.debug("Recipe name already exists.")
                    QMessageBox.warning(self, "Duplicate Recipe", "This recipe name already exists.  Please choose a different name.")
            else:
                QMessageBox.warning(self, "Error", "Please enter a recipe name.")
        except Exception as error:
            logging.exception(f"Error in handle_recipe_name_submission: {error}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def add_step_to_recipe(self):
        logging.debug("add_step_to_recipe called")
        try:
            step_text = self.ui.stepTextEdit.toPlainText().strip()
            logging.debug(f"Step text: {step_text}")
            if step_text:
                row_position = self.ui.recipeStepsTable.rowCount()
                self.insert_step(step_text, row_position)
                self.ui.stepTextEdit.clear()
                logging.debug(f"Step added successfully at row {row_position}")
            else:
                QMessageBox.warning(self, "Error", "Please enter a step before adding.")
        except Exception as error:
            logging.error(f"Error in add_step_to_recipe: {error}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def insert_step(self, step_text, row_position=None):
        if row_position is None:
            row_position = self.ui.recipeStepsTable.rowCount()

        self.ui.recipeStepsTable.insertRow(row_position)

        # Add step text
        self.ui.recipeStepsTable.setItem(row_position, 0, QTableWidgetItem(step_text))

        # Add buttons
        button_style = "background-color: rgb(139, 196, 190);"

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet(button_style)
        delete_button.clicked.connect(lambda _, r=row_position: self.delete_step(r))

        move_up_button = QPushButton("Move Up")
        move_up_button.setStyleSheet(button_style)
        move_up_button.clicked.connect(lambda _, r=row_position: self.move_step_up(r))

        move_down_button = QPushButton("Move Down")
        move_down_button.setStyleSheet(button_style)
        move_down_button.clicked.connect(lambda _, r=row_position: self.move_step_down(r))

        self.ui.recipeStepsTable.setCellWidget(row_position, 1, delete_button)
        self.ui.recipeStepsTable.setCellWidget(row_position, 2, move_up_button)
        self.ui.recipeStepsTable.setCellWidget(row_position, 3, move_down_button)

        logging.debug(f"Step inserted at row {row_position}")

    def delete_step(self, row):
        logging.debug(f"Attempting to delete step at row {row}")
        confirm = QMessageBox.question(self, 'Delete Step',
                                       "Are you sure you want to delete this step?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.ui.recipeStepsTable.removeRow(row)
            logging.debug(f"Step at row {row} deleted")
            for i in range(row, self.ui.recipeStepsTable.rowCount()):
                self.update_step_buttons(i)
        else:
            logging.debug("Step deletion cancelled")

    def move_step_up(self, row):
        logging.debug(f"Moving step up from row {row}")
        if row > 0:
            for col in range(self.ui.recipeStepsTable.columnCount()):
                current_item = self.ui.recipeStepsTable.takeItem(row, col)
                previous_item = self.ui.recipeStepsTable.takeItem(row - 1, col)
                self.ui.recipeStepsTable.setItem(row, col, previous_item)
                self.ui.recipeStepsTable.setItem(row - 1, col, current_item)

            self.update_step_buttons(row - 1)
            self.update_step_buttons(row)
            logging.debug(f"Step moved up to row {row - 1}")

    def move_step_down(self, row):
        logging.debug(f"Moving step down from row {row}")
        if row < self.ui.recipeStepsTable.rowCount() - 1:
            for col in range(self.ui.recipeStepsTable.columnCount()):
                current_item = self.ui.recipeStepsTable.takeItem(row, col)
                next_item = self.ui.recipeStepsTable.takeItem(row + 1, col)
                self.ui.recipeStepsTable.setItem(row, col, next_item)
                self.ui.recipeStepsTable.setItem(row + 1, col, current_item)

            self.update_step_buttons(row + 1)
            self.update_step_buttons(row)
            logging.debug(f"Step moved down to row {row + 1}")

    def update_step_buttons(self, row):
        button_style = "background-color: rgb(139, 196, 190);"

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet(button_style)
        delete_button.clicked.connect(lambda _, r=row: self.delete_step(r))

        move_up_button = QPushButton("Move Up")
        move_up_button.setStyleSheet(button_style)
        move_up_button.clicked.connect(lambda _, r=row: self.move_step_up(r))

        move_down_button = QPushButton("Move Down")
        move_down_button.setStyleSheet(button_style)
        move_down_button.clicked.connect(lambda _, r=row: self.move_step_down(r))

        self.ui.recipeStepsTable.setCellWidget(row, 1, delete_button)
        self.ui.recipeStepsTable.setCellWidget(row, 2, move_up_button)
        self.ui.recipeStepsTable.setCellWidget(row, 3, move_down_button)

    def save_steps_and_continue(self):
        logging.debug("Entering save_steps_and_continue method")
        try:
            # Get steps from the table
            steps = [self.ui.recipeStepsTable.item(row, 0).text() for row in range(self.ui.recipeStepsTable.rowCount())]

            if not steps:
                QMessageBox.warning(self, "Error", "No steps to save.  Please add at least one step.")
                return
            # Save steps to the database
            success = RecipeOperations.save_recipe_steps(
                self.database_manager.connection,
                self.current_recipe_id,
                steps
            )

            if success:
                logging.info(f"Recipe steps saved successfully for recipe ID: {self.current_recipe_id}")

                # Join steps into a single string
                instructions = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))

                # Update recipe instructions
                update_success = RecipeOperations.update_recipe_instructions(
                    self.database_manager.connection,
                    self.current_recipe_id,
                    instructions
                )

                if update_success:
                    # Navigate to finishRecipeInfoPage
                    self.ui.stackedWidget.setCurrentIndex(6)
                    self.populate_tags_list()
                    logging.info("Navigated to Finish Recipe Info page.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update recipe instructions. Please try again.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save recipe steps. Please try again.")

        except Exception as error:
            logging.error(f"Error in save_steps_and_continue: {error}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

        logging.debug("Exiting save_steps_and_continue method")

    def move_to_next_recipe_step(self):
        if 'name' in self.temp_recipe_data and 'servings' not in self.temp_recipe_data:
            self.show_servings_input()
        elif 'servings' in self.temp_recipe_data and 'instructions' not in self.temp_recipe_data:
            self.show_instructions_input()
        elif 'instructions' in self.temp_recipe_data:
            self.finalize_recipe_submission()

    def show_servings_input(self):
        # Show UI for inputting number of servings
        self.ui.servingsInput.setVisible(True)
        self.ui.servingsSubmitButton.setVisible(True)
        self.ui.servingsSubmitButton.clicked.connect(self.handle_servings_submission)

    def handle_servings_submission(self):
        servings = self.ui.servingsInput.value()
        self.temp_recipe_data['servings'] = servings
        self.move_to_next_recipe_step()

    def show_instructions_input(self):
        # Show UI for inputting instructions
        self.ui.instructionsInput.setVisible(True)
        self.ui.instructionsSubmitButton.setVisible(True)
        self.ui.instructionsSubmitButton.clicked.connect(self.handle_instructions_submission)

    def handle_instructions_submission(self):
        instructions = self.ui.instructionsInput.toPlainText()
        self.temp_recipe_data['instructions'] = instructions
        self.move_to_next_recipe_step()

    def finalize_recipe_submission(self):
        try:
            rec_id = RecipeOperations.add_recipe(
                self.database_manager.connection,
                self.temp_recipe_data['name'],
                self.temp_recipe_data['servings'],
                self.temp_recipe_data['instructions']
            )
            if rec_id:
                self.current_recipe_id = rec_id
                self.save_recipe_tags()
                QMessageBox.information(self, "Success", "Recipe added successfully!")
                self.clear_recipe_submission_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add recipe to the database.")
        except Exception as error:
            logging.exception("An error occurred while finalizing recipe submission")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def clear_recipe_submission_form(self):
        # Clear all inputs and reset the form
        self.ui.recipeNamefield.clear()
        self.ui.servingsInput.setValue(1)
        self.ui.instructionsInput.clear()
        self.temp_recipe_data.clear()
        # Hide all inputs except the initial recipe name input
        self.ui.servingsInput.setVisible(False)
        self.ui.servingsSubmitButton.setVisible(False)
        self.ui.instructionsInput.setVisible(False)
        self.ui.instructionsSubmitButton.setVisible(False)

    def search_and_populate_food_item(self):
        search_term = self.ui.findIngredientSearch.text().strip()
        if search_term:
            food = self.search_foods(search_term)
            self.populate_foods_list(food)
        else:
            QMessageBox.warning(self, "Error", "Please enter a search term.")

    def search_foods(self):
        try:
            search_term = self.ui.findIngredientSearch.text().strip()
            if not search_term:
                QMessageBox.warning(self, "Error", "Please enter a search term.")
                return

            matching_foods = FoodOperations.search_foods(self.database_manager.connection, search_term)
            if not matching_foods:
                reply = QMessageBox.question(self, 'Food Not Found',
                                            f"'{search_term}' not found. Do you want to add it?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.navigate_to_edit_food_page(new_food_name=search_term)
            else:
                self.populate_matching_foods_list(matching_foods)

            logging.info(f"Food search completed for term: {search_term}")
        except Exception as error:
            logging.error(f"Error searching foods: {str(error)}")
            QMessageBox.warning(self, "Error", f"An error occurred while searching for foods: {str(error)}")



    def populate_matching_foods_list(self, foods):
        try:
            self.ui.recipeIngredientsList.setRowCount(0)
            for food in foods:
                row = self.ui.recipeIngredientsList.rowCount()
                self.ui.recipeIngredientsList.insertRow(row)
                self.ui.recipeIngredientsList.setItem(row, 0, QTableWidgetItem(food.name))
                add_button = QPushButton("Add to Recipe")
                add_button.setStyleSheet("background-color: rgb(139, 196, 190);")
                add_button.clicked.connect(lambda _, f=food: self.add_food_to_recipe(f))
                self.ui.recipeIngredientsList.setCellWidget(row, 1, add_button)

            logging.info("Matching foods list populated successfully.")
        except Exception as error:
            logging.error(f"Error populating matching foods list: {error}")
            QMessageBox.warning(self, "Error", f"Failed to laod matching foods: {str(error)}")

    def populate_foods_list(self, foods):
        self.ui.FoodsList.setRowCount(0)
        self.ui.FoodsList.setColumnCount(4)

        recipe_foods = RecipeOperations.get_recipe_foods(self.database_manager.connection, self.current_recipe_id)

        for row, (rec_food_id, food_id, food_name, no_serve, serv_size) in enumerate(recipe_foods):
            self.ui.FoodsList.insertRow(row)
            self.ui.FoodsList.setItem(row, 0, QTableWidgetItem(food_name))
            self.ui.FoodsList.setItem(row, 1, QTableWidgetItem(str(no_serve)))
            self.ui.FoodsList.setItem(row, 2, QTableWidgetItem(serv_size))

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, rfid=rec_food_id, fid=food_id: self.edit_recipe_food(rfid, fid))
            self.ui.FoodsList.setCellWidget(row, 3, edit_button)

            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda checked, rfid=rec_food_id: self.remove_recipe_food(rfid))
            self.ui.FoodsList.setCellWidget(row, 4, remove_button)

    def select_food(self, food_id, food_name):
        self.selected_food_id = food_id
        self.ui.numberOfServingsInput.setEnabled(True)
        self.ui.servingSizeInput.setEnabled(True)
        self.ui.newFoodAddButton.setEnabled(True)


    def edit_recipe_food(self, rec_food_id, food_id):
        try:
            # Get current food details
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT NoServe, ServSize FROM RecipeFoods WHERE RecFoodId = ?", (rec_food_id,))
            current_details = cursor.fetchone()

            if current_details:
                new_no_serve, ok1 = QInputDialog.getText(self, "Edit Food", "Enter new number of servings:",
                                                        text=str(current_details[0]))
                if ok1:
                    new_serv_size, ok2 = QInputDialog.getText(self, "Edit Food", "Enter new serving size:",
                                                            text=current_details[1])
                    if ok2:
                        # Update recipe food
                        RecipeOperations.update_recipe_food(self.database_manager.connection, rec_food_id, new_no_serve,
                                                            new_serv_size)
                        QMessageBox.information(self, "Success", "Food item in recipe updated successfully.")
                        self.populate_foods_list()
        except Exception as error:
            QMessageBox.warning(self, "Error", f"An error occurred while editing the food in recipe: {str(error)}")


    def remove_recipe_food(self, rec_food_id):
        try:
            reply = QMessageBox.question(self, 'Remove Food',
                                            'Are you sure you want to remove this food item from the recipe?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                RecipeOperations.remove_food_from_recipe(self.database_manager.connection, rec_food_id)
                QMessageBox.information(self, "Success", "Food item removed from recipe successfully.")
                self.populate_foods_list()  # Refresh the list
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while removing the food from recipe: {str(e)}")

    def add_food_to_recipe(self, food):
        try:
            # Add to UI
            row = self.ui.recipeIngredientsTable.rowCount()
            self.ui.recipeIngredientsTable.insertRow(row)
            self.ui.recipeIngredientsTable.setItem(row, 0, QTableWidgetItem(food.name))
            self.ui.recipeIngredientsTable.setItem(row, 1, QTableWidgetItem(str(food.no_serve)))
            self.ui.recipeIngredientsTable.setItem(row, 2, QTableWidgetItem(food.serv_size))
            self.ui.recipeIngredientsTable.setItem(row, 3, QTableWidgetItem(str(food.calories)))
            self.ui.recipeIngredientsTable.setItem(row, 4, QTableWidgetItem(str(food.carbs)))
            self.ui.recipeIngredientsTable.setItem(row, 5, QTableWidgetItem(str(food.fat)))
            self.ui.recipeIngredientsTable.setItem(row, 6, QTableWidgetItem(str(food.protein)))

            remove_button = QPushButton("Remove")
            remove_button.setStyleSheet("background-color: rgb(139, 196, 190);")
            remove_button.clicked.connect(lambda _, f=food: self.remove_food_from_recipe(f))
            self.ui.recipeIngredientsTable.setCellWidget(row, 7, remove_button)

            # Add to current recipe foods list
            self.current_recipe_foods.append(food)

            # Add to database
            success = RecipeOperations.add_food_to_recipe(
                self.database_manager.connection,
                self.current_recipe_id,
                food.food_id,
                food.no_serve,
                food.serv_size
            )

            if success:
                logging.info(f"Food '{food.name}' added to recipe successfully.")
                QMessageBox.information(self, "Success", f"'{food.name}' added to the recipe.")
            else:
                raise Exception("Failed to add food to recipe in database.")

        except Exception as error:
            logging.error(f"Error adding food to recipe: {error}")
            QMessageBox.warning(self, "Error", f"Failed to add food to recipe: {str(error)}")
            # If an error occurred, remove the row from the table
            self.ui.recipeIngredientsTable.removeRow(row)
            if food in self.current_recipe_foods:
                self.current_recipe_foods.remove(food)

        finally:
            # Update the recipe ingredients table
            self.update_recipe_ingredients_table()

    def update_recipe_ingredients_table(self):
        try:
            self.ui.recipeIngredientsTable.setRowCount(0)
            for food in self.current_recipe_foods:
                row = self.ui.recipeIngredientsTable.rowCount()
                self.ui.recipeIngredientsTable.insertRow(row)
                self.ui.recipeIngredientsTable.setItem(row, 0, QTableWidgetItem(food.name))
                self.ui.recipeIngredientsTable.setItem(row, 1, QTableWidgetItem(str(food.no_serve)))
                self.ui.recipeIngredientsTable.setItem(row, 2, QTableWidgetItem(food.serv_size))
                self.ui.recipeIngredientsTable.setItem(row, 3, QTableWidgetItem(str(food.calories)))
                self.ui.recipeIngredientsTable.setItem(row, 4, QTableWidgetItem(str(food.carbs)))
                self.ui.recipeIngredientsTable.setItem(row, 5, QTableWidgetItem(str(food.fat)))
                self.ui.recipeIngredientsTable.setItem(row, 6, QTableWidgetItem(str(food.protein)))

                remove_button = QPushButton("Remove")
                remove_button.setStyleSheet("background-color: rgb(139, 196, 190;")
                remove_button.clicked.connect(lambda _, f=food: self.remove_food_from_recipe(f))
                self.ui.recipeIngredientsTable.setCellWidget(row, 7, remove_button)

            logging.info("Recipe ingredients table updated successfully.")
        except Exception as error:
            logging.error(f"Error updating recipe ingredients tabel: {error}")
            QMessageBox.warning(self, "Error", f"Failed to update ingredients table: {str(error)}")

    def remove_food_from_recipe(self, food):
        try:
            self.current_recipe_foods.remove(food)
            self.update_recipe_ingredients_table()
            RecipeOperations.remove_food_from_recipe(
                self.database_manager.connection,
                self.current_recipe_id,
                food.food_id
            )
            logging.info(f"Food '{food.name}' removed from recipe successfully.")
            QMessageBox.information(self, "Success", f"'{food.name}' removed from the recipe.")
        except Exception as error:
            logging.error(f"Error removing food from recipe: {str(error)}")
            QMessageBox.warning(self, "Error", f"Failed to remove food from recipe: {str(error)}")

    def insert_recipe_into_database(self, recipe_name):
        logging.debug(f"Inserting recipe into database: {recipe_name}")
        try:
            cursor = self.database_manager.connection.cursor()
            query = "INSERT INTO Recipes (RecName) VALUES (?)"
            cursor.execute(query, (recipe_name,))
            self.database_manager.connection.commit()
            QMessageBox.information(self, "Success", f"Recipe '{recipe_name}' added successfully.")
            # Retrieve the generated RecId
            cursor.execute("SELECT @@IDENTITY AS RecId")
            rec_id = cursor.fetchone()[0]
            return rec_id
        except Exception as error:
            QMessageBox.warning(self, "Error", f"Failed to add recipe: {str(error)}")
            self.database_manager.connection.rollback()
            return None

    def navigate_to_add_recipe_details_page(self, rec_id):
        logging.debug(f"Navigating to add recipe details page for recipe ID: {rec_id}")
        pass

    def add_new_food_item(self):
        logging.debug("Attempting to add new food item")
        food_name = self.ui.foodNameLineEdit.text().strip()
        no_serve = self.ui.quantityDoubleSpinBox.value()
        serv_size = self.ui.sizeComboBox.currentText()
        calories = int(self.ui.caloriesLineEdit.text())
        carbs = int(self.ui.carbsLineEdit.text())
        fat = int(self.ui.fatLineEdit.text())
        protein = int(self.ui.proteinLineEdit.text())

        # Validate inputs before proceeding
        if not all([food_name, serv_size]) or any([calories is None, protein is None, carbs is None, fat is None]):
            logging.warning("Not all fields were filled out correctly")
            QMessageBox.warning(self, "Input Error", "All fields must be filled out.")
            return

        try:
            success = FoodOperations.add_food_item(
                self.database_manager.connection,
                food_name, no_serve, serv_size, calories, protein, carbs, fat
            )
            if success:
                logging.info(f"Food item {food_name} added successfully")
                QMessageBox.information(self, "Success", "Food item added successfully.")
                self.populate_foods_table()
            else:
                logging.error("Failed to add food item")
                QMessageBox.warning(self, "Error", "Failed to add food item.")
        except Exception as error:
            logging.error(f"Error adding food item: {error}")
            QMessageBox.warning(self, "Error", str(error))

    def populate_size_combobox(self):
        try:
            measurements = FoodOperations.get_measurements(self.database_manager.connection)
            self.ui.sizeComboBox.clear()
            for meas_id, meas_name in measurements:
                self.ui.sizeComboBox.addItem(meas_name, meas_id)
            self.ui.sizeComboBox.setEditable(True)
            self.ui.sizeComboBox.setCurrentIndex(-1)
            logging.info("Size combobox populated successfully.")
        except Exception as error:
            logging.error(f"Error populating size combobox: {error}")
            QMessageBox.warning(self, "Error", f"Failed to load measurements: {str(error)}")

    def populate_foods_table(self):
        logging.debug("Populating foods table")
        try:
            cursor = self.database_manager.connection.cursor()
            query = """SELECT Foods.FoodId, Foods.FoodName, ServingInfo.NoServe, ServingInfo.ServSize, 
                       Nutrition.Calories, Nutrition.Carbs, Nutrition.Fat, Nutrition.Protein 
                       FROM Foods
                       JOIN ServingInfo ON Foods.ServId = ServingInfo.ServId
                       JOIN Nutrition ON Foods.FoodId = Nutrition.FoodId"""
            cursor.execute(query)
            rows = cursor.fetchall()

            self.ui.foodsTable.setRowCount(0)
            for row_number, row_data in enumerate(rows):
                self.ui.foodsTable.insertRow(row_number)
                food_id = row_data[0]
                for column_number, data in enumerate(row_data[1:]):
                    self.ui.foodsTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                self.add_food_action_buttons(row_number, food_id)
            logging.info("Foods table populated successfully")
        except PyodbcError as error:
            logging.error(f"Error populating foods table: {error}")
            QMessageBox.warning(self, "Error", f"Failed to laod foods: {str(error)}")

    def add_food_action_buttons(self, row, food_id):
        button_style = "background-color: rgb(139, 196, 190);"

        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet(button_style)
        edit_button.clicked.connect(lambda _, id=food_id: self.edit_food(id))

        remove_button = QPushButton("Remove")
        remove_button.setStyleSheet(button_style)
        remove_button.clicked.connect(lambda _, id=food_id: self.remove_food(id))

        self.ui.foodsTable.setCellWidget(row, self.ui.foodsTable.columnCount() -2, edit_button)
        self.ui.foodsTable.setCellWidget(row, self.ui.foodsTable.columnCount() -1, remove_button)

    def edit_food(self, food_id):
        try:
            logging.info(f"Editing food ID: {food_id}")
            food_details = self.get_food_details(food_id)
            if food_details:
                logging.debug(f"Food details retrieved: {food_details}")
                self.navigate_to_edit_existing_food_page(food_details, food_id)
            else:
                logging.warning(f"Failed to fetch details for food Id: {food_id}")
                QMessageBox.warning(self, "Error", "Failed to fetch food details.")
        except Exception as error:
            logging.error(f"Error editing food details: {str(error)}")
            QMessageBox.warning(self, "Error", f"An error occurred while editing food: {str(error)}")
            QMessageBox.warning(self, "Error", f"An error occurred while editing food: {str(error)}")

    def remove_food(self, food_id):
        confirm = QMessageBox.question(self, "Confirm Removal", "Are you sure you want to remove this food item?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                FoodOperations.delete_food_item(self.database_manager.connection, food_id)
                logging.info(f"Food item removed successfully.")
                self.populate_foods_table()
                QMessageBox.information(self, "Success", "Food item removed successfully.")
            except Exception as error:
                logging.error(f"Error removing food item: {error}")
                QMessageBox.warning(self, "Error", f"Error removing food item: {str(error)}")

    def save_food_and_return_to_add_foods(self):
        try:
            food_name = self.ui.foodNameLine.text().strip()
            no_serve = self.ui.quantityDoubleSpinBox.value()
            serv_size = self.ui.sizeComboBox.currentText()
            calories = int(self.ui.caloriesLineEdit.text())
            carbs = int(self.ui.carbsLine.text())
            fat = int(self.ui.fatLine.text())
            protein = int(self.ui.proteinLine.text())

            food_id = FoodOperations.add_food_item(
                self.database_manager.connection,
                food_name, no_serve, serv_size, calories, protein, carbs, fat
            )

            if food_id:
                QMessageBox.information(self, "Success", f"Food item '{food_name}' added successfully.")
                if hasattr(self, 'previous_page_index'):
                    self.ui.stackedWidget.setCurrentIndex(self.previous_page_index)
                else:
                    self.ui.stackedWidget.setCurrentIndex(4)
                self.search_foods()
            else:
                QMessageBox.warning(self, "Error", "Failed to add food item.")
        except Exception as error:
            logging.error(f"Error saving new food: {error}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def save_food_and_return_to_manage(self):
        self.save_food_item()
        self.ui.stackedWidget.setCurrentIndex(8)

    def get_food_details(self, food_id):
        try:
            cursor = self.database_manager.connection.cursor()
            query = """SELECT Foods.FoodName, ServingInfo.NoServe, ServingInfo.ServSize,
                    Nutrition.Calories, Nutrition.Carbs, Nutrition.Fat, Nutrition.Protein
                    FROM Foods
                    JOIN ServingInfo ON Foods.ServId = ServingInfo.ServId
                    JOIN Nutrition ON Foods.FoodId = Nutrition.FoodId
                    WHERE Foods.FoodId = ?"""
            cursor.execute(query, (food_id,))
            return cursor.fetchone()
        except Exception as error:
            logging.error(f"Error getting food details: {error}")
            return None

    def add_new_protein_type(self):
        protein_type = self.ui.newProteinTypeLine.text().strip()
        if protein_type:
            try:
                protein_id = ProteinOperations.add_protein(self.database_manager.connection, protein_type)
                if protein_id:
                    self.ui.newProteinTypeLine.clear()
                    self.populate_protein_types_table()
                    QMessageBox.information(self, "Success", f"Protein type '{protein_type}' added successfully.")
                else:
                    raise Exception("Failed to add protein type.")
            except Exception as error:
                logging.error(f"Error adding protein type: {error}")
                QMessageBox.warning(self, "Error", f"Failed to add protein type: {str(error)}")
        else:
            QMessageBox.information(self, "Input Error", "Protein type name cannot be empty.")

    def get_protein_names(self, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT ProteinId, ProteinName FROM Proteins ORDER BY ProteinName")
            return cursor.fetchall()
        except Exception as error:
            logging.error(f"Error fetching protein name: {error}")
            return[]

    def populate_protein_combo_box(self):
        logging.debug("Populating protein combo box")
        try:
            proteins = self.get_protein_names(self.database_manager.connection)
            logging.debug(f"Fetched proteins {proteins}")
            self.ui.proteinComboBox.clear()
            self.ui.proteinComboBox.addItem("Select Protein Type", None)
            for protein_id, protein_name in proteins:
                self.ui.proteinComboBox.addItem(protein_name, protein_id)
            logging.info("Protein combo box populated successfully.")
        except Exception as error:
            logging.error(f"Error populating protein combo box: {error}")
            QMessageBox.warning(self, "Error", f"Failed to load protein types: {str(error)}")

    def populate_protein_types_table(self):
        try:
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT ProteinId, ProteinName FROM Proteins ORDER BY ProteinName")
            protein_types = cursor.fetchall()

            self.ui.proteinTypesTable.setRowCount(0)
            self.ui.proteinTypesTable.setColumnCount(3)

            for row, (protein_id, protein_name) in enumerate(protein_types):
                self.ui.proteinTypesTable.insertRow(row)
                self.ui.proteinTypesTable.setItem(row, 0, QTableWidgetItem(protein_name))
                self.add_protein_type_action_buttons(row, protein_id)

            logging.info("Protein types table populated successfully.")
        except Exception as error:
            logging.error(f"Error populating protein types table: {error}")
            QMessageBox.warning(self, "Error", f"Failed to load protein types: {str(error)}")

    def add_protein_type_action_buttons(self, row, protein_id):
        button_style = "background-color: rgb(139, 196, 190);"

        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet(button_style)
        edit_button.clicked.connect(lambda _, id=protein_id: self.edit_protein_type(id))

        remove_button = QPushButton("Remove")
        remove_button.setStyleSheet(button_style)
        remove_button.clicked.connect(lambda _, id=protein_id: self.remove_protein_type(id))

        self.ui.proteinTypesTable.setCellWidget(row, 1, edit_button)
        self.ui.proteinTypesTable.setCellWidget(row, 2, remove_button)

    def edit_protein_type(self, protein_id):
        current_name = self.get_protein_type_name(protein_id)
        new_name, ok = QInputDialog.getText(self, "Edit Protein Type", "Enter new protein type name:",
                                            text=current_name)
        if ok and new_name:
            try:
                ProteinOperations.update_protein(self.database_manager.connection, protein_id, new_name)
                self.populate_protein_types_table()
                QMessageBox.information(self, "Success", "Protein type updated successfully.")
            except Exception as error:
                logging.error(f"Error updating protein type: {error}")
                QMessageBox.warning(self, "Error", f"Failed to update protein type: {str(error)}")

    def remove_protein_type(self, protein_id):
        confirm = QMessageBox.question(self, "Confirm Removal", "Are you sure you want to remove this protein type?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                ProteinOperations.delete_protein(self.database_manager.connection, protein_id)
                self.populate_protein_types_table()
                QMessageBox.information(self, "Success", "Protein type removed succcessfully.")
            except Exception as error:
                logging.error(f"Error removing protein type: {error}")
                QMessageBox.warning(self, "Error", f"Failed to remove protein type: {str(error)}")

    def get_protein_type_name(self, protein_id):
        cursor = self.database_manager.connection.cursor()
        cursor.execute("SELECT ProteinName FROM Proteins WHERE ProteinId = ?", (protein_id,))
        result = cursor.fetchone()
        return result[0] if result else ""

    def get_protein_names(self, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT ProteinId, ProteinName FROM Proteins ORDER BY ProteinName")
            return cursor.fetchall()
        except Exception as error:
            logging.error(f"Error fetching protein names: {error}")
            return[]

    def closeEvent(self, event):
        # Close database connection if initialized
        logging.info("Closing application and disconnection from database.")
        if hasattr(self, 'database_manager'):
            self.database_manager.close_connection()
        event.accept()