from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.services.llm_chat import chat_with_llm, is_llm_available, get_llm_provider
from app.services.platform_context import get_platform_context, get_llm_context

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    provider: str
    llm_enabled: bool
    

# Store conversation history (in-memory for now)
_conversations: Dict[str, List[Dict]] = {}


@router.post("/message")
async def send_message(request: ChatMessage):
    """Global chat endpoint - accessible from anywhere in the app"""
    
    # Get or create conversation history
    conv_id = request.conversation_id or "default"
    if conv_id not in _conversations:
        _conversations[conv_id] = []
    
    history = _conversations[conv_id]
    
    # Get response from LLM
    response = chat_with_llm(
        request.message,
        data_profile=None,
        recommendations=None,
        # Don't pass history to keep it simple for now
    )
    
    # Store in history
    history.append({"role": "user", "content": request.message})
    history.append({"role": "assistant", "content": response.get("answer", "")})
    
    # Keep only last 10 messages
    _conversations[conv_id] = history[-10:]
    
    return {
        "status": "success",
        "answer": response.get("answer", "Sorry, I couldn't process that."),
        "provider": response.get("provider", "unknown"),
        "llm_enabled": is_llm_available()
    }


@router.get("/status")
async def get_assistant_status():
    """Get AI assistant status"""
    return {
        "status": "online",
        "llm_enabled": is_llm_available(),
        "provider": get_llm_provider(),
        "capabilities": [
            "Answer questions about your data",
            "Recommend ML models",
            "Explain quality scores",
            "Guide model training",
            "Track uploads and history"
        ]
    }


@router.get("/context")
async def get_current_context():
    """Get current platform context (for debugging)"""
    return {
        "status": "success",
        "context": get_platform_context()
    }


@router.delete("/history/{conversation_id}")
async def clear_history(conversation_id: str = "default"):
    """Clear conversation history"""
    if conversation_id in _conversations:
        del _conversations[conversation_id]
    return {"status": "success", "message": "History cleared"}
