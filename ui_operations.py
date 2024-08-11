# ui_operations.py
# This script defines the main functionality for a PyQt5-based application managing recipes, foods, and custom tags.
# It includes methods for handling UI interactions, database operations, and navigation between different pages of the application.

import logging
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QInputDialog, QPushButton, QMessageBox, QDialog, QTextEdit, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from UI_Files.ui_mainwindow import Ui_MainWindow
from database import DatabaseManager
from customTags_operations import CustomTagOperations
from food_operations import FoodOperations
from proteins_operations import ProteinOperations
from recipes_operations import RecipeOperations
from custom_dialogs import TagRemovalDialog
from custom_dialogs import FoodRemovalDialog
from custom_dialogs import ProteinRemovalDialog
from pyodbc import Error as PyodbcError

logging.basicConfig(level=logging.DEBUG)

# Custom Widgets
class CustomButton(QPushButton):
    clicked_with_row = pyqtSignal(int)

    def __init__(self, text, row):
        super().__init__(text)
        self.row = row
        self.clicked.connect(self.emit_with_row)

    def emit_with_row(self):
        self.clicked_with_row.emit(self.row)

# MainWindow Class Initialization
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize the UI and home page
        logging.debug("Initializing MainWindow")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentIndex(0)

        self.current_rec_id = None
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

    def setup_connections(self):
        button_style = self.get_button_style()

        # Navigation buttons
        self.ui.findArecipeButton.clicked.connect(self.navigate_to_find_recipe_page)
        self.ui.returnTohomeButton.clicked.connect(self.navigate_to_home_page)
        self.ui.submitArecipeButton.clicked.connect(self.navigate_to_submit_recipe_page)
        self.ui.addNewFoodItemButton.clicked.connect(self.navigate_to_add_new_food_page)
        self.ui.addNewTagButton.clicked.connect(self.add_new_tag)
        self.ui.saveButton_3.clicked.connect(self.save_food_and_return_to_manage)
        self.ui.saveButton_4.clicked.connect(self.navigate_to_add_steps_page)
        self.ui.saveButton_5.clicked.connect(self.save_steps_and_continue)
        self.ui.saveButton_6.clicked.connect(self.save_and_show_recipe)
        self.ui.saveButton_7.clicked.connect(self.save_food_and_return_to_add_foods)
        self.ui.saveButton_8.clicked.connect(self.save_edited_food)
        self.ui.recipeSearchButton.clicked.connect(self.search_recipes)
        self.ui.editRecipeButton.clicked.connect(self.handle_edit_recipe_button)

        self.ui.searchCategoryComboBox.currentIndexChanged.connect(self.update_search_fields)

        self.update_search_fields()

        # Menu Actions
        self.home_action = QtWidgets.QAction("Home", self)
        self.ui.menuHome.addAction(self.home_action)
        self.home_action.triggered.connect(self.navigate_to_home_page)
        self.ui.actionCustom_Tags.triggered.connect(self.on_action_custom_tags_triggered)
        self.ui.actionFood_and_Nutrition_Info.triggered.connect(self.navigate_to_food_and_nutrition_info_page)
        self.ui.actionProtein_Types.triggered.connect(self.navigate_to_protein_types_page)

        # Apply button style
        self.apply_button_style(button_style)

        self.populate_recipe_search_categories()
        self.populate_protein_combo_box()
        self.populate_protein_type_combo_box()
        self.populate_custom_tags_combo_box()
        self.ui.searchCategoryComboBox.setCurrentIndex(4)
        self.ui.recipeNameLabel_2.setVisible(True)
        self.ui.searchCriteriaLineEdit.setVisible(True)
        self.ui.newRecipeNameLabel.setVisible(False)
        self.ui.addFoodsButton.setVisible(False)
        self.ui.addFoodsButton.setEnabled(False)

    def connectUI(self):
        button_style = "background-color: rgb(139, 196, 190);"

        # Navigation and action buttons
        self.ui.ingredientSearchButton.clicked.connect(self.search_and_populate_foods_list)
        self.ui.returnTohomeButton_2.clicked.connect(self.navigate_to_home_page)
        self.ui.returnTohomeButton_3.clicked.connect(self.navigate_to_home_page)
        self.ui.returnTohomeButton_4.clicked.connect(self.navigate_to_home_page)
        self.ui.addNewProteinTypeButton.clicked.connect(self.add_new_protein_type)
        self.on_recipe_category_changed(self.ui.searchCategoryComboBox.currentIndex())

        self.ui.submitButton.clicked.connect(self.handle_recipe_name_submission)
        self.ui.addFoodsButton.clicked.connect(self.navigate_to_add_foods_page)
        self.ui.ingredientSearchButton.clicked.connect(self.search_foods)
        self.ui.addStepButton.clicked.connect(self.add_step_to_recipe)
        self.ui.stackedWidget.currentChanged.connect(self.on_stacked_widget_changed)

        self.ui.addStepButton.setStyleSheet(button_style)
        self.ui.ingredientSearchButton.setStyleSheet(button_style)
        self.ui.returnTohomeButton_2.setStyleSheet(button_style)
        self.ui.returnTohomeButton_3.setStyleSheet(button_style)
        self.ui.returnTohomeButton_4.setStyleSheet(button_style)
        self.ui.addNewProteinTypeButton.setStyleSheet(button_style)
        self.ui.recipeSearchButton.setStyleSheet(button_style)
        self.ui.editRecipeButton.setStyleSheet(button_style)

    def get_button_style(self):
        return "background-color: rgb(139, 196, 190);"

    def apply_button_style(self, style):
        buttons = [
            self.ui.findArecipeButton, self.ui.returnTohomeButton, self.ui.submitArecipeButton,
            self.ui.addNewFoodItemButton, self.ui.addNewTagButton, self.ui.saveButton_3,
            self.ui.saveButton_4, self.ui.saveButton_5, self.ui.saveButton_6, self.ui.saveButton_7,
            self.ui.recipeSearchButton, self.ui.editRecipeButton
        ]
        for button in buttons:
            button.setStyleSheet(style)

    # Navigation Functions
    def navigate_to_home_page(self):
        logging.debug("Navigating to the Home page.")
        self.ui.stackedWidget.setCurrentIndex(0)
        logging.debug("Current index set to 0")

    def navigate_to_find_recipe_page(self):
        logging.debug("Navigating to the Find Recipe page.")
        self.clear_search_fields_and_hide_widgets()
        self.clear_results_table()
        # self.ui.searchCategoryComboBox.currentIndexChanged.connect(self.on_recipe_category_changed)
        self.ui.stackedWidget.setCurrentIndex(1)
        logging.debug("Current index set to 1")

    def navigate_to_submit_recipe_page(self):
        logging.debug("Navigating to the Submit Recipe page.")
        self.reset_submit_new_recipe_page()
        self.ui.stackedWidget.setCurrentIndex(3 )
        logging.debug("Current index set to 3")

    def navigate_to_add_foods_page(self):
        logging.debug("Navigating to the Add Foods to Recipe page.")

        # Clear any prior data from fields
        self.ui.findIngredientSearch.clear()
        self.ui.recipeIngredientsList.clear()
        logging.debug("Cleared findIngredientSearch field and recipeIngredientsList.")

        self.ui.stackedWidget.setCurrentIndex(4)
        logging.debug("Current index set to 4")

        # Debug current_recipe_foods
        logging.debug(f"Current recipe foods before updating table: {self.current_recipe_foods}")

        # Set up the recipeIngredientsList table
        self.ui.recipeIngredientsList.setColumnCount(4)
        headers = ["Ingredient", "Amount", "Unit", " "]
        self.ui.recipeIngredientsList.setHorizontalHeaderLabels(headers)

        # Optional: Adjust column widths
        header = self.ui.recipeIngredientsList.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # Ingredient name column
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)  # Amount column
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)  # Unit column
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)  # Buttons column
        self.ui.recipeIngredientsList.setColumnWidth(3, 100)

        # Update the recipe ingredients table
        self.update_recipe_ingredients_table()

        # Force UI update
        self.ui.recipeIngredientsTable.update()
        QtWidgets.QApplication.processEvents()
        logging.debug("UI update forced after navigating to Add Foods to Recipe page")

    def navigate_to_add_steps_page(self):
        logging.debug("Navigating to the Add Steps to Recipe page.")
        self.ui.stackedWidget.setCurrentIndex(5)
        self.populate_recipe_steps_table()
        self.ui.stepTextEdit.clear()
        logging.debug("Current index set to 5")

    def navigate_to_finish_recipe_info_page(self):
        logging.debug("Navigating to the Finish Recipe Info page.")
        self.ui.stackedWidget.setCurrentIndex(6)

        if self.current_rec_id:
            recipe = RecipeOperations.get_recipe_details(self.database_manager.connection, self.current_rec_id)
            if recipe:
                self.ui.noOfServingsLine.setText(str(recipe['servings']))

                # Set the protein type in the combo box
                self.populate_protein_combo_box()  # Ensure the combo box is populated
                index = self.ui.proteinComboBox.findText(recipe['protein_type'])
                if index >= 0:
                    self.ui.proteinComboBox.setCurrentIndex(index)

                # Set notes if they exist
                if 'notes' in recipe:
                    self.ui.notesTextEdit.setPlainText(recipe.get('notes', ''))

        self.populate_protein_combo_box()
        self.populate_tags_list()
        self.set_checked_tags_for_current_recipe()
        logging.debug("Current index set to 6")

    def on_action_custom_tags_triggered(self):
        logging.debug("Navigating to the Custom Tags page.")
        self.ui.stackedWidget.setCurrentIndex(7)
        logging.debug("Current index set to 7")
        self.populate_tags_table()

    def navigate_to_food_and_nutrition_info_page(self):
        logging.debug("Navigating to the Food and Nutrition Info page.")
        self.ui.stackedWidget.setCurrentIndex(8)
        self.ui.saveButton_7.hide()
        logging.debug("Current index set to 8")
        self.populate_foods_table()

    def navigate_to_add_new_food_page(self):
        try:
            logging.debug("Navigating to the Add New Food page.")
            self.ui.stackedWidget.setCurrentIndex(9)
            logging.debug("Current index set to 9")
            self.clear_food_input_fields()
            self.populate_size_combobox()

            # Show saveButton_8 and hide saveButton_3 and saveButton_7
            self.ui.saveButton_8.show()
            self.ui.saveButton_3.hide()
            self.ui.saveButton_7.hide()

            # Set tab order for the fields on the editFoodPage
            self.setTabOrder(self.ui.foodNameLine, self.ui.quantityDoubleSpinBox)
            self.setTabOrder(self.ui.quantityDoubleSpinBox, self.ui.sizeComboBox)
            self.setTabOrder(self.ui.sizeComboBox, self.ui.caloriesLineEdit)
            self.setTabOrder(self.ui.caloriesLineEdit, self.ui.carbsLineEdit)
            self.setTabOrder(self.ui.carbsLineEdit, self.ui.proteinLineEdit)
            self.setTabOrder(self.ui.proteinLineEdit, self.ui.fatLineEdit)
            self.setTabOrder(self.ui.fatLineEdit, self.ui.saveButton_8)

            # Connect saveButton_8 to the new save method
            self.ui.saveButton_8.clicked.disconnect()  # Disconnect any existing connections
            self.ui.saveButton_8.clicked.connect(self.save_new_food_and_return)

            if hasattr(self, 'current_editing_food_id'):
                del self.current_editing_food_id
        except Exception as error:
            logging.error(f"Error navigating to the Add New Food page: {str(error)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(error)}")

    def save_new_food_and_return(self):
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
                self.navigate_to_food_and_nutrition_info_page()
            else:
                QMessageBox.warning(self, "Error", "Failed to add food item.")
        except Exception as error:
            logging.error(f"Error saving new food: {error}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def navigate_to_edit_existing_food_page(self, food_details, food_id):
        try:
            logging.debug(f"Navigating to edit existing food page for food ID: {food_id}")
            self.ui.stackedWidget.setCurrentIndex(9)

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
            logging.debug(f"Set current_editing_food_id to {food_id}")
            logging.debug("Existing food details populated successfully")

            self.ui.saveButton_3.hide()
            self.ui.saveButton_7.hide()
            self.ui.saveButton_8.show()

        except Exception as error:
            logging.error(f"Error navigating to edit existing food page: {str(error)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(error)}")

    def adjust_column_sizes(self, table):
        table.resizeColumnsToContents()
        font_metrics = table.fontMetrics()
        for column in range(table.columnCount()):
            header_text = table.horizontalHeaderItem(column).text()
            header_width = font_metrics.horizontalAdvance(header_text) + 50
            if table.columnWidth(column) < header_width:
                table.setColumnWidth(column, header_width)

    def save_edited_food(self):
        try:
            if not hasattr(self, 'current_editing_food_id'):
                raise AttributeError("No food item is currently being edited.")

            # Gather the updated food details
            food_name = self.ui.foodNameLine.text().strip()
            quantity = self.ui.quantityDoubleSpinBox.value()
            size = self.ui.sizeComboBox.currentText()
            calories = int(self.ui.caloriesLineEdit.text())
            carbs = int(self.ui.carbsLine.text())
            fat = int(self.ui.fatLine.text())
            protein = int(self.ui.proteinLine.text())

            # Update the food in the database
            success = FoodOperations.update_food_item(
                self.database_manager.connection,
                self.current_editing_food_id,
                food_name, quantity, size, calories, protein, carbs, fat
            )

            if success:
                logging.info(f"Food item {food_name} updated successfully.")
                QMessageBox.information(self, "Success", "Food item updated successfully.")

                # Navigate back to the food table page
                self.navigate_to_food_and_nutrition_info_page()
            else:
                raise Exception("Failed to update food item in the database.")

        except AttributeError as error:
            logging.error(f"AttributeError in save_edited_food: {error}")
            QMessageBox.critical(self, "Error", str(error))
        except Exception as error:
            logging.error(f"Error saving edited food: {error}")
            QMessageBox.critical(self, "Error", f"An error occurred while saving the food item: {str(error)}")

    def navigate_to_protein_types_page(self):
        logging.debug("Navigating to the Protein Types page.")
        self.ui.stackedWidget.setCurrentIndex(10)
        logging.debug("Current index set to 10")
        self.populate_protein_types_table()

    def navigate_to_edit_food_page(self, new_food_name=None):
        self.previous_page_index = self.ui.stackedWidget.currentIndex()
        self.ui.stackedWidget.setCurrentIndex(9)

        # Hide saveButton_3, saveButton_8 and show saveButton_7
        self.ui.saveButton_3.hide()
        self.ui.saveButton_7.show()
        self.ui.saveButton_8.hide()

        if new_food_name:
            self.ui.foodNameLine.setText(new_food_name)
        self.populate_size_combobox()

    def navigate_to_add_recipe_details_page(self, rec_id):
        logging.debug(f"Navigating to add recipe details page for recipe ID: {rec_id}")
        pass

    def leave_find_recipe_page(self):
        logging.debug("Leaving the Find Recipe page.")
        self.ui.searchCategoryComboBox.currentIndexChanged.disconnect(self.on_recipe_category_changed)
        logging.info("Disconnected on_recipe_category_changed signal.")

    def update_search_fields(self):
        category_index = self.ui.searchCategoryComboBox.currentIndex()

        # Hide all fields first
        self.ui.caloriesLabel_2.hide()
        self.ui.calsFromLabel.hide()
        self.ui.calsToLabel.hide()
        self.ui.minCalLineEdit.hide()
        self.ui.maxCalLineEdit.hide()
        self.ui.macrosLabel.hide()
        self.ui.carbsLabel_2.hide()
        self.ui.proteinLabel_2.hide()
        self.ui.fatLabel_2.hide()
        self.ui.carbsLineEdit.hide()
        self.ui.proteinLineEdit.hide()
        self.ui.fatLineEdit.hide()
        self.ui.customTagsLabel.hide()
        self.ui.customTagsComboBox.hide()
        self.ui.proteinTypeLabel_2.hide()
        self.ui.proteinTypeComboBox.hide()

        # Show relevant fields based on the selected category
        if category_index == 0:  # Calorie Range
            self.ui.recipeNameLabel_2.hide()
            self.ui.searchCriteriaLineEdit.hide()
            self.ui.caloriesLabel_2.show()
            self.ui.calsFromLabel.show()
            self.ui.calsToLabel.show()
            self.ui.minCalLineEdit.show()
            self.ui.maxCalLineEdit.show()
        elif category_index == 1:  # Custom Tags
            self.ui.recipeNameLabel_2.hide()
            self.ui.searchCriteriaLineEdit.hide()
            self.ui.customTagsLabel.show()
            self.ui.customTagsComboBox.show()
        elif category_index == 2:  # Macros
            self.ui.recipeNameLabel_2.hide()
            self.ui.searchCriteriaLineEdit.hide()
            self.ui.macrosLabel.show()
            self.ui.carbsLabel_2.show()
            self.ui.proteinLabel_2.show()
            self.ui.fatLabel_2.show()
            self.ui.carbsLineEdit.show()
            self.ui.proteinLineEdit.show()
            self.ui.fatLineEdit.show()
        elif category_index == 3:  # Protein Type
            self.ui.recipeNameLabel_2.hide()
            self.ui.searchCriteriaLineEdit.hide()
            self.ui.proteinTypeLabel_2.show()
            self.ui.proteinTypeComboBox.show()
        else:
            self.ui.recipeNameLabel_2.show()
            self.ui.searchCriteriaLineEdit.show()

        logging.debug(f"Updated search fields for category index: {category_index}")

    def handle_recipe_name_submission(self):
        try:
            logging.debug("handle_recipe_name_submission called")
            recipe_name = self.ui.recipeNamefield.text().strip()
            logging.debug(f"Recipe name: {recipe_name}")

            if not recipe_name:
                logging.warning("Empty recipe name submitted")
                QMessageBox.warning(self, "Error", "Please enter a recipe name.")
                return

            try:
                logging.debug("Checking if recipe name exits")
                if RecipeOperations.recipe_name_exists(self.database_manager.connection, recipe_name):
                    logging.debug("Recipe name already exists.")
                    QMessageBox.warning(self, "Duplicate Recipe",
                                        "This recipe name already exists. Please choose a different name.")
                    return
            except Exception as error:
                logging.exception(f"Error checking if recipe name exists: {error}")
                QMessageBox.critical(self, "Error", f"An error occurred while checking the recipe name: {str(error)}")
                return

            try:
                logging.debug("Getting selected protein ID")
                selected_protein_id = self.ui.proteinComboBox.currentData() if hasattr(self.ui, 'proteinComboBox') else None
                logging.debug(f"Selected protein ID: {selected_protein_id}")
            except Exception as error:
                logging.exception(f"Error getting selected protein ID: {error}")
                QMessageBox.critical(self, "Error", f"An error occurred while getting the selected protein: {str(error)}")
                return

            try:
                logging.debug("Adding recipe to database")
                self.current_rec_id = RecipeOperations.add_recipe(
                    self.database_manager.connection,
                    recipe_name,
                    servings=1,
                    instructions='',
                    protein_id=selected_protein_id
                )
                logging.debug(f"Recipe added with ID: {self.current_rec_id}")
            except Exception as error:
                logging.exception(f"Error adding recipe to database: {error}")
                QMessageBox.critical(self, "Error", f"An error occurred while adding the recipe: {str(error)}")
                return

            if self.current_rec_id:
                try:
                    logging.debug("Updating UI after successful recipe addition")
                    self.ui.newRecipeNameLabel.setText(f"New Recipe: {recipe_name}")
                    self.ui.newRecipeNameLabel.setVisible(True)
                    self.ui.addFoodsButton.setVisible(True)
                    self.ui.addFoodsButton.setEnabled(True)
                    QMessageBox.information(self, "Success", f"Recipe '{recipe_name}' added successfully.  Next, add foods to this recipe.")
                except Exception as error:
                    logging.exception(f"Error updating UI after recipe addition: {error}")
                    QMessageBox.critical(self, "Error",
                                         f"Recipe was added but an error occurred while updating the UI: {str(error)}")
            else:
                logging.warning("Failed to add recipe")
                QMessageBox.warning(self, "Error", "Failed to add the recipe.  Please try again.")

        except Exception as error:
            logging.exception(f"Error in handle_recipe_name_submission: {error}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def reset_submit_new_recipe_page(self):
        logging.debug("Resetting submit new recipe page")
        self.ui.recipeNamefield.clear()
        self.ui.newRecipeNameLabel.setVisible(False)
        self.ui.addFoodsButton.setVisible(False)
        self.ui.addFoodsButton.setEnabled(False)

        # Clear stored recipe ID
        self.current_rec_id = None
        logging.debug("Submit new recipe page reset complete")

    def navigate_to_recipe_page(self, rec_id):
        logging.debug(f"Navigating to recipe page for recipe ID: {rec_id}")
        try:
            self.current_rec_id = rec_id
            self.populate_recipe_page(rec_id)
            self.ui.stackedWidget.setCurrentIndex(2)
        except Exception as error:
            logging.error(f"Error navigating to recipe page: {error}")
            QMessageBox.warning(self, "Error", f"An error occurred while navigating to the recipe page: {str(error)}")

    def add_step_to_recipe(self):
        logging.debug("add_step_to_recipe called")
        try:
            step_text = self.ui.stepTextEdit.toPlainText().strip()
            logging.debug(f"Step text: {step_text}")
            if step_text:
                row_position = self.ui.recipeStepsTable.rowCount()
                self.insert_step(step_text, row_position)
                self.ui.stepTextEdit.clear()

                # Save the updated steps to the database
                steps = [self.ui.recipeStepsTable.item(row, 0).text() for row in
                         range(self.ui.recipeStepsTable.rowCount())]
                RecipeOperations.save_recipe_steps(self.database_manager.connection, self.current_rec_id, steps)

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

        # Resize rows to fit contents
        self.ui.recipeStepsTable.resizeRowToContents(row_position)

        # Set the column sizes
        header = self.ui.recipeStepsTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # First column stretches
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)  # Button columns resize to content
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        # Adjust the first column to occupy approximately 3/4 of the total width
        total_width = self.ui.recipeStepsTable.width()
        header.resizeSection(0, int(total_width * 0.75))

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
                self.current_rec_id,
                steps
            )

            if success:
                logging.info(f"Recipe steps saved successfully for recipe ID: {self.current_rec_id}")

                # Join steps into a single string
                instructions = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))

                # Update recipe instructions
                update_success = RecipeOperations.update_recipe_instructions(
                    self.database_manager.connection,
                    self.current_rec_id,
                    instructions
                )

                if update_success:
                    # Navigate to finishRecipeInfoPage
                    self.ui.stackedWidget.setCurrentIndex(6)
                    self.populate_finish_recipe_info_page()
                    self.custom_tag_operations.populate_tags_list(self.ui.tagsListWidget, self.database_manager.connection)
                    self.check_tags_list_visibility()
                    self.set_checked_tags_for_current_recipe()
                    logging.info("Navigated to Finish Recipe Info page.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update recipe instructions. Please try again.")

        except Exception as error:
            logging.error(f"Error in save_steps_and_continue: {error}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

        logging.debug("Exiting save_steps_and_continue method")

    def populate_steps(self, rec_id):
        steps = RecipeOperations.get_recipe_steps(self.database_manager.connection, rec_id)

        self.ui.stepsTable.verticalHeader().setVisible(False)
        self.ui.stepsTable.setRowCount(0)
        self.ui.stepsTable.setHorizontalHeaderLabels(['Steps'])

        header = self.ui.stepsTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        for row, step in enumerate(steps):
            self.ui.stepsTable.insertRow(row)
            self.ui.stepsTable.setItem(row, 0, QTableWidgetItem(f"{step['number']}. {step['description']}"))

        self.ui.stepsTable.resizeColumnsToContents()
        self.ui.stepsTable.resizeRowsToContents()

        logging.info("Steps table populated successfully.")

    def load_and_display_recipe(self, rec_id):
        try:
            logging.info(f"Loading and displaying recipe with ID: {rec_id}")
            self.current_rec_id = rec_id

            # Populate the recipe page with the information
            self.populate_recipe_page(rec_id)

            # Navigate to the recipe page
            self.ui.stackedWidget.setCurrentIndex(2)

            # Force UI update
            self.ui.ingredientsTable.update()
            QtWidgets.QApplication.processEvents()

            # Check if the table is visible and has the correct number of rows
            logging.debug(f"Ingredients table visible: {self.ui.ingredientsTable.isVisible()}")
            logging.debug(f"Ingredients table row count: {self.ui.ingredientsTable.rowCount()}")

        except Exception as error:
            logging.error(f"Error loading and displaying recipe: {error}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while loading and displaying the recipe: {str(error)}")

    def populate_recipe_page(self, rec_id):
        try:
            logging.info(f"Populating recipe page for recipe ID: {rec_id}")

            # Update current_rec_id
            self.current_rec_id = rec_id
            logging.debug(f"Current recipe ID set to: {self.current_rec_id}")

            # Fetch recipe details
            recipe = RecipeOperations.get_recipe_info(self.database_manager.connection, rec_id)
            logging.debug(f"Recipe details: {recipe}")

            if recipe is None:
                logging.warning(f"No recipe found with ID: {rec_id}")
                QMessageBox.warning(self, "Error", f"No recipe found with ID: {rec_id}")
                return

            # Populate recipe name
            self.ui.recipeNameLabel.setText(str(recipe['name']))
            logging.debug(f"Set recipe name: {recipe['name']}")

            # Populate serving size
            self.ui.servingSizeLine.setText(str(recipe['servings']))
            logging.debug(f"Set serving size: {recipe['servings']}")

            # Populate ingredients
            self.populate_ingredients_table(rec_id)

            # Populate steps
            self.populate_steps_table(rec_id)
            self.ui.stepsTable.verticalHeader().setVisible(False)

            # Populate notes tab
            self.ui.notesTextEdit_2.setPlainText(recipe['notes'])

            # Populate nutrition table
            self.populate_nutrition_table(rec_id)

            # Populate tags
            recipe_tags = RecipeOperations.get_recipe_tags(self.database_manager.connection, rec_id)
            self.custom_tag_operations.display_tags_as_text(self.ui.tagsListWidget_2, recipe_tags)
            logging.debug(f"Populated tags: {recipe_tags}")
            logging.info("Recipe page populated successfully")

        except Exception as error:
            logging.error(f"Error populating recipe page: {error}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while loading the recipe: {str(error)}")

    def populate_ingredients(self, rec_id):
        ingredients = RecipeOperations.get_recipe_foods(self.database_manager.connection, rec_id)
        logging.debug(f"Fetched ingredients for recipe {rec_id}: {ingredients}")

        self.ui.ingredientsTable.verticalHeader().setVisible(False)
        self.ui.ingredientsTable.setRowCount(0)
        self.ui.ingredientsTable.setColumnCount(3)
        self.ui.ingredientsTable.setHorizontalHeaderLabels(['Ingredient', 'Amount', 'Unit'])

        for row, ingredient in enumerate(ingredients):
            self.ui.ingredientsTable.insertRow(row)
            self.ui.ingredientsTable.setItem(row, 0, QTableWidgetItem(ingredient['name']))
            self.ui.ingredientsTable.setItem(row, 1, QTableWidgetItem(str(ingredient['no_serve'])))
            self.ui.ingredientsTable.setItem(row, 2, QTableWidgetItem(ingredient['serv_size']))

        self.adjust_column_sizes(self.ui.ingredientsTable)

        logging.info("Ingredients table populated successfully.")

    def populate_ingredients_table(self, rec_id):
        ingredients = RecipeOperations.get_recipe_foods(self.database_manager.connection, rec_id)
        logging.debug(f"Fetched ingredients for recipe {rec_id}: {ingredients}")

        self.ui.ingredientsTable.setRowCount(0)
        self.ui.ingredientsTable.setColumnCount(3)
        self.ui.ingredientsTable.setHorizontalHeaderLabels(['Ingredient', 'Quantity', 'Measure'])

        for row, ingredient in enumerate(ingredients):
            self.ui.ingredientsTable.insertRow(row)
            self.ui.ingredientsTable.setItem(row, 0, QTableWidgetItem(ingredient['name']))
            self.ui.ingredientsTable.setItem(row, 1, QTableWidgetItem(str(ingredient['no_serve'])))
            self.ui.ingredientsTable.setItem(row, 2, QTableWidgetItem(ingredient['serv_size']))

        self.adjust_column_sizes(self.ui.ingredientsTable)

        logging.info(f"Ingredients table populated with {len(ingredients)} items.")

    def update_recipe_ingredients_table(self):
        try:
            logging.debug(f"Entering update_recipe_ingredients_table method")

            # Clear the table before populating
            self.ui.recipeIngredientsTable.setRowCount(0)
            logging.debug("Cleared recipeIngredientsTable")

            header_labels = ["Food Name", "Quantity", "Size", "Calories", "Carbs", "Fat", "Protein", ""]
            self.ui.recipeIngredientsTable.setHorizontalHeaderLabels(header_labels)

            # Update recipeIngredientsTable
            for index, food in enumerate(self.current_recipe_foods):
                logging.debug(f"Inserting food at row {index}: {food['name']}")
                self.ui.recipeIngredientsTable.insertRow(index)
                self.ui.recipeIngredientsTable.setItem(index, 0, QTableWidgetItem(food['name']))
                self.ui.recipeIngredientsTable.setItem(index, 1, QTableWidgetItem(str(food['no_serve'])))
                self.ui.recipeIngredientsTable.setItem(index, 2, QTableWidgetItem(food['serv_size']))
                self.ui.recipeIngredientsTable.setItem(index, 3, QTableWidgetItem(str(food['calories'])))
                self.ui.recipeIngredientsTable.setItem(index, 4, QTableWidgetItem(str(food['carbs'])))
                self.ui.recipeIngredientsTable.setItem(index, 5, QTableWidgetItem(str(food['fat'])))
                self.ui.recipeIngredientsTable.setItem(index, 6, QTableWidgetItem(str(food['protein'])))

                remove_button = QPushButton("Remove")
                remove_button.setStyleSheet("background-color: rgb(139, 196, 190);")
                remove_button.clicked.connect(lambda _, f=food: self.remove_food_from_recipe(food['food_id']))
                self.ui.recipeIngredientsTable.setCellWidget(index, 7, remove_button)

            # Verify the row count
            row_count = self.ui.recipeIngredientsTable.rowCount()
            logging.info(f"Recipe ingredients table updated with {row_count} items.")
            logging.debug(
                f"Ingredients in table: {[self.ui.recipeIngredientsTable.item(row, 0).text() for row in range(row_count)]}")

            header = self.ui.recipeIngredientsTable.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            for i in range(1, 7):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(7, QHeaderView.Fixed)
            self.ui.recipeIngredientsTable.setColumnWidth(7, 100)

            self.adjust_column_sizes(self.ui.recipeIngredientsTable)
            self.ui.recipeIngredientsTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        except Exception as error:
            logging.error(f"Error updating recipe ingredients table: {error}", exc_info=True)

        logging.info(f"Recipe ingredients table updated with {self.ui.recipeIngredientsTable.rowCount()} items.")
    def populate_recipe_details(self, recipe_id):
        try:
            logging.debug(f"Loading and displaying recipe with ID: {recipe_id}")

            # Fetch recipe details including ingredients
            recipe_details = RecipeOperations.get_recipe_info(self.database_manager.connection, recipe_id)

            # Set current recipe ID
            self.current_rec_id = recipe_id
            logging.debug(f"Current recipe ID set to: {recipe_id}")

            # Update the UI fields with the fetched recipe details
            self.ui.recipeNameLineEdit.setText(recipe_details['name'])
            self.ui.noOfServingsLineEdit.setText(str(recipe_details['servings']))
            self.ui.recipeInstructionsTextEdit.setPlainText(recipe_details['instructions'])
            self.ui.recipeNotesTextEdit.setPlainText(recipe_details['notes'])

            # Update current recipe foods
            self.current_recipe_foods.clear()
            for food in recipe_details['ingredients']:
                self.current_recipe_foods.append(food)
            logging.debug(f"Fetched ingredients for recipe {recipe_id}: {self.current_recipe_foods}")

            # Update the ingredients table
            self.update_recipe_ingredients_table()

            logging.info("Recipe page populated successfully.")
        except Exception as error:
            logging.error(f"Error loading recipe details: {error}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to load recipe details: {str(error)}")

    def display_recipe_details(self, rec_id):
        logging.debug(f"Displaying recipe details for recipe: {rec_id}")
        try:
            recipe_details = RecipeOperations.get_recipe_details(self.database_manager.connection, rec_id)
            if recipe_details:
                # Navigate to the recipe page
                self.ui.stackedWidget.setCurrentWidget(self.ui.recipePage)

                # Update UI elements on the recipe page with recipe details
                self.ui.recipeNameLabel.setText(recipe_details['name'])
                self.ui.servingSizeLabel.setText(str(recipe_details['servings']))
                self.ui.stepsLabel.setText(recipe_details['instructions'])

                # Populate ingredients
                self.populate_ingredients(rec_id)

                # Populate steps
                self.populate_steps(rec_id)

                logging.info("Recipe details displayed successfully.")
            else:
                logging.warning(f"No details found for recipe ID: {rec_id}")
                QMessageBox.warning(self, "Error", "Failed to load recipe details.")
        except Exception as error:
            logging.error(f"Error displaying recipe details: {error}")
            QMessageBox.warning(self, "Error", f"An error occurred while displaying recipe details: {str(error)}")

    def populate_steps_table(self, rec_id):
        try:
            steps = RecipeOperations.get_recipe_steps(self.database_manager.connection, rec_id)

            self.ui.stepsTable.verticalHeader().setVisible(False)
            self.ui.stepsTable.setRowCount(0)
            self.ui.stepsTable.setColumnCount(1)

            header = self.ui.stepsTable.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

            item = self.ui.stepsTable.horizontalHeaderItem(0)
            item.setTextAlignment(Qt.AlignLeft)

            for row, step in enumerate(steps):
                self.ui.stepsTable.insertRow(row)
                self.ui.stepsTable.setItem(row, 0, QTableWidgetItem(f"{step['number']}. {step['description']}"))

            # Resize rows to fit contents
            self.ui.stepsTable.resizeRowsToContents()

            self.ui.stepsTable.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            logging.debug(f"Populated steps: {len(steps)} items")
        except Exception as error:
            logging.error(f"Error populating steps table: {error}")
            QMessageBox.warning(self, "Error", f"Failed to populate the steps table: {str(error)}")

    def populate_nutrition_table(self, rec_id):
        try:
            total_nutrition = RecipeOperations.get_recipe_total_nutrition(self.database_manager.connection, rec_id)
            self.ui.nutritionTable.setRowCount(1)
            self.ui.nutritionTable.setColumnCount(4)
            self.ui.nutritionTable.setHorizontalHeaderLabels(["Calories", "Carbs (g)", "Fat (g)", "Protein (g)"])
            self.ui.nutritionTable.setItem(0, 0, QtWidgets.QTableWidgetItem(str(total_nutrition['calories'])))
            self.ui.nutritionTable.setItem(0, 1, QtWidgets.QTableWidgetItem(str(total_nutrition['carbs'])))
            self.ui.nutritionTable.setItem(0, 2, QtWidgets.QTableWidgetItem(str(total_nutrition['fat'])))
            self.ui.nutritionTable.setItem(0, 3, QtWidgets.QTableWidgetItem(str(total_nutrition['protein'])))
        except Exception as error:
            logging.error(f"Error populating nutrition table: {error}")
            QMessageBox.warning(self, "Error", f"Failed to populate the nutrition table: {str(error)}")

    def populate_finish_recipe_info_page(self):
        try:
            recipe = RecipeOperations.get_recipe_info(self.database_manager.connection, self.current_rec_id)
            if recipe:
                self.ui.noOfServingsLine.setText(str(recipe['servings']))
                self.ui.proteinComboBox.setCurrentText(recipe['protein_type'])
                self.ui.notesTextEdit_2.setPlainText(recipe['notes'])
                nutrition = RecipeOperations.get_recipe_total_nutrition(self.database_manager.connection,
                                                                        self.current_rec_id)
                self.ui.nutritionTable.setItem(0, 0, QTableWidgetItem(str(nutrition['calories'])))
                self.ui.nutritionTable.setItem(0, 1, QTableWidgetItem(str(nutrition['carbs'])))
                self.ui.nutritionTable.setItem(0, 2, QTableWidgetItem(str(nutrition['fat'])))
                self.ui.nutritionTable.setItem(0, 3, QTableWidgetItem(str(nutrition['protein'])))
                recipe_tags = RecipeOperations.get_recipe_tags(self.database_manager.connection, self.current_rec_id)
                self.custom_tag_operations.display_tags_as_text(self.ui.tagsListWidget_2, recipe_tags)
            else:
                logging.error(f"No recipe found with ID: {self.current_rec_id}")
        except Exception as error:
            logging.error(f"Error populating finish recipe info page: {error}")

    def handle_edit_recipe_button(self):
        logging.debug("Edit Recipe button clicked")
        if self.current_rec_id is None:
            logging.warning("No recipe selected to edit.")
            QMessageBox.warning(self, "Error", "No recipe selected to edit.")
            return
        logging.debug(f"Editing recipe with ID: {self.current_rec_id}")
        self.edit_recipe(self.current_rec_id)

    def edit_recipe(self, rec_id):
        try:
            logging.info(f"Entering edit_recipe function for recipe ID: {rec_id}")
            recipe = RecipeOperations.get_recipe_info(self.database_manager.connection, rec_id)
            if recipe is None:
                logging.warning(f"No recipe found with ID: {rec_id}")
                QMessageBox.warning(self, "Error", f"No recipe found with ID: {rec_id}")
                return

            logging.debug(f"Retrieved recipe details: {recipe}")

            # Populate fields for editing
            self.ui.recipeNamefield.setText(recipe['name'])
            self.ui.servingSizeLine.setText(str(recipe['servings']))
            self.ui.notesTextEdit.setPlainText(recipe['notes'])

            # Log the state of important UI elements
            logging.debug(f"Recipe name field text: {self.ui.recipeNamefield.text()}")
            logging.debug(f"Serving size line text: {self.ui.servingSizeLine.text()}")
            logging.debug(f"Notes text edit content: {self.ui.notesTextEdit.toPlainText()}")

            # Fetch and populate ingredients
            self.current_recipe_foods.clear()
            ingredients = RecipeOperations.get_recipe_foods(self.database_manager.connection, rec_id)
            logging.debug(f"Ingredients fetched: {ingredients}")
            self.current_recipe_foods = ingredients

            # Switch to the addFoodsToRecipePage
            logging.debug("Switching to addFoodsToRecipePage")
            self.ui.stackedWidget.setCurrentWidget(self.ui.addFoodsToRecipePage)

            # Check if the table has been updated already
            if self.ui.recipeIngredientsTable.rowCount() == 0:
                self.update_recipe_ingredients_table()

            logging.debug("Recipe ingredients table refreshed with {self.ui.recipeIngredientsTable.rowCount()} items")

            # Populate tags for editing
            self.custom_tag_operations.populate_tags_list(self.ui.tagsListWidget, self.database_manager.connection)
            recipe_tags = RecipeOperations.get_recipe_tags(self.database_manager.connection, rec_id)
            self.set_recipe_tags(recipe_tags)

            # Enable the existing functionality on addFoodsToRecipePage
            self.ui.newRecipeNameLabel.setVisible(True)
            self.ui.addFoodsButton.setVisible(True)
            self.ui.addFoodsButton.setEnabled(True)
            self.ui.newRecipeNameLabel.setText(f"Editing: {recipe['name']}")

            logging.debug(f"New recipe name label visible: {self.ui.newRecipeNameLabel.isVisible()}")
            logging.debug(f"New recipe name label text: {self.ui.newRecipeNameLabel.text()}")
            logging.debug(f"Add foods button visible: {self.ui.addFoodsButton.isVisible()}")
            logging.debug(f"Add foods button enabled: {self.ui.addFoodsButton.isEnabled()}")

            # Log the state after UI update
            logging.debug(f"Current stacked widget index after switch: {self.ui.stackedWidget.currentIndex()}")
            logging.debug(f"Current widget after update: {self.ui.stackedWidget.currentWidget().objectName()}")
            logging.debug(f"Recipe name field text after update: {self.ui.recipeNamefield.text()}")
            logging.debug(f"Serving size line text after update: {self.ui.servingSizeLine.text()}")
            logging.debug(f"Notes text edit content after update: {self.ui.notesTextEdit.toPlainText()}")
            logging.debug(f"Ingredients table row count after update: {self.ui.recipeIngredientsTable.rowCount()}")

            logging.info("Edit recipe page populated successfully")

        except Exception as error:
            logging.error(f"Error editing recipe: {error}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while editing the recipe: {str(error)}")

    def save_and_show_recipe(self):
        try:
            logging.info("Starting save_and_show_recipe")
            # Get values from UI
            new_servings_text = self.ui.noOfServingsLine.text().strip()
            new_servings = int(new_servings_text) if new_servings_text else 1
            new_protein_id = self.ui.proteinComboBox.currentData()
            new_recipe_notes = self.ui.notesTextEdit.toPlainText()

            logging.debug(f"New servings: {new_servings}, New protein ID: {new_protein_id}")
            logging.debug(f"Current recipe ID: {self.current_rec_id}")

            # Update the recipe
            success = RecipeOperations.update_recipe(
                self.database_manager.connection,
                self.current_rec_id,
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
                logging.debug(f"Populating recipe page for recipe ID: {self.current_rec_id}")
                self.populate_recipe_page(self.current_rec_id)

                # Navigate to the recipe page
                logging.debug(f"Current stacked widget index before switch: {self.ui.stackedWidget.currentIndex()}")
                self.ui.stackedWidget.setCurrentIndex(2)
                logging.debug(f"Current stacked widget index after switch: {self.ui.stackedWidget.currentIndex()}")

                # Ensure all UI elements are updated
                self.ui.ingredientsTable.update()
                self.ui.stepsTable.update()
                self.ui.nutritionTable.update()
                self.ui.tagsListWidget_2.update()
                QtWidgets.QApplication.processEvents()

            else:
                logging.warning("Failed to save recipe")
                QMessageBox.warning(self, "Error", "Failed to save recipe. Please try again.")

        except ValueError as ve:
            logging.error(f"Invalid input: {ve}")
            QMessageBox.warning(self, "Invalid Input", f"Please enter a valid number for servings: {ve}")
        except Exception as error:
            logging.error(f"Error saving and showing recipe: {error}")
            QMessageBox.critical(self, "Error", f"An error occurred while saving and showing the recipe: {str(error)}")

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
                self.current_rec_id = rec_id
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

    # Tag Functions
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
        if self.current_rec_id is None:
            logging.error("No current recipe selected")
            QMessageBox.warning(self, "Error", "No recipe selected.  Please select a recipe first.")
            return

        # Call the database operation from CustomTagOperations
        success = self.custom_tag_operations.add_tag_to_recipe(
            self.database_manager.connection,
            self.current_rec_id,
            tag_id
        )

        if success:
            logging.debug(f"Tag added to recipe successfully")
            self.update_recipe_tags_display()
        else:
            QMessageBox.warning(self, "Error", "Failed to add tag to the recipe")

    def update_recipe_tags_display(self):
        tags = RecipeOperations.get_recipe_tags(self.database_manager.connection, self.current_rec_id)

        self.ui.tagsTableWidget.setRowCount(0)

        for tag in tags:
            row_position = self.ui.tagsTableWidget.rowCount()
            self.ui.tagsTableWidget.insertRow(row_position)

            tag_name_item = QTableWidgetItem(tag['TagName'])
            self.ui.tagsTableWidget.setItem(row_position, 0, tag_name_item)

            remove_button = QPushButton("Remove")
            remove_button.setStyleSheet("background-color: rgb(139, 196, 190);")
            remove_button.clicked.connect(lambda _, t_id=tag['TagId']: self.remove_tag_from_recipe(t_id))
            self.ui.tagsTableWidget.setCellWidget(row_position, 1, remove_button)

        self.set_recipe_tags(tags)

    def set_recipe_tags(self, recipe_tags):
        logging.debug(f"Setting recipe tags: {recipe_tags}")
        for i in range(self.ui.tagsListWidget.count()):
            item = self.ui.tagsListWidget.item(i)
            tag_id = item.data(QtCore.Qt.UserRole)
            if any(tag['TagId'] == tag_id for tag in recipe_tags):
                item.setCheckState(QtCore.Qt.Checked)
                logging.debug(f"Checked tag: {item.text()} (ID: {tag_id}")
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
        logging.debug(f"Tags set on tagsListWidget")

        # Force UI update
        self.ui.tagsListWidget.update()
        QtWidgets.QApplication.processEvents()

    def remove_tag_from_recipe(self, tag_id):
        if not hasattr(self, 'current_rec_id'):
            logging.error("No current recipe ID found when trying to remove the tag")
            QMessageBox.warning(self, "Error", "No active recipe found.  Please select a recipe first.")
            return

        success = self.custom_tag_operations.remove_tag_from_recipe(
            self.database_manager.connection,
            self.current_rec_id,
            tag_id
        )

        if success:
            logging.info(f"Tag {tag_id} removed from recipe {self.current_rec_id}")
            self.update_recipe_tags_display()
        else:
            QMessageBox.warning(self, "Error", "Failed to remove tag from recipe")

    def save_recipe_tags(self):
        if not self.current_rec_id:
            logging.error("No current recipe ID found when trying to save tags")
            QMessageBox.warning(self, "Error", "No active recipe found.  Please create a recipe first.")
            return

        selected_tags = self.get_selected_tags()
        tag_ids = [tag_id for tag_id, _ in selected_tags]

        success = self.custom_tag_operations.save_recipe_tags(
            self.database_manager.connection,
            self.current_rec_id,
            tag_ids
        )

        if success:
            logging.info(f"Tags saved for recipe {self.current_rec_id}")
            self.update_recipe_tags_display()
        else:
            QMessageBox.warning(self, "Error", "Failed to save recipe tags")

    def get_selected_tags(self):
        selected_tags = []
        for index in range(self.ui.tagsListWidget.count()):
            item = self.ui.tagsListWidget.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                tag_id = item.data(QtCore.Qt.UserRole)
                tag_name = item.text()
                selected_tags.append((tag_id, tag_name))
        return selected_tags

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
                QMessageBox.warning(self, "Error", f"Error updating tag: {str(error)}")

    def check_tag_associations(self, tag_id):
        try:
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT RecipeId FROM RecipeTags WHERE TagId = ?", (tag_id,))
            associated_recipes = cursor.fetchall()
            return [recipe[0] for recipe in associated_recipes]
        except Exception as error:
            logging.error(f"Error checking tag associations: {error}")
            return []

    def remove_tag(self, tag_id):
        try:
            associated_recipes = self.check_tag_associations(tag_id)

            if associated_recipes:
                dialog = TagRemovalDialog(self, len(associated_recipes))
                result = dialog.exec_()

                if result == 1:  # View associated recipes
                    self.view_associated_recipes(associated_recipes)
                    return
                elif result == 2:  # Delete tag and remove associations
                    confirm = QMessageBox.question(self, "Confirm Deletion",
                                                   "Are you sure you want to delete this tag and remove it from all associated recipes?",
                                                   QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.No:
                        return
                else:  # Cancel
                    return
            else:
                confirm = QMessageBox.question(self, "Confirm Removal",
                                               "Are you sure you want to remove this tag?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.No:
                    return

            # Proceed with tag deletion
            self.custom_tag_operations.delete_tag(self.database_manager.connection, tag_id)
            logging.info(f"Tag removed successfully.")
            self.populate_tags_table()
            QMessageBox.information(self, "Success", "Tag removed successfully.")
        except PyodbcError as db_error:
            logging.error(f"Database error while removing tag: {db_error}")
            QMessageBox.warning(self, "Error", f"Failed to remove tag due to a database error. Please try again.")

        except Exception as error:
            logging.error(f"Error removing tag: {error}")
            QMessageBox.warning(self, "Error", f"Error removing tag: {str(error)}")

        except Exception as error:
            logging.error(f"Error removing tag: {error}")
            QMessageBox.warning(self, "Error", f"Error removing tag: {str(error)}")

        except Exception as error:
            logging.error(f"Error removing tag: {error}")
            QMessageBox.warning(self, "Error", f"Error removing tag: {str(error)}")

    def view_associated_recipes(self, recipe_ids):
        try:
            # Fetch recipe details
            cursor = self.database_manager.connection.cursor()
            placeholders = ','.join('?' * len(recipe_ids))
            query = f"SELECT RecId, RecName FROM Recipes WHERE RecId IN ({placeholders})"
            cursor.execute(query, recipe_ids)
            results = cursor.fetchall()

            # Navigate to findArecipePage
            self.ui.stackedWidget.setCurrentWidget(self.ui.findArecipePage)

            # Display results in the resultsTable
            self.display_recipe_search_results(results)

        except Exception as error:
            logging.error(f"Error viewing associated recipes: {error}")
            QMessageBox.warning(self, "Error", f"Error viewing associated recipes: {str(error)}")

    def find_current_tag_name(self, tag_id):
        cursor = self.database_manager.connection.cursor()
        cursor.execute("SELECT TagName FROM CustomTags WHERE TagId = ?", (tag_id,))
        result = cursor.fetchone()
        return result[0] if result else ""

    def set_checked_tags_for_current_recipe(self):
        logging.debug("Setting checked tags for current recipes.")
        if self.current_rec_id:
            recipe_tags = RecipeOperations.get_recipe_tags(self.database_manager.connection, self.current_rec_id)
            logging.debug(f"Recipe tags: {recipe_tags}")
            self.set_recipe_tags(recipe_tags)
        else:
            logging.error("No current recipe ID found when trying to set checked tags")
            QMessageBox.warning(self, "Error", "No active recipe found.  PLease create a recipe first.")

    # Food Functions
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
            self.ui.recipeIngredientsList.setColumnCount(4)

            header = self.ui.recipeIngredientsList.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)  # Ingredient name column
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Amount column
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Unit column
            header.setSectionResizeMode(3, QHeaderView.Fixed)  # Button column
            self.ui.recipeIngredientsList.setColumnWidth(3, 100)  # Set the fixed width for the last column

            for food in foods:
                row = self.ui.recipeIngredientsList.rowCount()
                self.ui.recipeIngredientsList.insertRow(row)
                self.ui.recipeIngredientsList.setItem(row, 0, QTableWidgetItem(food.name))
                self.ui.recipeIngredientsList.setItem(row, 1, QTableWidgetItem(str(food.no_serve)))
                self.ui.recipeIngredientsList.setItem(row, 2, QTableWidgetItem(food.serv_size))

                add_button = QPushButton("Add to Recipe")
                add_button.setStyleSheet("background-color: rgb(139, 196, 190);")
                add_button.clicked.connect(lambda _, f=food: self.add_food_to_recipe(f))
                self.ui.recipeIngredientsList.setCellWidget(row, 3, add_button)

            self.ui.recipeIngredientsList.resizeColumnsToContents()

            self.ui.recipeIngredientsList.resizeColumnsToContents()
            logging.info("Matching foods list populated successfully.")
        except Exception as error:
            logging.error(f"Error populating matching foods list: {error}")
            QMessageBox.warning(self, "Error", f"Failed to laod matching foods: {str(error)}")

    def select_food(self, food_id):
        self.selected_food_id = food_id
        self.ui.numberOfServingsInput.setEnabled(True)
        self.ui.servingSizeInput.setEnabled(True)
        self.ui.newFoodAddButton.setEnabled(True)

    def add_food_to_recipe(self, food):
        try:
            # Convert food to a dictionary
            if not isinstance(food, dict):
                food = {
                    'food_id': food.food_id,
                    'name': food.name,
                    'no_serve': food.no_serve,
                    'serv_size': food.serv_size,
                    'calories': food.calories,
                    'carbs': food.carbs,
                    'fat': food.fat,
                    'protein': food.protein
                }

                logging.debug(f"Current recipe foods before adding: {self.current_recipe_foods}")

                existing_food = next((f for f in self.current_recipe_foods if f['food_id'] == food['food_id']), None)
                if existing_food:
                    logging.debug(f"Food with ID {food['food_id']} already exists in the recipe.")
                    return

                # Add to database
                success = RecipeOperations.add_food_to_recipe(
                    self.database_manager.connection,
                    self.current_rec_id,
                    food['food_id'],
                    food['no_serve'],
                    food['serv_size']
                )

                if success:
                    logging.info(f"Food '{food['name']}' added to recipe successfully.")
                    QMessageBox.information(self, "Success", f"'{food['name']}' added to the recipe.")
                    self.current_recipe_foods.append(food)
                    self.refresh_recipe_ingredients_table()

                    # Clear the search field and the ingredients list after adding the item
                    self.ui.findIngredientSearch.clear()
                    self.ui.recipeIngredientsList.setRowCount(0)
                    self.ui.recipeIngredientsList.clearContents()

                    # self.ui.recipeIngredientsList.clear()
                    logging.debug(
                        "Cleared findIngredientSearch field and recipeIngredientsList after adding food to recipe.")
                else:
                    raise Exception("Failed to add food to recipe in database.")

                logging.debug(f"Current recipe foods after adding: {self.current_recipe_foods}")

        except Exception as error:
            logging.error(f"Error adding food to recipe: {error}")
            QMessageBox.warning(self, "Error", f"Failed to add food to recipe: {str(error)}")

    def edit_recipe_food(self, rec_food_id):
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
                        RecipeOperations.update_recipe_food(self.database_manager.connection, rec_food_id,
                                                            new_no_serve,
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

    def remove_food_from_recipe(self, food_id):
        try:
            logging.debug(f"Attempting to remove food with ID: {food_id} from recipe")

            # Update the current_recipe_foods list by removing the selected food
            self.current_recipe_foods = [food for food in self.current_recipe_foods if food['food_id'] != food_id]
            logging.debug(f"Current recipe foods after removal: {self.current_recipe_foods}")

            # Remove from the database
            success = RecipeOperations.remove_food_from_recipe(self.database_manager.connection,
                                                                self.current_rec_id, food_id)
            if success:
                logging.info(f"Food with ID {food_id} removed from recipe successfully.")
                QMessageBox.information(self, "Success", f"Food removed from the recipe.")
                # Refresh the ingredients table with the updated list
                self.update_recipe_ingredients_table()
            else:
                raise Exception("Failed to remove food from recipe in database.")
        except Exception as error:
            logging.error(f"Error removing food from recipe: {error}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to remove food: {str(error)}")
            raise

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

                # Ensure the newly added food is displayed
                self.search_foods()
                self.update_recipe_ingredients_table()
            else:
                QMessageBox.warning(self, "Error", "Failed to add food item.")
        except Exception as error:
            logging.error(f"Error saving new food: {error}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(error)}")

    def save_food_and_return_to_manage(self):
        self.save_food_item()
        self.ui.stackedWidget.setCurrentIndex(8)

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
        try:
            # Check for associated recipes
            associated_recipes = FoodOperations.check_food_associations(self.database_manager.connection, food_id)

            if associated_recipes:
                dialog = FoodRemovalDialog(self, len(associated_recipes))
                result = dialog.exec_()

                if result == QDialog.Accepted:  # View associated recipes
                    self.view_associated_recipes(associated_recipes)
                    return
                else:  # Cancel
                    return
            else:
                confirm = QMessageBox.question(self, "Confirm Removal",
                                               "Are you sure you want to remove this food item?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.No:
                    return

            # Proceed with food deletion only if there are no associated recipes
            FoodOperations.delete_food_item(self.database_manager.connection, food_id)
            logging.info(f"Food item with ID {food_id} removed successfully.")
            self.populate_foods_table()
            QMessageBox.information(self, "Success", "Food item removed successfully.")
        except Exception as error:
            logging.error(f"Error removing food item: {error}")
            QMessageBox.warning(self, "Error", f"Failed to remove food item: {str(error)}")

    def view_associated_recipes(self, recipe_ids):
        try:
            # Fetch recipe details
            results = RecipeOperations.get_recipes_by_ids(self.database_manager.connection, recipe_ids)

            # Navigate to findArecipePage
            self.ui.stackedWidget.setCurrentWidget(self.ui.findArecipePage)

            # Display results in the resultsTable
            self.display_recipe_search_results(results)

        except Exception as error:
            logging.error(f"Error viewing associated recipes: {error}")
            QMessageBox.warning(self, "Error", f"Error viewing associated recipes: {str(error)}")

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

    def add_new_food_item(self):
        logging.debug("Attempting to add new food item")
        food_name = self.ui.foodNameLineEdit.text().strip()
        no_serve = self.ui.quantityDoubleSpinBox.value()
        serv_size = self.ui.sizeComboBox.currentText()
        calories = int(self.ui.caloriesLineEdit.text())
        carbs = float(self.ui.carbsLineEdit.text())
        fat = float(self.ui.fatLineEdit.text())
        protein = float(self.ui.proteinLineEdit.text())

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
                       JOIN Nutrition ON Foods.FoodId = Nutrition.FoodId
                       ORDER BY CAST(Foods.FoodName AS NVARCHAR(MAX)) ASC"""
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
            QMessageBox.warning(self, "Error", f"Failed to load foods: {str(error)}")

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

    def search_and_populate_food_item(self):
        search_term = self.ui.findIngredientSearch.text().strip()
        if search_term:
            food = self.search_foods(search_term)
            self.populate_foods_list(food)
        else:
            QMessageBox.warning(self, "Error", "Please enter a search term.")

    def save_new_food(self):
        try:
            food_name = self.ui.foodNameLine.text().strip()
            no_serve = self.ui.quantityDoubleSpinBox.value()
            serv_size = self.ui.sizeComboBox.currentText()
            calories = int(self.ui.caloriesLineEdit.text())
            carbs = float(self.ui.carbsLineEdit.text())
            fat = float(self.ui.fatLine.text())
            protein = float(self.ui.proteinLineEdit.text())

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

    # Search and Display Functions
    def search_recipes(self):
        category_index = self.ui.searchCategoryComboBox.currentIndex()
        logging.debug(f"Selected category index: {category_index}")

        try:
            if category_index == 1: # Custom Tags
                search_text = self.ui.customTagsComboBox.currentText()
            elif category_index == 0: # Calorie Range
                min_cal = int(self.ui.minCalLineEdit.text())
                max_cal = int(self.ui.maxCalLineEdit.text())
                if min_cal > max_cal:
                    raise ValueError("Minimum calorie value should be less than or equal to maxiumum calorie value.")
                search_text = f"{min_cal}-{max_cal}"
            elif category_index == 2: # Macros
                carbs = self.ui.carbsLineEdit.text() or '0'
                protein = self.ui.proteinLineEdit.text() or '0'
                fat = self.ui.fatLineEdit.text() or '0'
                if carbs == '0' and protein == '0' and fat == '0':
                    raise ValueError("At least one macronutrient value must be provided.")
                search_text = f"{carbs},{protein},{fat}"
            elif category_index == 3:  # Protein Type
                protein_type = self.ui.proteinTypeComboBox.currentData()
                if protein_type is None:
                    raise ValueError("Please select a protein type.")
                search_text = str(protein_type)
            else:
                search_text = self.ui.searchCriteriaLineEdit.text() if self.ui.searchCriteriaLineEdit.isVisible() else ""

            logging.debug(f"Searching recipes with category: {category_index}, search_text: {search_text}")

            results = RecipeOperations.search_recipes(self.database_manager.connection, category_index, search_text)

            if not results:
                QMessageBox.information(self, "No Results", "No recipes found matching your criteria.")
            else:
                logging.info(f"Found {len(results)} recipes matching the criteria")
                self.display_recipe_search_results(results)
        except ValueError as error:
            QMessageBox.warning(self, "Invalid Input", str(error))
        except Exception as error:
            logging.error(f"Error performing recipe search: {error}", exc_info=True)
            QMessageBox.warning(self, "Error", f"An error occurred while searching for recipes: {str(error)}")

    def display_recipe_search_results(self, results):
        logging.debug(f"Entering display_recipe_search_results with {len(results)} results")
        self.ui.resultsTable.setRowCount(0)
        self.ui.resultsTable.setColumnCount(2)
        self.ui.resultsTable.setHorizontalHeaderLabels(["Recipe Name", ""])

        # Hide vertical header (row numbers)
        self.ui.resultsTable.verticalHeader().setVisible(False)

        # Set up column sizes
        header = self.ui.resultsTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        logging.debug("Column sizes set: First column stretches, second column resizes to contents")

        button_style = """
            background-color: rgb(139, 196, 190);
            color: black;
            border: none;
            padding: 5px;
            margin: 5px;
        """

        for row, result in enumerate(results):
            try:
                if len(result) == 2:
                    rec_id, rec_name = result
                    logging.debug(f"Adding row {row}: Recipe ID {rec_id}, Name {rec_name}")
                    self.ui.resultsTable.insertRow(row)
                    self.ui.resultsTable.setItem(row, 0, QTableWidgetItem(rec_name))

                    select_button = QPushButton("Select")
                    select_button.setStyleSheet(button_style)
                    select_button.clicked.connect(lambda _, rid=rec_id: self.load_and_display_recipe(rid))

                    # Create a layout to add padding around the button
                    button_layout = QtWidgets.QHBoxLayout()
                    button_layout.setContentsMargins(.5, .5, 1, .5)
                    button_layout.addWidget(select_button)

                    # Create a QWidget to contain the layout
                    container_widget = QtWidgets.QWidget()
                    container_widget.setLayout(button_layout)

                    self.ui.resultsTable.setCellWidget(row, 1, container_widget)
                else:
                    raise ValueError(f"Unexpected result format: {result}")
            except ValueError as error:
                logging.error(f"Error unpacking result at row {row}: {error}")
                self.ui.resultsTable.insertRow(row)
                self.ui.resultsTable.setItem(row, 0, QTableWidgetItem("Error: Invalid Data"))

        # Prevent horizontal scrollbar from appearing
        self.ui.resultsTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.ui.resultsTable.update()
        QtWidgets.QApplication.processEvents()
        logging.debug(f"Final table has {self.ui.resultsTable.rowCount()} rows")

        logging.info("Recipe search results displayed successfully.")

    def on_recipe_category_changed(self, index):
        logging.debug(f"Search category changed to index {index}")
        # Hide all fields initially
        self.ui.minCalLineEdit.hide()
        self.ui.maxCalLineEdit.hide()
        self.ui.caloriesLabel_2.hide()
        self.ui.calsFromLabel.hide()
        self.ui.calsToLabel.hide()
        self.ui.macrosLabel.hide()
        self.ui.carbsLabel_2.hide()
        self.ui.proteinLabel_2.hide()
        self.ui.fatLabel_2.hide()
        self.ui.carbsLineEdit.hide()
        self.ui.proteinLineEdit.hide()
        self.ui.fatLineEdit.hide()
        self.ui.proteinTypeLabel_2.hide()
        self.ui.proteinTypeComboBox.hide()
        self.ui.recipeNameLabel_2.hide()
        self.ui.searchCriteriaLineEdit.hide()
        self.ui.customTagsLabel.hide()
        self.ui.customTagsComboBox.hide()

        # Show appropriate input fields based on selected category index
        if index == 0:  # Calorie Range
            self.ui.minCalLineEdit.show()
            self.ui.maxCalLineEdit.show()
            self.ui.caloriesLabel_2.show()
            self.ui.calsFromLabel.show()
            self.ui.calsToLabel.show()
        elif index == 1: # Custom Tags
            self.ui.customTagsLabel.show()
            self.ui.customTagsComboBox.show()
        elif index == 2:  # Macros
            self.ui.macrosLabel.show()
            self.ui.carbsLabel_2.show()
            self.ui.proteinLabel_2.show()
            self.ui.fatLabel_2.show()
            self.ui.carbsLineEdit.show()
            self.ui.proteinLineEdit.show()
            self.ui.fatLineEdit.show()
        elif index == 3:  # Protein Type
            self.ui.proteinTypeLabel_2.show()
            self.ui.proteinTypeComboBox.show()
        elif index == 4:  # Recipe Name
            self.ui.recipeNameLabel_2.show()
            self.ui.searchCriteriaLineEdit.show()
        elif index == 6:  # Custom Tags
            self.ui.searchCriteriaLineEdit.show()

        logging.debug("UI updated based on selected search category.")

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
        self.ui.foodsTable.setRowCount(0)
        for row, food in enumerate(foods):
            self.ui.foodsTable.insertRow(row)
            self.ui.foodsTable.setItem(row, 0, QTableWidgetItem(food.name))
            select_button = QPushButton("Select")
            select_button.clicked.connect(lambda checked, food=food: self.handle_food_selection(food))
            self.ui.foodsTable.setCellWidget(row, 1, select_button)
        logging.info("Foods list table updated successfully.")

    def on_recipe_search_clicked(self):
        category = self.ui.searchCategoryComboBox.currentText()
        search_text = self.ui.receipSearchLineEdit.text() if self.ui.recipeSearchLineEdit.isVisible() else ""

        try:
            results = self.serach_recipes(category, search_text)
            if results:
                self.display_recipe_search_results(results)
            else:
                QMessageBox.information(self, "No Results", "No recipes found matching your criteria.")
        except Exception as error:
            logging.error(f"Error performing recipe search: {error}")
            QMessageBox.warning(self, "Error", f"An error occurred while searching for recipes: {str(error)}")

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

    # Helper and Utility Functions
    def clear_food_input_fields(self):
        self.ui.foodNameLine.clear()
        self.ui.quantityDoubleSpinBox.setValue(0)
        self.ui.sizeComboBox.setCurrentIndex(0)
        self.ui.caloriesLineEdit.clear()
        self.ui.carbsLine.clear()
        self.ui.fatLine.clear()
        self.ui.proteinLine.clear()

    def clear_search_fields_and_hide_widgets(self):
        logging.debug("Clearing search fields and hiding widgets.")

        # Clear search criteria line edit
        self.ui.searchCriteriaLineEdit.clear()
        self.ui.calsFromLabel.hide()
        self.ui.calsToLabel.hide()
        self.ui.caloriesLabel_2.hide()
        self.ui.macrosLabel.hide()
        self.ui.carbsLabel_2.hide()
        self.ui.proteinLabel_2.hide()
        self.ui.fatLabel_2.hide()
        self.ui.carbsLineEdit.hide()
        self.ui.proteinLineEdit.hide()
        self.ui.fatLineEdit.hide()
        self.ui.proteinTypeLabel_2.hide()
        self.ui.proteinTypeComboBox.hide()
        self.ui.minCalLineEdit.hide()
        self.ui.maxCalLineEdit.hide()
        self.ui.recipeNameLabel_2.hide()
        self.ui.searchCriteriaLineEdit.hide()
        self.ui.searchCategoryComboBox.setCurrentIndex(4)
        self.ui.recipeNameLabel_2.show()
        self.ui.searchCriteriaLineEdit.show()
        logging.info("Search fields cleared and widgets hidden.")

    def clear_results_table(self):
        self.ui.resultsTable.setRowCount(0)
        self.ui.resultsTable.clearContents()
        logging.debug("Results table cleared.")

    def handle_food_selection(self, food):
        logging.debug(f"Food selected: {food.FoodName}")
        self.selected_food = food
        self.ui.numberOfServingsInput.show()
        self.ui.servingSizeInput.show()
        self.ui.newFoodAddButton.show()

    def on_stacked_widget_changed(self, index):
        if index == 5:
            self.populate_tags_table()
        elif index == 4:
            self.refresh_recipe_ingredients_table()

    def refresh_recipe_ingredients_table(self):
        try:
            logging.debug("Refreshing recipe ingredients table")

            # Fetch the latest ingredients from the database
            ingredients = RecipeOperations.get_recipe_foods(self.database_manager.connection, self.current_rec_id)
            logging.debug(f"Fetched {len(ingredients)} ingredients for recipe {self.current_rec_id}")

            self.current_recipe_foods.clear()
            self.current_recipe_foods.extend(ingredients)
            self.ui.recipeIngredientsTable.setRowCount(0)

            # Update the ingredients table
            for index, food in enumerate(self.current_recipe_foods):
                logging.debug(f"Inserting food at row {index}: {food['name']}")
                self.ui.recipeIngredientsTable.insertRow(index)

                # Set the food name
                self.ui.recipeIngredientsTable.setItem(index, 0, QTableWidgetItem(food['name']))

                # Set the number of servings
                self.ui.recipeIngredientsTable.setItem(index, 1, QTableWidgetItem(str(food['no_serve'])))

                # Set the serving size
                self.ui.recipeIngredientsTable.setItem(index, 2, QTableWidgetItem(food['serv_size']))

                # Set the calories
                self.ui.recipeIngredientsTable.setItem(index, 3, QTableWidgetItem(str(food['calories'])))

                # Set the carbohydrates
                self.ui.recipeIngredientsTable.setItem(index, 4, QTableWidgetItem(str(food['carbs'])))

                # Set the fat
                self.ui.recipeIngredientsTable.setItem(index, 5, QTableWidgetItem(str(food['fat'])))

                # Set the protein
                self.ui.recipeIngredientsTable.setItem(index, 6, QTableWidgetItem(str(food['protein'])))

                # Add a Remove button
                remove_button = QPushButton("Remove")
                remove_button.setStyleSheet("background-color: rgb(139, 196, 190);")
                remove_button.clicked.connect(lambda _, f_id=food['food_id']: self.remove_food_from_recipe(f_id))

                self.ui.recipeIngredientsTable.setCellWidget(index, 7, remove_button)

            logging.info(f"Recipe ingredients table refreshed with {len(ingredients)} items")
        except Exception as error:
            logging.error(f"Error refreshing recipe ingredients table: {error}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to refresh ingredients table: {str(error)}")

    def check_tags_list_visibility(self):
        if hasattr(self.ui, 'tagsListWidget'):
            logging.debug(f"tagsListWidget visibility: {self.ui.tagsListWidget.isVisible()}")
            logging.debug(f"tagsListWidget parent visibility: {self.ui.tagsListWidget.parent().isVisible()}")
            logging.debug(f"tagsListWidget item count: {self.ui.tagsListWidget.count()}")
        else:
            logging.error("tagsListWidget not found in UI")

    # Data Population Functions
    def populate_recipe_search_categories(self):
        logging.debug("Populating search categories.")
        try:
            cursor = self.database_manager.connection.cursor()
            logging.debug("Executing query to fetch categories")
            query = "SELECT CategoryId, CategoryName FROM SearchCategories ORDER BY CategoryName"
            cursor.execute(query)
            categories = cursor.fetchall()
            logging.debug(f"Fetched categories: {categories}")

            self.ui.searchCategoryComboBox.blockSignals(True)
            logging.debug("Clearing ComboBox items")
            self.ui.searchCategoryComboBox.clear()

            for category_id, category_name in categories:
                logging.debug(f"Adding category: {category_name} with ID: {category_id}")
                self.ui.searchCategoryComboBox.addItem(category_name, category_id)

            self.ui.searchCategoryComboBox.blockSignals(False)
            logging.info("Search categories populated successfully.")
        except Exception as error:
            logging.error(f"Error populating search categories: {error}")
            QMessageBox.warning(self, "Database Error", f"Error loading search categories: {str(error)}")
        finally:
            logging.debug("Exiting populate_recipe_search_categories")

    def populate_foods_list(self, foods):
        self.ui.FoodsList.setRowCount(0)
        self.ui.FoodsList.setColumnCount(4)

        recipe_foods = RecipeOperations.get_recipe_foods(self.database_manager.connection, self.current_rec_id)

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

    def populate_custom_tags_combo_box(self):
        try:
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT TagId, TagName FROM CustomTags ORDER BY TagName")
            tags = cursor.fetchall()

            self.ui.customTagsComboBox.clear()
            self.ui.customTagsComboBox.addItem("Select Tag", None)
            for tag_id, tag_name in tags:
                self.ui.customTagsComboBox.addItem(tag_name, tag_id)

            logging.info("Custom tags combo box populated successfully.")
        except Exception as error:
            logging.error(f"Error populating custom tags combo box: {error}")
            QMessageBox.warning(self, "Error", f"Failed to laod custom tags: {str(error)}")

    def populate_recipe_steps_table(self):
        try:
            if not self.current_rec_id:
                logging.warning("No current recipe ID found when trying to populate steps table")
                return

            steps = RecipeOperations.get_recipe_steps(self.database_manager.connection, self.current_rec_id)
            self.ui.recipeStepsTable.setRowCount(0)
            for row, step in enumerate(steps):
                self.insert_step(step['description'], row)

            # Resize rows to fit contents
            self.ui.recipeStepsTable.resizeRowsToContents()

            logging.info(f"Populated steps table with {len(steps)} steps")
        except Exception as error:
            logging.error(f"Error populating recipe steps table: {error}")
            QMessageBox.warning(self, "Error", f"Failed to load recipe steps: {str(error)}")

    def populate_protein_combo_box(self):
        logging.debug("Populating protein combo box")
        try:
            proteins = ProteinOperations.get_protein_names(self.database_manager.connection)
            logging.debug(f"Fetched proteins {proteins}")
            self.ui.proteinComboBox.clear()
            self.ui.proteinComboBox.addItem("Select Protein Type", None)
            for protein_id, protein_name in proteins:
                self.ui.proteinComboBox.addItem(protein_name, protein_id)
            logging.info("Protein combo box populated successfully.")
        except Exception as error:
            logging.error(f"Error populating protein combo box: {error}")
            QMessageBox.warning(self, "Error", f"Failed to load protein types: {str(error)}")

    def populate_protein_type_combo_box(self):
        try:
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT ProteinId, ProteinName FROM Proteins ORDER BY ProteinName")
            proteins = cursor.fetchall()

            self.ui.proteinTypeComboBox.clear()
            for protein_id, protein_name in proteins:
                self.ui.proteinTypeComboBox.addItem(protein_name, protein_id)

            logging.info("Protein type combo box populated successfully.")
        except Exception as error:
            logging.error(f"Error populating protein type combo box: {error}")
            QMessageBox.warning(self, "Error", f"Failed to laod protein types: {str(error)}")

    def populate_protein_types_table(self):
        try:
            protein_types = ProteinOperations.get_protein_names(self.database_manager.connection)

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

    def edit_protein_type(self, protein_id):
        current_name = ProteinOperations.get_protein_type_name(self.database_manager.connection, protein_id)
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
        try:
            associated_recipes = self.check_protein_associations(protein_id)

            if associated_recipes:
                dialog = ProteinRemovalDialog(self, len(associated_recipes))
                result = dialog.exec_()

                if result == 1:  # View associated recipes
                    self.view_associated_recipes(associated_recipes)
                    return
                elif result == 2:  # Delete protein type and remove associations
                    confirm = QMessageBox.question(self, "Confirm Deletion",
                                                   "Are you sure you want to delete this protein type and remove it from all associated recipes?",
                                                   QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.No:
                        return
                else:  # Cancel
                    return
            else:
                confirm = QMessageBox.question(self, "Confirm Removal",
                                               "Are you sure you want to remove this protein type?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.No:
                    return

            # Proceed with protein type deletion
            ProteinOperations.delete_protein(self.database_manager.connection, protein_id)
            logging.info(f"Protein type removed successfully.")
            self.populate_protein_types_table()
            QMessageBox.information(self, "Success", "Protein type removed successfully.")
        except Exception as error:
            logging.error(f"Error removing protein type: {error}")
            QMessageBox.warning(self, "Error", f"Failed to remove protein type: {str(error)}")

    def check_protein_associations(self, protein_id):
        try:
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT RecId FROM Recipes WHERE ProteinId = ?", (protein_id,))
            associated_recipes = cursor.fetchall()
            return [recipe[0] for recipe in associated_recipes]
        except Exception as error:
            logging.error(f"Error checking protein associations: {error}")
            return []

    def closeEvent(self, event):
        # Close database connection if initialized
        logging.info("Closing application and disconnection from database.")
        if hasattr(self, 'database_manager'):
            self.database_manager.close_connection()
        event.accept()