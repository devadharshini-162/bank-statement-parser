from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import json

# Import custom logic specific to our Parser project
from extractor import extract_transactions
from utils import transactions_to_dataframe, save_to_excel, validate_transactions, generate_output_filename
from database import init_db, log_processing, get_processing_history

# Initialize SQLite Database
init_db()

# Create a FastAPI app instance with metadata
app = FastAPI(title="Bank Statement Parser API", version="1.0.0")

# Setup CORS (Cross-Origin Resource Sharing) middleware to allow cross-origin requests
# This is especially useful when building a separate frontend later!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allows all origins (e.g. localhost frontend calling the backend API)
    allow_credentials=True,
    allow_methods=["*"],      # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],      # Allows all HTTP headers
)

# Define directory constants
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

# Create folders synchronously if they don't already exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
def read_root():
    """
    Basic health-check or welcome endpoint.
    Returns a simple JSON indicating that the server is alive.
    """
    return {"message": "Bank Statement Parser API is running", "version": "1.0.0"}


@app.post("/parse")
async def parse_statement(file: UploadFile = File(...)):
    """
    Core parsing endpoint. It handles a PDF upload, extracts AI transactions,
    validates the result, saves to Excel, and returns stats.
    """
    # Validate that the uploaded file is a PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

    # Create a unique temporary filename incorporating a UUID
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join(UPLOAD_DIR, temp_filename)

    try:
        # Save the uploaded file temporarily to the working disk
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call the Gemini extractor process defined in extractor.py
        transactions = extract_transactions(temp_file_path)

        # If it returns empty, likely AI couldn't parse it or it wasn't a bank statement
        if not transactions:
            raise HTTPException(
                status_code=422, 
                detail="Failed to parse transactions. Ensure the file contains a valid bank statement."
            )

        # Convert the dictionary output to a Pandas DataFrame
        df = transactions_to_dataframe(transactions)

        # Validate extracted logic (totals, anomalies, etc.)
        validation_results = validate_transactions(df)

        # Generate output filename (e.g., parsed_filename_timestamp.xlsx)
        output_filename = generate_output_filename(file.filename)
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Output the parsed DataFrame into formatted Excel
        save_to_excel(df, output_path)

        # Log to SQLite history
        anomalies_cnt = len(validation_results["anomalies"]) if isinstance(validation_results["anomalies"], list) else 0
        log_processing(
            filename=file.filename,
            total_transactions=len(transactions),
            total_debits=validation_results["total_debits"],
            total_credits=validation_results["total_credits"],
            anomalies_count=anomalies_cnt,
            is_valid=validation_results["is_valid"]
        )

        return {
    "filename": output_filename,
    "total_transactions": len(transactions),
    "total_debits": validation_results["total_debits"],
    "total_credits": validation_results["total_credits"],
    "anomalies_count": len(validation_results["anomalies"]) if isinstance(validation_results["anomalies"], list) else 0,
    "anomalies": validation_results["anomalies"] if isinstance(validation_results["anomalies"], list) else [],
    "is_valid": validation_results["is_valid"],
    "excel_download_path": f"/download/{output_filename}",
    "transactions": transactions
}

    except HTTPException:
        # Re-raise already raised HTTP Exceptions so they aren't caught by a general Exception
        raise
    except Exception as e:
        # Catch unexpected errors to avoid crashing the server without a clear message
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up: Make absolutely sure the temporary uploaded PDF is deleted
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/download/{filename}")
def download_excel(filename: str):
    """
    Downloads an existing generated Excel file.
    Takes a filename parameter and streams it back via FileResponse.
    """
    file_path = os.path.join(OUTPUT_DIR, filename)

    # If the requested file isn't in our outputs directory, return a clean 404 Error
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Excel file not found. It may have been deleted or the name is incorrect.")

    # Return as an Excel download
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.get("/history")
def read_history():
    """
    Returns the processing history from the SQLite database.
    """
    try:
        return get_processing_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
