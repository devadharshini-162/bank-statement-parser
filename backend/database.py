import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# =========================================================================
# MAGIC CLOUD ABSTRACTION (SQLAlchemy)
# =========================================================================
# Why use SQLAlchemy? Because it "abstracts" the database!
# Right now, we are pointing this variable to a local SQLite file so you can develop 
# locally without needing to pay for AWS yet.
# When you finally create your AWS RDS PostgreSQL database, you DO NOT need to 
# change any Python code below! You simply change this one string in your `.env` file to:
# DATABASE_URL = "postgresql://your_aws_user:your_password@your-aws-db-link.amazonaws.com:5432/postgres"

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///history.db")

# If we are using SQLite locally, we need to allow multiple threads. 
# Postgres doesn't need this check, so we do it conditionally.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# The engine is the core connection to the database (whether SQLite or AWS AWS)
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# A Session is what we use to actually talk to the database to add or query rows
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our Models
Base = declarative_base()

# =========================================================================
# DATABASE MODELS (Tables)
# =========================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)  # We store hashes, never real passwords!
    role = Column(String, default="ACCOUNTANT")  # "ADMIN" or "ACCOUNTANT"

    # A single User can have multiple History records. This creates a relationship!
    histories = relationship("History", back_populates="user")

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    
    # -----------------------------------------------------
    # NEW MULTI-TENANT FEATURE: Link history to a User
    # -----------------------------------------------------
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="histories")

    # Metrics
    filename = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_transactions = Column(Integer)
    total_debits = Column(Integer)
    total_credits = Column(Integer)
    anomalies_count = Column(Integer)
    is_valid = Column(Boolean)

# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def init_db():
    """
    Creates all tables in the database if they don't exist yet.
    """
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency to get a database session for a FastAPI request.
    It yields the session and safely closes it when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
