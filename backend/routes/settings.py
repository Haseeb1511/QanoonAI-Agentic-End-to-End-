from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional
from backend.routes.auth import get_current_user
from src.db_connection.connection import supabase_client

router = APIRouter()


class PromptUpdate(BaseModel):
    custom_prompt: Optional[str] = None


@router.get("/settings")
async def get_settings(user=Depends(get_current_user)):
    """Get user settings including custom prompt"""
    try:
        response = await run_in_threadpool(
            lambda: supabase_client.table("user_settings")
                .select("custom_prompt")
                .eq("user_id", str(user.id))
                .limit(1)
                .execute()
        )
        
        custom_prompt = None # default value
        if response.data and len(response.data) > 0:
            custom_prompt = response.data[0].get("custom_prompt")
        
        # it return thises 3 values and we display them in frontend
        return {
            "email": user.email,
            "user_id": str(user.id),
            "custom_prompt": custom_prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/settings/prompt")
async def save_prompt(data: PromptUpdate, user=Depends(get_current_user)):
    """Save or update user's custom prompt"""
    try:
        # Upsert: insert if not exists, update if exists
        await run_in_threadpool(
            lambda: supabase_client.table("user_settings")
                .upsert({
                    "user_id": str(user.id),
                    "custom_prompt": data.custom_prompt,
                    "updated_at": "now()"
                })
                .execute()
        )
        return {"success": True, "message": "Prompt saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/settings/prompt")
async def reset_prompt(user=Depends(get_current_user)):
    """Reset custom prompt to default (delete user's custom prompt)"""
    try:
        await run_in_threadpool(
            lambda: supabase_client.table("user_settings")
                .update({"custom_prompt": None, "updated_at": "now()"})
                .eq("user_id", str(user.id))
                .execute()
        )
        return {"success": True, "message": "Prompt reset to default"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
