import logging
from typing import Dict, Any
from datetime import datetime

# Import models for type conversion
from app.models.output_models import (
    CompanyEvaluation,
    PersonalFit,
    ResumeSuggestions,
    Recommendation,
)
    
from app.services.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)


# ------------------------------------------------
# Node 1 — Research Node (using Repository)
# ------------------------------------------------

async def research_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Research node using EvaluationService and cache.
    Awaits async get_research() method call.
    """
    company = state["company_name"]
    role = state["job_role"]
    salary = state["salary_expectation"]

    logger.info(f"=== [RESEARCH NODE] Starting ===")
    logger.info(f"Company: {company}, Role: {role}, Salary: {salary}")

    # Await the async get_research call
    research_results = await EvaluationService.get_research(company, role, salary)

    logger.info(f"=== [RESEARCH NODE] Completed ===")
    
    return {
        "research_results": research_results
    }


# ------------------------------------------------
# Node 2 — Company Evaluation Node
# ------------------------------------------------

async def company_eval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate company using EvaluationService.
    Awaits async evaluate_company() method call.
    """
    logger.info(f"=== [COMPANY EVAL NODE] Starting ===")
    company_name = state.get("company_name", "Unknown")
    logger.info(f"Company: {company_name}")

    # Await the async evaluate_company call
    evaluation = await EvaluationService.evaluate_company(
        state["company_name"],
        state["company_url"],
        state["job_role"],
        state["salary_expectation"],
        state["research_results"]
    )

    logger.info(f"=== [COMPANY EVAL NODE] Completed ===")

    return {
        "company_eval": evaluation
    }


# ------------------------------------------------
# Node 3 — Personal Fit Node
# ------------------------------------------------

async def personal_fit_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate personal fit using EvaluationService.
    Awaits async evaluate_personal_fit() method call.
    """
    logger.info(f"=== [PERSONAL FIT NODE] Starting ===")

    # Await the async evaluate_personal_fit call
    fit = await EvaluationService.evaluate_personal_fit(
        state["company_name"],
        state["job_role"],
        state["job_description"],
        state["salary_expectation"],
        state["company_eval"],
        state["research_results"]
    )

    logger.info(f"=== [PERSONAL FIT NODE] Completed ===")

    return {
        "personal_fit": fit
    }


# ------------------------------------------------
# Node 4 — Resume Optimization Node
# ------------------------------------------------

async def resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate resume suggestions using EvaluationService.
    Awaits async suggest_resume_improvements() method call.
    """
    logger.info(f"=== [RESUME OPT NODE] Starting ===")

    # Await the async suggest_resume_improvements call
    suggestions = await EvaluationService.suggest_resume_improvements(
        state["company_name"],
        state["job_role"],
        state["job_description"],
        state["company_eval"],
        state["personal_fit"]
    )

    logger.info(f"=== [RESUME OPT NODE] Completed ===")

    return {
        "resume_suggestions": suggestions
    }


# ------------------------------------------------
# Node 5 — Recommendation Node (NEW)
# ------------------------------------------------

async def recommendation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final recommendation using EvaluationService.
    Synthesizes all evaluations into a final decision.
    Awaits async generate_recommendation() method call.
    """
    logger.info(f"=== [RECOMMENDATION NODE] Starting ===")

    # Extract company evaluation for metrics
    company_eval = state.get("company_eval", {})
    company_score = company_eval.get("overall_score", 0)
    
    # Extract personal fit score
    personal_fit = state.get("personal_fit", {})
    personal_fit_score = int(personal_fit.get("personal_fit_score", 0))
    
    # Extract resume alignment score
    resume_sug = state.get("resume_suggestions", {})
    resume_score = resume_sug.get("resume_alignment_score", 0)

    # Await the async generate_recommendation call
    recommendation = await EvaluationService.generate_recommendation(
        state["company_name"],
        state["job_role"],
        company_score,
        personal_fit_score,
        resume_score,
        company_eval,
        personal_fit
    )

    logger.info(f"=== [RECOMMENDATION NODE] Completed ===")

    return {
        "recommendation": recommendation
    }


# ------------------------------------------------
# Node 6 — Final Report Generation Node (NEW)
# ------------------------------------------------

async def report_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate all evaluations into a final CompanyFitReport.
    Combines company eval, personal fit, resume suggestions, and recommendation.
    """
    logger.info(f"=== [REPORT GENERATION NODE] Starting ===")

    generated_date = datetime.now().strftime("%B %Y")
    
  
    # Convert dicts to models for type safety
    company_eval = state.get("company_eval", {})
    personal_fit = state.get("personal_fit", {})
    resume_suggestions = state.get("resume_suggestions", {})
    recommendation = state.get("recommendation", {})
    
    # Generate final aggregated report
    final_report = EvaluationService.generate_final_report(
        state["company_name"],
        generated_date,
        CompanyEvaluation(**company_eval) if company_eval else CompanyEvaluation(
            metadata={}, role_applied="", overall_score=0, company_metrics=[], technology_stack=[]
        ),
        PersonalFit(**personal_fit) if personal_fit else PersonalFit(
            personal_fit_score=0, strengths_match=[], skill_gaps=[], career_growth_assessment="", final_recommendation=""
        ),
        ResumeSuggestions(**resume_suggestions) if resume_suggestions else ResumeSuggestions(
            resume_alignment_score=0, resume_gaps=[], resume_recommendations=[], interview_questions={}
        ),
        Recommendation(**recommendation) if recommendation else Recommendation(
            decision="Consider", reason="Insufficient data"
        )
    )

    logger.info(f"=== [REPORT GENERATION NODE] Completed ===")

    return {
        "final_report": final_report.model_dump()
    }