# CST8917 Assignment 1: Durable Workflow for Image Metadata Processing

## Objective

This project implements a serverless image metadata processing pipeline using Azure Durable Functions in Python. The objective is to demonstrate the use of blob triggers, activity functions, and output bindings to create a complete event-driven solution deployed to Azure.

## Scenario

A fictional content moderation team requires an automated system to analyze metadata from user-uploaded images. This Azure Durable Functions application fulfills this requirement by:

* Automatically triggering when new images are uploaded to a specified blob storage container.
* Extracting essential metadata (file size, format, dimensions).
* Storing the extracted metadata in an Azure SQL Database.

## Workflow Overview

The solution is built around an Azure Durable Functions orchestration, which coordinates the execution of several functions to achieve the image metadata processing goal:

1.  **Blob Trigger (Client Function)**: Initiates the workflow upon a new image upload.
2.  **Orchestrator Function**: Manages the sequence of operations.
3.  **Extract Metadata (Activity Function)**: Processes the image to get its properties.
4.  **Store Metadata (Activity Function)**: Persists the extracted data into a SQL database.

## Workflow Requirements (Detailed)

### Step 1: Blob Trigger (Client Function)

* A blob-triggered Azure Function serves as the entry point, starting the Durable Function orchestration.
* It monitors a specific blob container (e.g., `images-input`) for new image uploads.
* It is configured to accept `.jpg`, `.png`, or `.gif` image files.

### Step 2: Orchestrator Function

The orchestrator function (`OrchestratorFunction`) is responsible for defining and executing the workflow. It:

* Receives the blob information (e.g., image name, URI) from the blob trigger.
* Calls the `ExtractMetadata` activity function to get image details.
* Calls the `StoreMetadata` activity function to save the extracted metadata to Azure SQL Database.

### Step 3: Activity Function – Extract Metadata

This activity function (`ExtractMetadata`) is designed to extract key metadata from the uploaded image. It processes the image to obtain:

* **File name**: The original name of the uploaded image file.
* **File size in KB**: The size of the image file in kilobytes.
* **Width and height (in pixels)**: The dimensions of the image.
* **Image format**: The format of the image (e.g., JPEG, PNG, GIF).

### Step 4: Activity Function – Store Metadata

This activity function (`StoreMetadata`) is responsible for persisting the extracted metadata. It utilizes an **Azure SQL output binding** to:

* Connect to a pre-configured Azure SQL Database.
* Insert the image metadata (file name, size, dimensions, format) into a designated table (e.g., `dbo.ImageMetadata`).

## Project Structure

The project follows the standard Azure Functions Python project structure:

```
image-metadata-pipeline-v1/
├── BlobTriggerClient/
│   └── __init__.py
│   └── function.json
├── ExtractMetadata/
│   └── __init__.py
│   └── function.json
├── OrchestratorFunction/
│   └── __init__.py
│   └── function.json
├── StoreMetadata/
│   └── __init__.py
│   └── function.json
├── host.json
├── local.settings.json
├── requirements.txt
├── extensions.csproj  (for Azure SQL binding)
└── ... other files
```

## Setup and Deployment

### Prerequisites

* Azure Account with an active subscription.
* Azure CLI installed and configured (`az login`).
* Azure Functions Core Tools v4 installed (`func`).
* Python 3.10 (or compatible version) installed.
* An Azure Storage Account (used for blob trigger and Durable Functions state).
* An Azure SQL Database and a table (e.g., `ImageMetadata` with columns like `FileName`, `FileSizeKB`, `Width`, `Height`, `ImageFormat`) created. Ensure your SQL server firewall allows connections from Azure services or your specific IP if testing locally.

### Local Setup (for testing with `pyodbc` workaround)

Due to platform limitations of the .NET-based SQL binding on macOS/Linux locally, the `StoreMetadata` function might use `pyodbc` for local testing.

1.  **Install ODBC Driver for SQL Server**:
    * **macOS (Apple Silicon)**:
        ```bash
        brew tap microsoft/mssql-release [https://github.com/Microsoft/homebrew-mssql-release](https://github.com/Microsoft/homebrew-mssql-release)
        brew update
        ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools
        ```
    * For other OS, refer to Microsoft's documentation.
2.  **Configure `odbcinst.ini`**:
    * Locate or create `/usr/local/etc/odbcinst.ini` (or `/opt/homebrew/etc/odbcinst.ini`).
    * Add the following content, ensuring the `Driver` path is correct for your system (e.g., `/opt/homebrew/lib/libmsodbcsql.18.dylib` for Apple Silicon):
        ```ini
        [ODBC Driver 18 for SQL Server]
        Description=Microsoft ODBC Driver 18 for SQL Server
        Driver=/opt/homebrew/lib/libmsodbcsql.18.dylib
        UsageCount=1
        ```
3.  **Update `StoreMetadata/__init__.py`**: Modify it to use `pyodbc.connect` and `cursor.execute` for insertion.
4.  **Update `StoreMetadata/function.json`**: Remove the `sql` output binding.
5.  **Update `requirements.txt`**: Add `pyodbc`.
6.  **Install Python dependencies**: `pip install -r requirements.txt`
7.  **Configure `local.settings.json`**: Ensure `SqlConnectionString` includes the `Driver={/path/to/driver.dylib}` part and correct credentials.
8.  **Run locally**: `func start --verbose`

### Azure Deployment

For deployment to Azure, we revert `StoreMetadata` to use the native Azure SQL output binding, as it's fully supported in the Azure environment.

1.  **Revert `StoreMetadata` function**:
    * **`StoreMetadata/function.json`**: Re-add the `sql` output binding (as shown in previous conversations).
    * **`StoreMetadata/__init__.py`**: Revert to simply returning the metadata dictionary to the output binding (as shown in previous conversations).
    * **`requirements.txt`**: Remove `pyodbc`.
    * **`extensions.csproj`**: Ensure this file exists in your root directory with the `Microsoft.Azure.WebJobs.Extensions.Sql` package reference.

2.  **Create Azure Resources (if not already done)**:
    ```bash
    RESOURCE_GROUP_NAME="cst8917-assignment-1-rg" # Or your chosen name
    STORAGE_ACCOUNT_NAME="imagemetastoragedaniel" # Your existing storage account
    FUNCTION_APP_NAME="imagemetadatafuncappdaniel" # Your chosen name
    LOCATION="eastus" # Or your chosen region

    az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
    az functionapp create --resource-group $RESOURCE_GROUP_NAME --consumption-plan-location $LOCATION --runtime python --runtime-version 3.10 --functions-version 4 --name $FUNCTION_APP_NAME --storage-account $STORAGE_ACCOUNT_NAME --os Linux
    ```

3.  **Deploy Function App Code**:
    Navigate to your project's root directory in the terminal and run:
    ```bash
    func azure functionapp publish $FUNCTION_APP_NAME --python --no-bundler
    ```
    (Replace `$FUNCTION_APP_NAME` with your actual Function App name).

4.  **Set Application Settings in Azure Portal**:
    This is crucial for your deployed app to find the storage and SQL database.
    * Go to the Azure Portal -> Your Function App -> **Configuration** -> **Application settings**.
    * Add/Edit the following settings:
        * **`AzureWebJobsStorage`**: Your Azure Storage Account connection string.
            `DefaultEndpointsProtocol=https;AccountName=imagemetastoragedaniel;AccountKey=5KyoTKWhID+mMEHsjox+z7XV/6hdRNkWgIXUMLJK6qdvBZggIxRqj+JgB3WPp92S4AYG2OVMXqpC+ASt1Ba5Yw==;EndpointSuffix=core.windows.net`
        * **`SqlConnectionString`**: Your Azure SQL Database connection string.
            `Server=tcp:cst8917-meta-sql-server.database.windows.net,1433;Initial Catalog=ImageMetadataDB;Persist Security Info=False;User ID=adminuser;Password=YourPassword123!;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;`
            **IMPORTANT**: Replace `YourPassword123!` with your actual SQL database password.
    * Click **"Save"**.

## Testing the Solution

1.  **Trigger the Blob Trigger**: Upload a `.jpg`, `.png`, or `.gif` image file to the `images-input` container in your Azure Storage Account via the Azure Portal.
2.  **Monitor Logs**: Go to your Function App in the Azure Portal, then navigate to **"Log stream"** under "Monitoring". Observe the execution logs for `BlobTriggerClient`, `OrchestratorFunction`, `ExtractMetadata`, and `StoreMetadata` to confirm successful execution.
3.  **Verify SQL Database**: Access your Azure SQL Database via the Azure Portal's **"Query editor (preview)"**. Log in and run `SELECT * FROM ImageMetadata;` to confirm that the extracted image metadata has been successfully inserted into the table.

## YouTube Demo Link
[Your YouTube Demo Video Link Here (Max 5 minutes)]
