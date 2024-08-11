# customTags_operations.py
# This module provides operations for managing custom tags in a recipe application.
# It includes functionality to add, update, delete, and retrieve tags from the database,
# as well as populate UI components with tags and manage tags associated with recipes.

import pyodbc
import logging
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox

logging.basicConfig(level=logging.DEBUG)

class CustomTagOperations:
    # Add a new tag to the database if it doesn't already exist
    def add_tag(self, connection, tag_name):
        try:
            with connection.cursor() as cursor:
                # Check if tag already exists
                cursor.execute("SELECT COUNT(*) FROM CustomTags WHERE TagName = ?", (tag_name,))
                if cursor.fetchone()[0] > 0:
                    logging.warning(f"Tag '{tag_name}' already exists")
                    return None

                # Insert the new tag and get its ID
                insert_query = "INSERT INTO CustomTags (TagName) OUTPUT INSERTED.TagId VALUES (?);"
                cursor.execute(insert_query, (tag_name,))
                tag_id = cursor.fetchone()[0]
                connection.commit()

                if tag_id:
                    logging.info(f"Successfully added tag with id: {tag_id}")
                    return tag_id
                else:
                    logging.error(f"Failed to retrieve tag id after adding")
                    return None
        except pyodbc.Error as error:
            logging.error(f"Error adding tag: {error}")
            connection.rollback()
            return None

    # Update the name of an existing tag in the database
    def update_tag(self, connection, tag_id, new_tag_name):
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE CustomTags SET TagName = ? WHERE TagId = ?", (new_tag_name, tag_id))
                connection.commit()
        except pyodbc.Error as error:
            logging.error(f"Error while updating tag: {error}")
            connection.rollback()

    # Delete a tag from the database
    def delete_tag(self, connection, tag_id):
        try:
            with connection.cursor() as cursor:
                # First, remove all associations in the RecipeTags table
                cursor.execute("DELETE FROM RecipeTags WHERE TagId = ?", (tag_id,))

                # Then, delete the tag from the CustomTags table
                cursor.execute("DELETE FROM CustomTags WHERE TagId = ?", (tag_id,))

                connection.commit()
                logging.info(f"Tag with ID {tag_id} and its associations deleted successfully")
        except pyodbc.Error as error:
            logging.error(f"Error while deleting tag: {error}")
            connection.rollback()
            raise

    # Retrieve all tags
    def get_all_tags(self, connection):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT TagId, TagName FROM CustomTags ORDER BY TagName")
                return cursor.fetchall()
        except pyodbc.Error as error:
            logging.error(f"Error while getting tags: {error}")
            return[]

    # Populates a QListWidget with all tags from the database, and allows the user to select them
    def populate_tags_list(self, tags_list_widget, connection):
        logging.debug("Entering populate_tags_list method")
        try:
            tags_list_widget.clear()
            tags = self.get_all_tags(connection)
            logging.debug(f"Retrieved {len(tags)} from the database")

            for tag_id, tag_name in tags:
                item = QtWidgets.QListWidgetItem(tag_name)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setData(QtCore.Qt.UserRole, tag_id)
                tags_list_widget.addItem(item)
                logging.debug(f"Added tag to list: {tag_name} (ID: {tag_id})")

            logging.info(f"Tags list populated successfully with {tags_list_widget.count()} items.")
        except Exception as error:
            logging.error(f"Error populating tags list: {error}")
            raise
        finally:
            logging.debug("Exiting populate_tags_list method")

    # Displays a list of tags as non-checkable text items in a QListWidget
    def display_tags_as_text(self, tags_list_widget, recipe_tags):
        try:
            tags_list_widget.clear()
            for tag in recipe_tags:
                item = QtWidgets.QListWidgetItem(tag['TagName'])
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsUserCheckable)
                tags_list_widget.addItem(item)
            logging.debug(f"Displayed {len(recipe_tags)} tags as text")
        except Exception as error:
            logging.error(f"Error displaying tags: {error}")

    # Populates a QComboBox with all custom tags from the database
    def populate_custom_tags_combo_box(self, ui, connection):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT TagId, TagName FROM CustomTags ORDER BY TagName")
                tags = cursor.fetchall()

                ui.customTagsComboBox.clear()
                ui.customTagsComboBox.addItem("Select Tag", None)
                for tag_id, tag_name in tags:
                    ui.customTagsComboBox.addItem(tag_name, tag_id)

            logging.info("Custom tags combo box populated successfully.")
        except Exception as error:
            logging.error(f"Error populating custom tags combo box: {error}")
            QMessageBox.warning(ui.customTagsComboBox, "Error", f"Failed to laod custom tags: {str(error)}")

    # Associates a tag with a recipe in the database
    def add_tag_to_recipe(self, connection, recipe_id, tag_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO RecipeTags (RecId, TagId) VALUES (?, ?)", (recipe_id, tag_id))
                connection.commit()
                logging.info(f"Tag {tag_id} added to recipe {recipe_id} successfully")
                return True
        except pyodbc.Error as error:
            logging.error(f"Error adding tag to recipe: {error}")
            connection.rollback()
            return False

    # Save the tags associated with a recipe
    def save_recipe_tags(self, connection, recipe_id, tag_ids):
        try:
           with connection.cursor() as cursor:
                # Remove all existing tags for the recipe
                cursor.execute("DELETE FROM RecipeTags WHERE RecipeId = ?", (recipe_id,))

                # Add new tags
                for tag_id in tag_ids:
                    cursor.execute("INSERT INTO RecipeTags (RecipeId, TagId) VALUES (?, ?)", (recipe_id, tag_id))

                connection.commit()
                logging.info(f"Tags saved for recipe {recipe_id}")
                return True
        except pyodbc.Error as error:
            logging.error(f"Error saving recipe tags: {error}")
            connection.rollback()
            return False

    # Remove a tag association from a recipe
    def remove_tag_from_recipe(self, connection, recipe_id, tag_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM RecipeTags WHERE RecId = ? AND TagId = ?", (recipe_id, tag_id))
                connection.commit()
                logging.info(f"Tag {tag_id} removed from recipe {recipe_id}")
                return True
        except pyodbc.Error as error:
            logging.error(f"Error removing tag from recipe: {error}")
            connection.rollback()
            return False