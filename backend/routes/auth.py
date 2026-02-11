from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.db_connection.connection import supabase_client
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# -------------------- JWT verification dependency --------------------
# HTTPBearer automatically checks for "Authorization: Bearer <token>"
# and enables the "Authorize" button in Swagger UI.
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the Bearer token from the Authorization header.
    Returns the user object if valid, raises 401 otherwise.
    Compatible with both Frontend and Swagger UI.
    """
    token = credentials.credentials

    try:
        # Verify token with Supabase
        user = supabase_client.auth.get_user(token)
    except Exception as e:
        # Handle cases where Supabase client raises an error (e.g. network)
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    if not user or not user.user:
        raise HTTPException(status_code=401, detail="Invalid token or expired session")

    return user.user
