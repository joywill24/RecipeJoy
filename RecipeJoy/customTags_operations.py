# customTags_operations.py
import uuid
import logging

class CustomTagOperations:
    @staticmethod
    def add_tag(connection, tag_name):
        try:
            cursor = connection.cursor()

            # Generate a unique identifier for TagId
            tag_id = uuid.uuid4()

            # Insert a record into the CustomTags table
            cursor.execute("""
                INSERT INTO CustomTags (TagId, TagName)
                VALUES (?, ?)
                """,
                (tag_id, tag_name)
            )
            connection.commit()

            print("Tag added successfully.")
            return tag_id
        except Exception as error:
            logging.error(f"Error while adding tag: {error}")
            return None

    @staticmethod
    def update_tag(connection, tag_id, new_tag_name):
        try:
            cursor = connection.cursor()

            # Update the CustomTags table
            cursor.execute("""
                UPDATE CustomTags
                SET TagName = ?
                WHERE TagId = ?
                """,
                (new_tag_name, tag_id)
            )
            connection.commit()

            print("Tag updated successfully.")
        except Exception as error:
            logging.error(f"Error while updating tag: {error}")

    @staticmethod
    def delete_tag(connection, tag_id):
        try:
            cursor = connection.cursor()

            # Delete from CustomTags table
            cursor.execute("""
                DELETE FROM CustomTags
                WHERE TagId = ?
                """,
                (tag_id,)
            )
            connection.commit()

            print("Tag deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting tag: {error}")