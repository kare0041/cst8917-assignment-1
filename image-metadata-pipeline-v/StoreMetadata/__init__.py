import logging
import pyodbc
import os
import azure.functions as func

def main(metadata: dict) -> str:
    logging.info(f"StoreMetadata activity function started with metadata: {metadata}")

    try:
        # Get SQL connection string from environment variable
        conn_str = os.getenv("SQL_CONNECTION_STRING")
        if not conn_str:
            raise ValueError("SQL_CONNECTION_STRING environment variable is not set.")

        # Establish database connection
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO ImageMetadata (FileName, FileSizeKB, Width, Height, ImageFormat)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(
                insert_query,
                metadata["FileName"],
                metadata["FileSizeKB"],
                metadata["Width"],
                metadata["Height"],
                metadata["ImageFormat"]
            )
            conn.commit()

        logging.info("Metadata successfully stored in SQL database.")
        return "Metadata stored successfully."

    except Exception as e:
        logging.error(f"Error storing metadata to SQL database: {e}")
        raise