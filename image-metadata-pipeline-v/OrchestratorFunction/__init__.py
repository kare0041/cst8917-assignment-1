import logging
import json
import azure.durable_functions as df

# This is the orchestrator function that defines the workflow for image metadata processing.
# It calls activity functions sequentially to extract and store metadata.
def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("Orchestrator function started.")

    # Get the input from the client function (BlobTriggerClient)
    # This input contains the file name and the image content as a hex string.
    orchestrator_input = context.get_input()
    file_name = orchestrator_input["fileName"]
    image_content_hex = orchestrator_input["imageContent"] # Keep as hex string here

    logging.info(f"Orchestrating processing for image: {file_name}")

    try:
        # Step 1: Call the 'ExtractMetadata' activity function.
        # Pass the image content as the hex string. The activity will convert it back to bytes.
        metadata = yield context.call_activity("ExtractMetadata", {
            "fileName": file_name, # Pass file name for logging/context in activity
            "imageContentHex": image_content_hex # Pass hex string
        })
        logging.info(f"Extracted metadata for {file_name}: {metadata}")

        # The 'ExtractMetadata' activity now returns metadata including FileName
        # No need to add FileName here if it's already included.
        # Ensure the key matches what your SQL table expects (e.g., "FileName")
        if "FileName" not in metadata: # Defensive check
            metadata["FileName"] = file_name


        # Step 2: Call the 'StoreMetadata' activity function.
        # Pass the extracted metadata (which is already a dictionary and JSON-serializable).
        store_result = yield context.call_activity("StoreMetadata", metadata)
        logging.info(f"Store metadata result for {file_name}: {store_result}")

        return f"Image '{file_name}' metadata processed and stored successfully."

    except Exception as e:
        logging.error(f"Error in orchestration for {file_name}: {e}")
        # Re-raise the exception to mark the orchestration as failed.
        raise

main = df.Orchestrator.create(orchestrator_function)
