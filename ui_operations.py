# ui_operations.py
import logging

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QInputDialog, QPushButton
from UI_Files.ui_mainwindow import Ui_MainWindow
from database import DatabaseManager
from customTags_operations import CustomTagOperations
from pyodbc import Error as PyodbcError

logging.basicConfig(level=logging.DEBUG)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize the UI and home page
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentIndex(0)
        # Initialize database manager
        self.database_manager = DatabaseManager()
        self.database_manager.connect_to_database()
        self.connect_buttons()
        # Initialize methods
        self.ui.submitButton.clicked.connect(self.handle_recipe_name_submission)
        self.ui.searchButton.clicked.connect(self.search_and_populate_foods_list)
        self.ui.newFoodAddButton.clicked.connect(self.add_selected_food_to_recipe)
        self.ui.addNewTagButton.clicked.connect(self.add_new_tag)
        # Create actions for menu items
        self.home_action = QtWidgets.QAction("Home", self)
        # Connect actions to their methods
        self.home_action.triggered.connect(self.navigate_to_home_page)
        # Add actions to the menu items
        self.ui.menuHome.addAction(self.home_action)
        self.ui.actionCustom_Tags.triggered.connect(self.on_action_custom_tags_triggered)

        # self.populate_foods_table()
        self.custom_tag_operations = CustomTagOperations()
        self.editing_tag = False

        # Populate tags table
        self.populate_tags_table()

    def navigate_to_home_page(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_action_custom_tags_triggered(self):
        self.ui.stackedWidget.setCurrentIndex(5)

    def connect_buttons(self):
        # Connect the buttons to their methods
        self.ui.findArecipeButton.clicked.connect(self.navigate_to_find_recipe_page)
        self.ui.returnTohomeButton.clicked.connect(self.navigate_to_home_page)
        self.ui.searchButton.clicked.connect(self.execute_recipe_search)
        self.ui.searchCategoryComboBox.currentIndexChanged.connect(self.on_search_category_changed)
        self.ui.submitArecipeButton.clicked.connect(self.navigate_to_submit_recipe_page)

    def add_new_tag(self):
        tag_name = self.ui.newTagNameLine.text().strip()
        try:
            if tag_name:
                tag_id = self.custom_tag_operations.add_tag(self.database_manager.connection, tag_name)
                if tag_id is not None:
                    logging.info(f"Tag added with id: {tag_id}")
                    # Clear existing rows in the table
                    self.ui.tagsTableWidget.clearContents()
                    self.ui.tagsTableWidget.setRowCount(0)
                    # Repopulate the tags table
                    self.populate_tags_table()
                    self.ui.newTagNameLine.clear()
                else:
                    logging.error("Failed to add tag.")
                    QMessageBox.warning(self, "Error", "Failed to add tag.")
            else:
                logging.error("Tag name cannot be empty.")
                QMessageBox.warning(self, "Error", "Please enter a tag name.")
        except Exception as error:
            logging.error(f"Error adding tag: {error}")
            QMessageBox.warning(self, "Error", f"Failed to add tag: {str(error)}")

    def add_tag_to_table(self, tag_name, tag_id):
        row_position = self.ui.tagsTableWidget.rowCount()
        self.ui.tagsTableWidget.insertRow(row_position)

        tag_item = QTableWidgetItem(tag_name)
        self.ui.tagsTableWidget.setItem(row_position, 0, tag_item)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: self.edit_tag(row_position, tag_id))
        self.ui.tagsTableWidget.setCellWidget(row_position, 1, edit_button)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_tag(row_position, tag_id))
        self.ui.tagsTableWidget.setCellWidget(row_position, 2, remove_button)

    def populate_tags_table(self):
        cursor = self.database_manager.connection.cursor()
        cursor.execute("SELECT TagId, TagName FROM CustomTags")
        tags = cursor.fetchall()
        for tag_id, tag_name in tags:
            self.add_tag_to_table(tag_name, tag_id)

    def edit_tag(self, row, tag_id):
        current_tag_name = self.ui.tagsTableWidget.item(row, 0).text()
        new_tag_name, ok = QInputDialog.getText(self, "Edit Tag", "Enter the new tag name:", text=current_tag_name)
        if ok and new_tag_name:
            self.custom_tag_operations.update_tag(self.database_manager.connection, tag_id, new_tag_name)
            self.ui.tagsTableWidget.setItem(row, 0, QTableWidgetItem(new_tag_name))

    def remove_tag(self, row, tag_id):
        confirm = QMessageBox.question(self, "Confirm Removal", "Are you sure you want to remove this tag?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.custom_tag_operations.delete_tag(self.database_manager.connection, tag_id)
            self.ui.tagsTableWidget.removeRow(row)

    def populate_search_categories(self):
        categories = self.database_manager.get_search_categories()
        self.ui.searchCategoryComboBox.addItems(categories)

    def navigate_to_find_recipe_page(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def execute_recipe_search(self):
        category = self.ui.searchCategoryComboBox.currentText()
        criteria = self.ui.searchCriteriaLineEdit.text()
        self.fetch_recipes_by_criteria(category, criteria)

    def fetch_recipes_by_criteria(self, category, criteria):
        try:
            cursor = self.database_manager.connection.cursor()
            query = ""
            if category == "Recipe Name":
                query = "SELECT * FROM Recipes WHERE RecName LIKE ?"
                cursor.execute(query, ("%" + criteria + "%",))
            elif category == "Calorie Range":
                min_cal, max_cal = map(int, criteria.split("-"))
                query = "SELECT * FROM Recipes WHERE RecCals BETWEEN ? AND ?"
                cursor.execute(query, (min_cal, max_cal))
            elif category == "Macros":
                min_protein, max_protein, min_carbs, max_carbs, min_fat, max_fat = map(int, criteria.split(','))
                query = """SELECT * FROM Recipes
                            WHERE RecProtein BETWEEN ? AND ?
                            AND RecCarbs BETWEEN ? AND ?
                            AND RecFat BETWEEN ? AND ?"""
                cursor.execute(query, (min_protein, max_protein, min_carbs, max_carbs, min_fat, max_fat))
            elif category == "Meal Type":
                query = "SELECT * FROM Recipes WHERE MealTypeId IN (SELECT MealTypeId FROM MealType WHERE MealTypeName = ?)"
                cursor.execute(query, (criteria,))
            elif category == "Protein Type":
                query = "SELECT * FROM Recipes WHERE ProteinId IN (SELECT ProteinId FROM Proteins WHERE ProteinName = ?)"
                cursor.execute(query, (criteria,))
            elif category == "Custom Tags":
                query = "SELECT * FROM Recipes WHERE TagId IN (SELECT TagId FROM CustomTags WHERE TagName = ?)"
                cursor.execute(query, (criteria,))

            results = cursor.fetchall()
            self.populate_results_table(results)
        except Exception as error:
            logging.error(f"Error while performing search: {error}")

    def populate_results_table(self, results):
        self.ui.resultsTableWidget.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.ui.resultsTableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.resultsTableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def add_new_search_category(self):
        category_name = self.ui.newCategoryLineEdit.text().strip()
        if category_name:
            self.database_manager.insert_search_category(category_name)
            self.populate_search_categories()
            QMessageBox.information(self, "Category Added", f"Category '{category_name}' added successfully.")
            self.ui.newCategoryLineEdit.clear()
        else:
            QMessageBox.warning(self, "Error", "Category name cannot be empty.")

    def on_search_category_changed(self, index):
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

    def onSearchCategoryChanged(self, index):
        self.on_search_category_changed(index)

    def navigate_to_submit_recipe_page(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.findIngredientSearch.hide()
        self.ui.searchButton.hide()
        self.ui.FoodsList.hide()
        self.ui.numberOfServingsInput.hide()
        self.ui.servingSizeInput.hide()
        self.ui.newFoodAddButton.hide()

    def search_and_populate_foods_list(self):
        food_name = self.ui.findIngredientSearch.text()
        # Call the method in food_operations.py to search for foods
        foods = self.food_operations.search_foods(self.database_manager.connection, food_name)
        self.update_foods_list_table(foods)

    def update_foods_list_table(self, foods):
        self.ui.FoodsList.setRowCount(0)
        for row, food in enumerate(foods):
            self.ui.FoodsList.insertRow(row)
            self.ui.FoodsList.setItem(row, 0, QTableWidgetItem(food.FoodName))
            select_button = QPushButton("Select")
            select_button.clicked.connect(lambda checked, food=food: self.handle_food_selection(food))
            self.ui.FoodsList.setCellWidget(row, 1, select_button)

    def handle_food_selection(self, food):
        self.selected_food = food
        self.ui.numberOfServingsInput.show()
        self.ui.servingSizeInput.show()
        self.ui.newFoodAddButton.show()

    def add_selected_food_to_recipe(self):
        no_servings = self.ui.numberOfServingsInput.text()
        serving_size = self.ui.servingSizeInput.text()
        # Call the method in food_operations.py to update the food item's serving information
        self.food_operations.update_food_item(self.databae_manager.connection, self.selected_food.FoodId, no_servings, serving_size)
        # Add the selected food item to the list for the recipe's food items
        self.recipe_foods.append(self.selected_food)
        # Clear the input fields
        self.ui.numberOfServingsInput.clear()
        self.ui.servingSizeInput.clear()

    def handle_recipe_name_submission(self):
        recipe_name = self.ui.recipeNamefield.text().strip()
        if recipe_name:
            if self.database_manager.recipe_name_exists(recipe_name):
                # Recipe name already exists
                reply = QMessageBox.question(self, "Recipe Name Exists", f"The recipe name '{recipe_name}' already exists.  Do you want to enter a new name?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # Clear the recipe name field and allow the user to enter a new name
                    self.ui.recipeNamefield.clear()
                else:
                    # User canceled, do not add
                    pass
            else:
                # Recipe name does not exist, add it to the database
                rec_id = self.insert_recipe_into_database(recipe_name)
                if rec_id is not None:
                    # Display the recipe name on the screen
                    self.ui.newRecipeNameLabel.setText(recipe_name)
                    # Call the add_recipe method from recipes_operations.py
                    self.navigate_to_add_recipe_details_page(rec_id)
        else:
            QMessageBox.warning(self, "Error", "Please enter a new recipe name.")

    def insert_recipe_into_database(self, recipe_name):
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
        # Show the page for adding the remainder of recipe details
        # Pass the rec_id to the new page
        pass

    def closeEvent(self, event):
        # Close database connection if initialized
        if hasattr(self, 'database_manager'):
            self.database_manager.close_connection()
        event.accept()