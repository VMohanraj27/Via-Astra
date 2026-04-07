import mlflow

from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY, MODEL_NAME
from app.models.output_models import (
    CompanyEvaluation,
    PersonalFit,
    ResumeSuggestions,
    CompanyFitReport,
    Recommendation,
)

mlflow.gemini.autolog()

def get_llm():
    """Initialize base LLM instance."""
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY
    )
    return llm


def get_structured_llm(pydantic_schema):
    """
    Get LLM configured for structured output.
    
    Args:
        pydantic_schema: Pydantic model class for output validation
        
    Returns:
        LLM instance configured with structured output
    """
    llm = get_llm()
    return llm.with_structured_output(pydantic_schema, method="json_mode")


def get_company_eval_llm():
    """Get LLM structured for CompanyEvaluation output."""
    return get_structured_llm(CompanyEvaluation)


def get_personal_fit_llm():
    """Get LLM structured for PersonalFit output."""
    return get_structured_llm(PersonalFit)


def get_resume_suggestions_llm():
    """Get LLM structured for ResumeSuggestions output."""
    return get_structured_llm(ResumeSuggestions)


def get_company_fit_report_llm():
    """Get LLM structured for CompanyFitReport output (complete report)."""
    return get_structured_llm(CompanyFitReport)


def get_recommendation_llm():
    """Get LLM structured for Recommendation output (final decision)."""
    return get_structured_llm(Recommendation)