import logging
from pathlib import Path
from typing import Dict, Any

import mlflow
from langchain_core.messages import SystemMessage, HumanMessage

from app.research.parallel_research import run_company_research

logger = logging.getLogger(__name__)
from app.llm.prompts import (
    COMPANY_EVAL_SYSTEM_PROMPT,
    PERSONAL_FIT_SYSTEM_PROMPT,
    RESUME_ATS_SYSTEM_PROMPT,
    company_eval_user_prompt,
    personal_fit_user_prompt,
    resume_user_prompt,
)

from app.llm.gemini_client import (
    get_company_eval_llm,
    get_personal_fit_llm,
    get_resume_suggestions_llm,
)

from app.models.output_models import (
    CompanyEvaluation,
    PersonalFit,
    ResumeSuggestions,
)


# ------------------------------------------------
# Utility: Load Knowledge Base Files
# ------------------------------------------------

def load_resume() -> str:
    """Load sanitized master resume."""
    return Path("knowledge/resume_master.md").read_text()


def load_framework() -> str:
    """Load company assessment framework."""
    return Path("knowledge/company_assessment_framework.md").read_text()


# ------------------------------------------------
# Node 1 — Tavily Research Node
# ------------------------------------------------

async def research_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Heavy research node responsible for collecting all company
    intelligence using Tavily async search across evaluation metrics.
    """

    company = state["company_name"]
    role = state["job_role"]
    salary = state["salary_expectation"]

    logger.info(f"=== [RESEARCH NODE] Starting ===")
    logger.info(f"Company: {company}, Role: {role}, Salary: {salary}")

    with mlflow.start_run(run_name="tavily_research_node", nested=True):

        mlflow.log_param("company", company)
        mlflow.log_param("role", role)
        mlflow.log_param("salary", salary)

        logger.info(f"[RESEARCH NODE] Initiating Tavily research queries...")
        
        research_results = await run_company_research(
            company=company,
            role=role,
            salary=salary
        )

        num_metrics = len(research_results)
        total_results = sum(len(results) for results in research_results.values())
        
        logger.info(f"[RESEARCH NODE] Research complete: {num_metrics} metrics, {total_results} total result sets")
        mlflow.log_metric("research_metrics_collected", num_metrics)
        mlflow.log_metric("research_total_results", total_results)

        logger.info(f"=== [RESEARCH NODE] Completed ===")
        
        return {
            "research_results": research_results
        }


# ------------------------------------------------
# Node 2 — Company Evaluation Node
# ------------------------------------------------

async def company_eval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate company against research framework with structured output.
    """

    logger.info(f"=== [COMPANY EVAL NODE] Starting ===")
    company_name = state.get("company_name", "Unknown")
    logger.info(f"Company: {company_name}")

    with mlflow.start_run(run_name="company_evaluation_node", nested=True):

        logger.info(f"[COMPANY EVAL NODE] Loading framework...")
        framework = load_framework()
        logger.debug(f"[COMPANY EVAL NODE] Framework loaded, length: {len(framework)}")

        prompt_context = {
            "company_name": state["company_name"],
            "company_url": state["company_url"],
            "job_role": state["job_role"],
            "salary_expectation": state["salary_expectation"],
            "framework": framework,
            "research": state["research_results"],
        }

        logger.info(f"[COMPANY EVAL NODE] Building user prompt...")
        user_prompt = company_eval_user_prompt(prompt_context)
        logger.debug(f"[COMPANY EVAL NODE] Prompt length: {len(user_prompt)}")
        
        messages = [
            SystemMessage(content=COMPANY_EVAL_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        logger.info(f"[COMPANY EVAL NODE] Loading LLM client...")
        structured_llm = get_company_eval_llm()
        logger.info(f"[COMPANY EVAL NODE] LLM client loaded")

        try:
            logger.info(f"[COMPANY EVAL NODE] Invoking LLM for company evaluation...")
            # LLM returns validated CompanyEvaluation object
            evaluation = await structured_llm.ainvoke(messages)

            logger.info(f"[COMPANY EVAL NODE] LLM evaluation completed")
            logger.info(f"[COMPANY EVAL NODE] Evaluation metrics count: {len(evaluation.evaluation_metrics)}")
            
            mlflow.log_metric(
                "company_metrics_evaluated",
                len(evaluation.evaluation_metrics)
            )

            logger.info(f"=== [COMPANY EVAL NODE] Completed ===")

            return {
                "company_eval": evaluation.model_dump()
            }

        except Exception as e:
            logger.error(f"[COMPANY EVAL NODE] ERROR - {str(e)}", exc_info=True)

# ------------------------------------------------
# Node 3 — Personal Fit Evaluation
# ------------------------------------------------

async def personal_fit_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate candidate alignment with company and role with structured output.
    """

    logger.info(f"=== [PERSONAL FIT NODE] Starting ===")
    logger.info(f"Role: {state.get('job_role', 'Unknown')}")

    with mlflow.start_run(run_name="personal_fit_node", nested=True):

        logger.info(f"[PERSONAL FIT NODE] Loading resume...")
        resume = load_resume()
        logger.debug(f"[PERSONAL FIT NODE] Resume loaded, length: {len(resume)}")

        prompt_context = {
            "resume": resume,
            "job_description": state["job_description"],
            "research": state["research_results"],
            "job_role": state["job_role"],
            "salary_expectation": state["salary_expectation"],
        }

        logger.info(f"[PERSONAL FIT NODE] Building user prompt...")
        user_prompt = personal_fit_user_prompt(prompt_context)
        logger.debug(f"[PERSONAL FIT NODE] Prompt length: {len(user_prompt)}")
        
        messages = [
            SystemMessage(content=PERSONAL_FIT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        logger.info(f"[PERSONAL FIT NODE] Loading LLM client...")
        structured_llm = get_personal_fit_llm()
        logger.info(f"[PERSONAL FIT NODE] LLM client loaded")

        try:
            logger.info(f"[PERSONAL FIT NODE] Invoking LLM for personal fit analysis...")
            # LLM returns validated PersonalFit object
            fit_analysis = await structured_llm.ainvoke(messages)

            logger.info(f"[PERSONAL FIT NODE] LLM analysis completed")
            logger.info(f"[PERSONAL FIT NODE] Personal fit score: {fit_analysis.personal_fit_score}")

            mlflow.log_metric(
                "personal_fit_score",
                fit_analysis.personal_fit_score
            )

            logger.info(f"=== [PERSONAL FIT NODE] Completed ===")

            return {
                "personal_fit": fit_analysis.model_dump()
            }

        except Exception as e:
            logger.error(f"[PERSONAL FIT NODE] ERROR - {str(e)}", exc_info=True)
            mlflow.log_param("personal_fit_error", str(e))
            raise RuntimeError(
                f"Personal fit analysis failed: {e}"
            )


# ------------------------------------------------
# Node 4 — Resume Optimization Node
# ------------------------------------------------

async def resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate ATS optimization suggestions and resume improvements with structured output.
    """

    logger.info(f"=== [RESUME OPTIMIZER NODE] Starting ===")
    logger.info(f"Company: {state.get('company_name', 'Unknown')}, Role: {state.get('job_role', 'Unknown')}")

    with mlflow.start_run(run_name="resume_optimizer_node", nested=True):

        logger.info(f"[RESUME OPTIMIZER NODE] Loading resume...")
        resume = load_resume()
        logger.debug(f"[RESUME OPTIMIZER NODE] Resume loaded, length: {len(resume)}")

        prompt_context = {
            "resume": resume,
            "job_description": state["job_description"],
            "company_name": state["company_name"],
            "job_role": state["job_role"],
            "company_eval": state["company_eval"],
            "personal_fit": state["personal_fit"],
        }

        logger.info(f"[RESUME OPTIMIZER NODE] Building user prompt...")
        user_prompt = resume_user_prompt(prompt_context)
        logger.debug(f"[RESUME OPTIMIZER NODE] Prompt length: {len(user_prompt)}")
        
        messages = [
            SystemMessage(content=RESUME_ATS_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        logger.info(f"[RESUME OPTIMIZER NODE] Loading LLM client...")
        structured_llm = get_resume_suggestions_llm()
        logger.info(f"[RESUME OPTIMIZER NODE] LLM client loaded")

        try:
            logger.info(f"[RESUME OPTIMIZER NODE] Invoking LLM for resume optimization...")
            # LLM returns validated ResumeSuggestions object
            suggestions = await structured_llm.ainvoke(messages)

            logger.info(f"[RESUME OPTIMIZER NODE] LLM optimization completed")
            logger.info(f"[RESUME OPTIMIZER NODE] Resume improvements generated: {len(suggestions.improved_bullets)} bullets")

            mlflow.log_metric(
                "resume_improvements",
                len(suggestions.improved_bullets)
            )

            logger.info(f"=== [RESUME OPTIMIZER NODE] Completed ===")

            return {
                "resume_suggestions": suggestions.model_dump()
            }

        except Exception as e:
            logger.error(f"[RESUME OPTIMIZER NODE] ERROR - {str(e)}", exc_info=True)
            mlflow.log_param("resume_optimizer_error", str(e))
            raise RuntimeError(
                f"Resume optimization failed: {e}"
            )