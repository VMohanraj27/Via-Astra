import logging
from typing import Dict, Any

from app.services.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)


# ------------------------------------------------
# Node 1 — Research Node (using Repository)
# ------------------------------------------------

async def research_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Research node using EvaluationService and cache.
    """
    company = state["company_name"]
    role = state["job_role"]
    salary = state["salary_expectation"]

    logger.info(f"=== [RESEARCH NODE] Starting ===")
    logger.info(f"Company: {company}, Role: {role}, Salary: {salary}")

    research_results = EvaluationService.get_research(company, role, salary)

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
    """
    logger.info(f"=== [COMPANY EVAL NODE] Starting ===")
    company_name = state.get("company_name", "Unknown")
    logger.info(f"Company: {company_name}")

    evaluation = EvaluationService.evaluate_company(
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
    """
    logger.info(f"=== [PERSONAL FIT NODE] Starting ===")

    fit = EvaluationService.evaluate_personal_fit(
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
    """
    logger.info(f"=== [RESUME OPT NODE] Starting ===")

    suggestions = EvaluationService.suggest_resume_improvements(
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