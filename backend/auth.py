import os
from datetime import datetime, timedelta
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
import bcrypt

# FastAPI provides HTTPBearer which automatically looks for the 
# "Authorization: Bearer <TOKEN>" header in incoming API requests.
security = HTTPBearer()

# We need a secret signing key to create and verify our JSON Web Tokens (JWT).
# Without this exact key, nobody can forge a token claiming to be an admin.
SECRET_KEY = os.environ.get("JWT_SECRET", "super-secret-local-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Tokens live for 7 days

def get_password_hash(password: str) -> str:
    """Takes a plain text password and returns a hashed version."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the plain password matches the hashed version in the database."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """
    Creates a JWT token containing a payload (`data`).
    The payload usually contains the user's ID or username.
    """
    to_encode = data.copy()
    
    # Calculate exactly when this token should die
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode it using our SECRET_KEY and the HS256 algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    This is a 'Dependency' function in FastAPI.
    Whenever a route needs to be protected, we add this function to it.
    It automatically intercepts the request, grabs the token, decodes it,
    and returns the username inside. If it fails, it throws a 401 Unauthorized error.
    """
    token = credentials.credentials
    try:
        # We try to decode the token. If it was modified or expired, this will throw an error!
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        
        # We can also extract the role!
        role: str = payload.get("role", "ACCOUNTANT")
        
        return {"username": username, "role": role}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token signature")
