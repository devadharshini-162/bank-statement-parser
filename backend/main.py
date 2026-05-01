from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import shutil
import os
import uuid

# Import our custom logic
from extractor import extract_transactions
from utils import transactions_to_dataframe, save_to_excel, validate_transactions, generate_output_filename
from database import init_db, get_db, User, History
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from aws_service import upload_to_s3, generate_presigned_url

# Initialize the Database tables
init_db()

app = FastAPI(title="Bank Statement Parser API - SaaS Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================================
# AUTHENTICATION ENDPOINTS
# =========================================================================

class UserAuthParams(BaseModel):
    username: str
    password: str

@app.post("/signup")
def create_user(user: UserAuthParams, db: Session = Depends(get_db)):
    # Check if username exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, password_hash=hashed_password, role="ACCOUNTANT")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully. You can now log in."}

@app.post("/login")
def login(user: UserAuthParams, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Generate token
    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer", "username": db_user.username, "role": db_user.role}

# =========================================================================
# SECURED API ENDPOINTS
# =========================================================================

@app.post("/parse")
async def parse_statement(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # PROTECTS THE ROUTE
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

    # Get the user ID from the database using the username inside our token
    db_user = db.query(User).filter(User.username == current_user["username"]).first()

    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join(UPLOAD_DIR, temp_filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        transactions = extract_transactions(temp_file_path)

        if not transactions:
            raise HTTPException(status_code=422, detail="Failed to parse transactions.")

        df = transactions_to_dataframe(transactions)
        validation_results = validate_transactions(df)

        output_filename = generate_output_filename(file.filename)
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        save_to_excel(df, output_path)

        # -----------------------------------------------------
        # NEW CLOUD STORAGE: AWS S3 UPLOAD
        # -----------------------------------------------------
        # Upload the physically generated file to Amazon S3
        upload_to_s3(output_path, output_filename)
        
        # Give the user a secure, expiring URL to download it directly from AWS
        secure_download_url = generate_presigned_url(output_filename)

        # Log history into the database and link it to the user
        anomalies_cnt = len(validation_results["anomalies"]) if isinstance(validation_results["anomalies"], list) else 0
        
        new_history = History(
            user_id=db_user.id,
            filename=file.filename,
            total_transactions=len(transactions),
            total_debits=validation_results["total_debits"],
            total_credits=validation_results["total_credits"],
            anomalies_count=anomalies_cnt,
            is_valid=validation_results["is_valid"]
        )
        db.add(new_history)
        db.commit()

        return {
            "filename": output_filename,
            "total_transactions": len(transactions),
            "total_debits": validation_results["total_debits"],
            "total_credits": validation_results["total_credits"],
            "anomalies_count": anomalies_cnt,
            "anomalies": validation_results["anomalies"] if isinstance(validation_results["anomalies"], list) else [],
            "is_valid": validation_results["is_valid"],
            "excel_download_path": secure_download_url,
            "transactions": transactions
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/history")
def read_history(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user) # PROTECTS THE ROUTE
):
    """Returns the processing history specifically for the logged-in user."""
    db_user = db.query(User).filter(User.username == current_user["username"]).first()
    
    # If the user is an ADMIN, they get to see company-wide history
    if db_user.role == "ADMIN":
        histories = db.query(History).order_by(History.timestamp.desc()).all()
    else:
        # Otherwise, they only see their own history
        histories = db.query(History).filter(History.user_id == db_user.id).order_by(History.timestamp.desc()).all()
    
    # SQLAlchemy objects need to be converted to dictionaries for FastAPI JSON serialization
    result = []
    for h in histories:
        result.append({
            "filename": h.filename,
            "timestamp": h.timestamp.isoformat(),
            "total_transactions": h.total_transactions,
            "total_debits": h.total_debits,
            "total_credits": h.total_credits,
            "anomalies_count": h.anomalies_count,
            "is_valid": h.is_valid
        })
    return result

@app.get("/download/{filename}")
def download_excel(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Excel file not found.")
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
