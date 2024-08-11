# custom_dialogs.py
# This module defines custom QDialog classes for removing tags, food items, and protein types.

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

# Creates specific user dialog for Tag Removal
class TagRemovalDialog(QDialog):
    def __init__(self, parent=None, associated_recipes_count=0):
        super().__init__(parent)
        self.setWindowTitle("Tag in Use")

        layout = QVBoxLayout()

        message = QLabel(
            f"This tag is associated with {associated_recipes_count} recipe(s). What would you like to do?")
        layout.addWidget(message)

        button_layout = QHBoxLayout()

        view_button = QPushButton("View Recipes")
        view_button.clicked.connect(lambda: self.done(1))  # Custom return code for View Recipes

        delete_button = QPushButton("Delete All")
        delete_button.clicked.connect(lambda: self.done(2))  # Custom return code for Delete All

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(view_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

# Creates specific user dialog for Food Removal
class FoodRemovalDialog(QDialog):
    def __init__(self, parent=None, num_recipes=0):
        super().__init__(parent)
        self.setWindowTitle("Food Item in Use")

        layout = QVBoxLayout()

        message = QLabel(
            f"This food item is associated with {num_recipes} recipe(s). What would you like to do?")
        layout.addWidget(message)

        button_layout = QHBoxLayout()

        view_button = QPushButton("View Associated Recipes")
        view_button.clicked.connect(lambda: self.done(1))  # Custom return code for View Recipes

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(view_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

# Creates specific user dialog for Protein Removal
class ProteinRemovalDialog(QDialog):
    def __init__(self, parent=None, associated_recipes_count=0):
        super().__init__(parent)
        self.setWindowTitle("Protein Type in Use")

        layout = QVBoxLayout()

        message = QLabel(
            f"This protein type is associated with {associated_recipes_count} recipe(s). What would you like to do?")
        layout.addWidget(message)

        button_layout = QHBoxLayout()

        view_button = QPushButton("View Recipes")
        view_button.clicked.connect(lambda: self.done(1))  # Custom return code for View Recipes

        delete_button = QPushButton("Delete All")
        delete_button.clicked.connect(lambda: self.done(2))  # Custom return code for Delete All

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(view_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)