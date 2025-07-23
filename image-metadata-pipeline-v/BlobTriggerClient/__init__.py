import logging
import json
import azure.functions as func
import azure.durable_functions as df

# This function is triggered when a new blob is uploaded to the 'images-input' container.
# It acts as the client function that starts the Durable Functions orchestration.
async def main(inputblob: func.InputStream, starter: str):
    logging.info(f"Python blob trigger function processed blob\n"
                 f"Name: {inputblob.name}\n"
                 f"Blob Size: {inputblob.length} Bytes")

    # Get the Durable Functions client
    client = df.DurableOrchestrationClient(starter)

    # Extract the file name from the blob path
    file_name = inputblob.name.split('/')[-1]

    # Read the content of the blob directly.
    # We read the entire content into memory. For very large images, consider streaming
    # or using a different pattern, but for typical metadata extraction, this is fine.
    image_content = inputblob.read()

    # Prepare the input for the orchestrator function.
    # Since JSON serialization doesn't handle raw bytes directly, convert bytes to a hex string.
    orchestrator_input = {
        "fileName": file_name,
        "imageContent": image_content.hex() # Convert bytes to hex string for JSON serialization
    }

    # Start the orchestration. The orchestrator function will be named 'OrchestratorFunction'.
    instance_id = await client.start_new("OrchestratorFunction", None, orchestrator_input)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    # In a blob trigger context, there's no direct HTTP response to the uploader.
    # The logging provides confirmation of the orchestration start.
