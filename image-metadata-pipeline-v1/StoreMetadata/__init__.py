import logging
import json
import azure.functions as func

# This activity function stores the image metadata into an Azure SQL Database
# using the native SQL output binding.
def main(metadata: dict, outputSql: func.Out[str]):
    logging.info(f"StoreMetadata activity function started with metadata: {metadata}")

    try:
        # The 'metadata' dictionary contains FileName, FileSizeKB, Width, Height, ImageFormat.
        # The SQL output binding expects a JSON string or a list of JSON strings.
        # Ensure the keys in the dictionary match your SQL table column names.
        # Example SQL Table Structure (assuming 'Id' is auto-incrementing and 'ProcessedDate' is default GETDATE()):
        # CREATE TABLE dbo.ImageMetadata (
        #     Id INT IDENTITY(1,1) PRIMARY KEY,
        #     FileName NVARCHAR(255),
        #     FileSizeKB DECIMAL(10, 2),
        #     Width INT,
        #     Height INT,
        #     ImageFormat NVARCHAR(50),
        #     ProcessedDate DATETIME DEFAULT GETDATE()
        # );

        # Convert the dictionary to a JSON string.
        # The SQL output binding will automatically insert this as a new row.
        # If you were inserting multiple rows, you'd pass a list of dictionaries.
        outputSql.set(json.dumps(metadata))

        logging.info("Metadata successfully sent to SQL output binding.")
        return "Metadata stored successfully."

    except Exception as e:
        logging.error(f"Error storing metadata to SQL via output binding: {e}")
        # Re-raise the exception so the orchestrator can handle it.
        raise
