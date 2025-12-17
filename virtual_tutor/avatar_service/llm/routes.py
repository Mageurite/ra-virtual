"""
LLM Chat API Routes - Serverless AI Engine
Provides streaming and non-streaming chat endpoints
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import json

from llm.service import get_chat_service, get_guardrail
from llm.config import config

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request"""
    message: str = Field(..., description="User message")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None, 
        description="Previous conversation messages"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional system prompt"
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model override"
    )
    stream: bool = Field(
        default=True,
        description="Enable streaming response"
    )


class ChatResponse(BaseModel):
    """Non-streaming chat response"""
    response: str
    model: str


class RAGChatRequest(BaseModel):
    """Chat request with RAG"""
    message: str
    user_id: str = Field(..., description="User ID for personal knowledge")
    conversation_history: Optional[List[ChatMessage]] = None
    model: Optional[str] = None


# ============================================================================
# Chat Endpoints
# ============================================================================

@router.post("/completion")
async def chat_completion(request: ChatRequest):
    """
    Non-streaming chat completion
    
    Example:
    ```json
    {
        "message": "What is machine learning?",
        "conversation_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ]
    }
    ```
    """
    try:
        # Get chat service
        chat_service = get_chat_service(request.model)
        
        # Check guardrail
        if config.GUARDRAIL_ENABLED:
            guardrail = get_guardrail()
            classification, is_safe = await guardrail.classify_content(request.message)
            
            if not is_safe:
                blocked_response = guardrail.get_blocked_response(classification)
                return ChatResponse(
                    response=blocked_response,
                    model=request.model or config.DEFAULT_MODEL
                )
        
        # Format history
        history = None
        if request.conversation_history:
            history = [msg.model_dump() for msg in request.conversation_history]
        
        # Get response
        response = await chat_service.chat_completion(
            message=request.message,
            conversation_history=history,
            system_prompt=request.system_prompt
        )
        
        return ChatResponse(
            response=response,
            model=request.model or config.DEFAULT_MODEL
        )
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat completion
    
    Returns:
        Server-Sent Events (SSE) stream of text chunks
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/chat/stream" \\
      -H "Content-Type: application/json" \\
      -d '{"message": "Tell me a story", "stream": true}'
    ```
    """
    try:
        # Get chat service
        chat_service = get_chat_service(request.model)
        
        # Check guardrail
        if config.GUARDRAIL_ENABLED:
            guardrail = get_guardrail()
            classification, is_safe = await guardrail.classify_content(request.message)
            
            if not is_safe:
                blocked_response = guardrail.get_blocked_response(classification)
                
                async def blocked_stream():
                    yield f"data: {json.dumps({'chunk': blocked_response})}\n\n"
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(
                    blocked_stream(),
                    media_type="text/event-stream"
                )
        
        # Format history
        history = None
        if request.conversation_history:
            history = [msg.model_dump() for msg in request.conversation_history]
        
        # Stream response
        async def generate():
            try:
                async for chunk in chat_service.chat_stream(
                    message=request.message,
                    conversation_history=history,
                    system_prompt=request.system_prompt
                ):
                    # Send as SSE format
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Send completion marker
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Stream generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Chat stream error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stream error: {str(e)}"
        )


@router.post("/rag", response_model=ChatResponse)
async def chat_with_rag(request: RAGChatRequest):
    """
    Chat with RAG (Retrieval Augmented Generation)
    Requires RAG service to be running
    
    Example:
    ```json
    {
        "message": "What did the professor say about neural networks?",
        "user_id": "student123",
        "conversation_history": []
    }
    ```
    """
    if not config.RAG_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service is not enabled"
        )
    
    try:
        # Get chat service
        chat_service = get_chat_service(request.model)
        
        # Format history
        history = None
        if request.conversation_history:
            history = [msg.model_dump() for msg in request.conversation_history]
        
        # Get RAG response
        response = await chat_service.chat_with_rag(
            message=request.message,
            user_id=request.user_id,
            conversation_history=history
        )
        
        return ChatResponse(
            response=response,
            model=request.model or config.DEFAULT_MODEL
        )
        
    except Exception as e:
        logger.error(f"RAG chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG chat error: {str(e)}"
        )


# ============================================================================
# Model Management
# ============================================================================

@router.get("/models")
async def list_models():
    """
    List available LLM models from Ollama
    
    Returns:
    ```json
    {
        "models": ["mistral-nemo:12b", "llama3.1:8b"],
        "default": "mistral-nemo:12b"
    }
    ```
    """
    try:
        models = config.get_available_models()
        return {
            "models": models,
            "default": config.DEFAULT_MODEL
        }
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return {
            "models": [config.DEFAULT_MODEL, config.FALLBACK_MODEL],
            "default": config.DEFAULT_MODEL
        }


@router.get("/health")
async def health_check():
    """
    Health check for LLM service
    """
    try:
        is_healthy = config.validate()
        if is_healthy:
            return {
                "status": "healthy",
                "ollama_url": config.OLLAMA_BASE_URL,
                "default_model": config.DEFAULT_MODEL
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ollama service is not available"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )
