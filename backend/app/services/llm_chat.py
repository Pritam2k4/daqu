"""
LLM Chat Service
Integrates Groq/OpenAI for intelligent chatbot responses
"""
import os
from typing import Dict, Any, Optional, List
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class LLMChatService:
    """
    Provides LLM-powered responses for Model Studio chatbot.
    Supports Groq (default) and OpenAI.
    """
    
    SYSTEM_PROMPT = """You are DataReady AI's Model Studio Assistant. Give SHORT, DIRECT answers.

Rules:
- Maximum 3-4 sentences per response
- Use bullet points for lists
- Be practical, skip the theory
- Bold **key terms** only

You know: XGBoost, LightGBM, CatBoost, Random Forest, Logistic/Linear Regression.

Answer questions about ML models, data quality, and the user's dataset."""

    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available LLM clients"""
        # Try Groq first (free tier available)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=groq_key)
                print("✓ Groq client initialized")
            except ImportError:
                print("Groq package not installed")
        
        # Try OpenAI as fallback
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_key)
                print("✓ OpenAI client initialized")
            except ImportError:
                print("OpenAI package not installed")
    
    def is_available(self) -> bool:
        """Check if any LLM is available"""
        return self.groq_client is not None or self.openai_client is not None
    
    def get_provider(self) -> str:
        """Get current LLM provider name"""
        if self.groq_client:
            return "groq"
        elif self.openai_client:
            return "openai"
        return "none"
    
    def chat(self, 
             user_message: str, 
             data_profile: Dict[str, Any] = None,
             recommendations: List[Dict] = None,
             conversation_history: List[Dict] = None,
             include_platform_context: bool = True) -> Dict[str, Any]:
        """
        Send a message to the LLM and get a response.
        """
        
        # Try direct answer first for platform questions
        if include_platform_context:
            try:
                from app.services.platform_context import try_direct_answer
                direct = try_direct_answer(user_message)
                if direct:
                    return {"success": True, "answer": direct, "provider": "direct"}
            except:
                pass
        
        if not self.is_available():
            return {
                "success": False,
                "error": "No LLM configured",
                "answer": "I'm in offline mode. Add GROQ_API_KEY to enable smart chat."
            }
        
        # Build context
        context_parts = []
        
        # Add platform context
        if include_platform_context:
            try:
                from app.services.platform_context import get_llm_context
                context_parts.append(get_llm_context())
            except:
                pass
        
        # Add data profile context
        if data_profile:
            context_parts.append(self._build_context(data_profile, recommendations))
        
        context = "\n".join(context_parts) if context_parts else "No data loaded."
        
        # Build messages
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "system", "content": f"CONTEXT:\n{context}"}
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            if self.groq_client:
                return self._chat_groq(messages)
            elif self.openai_client:
                return self._chat_openai(messages)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": f"Sorry, I encountered an error: {str(e)}"
            }
    
    def _build_context(self, data_profile: Dict, recommendations: List[Dict]) -> str:
        """Build context string from data profile"""
        if not data_profile:
            return "No data loaded yet."
        
        context = f"""
User's Dataset:
- Rows: {data_profile.get('rows', 'Unknown')}
- Columns: {data_profile.get('columns', 'Unknown')}
- Numeric columns: {data_profile.get('numeric_columns', 0)}
- Categorical columns: {data_profile.get('categorical_columns', 0)}
- Missing data: {data_profile.get('missing_percentage', 0)}%
- Task type: {data_profile.get('task_type', 'Unknown')}
- Target column: {data_profile.get('target_column', 'Not set')}
"""
        
        if data_profile.get('task_type') == 'classification':
            context += f"""
- Number of classes: {data_profile.get('num_classes', 'Unknown')}
- Class imbalance ratio: {data_profile.get('imbalance_ratio', 1)}:1
- Is imbalanced: {'Yes' if data_profile.get('is_imbalanced') else 'No'}
"""
        
        if recommendations:
            context += "\nCurrent Recommendations:\n"
            for rec in recommendations[:3]:
                context += f"- {rec.get('name')}: {rec.get('why', '')}\n"
        
        return context
    
    def _chat_groq(self, messages: List[Dict]) -> Dict[str, Any]:
        """Chat using Groq API"""
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast, concise model
            messages=messages,
            temperature=0.5,
            max_tokens=300  # Shorter responses
        )
        
        return {
            "success": True,
            "answer": response.choices[0].message.content,
            "provider": "groq",
            "model": "llama-3.1-8b-instant"
        }
    
    def _chat_openai(self, messages: List[Dict]) -> Dict[str, Any]:
        """Chat using OpenAI API"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        return {
            "success": True,
            "answer": response.choices[0].message.content,
            "provider": "openai",
            "model": "gpt-4o-mini"
        }
    
    def get_model_explanation(self, model_name: str, data_profile: Dict = None) -> str:
        """Get detailed explanation of a specific model"""
        prompt = f"""Explain the {model_name} model in the context of the user's data.
        
Include:
1. How it works (brief, non-technical)
2. Why it's good for their specific data
3. Key hyperparameters to consider
4. Potential pitfalls to watch for

Keep it concise (under 200 words)."""
        
        response = self.chat(prompt, data_profile)
        return response.get("answer", f"Unable to explain {model_name}")
    
    def get_data_insights(self, data_profile: Dict) -> str:
        """Get AI-generated insights about the data"""
        prompt = """Based on the data profile, provide 3-5 key insights that would help the user prepare their data for ML training.

Focus on:
- Data quality issues to address
- Feature engineering opportunities  
- Potential challenges for modeling

Be specific and actionable."""
        
        response = self.chat(prompt, data_profile)
        return response.get("answer", "Unable to generate insights")


# Global instance
llm_service = LLMChatService()


def chat_with_llm(message: str, data_profile: Dict = None, recommendations: List[Dict] = None) -> Dict[str, Any]:
    """Helper function for chatting with LLM"""
    return llm_service.chat(message, data_profile, recommendations)


def is_llm_available() -> bool:
    """Check if LLM is available"""
    return llm_service.is_available()


def get_llm_provider() -> str:
    """Get current LLM provider"""
    return llm_service.get_provider()
