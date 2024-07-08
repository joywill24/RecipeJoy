# customTags_operations.py
import pyodbc
import logging

logging.basicConfig(level=logging.DEBUG)

class CustomTagOperations:
    def add_tag(self, connection, tag_name):
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO CustomTags (TagName) VALUES (?)", (tag_name,))
            connection.commit()
            cursor.execute("SELECT SCOPE_IDENTITY()")
            tag_id = cursor.fetchone()[0]
            logging.info(f"Successfully added tag with id: {tag_id}")
            return tag_id
        except pyodbc.Error as error:
            logging.error(f"Error adding tag: {error}")
            connection.rollback()
            return None

    def update_tag(self, connection, tag_id, new_tag_name):
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE CustomTags SET TagName = ? WHERE TagId = ?", (new_tag_name, tag_id))
            connection.commit()
        except pyodbc.Error as error:
            logging.error(f"Error while updating tag: {error}")

    def delete_tag(self, connection, tag_id):
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM CustomTags WHERE TagId = ?", (tag_id,))
            connection.commit()
        except pyodbc.Error as error:
            logging.error(f"Error while deleting tag: {error}")
