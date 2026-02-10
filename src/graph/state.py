import os
from typing import TypedDict, Annotated,Dict,Any,List
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict,total=False):
    documents_path:str
    documents:List[Document]
    chunks:List[Document] 
    collection_name:str
    retrieved_docs:List[Document]
    context: str 
    answer:str
    messages: Annotated[list[BaseMessage], add_messages]
    doc_ids:List[str]  # Array of doc_ids for multi-PDF support
    existing_doc_ids: List[str]  # Doc IDs that already exist in vectorstore
    new_doc_ids: List[str]  # Doc IDs that need ingestion
    user_id:str   # for tenant isolation
    summary:str
    vectorstore_uploaded:bool
    rewritten_query:str
    token_usage: Dict[str, Any]
    custom_prompt: str  # User's custom prompt

    
    retrieval_confidence: float  # CRAG: ratio of relevant docs (0.0–1.0)
    crag_retries: int  # CRAG: retry counter (max 1)