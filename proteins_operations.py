# proteins_operations.py
import logging

class ProteinOperations:
    @staticmethod
    def add_protein(connection, protein_name):
        try:
            cursor = connection.cursor()

            # Insert a record into the Proteins table
            cursor.execute("""
                INSERT INTO Proteins (ProteinName)
                VALUES (?)
                """,
                (protein_name,))
            connection.commit()

            # Retrieve the generated ProteinId
            cursor.execute("SELECT @@IDENTITY AS ProteinId")
            protein_id = cursor.fetchone()[0]

            print("Protein added successfully.")
            return protein_id
        except Exception as error:
            logging.error(f"Error while adding protein: {error}")
            return None

    @staticmethod
    def update_protein(connection, protein_id, new_protein_name):
        try:
            cursor = connection.cursor()

            # Update the Proteins table
            cursor.execute("""
                UPDATE Proteins
                SET ProteinName = ?
                WHERE ProteinId = ?
                """,
                (new_protein_name, protein_id))
            connection.commit()

            print("Protein updated successfully.")
        except Exception as error:
            logging.error(f"Error while updating protein: {error}")

    @staticmethod
    def delete_protein(connection, protein_id):
        try:
            cursor = connection.cursor()

            # Delete from Proteins table
            cursor.execute("""
                DELETE FROM Proteins
                WHERE ProteinId = ?
                """,
                (protein_id,))
            connection.commit()

            print("Protein deleted successfully.")
        except Exception as error:
            logging.error(f"Error while deleting protein: {error}")