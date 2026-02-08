from fastapi import HTTPException,Depends
from src.db_connection.connection import supabase_client
from fastapi import APIRouter
from backend.routes.auth import get_current_user

router = APIRouter()

# ============================= Load Thread Messages =============================

async def load_thread_messages(thread_id: str,user_id:str):
    response = (
        await run_in_threadpool(
        lambda:supabase_client
        .table("threads")
        .select("messages, doc_ids,summary")
        .eq("thread_id", thread_id)
        .eq("user_id",user_id)   # filter by login user id
        .single()
        .execute()
    ))
    if not response.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    return response.data["messages"], response.data["doc_ids"],response.data.get("summary","")



# ============================= Get All Threads with Previews =============================
# sidebar chats threads
@router.get("/all_threads")
async def get_all_threads(user=Depends(get_current_user)):
    """Get all threads with previews"""
    try:
        response = (
            await run_in_threadpool(
            lambda:supabase_client
            .table("threads")
            .select("thread_id, doc_ids, messages")
            .eq("user_id",user.id)  # filter by login user
            .execute()
        ))
        
        threads = []
        if response.data:
            for thread in response.data:
                messages = thread.get("messages", [])
                preview = "New Chat"
                if messages and len(messages) > 0:
                    preview = messages[0].get("content", "New Chat")[:50] + "..."
                
                threads.append({
                    "thread_id": thread["thread_id"],
                    "doc_ids": thread["doc_ids"],
                    "preview": preview
                })
        
        return threads
    except Exception as e:
        print(f"Error fetching threads: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


    
# ============================= Get Specific Thread Data =============================

@router.get("/get_threads/{thread_id}")
async def get_threads(thread_id: str,user=Depends(get_current_user)):
    """Get a specific thread's data"""
    messages, doc_ids,summary = await load_thread_messages(thread_id,user.id)
    return {
        "thread_id": thread_id,
        "doc_ids": doc_ids,
        "messages": messages
    }



# =========================== Endpoint to fetch token usage for a user from Database ===============================

from fastapi.concurrency import run_in_threadpool

@router.get("/user/tokens")
async def get_user_total_token_usage(user=Depends(get_current_user)):
    """
    Fetch TOTAL token usage across ALL threads for the current user.
    """
    try:
        response = await run_in_threadpool(
            lambda: supabase_client
            .table("usage")
            .select("total_tokens, prompt_tokens, completion_tokens")
            .eq("user_id", user.id)
            .execute()
        )

        if not response.data:
            return {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}

        # Sum all usage entries for this user across all threads
        total_tokens = sum(row.get("total_tokens", 0) or 0 for row in response.data)
        prompt_tokens = sum(row.get("prompt_tokens", 0) or 0 for row in response.data)
        completion_tokens = sum(row.get("completion_tokens", 0) or 0 for row in response.data)

        return {
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user token usage: {str(e)}")
