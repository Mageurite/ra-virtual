"""
LLM Chat Service
Simplified LLM service based on mageurite implementation
Supports streaming chat with optional RAG integration
"""
import asyncio
import logging
from typing import AsyncIterator, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from functools import lru_cache

from llm.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMChatService:
    """LLM Chat Service with streaming support"""
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or config.DEFAULT_MODEL
        self._llm = None
    
    @property
    def llm(self):
        """Lazy load LLM instance"""
        if self._llm is None:
            self._llm = ChatOllama(
                model=self.model,
                base_url=config.OLLAMA_BASE_URL,
                temperature=config.TEMPERATURE,
                disable_streaming=not config.ENABLE_STREAMING,
            )
        return self._llm
    
    def format_conversation_history(
        self, 
        messages: list[dict],
        max_turns: int = None
    ) -> list:
        """
        Format conversation history for LLM
        
        Args:
            messages: List of {"role": "user"|"assistant", "content": str}
            max_turns: Maximum number of conversation turns to keep
        
        Returns:
            List of LangChain message objects
        """
        max_turns = max_turns or config.MAX_HISTORY_TURNS
        
        # Keep last N turns (user + assistant pairs)
        recent_messages = messages[-(max_turns * 2):]
        
        formatted = []
        for msg in recent_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "user":
                formatted.append(HumanMessage(content=content))
            elif role == "assistant":
                formatted.append(AIMessage(content=content))
            elif role == "system":
                formatted.append(SystemMessage(content=content))
        
        return formatted
    
    async def chat_completion(
        self,
        message: str,
        conversation_history: Optional[list[dict]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Non-streaming chat completion
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            system_prompt: Optional system prompt
        
        Returns:
            AI response text
        """
        try:
            # Build messages
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            if conversation_history:
                messages.extend(self.format_conversation_history(conversation_history))
            
            messages.append(HumanMessage(content=message))
            
            # Get response
            response = await self.llm.ainvoke(messages)
            
            return response.content
            
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise
    
    async def chat_stream(
        self,
        message: str,
        conversation_history: Optional[list[dict]] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Streaming chat completion
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            system_prompt: Optional system prompt
        
        Yields:
            Text chunks as they are generated
        """
        try:
            # Build messages
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            if conversation_history:
                messages.extend(self.format_conversation_history(conversation_history))
            
            messages.append(HumanMessage(content=message))
            
            # Stream response
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)
                    
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield f"Error: {str(e)}"
    
    async def chat_with_rag(
        self,
        message: str,
        user_id: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> str:
        """
        Chat with RAG (Retrieval Augmented Generation)
        Requires RAG service to be running
        
        Args:
            message: User message
            user_id: User ID for personal knowledge retrieval
            conversation_history: Previous conversation messages
        
        Returns:
            AI response with RAG context
        """
        if not config.RAG_ENABLED:
            logger.warning("RAG is disabled, falling back to normal chat")
            return await self.chat_completion(message, conversation_history)
        
        try:
            import httpx
            
            # Query RAG service
            async with httpx.AsyncClient(timeout=30.0) as client:
                rag_response = await client.post(
                    f"{config.RAG_SERVICE_URL}/retriever",
                    json={
                        "user_id": user_id,
                        "query": message,
                        "personal_k": config.RAG_TOP_K,
                        "public_k": config.RAG_TOP_K,
                    }
                )
                
                if rag_response.status_code == 200:
                    rag_data = rag_response.json()
                    retrieved_docs = rag_data.get("final_results", [])
                    
                    # Build context from retrieved documents
                    context = "\n\n".join([
                        f"Document {i+1}:\n{doc.get('page_content', '')}"
                        for i, doc in enumerate(retrieved_docs[:5])
                    ])
                    
                    # Build RAG prompt
                    rag_prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.

Context:
{context}

User Question: {message}

Provide a clear and helpful answer based on the context above. If the context doesn't contain relevant information, say so and provide a general response."""
                    
                    return await self.chat_completion(
                        rag_prompt,
                        conversation_history=conversation_history
                    )
                else:
                    logger.warning(f"RAG service returned {rag_response.status_code}, falling back to normal chat")
                    return await self.chat_completion(message, conversation_history)
                    
        except Exception as e:
            logger.error(f"RAG chat error: {e}, falling back to normal chat")
            return await self.chat_completion(message, conversation_history)


# Guardrail functions (optional)
class ContentGuardrail:
    """Content safety guardrail"""
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or config.DEFAULT_MODEL
        self.llm = ChatOllama(
            model=self.model,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.0,  # Use 0 for classification
        )
    
    async def classify_content(self, message: str) -> tuple[str, bool]:
        """
        Classify content safety
        
        Returns:
            (classification, is_safe)
            classification: "normal" | "homework_request" | "harmful"
            is_safe: True if normal, False otherwise
        """
        if not config.GUARDRAIL_ENABLED:
            return "normal", True
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a content classifier. Classify the input into one of:
                
1. "normal" - appropriate academic questions, general queries
2. "homework_request" - requests for direct assignment answers or solutions
3. "harmful" - inappropriate, explicit, or harmful content

Respond with ONLY ONE WORD: normal, homework_request, or harmful."""),
                ("user", "{input}")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            result = await chain.ainvoke({"input": message})
            
            classification = result.strip().lower()
            is_safe = classification == "normal"
            
            logger.info(f"Content classification: {classification} (safe: {is_safe})")
            return classification, is_safe
            
        except Exception as e:
            logger.error(f"Guardrail classification error: {e}")
            # Fail-safe: allow content by default
            return "normal", True
    
    def get_blocked_response(self, classification: str) -> str:
        """Get appropriate blocked response"""
        if classification == "homework_request":
            return "I'm here to help you understand the material, but I can't provide direct answers to assignments. What concept would you like me to explain?"
        elif classification == "harmful":
            return "I'm sorry, I can't help with that request. Please ensure your questions are appropriate."
        else:
            return "Sorry, your question couldn't be processed. Please try rephrasing it."


# Singleton instances
_chat_service_instance = None
_guardrail_instance = None


def get_chat_service(model: Optional[str] = None) -> LLMChatService:
    """Get or create chat service instance"""
    global _chat_service_instance
    if _chat_service_instance is None or (model and model != _chat_service_instance.model):
        _chat_service_instance = LLMChatService(model)
    return _chat_service_instance


def get_guardrail() -> ContentGuardrail:
    """Get or create guardrail instance"""
    global _guardrail_instance
    if _guardrail_instance is None:
        _guardrail_instance = ContentGuardrail()
    return _guardrail_instance
