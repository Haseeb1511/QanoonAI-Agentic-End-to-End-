# ============================= Log token usage =============
from tenacity import retry,stop_after_attempt,wait_exponential
from src.db_connection.connection import supabase_client
from fastapi.concurrency import run_in_threadpool

# run in threadpool ====>  Take this blocking synchronous function and run it in a separate worker thread, so it doesn’t block the event loop.
# Supabase Python client is synchronous

@retry(stop=stop_after_attempt(3),wait = wait_exponential(multiplier=1,min=2,max=10))
async def log_token_usage(user_id:str,doc_id:str,thread_id:str,token_usage:dict):
    """
    Background task to log token usage to Supabase with retry logic.
    """
    print(f"BACKGROUND TASK STARTED ") 
    try:
        await run_in_threadpool(
            lambda: supabase_client.table("usage").insert({
                "user_id": user_id,
                "doc_id": doc_id,
                "thread_id": thread_id,
                "total_tokens": token_usage["total_tokens"],
                "prompt_tokens": token_usage["prompt_tokens"],
                "completion_tokens": token_usage["completion_tokens"],
                "query": token_usage["query"],
                "answer": token_usage["answer"]
            }).execute()
        )
    except Exception as e:
        print(f"Failed to log token usage for thread {thread_id}: {e}")
        raise