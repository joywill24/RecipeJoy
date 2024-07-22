# customTags_operations.py
import pyodbc
import logging

logging.basicConfig(level=logging.DEBUG)

class CustomTagOperations:
    def add_tag(self, connection, tag_name):
        try:
            cursor = connection.cursor()

            # Check if tag already exists
            cursor.execute("SELECT COUNT(*) FROM CustomTags WHERE TagName = ?", (tag_name,))
            if cursor.fetchone()[0] > 0:
                logging.warning(f"Tag '{tag_name}' already exists")
                return None

            insert_query = "INSERT INTO CustomTags (TagName) OUTPUT INSERTED.TagId VALUES (?);"
            cursor.execute(insert_query, (tag_name,))
            tag_id = cursor.fetchone()[0]
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

    def get_all_tags(self, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT TagId, TagName FROM CustomTags ORDER BY TagName")
            return cursor.fetchall()
        except pyodbc.Error as error:
            logging.error(f"Error while getting tags: {error}")
            return[]