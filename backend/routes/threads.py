from fastapi import HTTPException
from src.db_connection.connection import supabase_client
from fastapi import APIRouter


router = APIRouter()

# ============================= Load Thread Messages =============================

async def load_thread_messages(thread_id: str):
    response = (
        supabase_client
        .table("threads")
        .select("messages, doc_id")
        .eq("thread_id", thread_id)
        .single()
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    return response.data["messages"], response.data["doc_id"]





@router.get("/all_threads")
async def get_all_threads():
    """Get all threads with previews"""
    try:
        response = (
            supabase_client
            .table("threads")
            .select("thread_id, doc_id, messages")
            .execute()
        )
        
        threads = []
        if response.data:
            for thread in response.data:
                messages = thread.get("messages", [])
                preview = "New Chat"
                if messages and len(messages) > 0:
                    preview = messages[0].get("content", "New Chat")[:50] + "..."
                
                threads.append({
                    "thread_id": thread["thread_id"],
                    "doc_id": thread["doc_id"],
                    "preview": preview
                })
        
        return threads
    except Exception as e:
        print(f"❌ Error fetching threads: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/get_threads/{thread_id}")
async def get_threads(thread_id: str):
    """Get a specific thread's data"""
    try:
        response = (
            supabase_client
            .table("threads")
            .select("*")
            .eq("thread_id", thread_id)
            .single()
            .execute()
        )
        
        if response.data:
            return {
                "thread_id": response.data["thread_id"],
                "doc_id": response.data["doc_id"],
                "messages": response.data["messages"]
            }
        else:
            raise HTTPException(status_code=404, detail="Thread not found")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Thread not found: {str(e)}")