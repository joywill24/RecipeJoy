# proteins_operations.py
# This module provides various operations for managing protein records in the Proteins table of a database.
# It includes functionality to add, update, delete, and retrieve protein records.

import logging

class ProteinOperations:

    # Add a new protein to the database
    @staticmethod
    def add_protein(connection, protein_name):
        try:
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO Proteins (ProteinName)
                VALUES (?)
                """,
                (protein_name,))
            connection.commit()

            # Retrieve the generated ProteinId
            cursor.execute("SELECT @@IDENTITY AS ProteinId")
            protein_id = cursor.fetchone()[0]

            logging.info("Protein added successfully.")
            return protein_id
        except Exception as error:
            logging.error(f"Error while adding protein: {error}")
            return None

    # Update the name of an existing protein in the database
    @staticmethod
    def update_protein(connection, protein_id, new_protein_name):
        try:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE Proteins
                SET ProteinName = ?
                WHERE ProteinId = ?
            """, (new_protein_name, protein_id))
            connection.commit()

            logging.info("Protein updated successfully.")
        except Exception as error:
            logging.error(f"Error while updating protein: {error}")

    # Delete a protein from the database
    @staticmethod
    def delete_protein(connection, protein_id):
        try:
            cursor = connection.cursor()

            cursor.execute("""
                DELETE FROM Proteins
                WHERE ProteinId = ?
            """, (protein_id,))
            connection.commit()

            logging.info("Protein deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting protein: {error}")

    # Retrieve all protein names and IDs from the database
    @staticmethod
    def get_protein_names(connection):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT ProteinId, ProteinName FROM Proteins ORDER BY ProteinName")
            return cursor.fetchall()
        except Exception as error:
            logging.error(f"Error fetching protein name: {error}")
            return[]

    # Retrieve all protein names by their IDs
    @staticmethod
    def get_protein_type_name(connection, protein_id):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT ProteinName FROM Proteins WHERE ProteinId = ?", (protein_id,))
            result = cursor.fetchone()
            return result[0] if result else ""
        except Exception as error:
            logging.error(f"Error fetching protein type: {error}")
            return ""