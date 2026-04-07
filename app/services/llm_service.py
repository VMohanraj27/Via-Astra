import logging
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY
from app.models.output_models import (
    CompanyEvaluation,
    PersonalFit,
    ResumeSuggestions,
    CompanyFitReport,
    Recommendation,
)

logger = logging.getLogger(__name__)

# Available models in priority order
AVAILABLE_MODELS = [
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


class ModelSelector:
    """
    Manages round-robin model selection with fallback on API errors.
    """
    
    def __init__(self, model_list: List[str] = None):
        """
        Initialize model selector.
        
        Args:
            model_list: List of available models (defaults to AVAILABLE_MODELS)
        """
        self.models = model_list if model_list else AVAILABLE_MODELS
        self.current_index = 0
        self.failed_models = set()
        logger.info(f"ModelSelector initialized with models: {self.models}")
    
    def get_next_model(self) -> str:
        """
        Get next available model in round-robin fashion.
        Skips failed models.
        
        Returns:
            Model name
        """
        available = [m for m in self.models if m not in self.failed_models]
        
        if not available:
            logger.warning("All models failed, resetting failed set")
            self.failed_models.clear()
            available = self.models
        
        model = available[self.current_index % len(available)]
        self.current_index = (self.current_index + 1) % len(available)
        
        logger.info(f"ModelSelector: Using model {model}")
        return model
    
    def mark_failed(self, model: str) -> None:
        """
        Mark model as failed (e.g., due to 429 error).
        
        Args:
            model: Model name
        """
        self.failed_models.add(model)
        logger.warning(f"ModelSelector: Marked {model} as failed. Failed models: {self.failed_models}")
    
    def reset(self) -> None:
        """Reset model selector state."""
        self.current_index = 0
        self.failed_models.clear()
        logger.info("ModelSelector: Reset")


class LLMService:
    """
    Service layer for LLM operations with model selection and error handling.
    """
    
    def __init__(self, model_list: List[str] = None, max_retries: int = 3):
        """
        Initialize LLM service.
        
        Args:
            model_list: List of models to use
            max_retries: Maximum retries before giving up
        """
        self.model_selector = ModelSelector(model_list)
        self.max_retries = max_retries
    
    def _create_llm(self, model: str):
        """
        Create LLM instance for specified model.
        
        Args:
            model: Model name
            
        Returns:
            ChatGoogleGenerativeAI instance
        """
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=GOOGLE_API_KEY
        )
    
    def get_structured_llm(self, pydantic_schema, retry_count: int = 0):
        """
        Get LLM configured for structured output with automatic retry on failures.
        
        Args:
            pydantic_schema: Pydantic model for output validation
            retry_count: Current retry count (internal)
            
        Returns:
            Structured LLM instance
            
        Raises:
            Exception: If all models fail after max retries
        """
        if retry_count > self.max_retries:
            raise Exception(
                f"All models exhausted after {self.max_retries} retries. "
                f"Failed models: {self.model_selector.failed_models}"
            )
        
        model = self.model_selector.get_next_model()
        llm = self._create_llm(model)
        
        try:
            structured_llm = llm.with_structured_output(pydantic_schema, method="json_mode")
            logger.info(f"LLMService: Created structured LLM with model {model}")
            return structured_llm
        
        except Exception as e:
            error_msg = str(e)
            
            # Check for 429 (rate limit) error
            if "429" in error_msg or "rate limit" in error_msg.lower():
                logger.warning(f"LLMService: 429 error on {model}, marking as failed")
                self.model_selector.mark_failed(model)
                return self.get_structured_llm(pydantic_schema, retry_count + 1)
            
            # For other errors, still try next model but log it
            logger.warning(f"LLMService: Error on {model}: {error_msg}, trying next model")
            self.model_selector.mark_failed(model)
            return self.get_structured_llm(pydantic_schema, retry_count + 1)
    
    def get_company_eval_llm(self):
        """Get LLM for company evaluation (CompanyEvaluation output)."""
        return self.get_structured_llm(CompanyEvaluation)
    
    def get_personal_fit_llm(self):
        """Get LLM for personal fit evaluation (PersonalFit output)."""
        return self.get_structured_llm(PersonalFit)
    
    def get_resume_suggestions_llm(self):
        """Get LLM for resume suggestions (ResumeSuggestions output)."""
        return self.get_structured_llm(ResumeSuggestions)
    
    def get_company_fit_report_llm(self):
        """Get LLM for complete company fit report (CompanyFitReport output)."""
        return self.get_structured_llm(CompanyFitReport)
    
    def get_recommendation_llm(self):
        """Get LLM for final recommendation (Recommendation output)."""
        return self.get_structured_llm(Recommendation)
    
    def reset(self) -> None:
        """Reset model selector."""
        self.model_selector.reset()


# Global instance
_llm_service_instance: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance."""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
