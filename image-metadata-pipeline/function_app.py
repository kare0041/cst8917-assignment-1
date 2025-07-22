import logging
import azure.functions as func
import azure.durable_functions as df

from PIL import Image
import requests
from io import BytesIO

import pyodbc
import os

app = func.FunctionApp()

# --- Blob Trigger: Starts the orchestration ---
@app.function_name(name="BlobTriggerClient")
@app.blob_trigger(arg_name="blob", path="images-input/{name}", connection="AzureWebJobsStorage")
@app.durable_client_input(client_name="starter")
async def blob_trigger_function(blob: func.InputStream, starter: df.DurableOrchestrationClient):
    client = df.DurableOrchestrationClient(starter)
    image_info = {
        "blob_name": blob.name,
        "blob_url": blob.uri
    }
    instance_id = await client.start_new("OrchestratorFunction", None, image_info)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")


# --- Orchestrator Function ---
@app.function_name(name="OrchestratorFunction")
@app.durable_orchestration_trigger(context_name="context")
def orchestrator_function(context: df.DurableOrchestrationContext):
    image_info = context.get_input()
    metadata = yield context.call_activity("ExtractMetadata", image_info)
    yield context.call_activity("StoreMetadata", metadata)
    return metadata


# --- Extract Metadata Activity ---
@app.function_name(name="ExtractMetadata")
@app.durable_activity_trigger(input_name="image_info")
def extract_metadata(image_info: dict):
    try:
        response = requests.get(image_info["blob_url"])
        image = Image.open(BytesIO(response.content))
        metadata = {
            "FileName": image_info["blob_name"].split("/")[-1],
            "FileSizeKB": round(len(response.content) / 1024, 2),
            "Width": image.width,
            "Height": image.height,
            "Format": image.format
        }
        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata: {str(e)}")
        raise


# --- Store Metadata Activity ---
@app.function_name(name="StoreMetadata")
@app.durable_activity_trigger(input_name="metadata")
def store_metadata(metadata: dict):
    try:
        conn_str = os.getenv("SQL_CONNECTION_STRING")
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ImageMetadata (FileName, FileSizeKB, Width, Height, Format)
                VALUES (?, ?, ?, ?, ?)""",
                metadata["FileName"], metadata["FileSizeKB"],
                metadata["Width"], metadata["Height"], metadata["Format"]
            )
            conn.commit()
    except Exception as e:
        logging.error(f"Error storing metadata: {str(e)}")
        raise
