import logging
import io
from PIL import Image, UnidentifiedImageError

# This activity function extracts metadata from an image.
# It expects a dictionary containing 'fileName' and 'imageContentHex' as input.
def main(input_data: dict) -> dict:
    logging.info("ExtractMetadata activity function started.")

    file_name = input_data.get("fileName", "unknown_file")
    image_content_hex = input_data.get("imageContentHex")

    if not image_content_hex:
        logging.error(f"Missing 'imageContentHex' in input for {file_name}.")
        raise ValueError("Image content (hex string) is required.")

    try:
        # Convert the hex string back to bytes here, right before processing the image.
        image_data = bytes.fromhex(image_content_hex)

        # Use BytesIO to treat the byte string as a file-like object,
        # which Pillow can then open directly.
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)

        # Extract metadata
        file_size_kb = len(image_data) / 1024.0 # File size in KB
        width, height = img.size
        image_format = img.format

        metadata = {
            "FileName": file_name, # Include file name in the returned metadata
            "FileSizeKB": round(file_size_kb, 2),
            "Width": width,
            "Height": height,
            "ImageFormat": image_format
        }

        logging.info(f"Successfully extracted metadata for {file_name}: {metadata}")
        return metadata

    except UnidentifiedImageError as e:
        logging.error(f"Error: Could not identify image file '{file_name}'. It might be corrupted or an unsupported format. {e}")
        raise # Re-raise to propagate the error to the orchestrator
    except Exception as e:
        logging.error(f"An unexpected error occurred while extracting metadata for '{file_name}': {e}")
        raise # Re-raise to propagate the error to the orchestrator
