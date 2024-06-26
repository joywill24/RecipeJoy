# ui_operations.py
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from UI_Files.ui_mainwindow import Ui_MainWindow
from database import DatabaseManager
import logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Set initial page to home page
        self.ui.stackedWidget.setCurrentIndex(1)
        # Initialize database manager
        self.database_manager = DatabaseManager()

        self.database_manager.connect_to_database()
        self.connect_buttons()
        # self.populate_search_categories()

    def connect_buttons(self):
        # Connect the buttons to their methods
        self.ui.findArecipeButton.clicked.connect(self.show_find_recipe_page)
        self.ui.returnTohomeButton.clicked.connect(self.show_home_page)
        self.ui.searchButton.clicked.connect(self.perform_search)
        self.ui.searchCategoryComboBox.currentIndexChanged.connect(self.onSearchCategoryChanged)

        # Connect the addCategoryButton
        # if hasattr(self.ui, 'addCategoryButton'):
            # self.ui.addCategoryButton.clicked.connect(self.add_search_category)

    def populate_search_categories(self):
        categories = self.database_manager.get_search_categories()
        self.ui.searchCategoryComboBox.addItems(categories)


    def show_home_page(self):
        print("Showing Home Page")
        self.ui.stackedWidget.setCurrentIndex(0)
    def show_find_recipe_page(self):
        print("Showing Find Recipe Page")
        self.ui.stackedWidget.setCurrentIndex(1)

    def perform_search(self):
        category = self.ui.searchCategoryComboBox.currentText()
        criteria = self.ui.searchCriteriaLineEdit.text()
        self.search_recipes(category, criteria)

    def search_recipes(self, category, criteria):
        try:
            cursor = self.database_manager.connection.cursor()
            query = ""

            if category == "Recipe Name":
                query = "SELECT * FROM Recipes WHERE RecipeName LIKE ?"
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
            self.display_results(results)
        except Exception as error:
            logging.error(f"Error while performing search: {error}")

    def display_results(self, results):
        self.ui.resultsTableWidget.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.ui.resultsTableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.resultsTableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def add_search_category(self):
        category_name = self.ui.newCategoryLineEdit.text().strip()
        if category_name:
            self.database_manager.insert_search_category(category_name)
            self.populate_search_categories()
            QMessageBox.information(self, "Category Added", f"Category '{category_name}' added successfully.")
            self.ui.newCategoryLineEdit.clear()
        else:
            QMessageBox.warning(self, "Error", "Category name cannot be empty.")

    def onSearchCategoryChanged(self, index):
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

    def closeEvent(self, event):
        # Close database connection if initialized
        if hasattr(self, 'database_manager'):
            self.database_manager.close_connection()
        event.accept()