from src.utils.file_hash import get_file_hash
import uuid
import aiofiles
from pathlib import Path
from langchain_core.messages import HumanMessage
from src.db_connection.connection import supabase_client
from fastapi import Request, HTTPException

UPLOAD_DIR = Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)




# helper: extract JWT from request
def get_access_token_from_request(request: Request) -> str:
    """
    Incomming request ==> Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123.def456
    Read the header ===> auth_header == "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123.def456"
    split by space:
    [
    "Bearer",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123.def456"
    ]
    take the index 1 ==> "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123.def456"
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return auth_header.split(" ")[1]






# Initail state for the graph
async def prepare_initial_state(pdf, question: str, request: Request):
    """ 
    Prepares the state for RAG graph.
    - Saves PDF
    - Generates doc_id
    - Gets user_id from Supabase access token
    """
    # path to store uploaded pdf
    pdf_path = UPLOAD_DIR / pdf.filename

    # load the pdf as async
    async with aiofiles.open(pdf_path, "wb") as f:
        while chunk := await pdf.read(1024 * 1024):
            await f.write(chunk)

    # generate doc_id, thread id
    doc_id = get_file_hash(str(pdf_path))  # generate unique doc id based on file content using get_file_hash funciton
    thread_id = str(uuid.uuid4())  # genearate thread id for the conversation

    # Extract access token(JWT) from request headers
    access_token = get_access_token_from_request(request)

    # Get user info from Supabase
    user_response = supabase_client.auth.get_user(access_token)
    user_id = user_response.user.id
    
    # Use user-based collection name for multi-PDF support
    collection_name = f"user_{user_id}"

    # Fetch custom prompt for this user (if exists)
    custom_prompt = None
    try:
        settings_response = supabase_client.table("user_settings") \
            .select("custom_prompt") \
            .eq("user_id", str(user_id)) \
            .limit(1) \
            .execute()
        if settings_response.data and len(settings_response.data) > 0:
            custom_prompt = settings_response.data[0].get("custom_prompt")
    except Exception:
        pass  # Use default prompt if fetch fails
    
    # Prepare state
    state = {
        "user_id": user_id,   # unique user id from supbase
        "documents_path": str(pdf_path),
        "doc_ids": [doc_id],  # array of doc_ids for multi-PDF support
        "collection_name": collection_name,
        "messages": [HumanMessage(content=question)],
        "summary": "",
        "custom_prompt": custom_prompt  # User's custom prompt (None = use default)
    }

    return state, thread_id, [doc_id]  # Changed: return array





# filename = "Legal Case.pdf"
# parts = filename.rsplit(".", 1)
# print(parts)
# ['Legal Case', 'pdf']

# multiple dots file
# filename = "my.important.document.pdf"
# parts = filename.rsplit(".", 1)
# print(parts)
# ['my.important.document', 'pdf']