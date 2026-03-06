from pathlib import Path
from typing import Dict, Any

import mlflow
from langchain_core.messages import SystemMessage, HumanMessage

from app.research.parallel_research import run_company_research
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

    with mlflow.start_run(run_name="tavily_research_node", nested=True):

        mlflow.log_param("company", company)
        mlflow.log_param("role", role)

        research_results = await run_company_research(
            company=company,
            role=role,
            salary=salary
        )

        mlflow.log_metric("research_metrics_collected", len(research_results))

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

    with mlflow.start_run(run_name="company_evaluation_node", nested=True):

        framework = load_framework()

        prompt_context = {
            "company_name": state["company_name"],
            "company_url": state["company_url"],
            "job_role": state["job_role"],
            "salary_expectation": state["salary_expectation"],
            "framework": framework,
            "research": state["research_results"],
        }

        user_prompt = company_eval_user_prompt(prompt_context)
        
        messages = [
            SystemMessage(content=COMPANY_EVAL_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        # Get LLM configured for structured CompanyEvaluation output
        structured_llm = get_company_eval_llm()

        try:
            # LLM returns validated CompanyEvaluation object
            evaluation = await structured_llm.ainvoke(messages)

            mlflow.log_metric(
                "company_metrics_evaluated",
                len(evaluation.evaluation_metrics)
            )

            return {
                "company_eval": evaluation.model_dump()
            }

        except Exception as e:
            mlflow.log_param("company_eval_error", str(e))
            raise RuntimeError(
                f"Company evaluation failed: {e}"
            )


# ------------------------------------------------
# Node 3 — Personal Fit Evaluation
# ------------------------------------------------

async def personal_fit_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate candidate alignment with company and role with structured output.
    """

    with mlflow.start_run(run_name="personal_fit_node", nested=True):

        resume = load_resume()

        prompt_context = {
            "resume": resume,
            "job_description": state["job_description"],
            "research": state["research_results"],
            "job_role": state["job_role"],
            "salary_expectation": state["salary_expectation"],
        }

        user_prompt = personal_fit_user_prompt(prompt_context)
        
        messages = [
            SystemMessage(content=PERSONAL_FIT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        # Get LLM configured for structured PersonalFit output
        structured_llm = get_personal_fit_llm()

        try:
            # LLM returns validated PersonalFit object
            fit_analysis = await structured_llm.ainvoke(messages)

            mlflow.log_metric(
                "personal_fit_score",
                fit_analysis.personal_fit_score
            )

            return {
                "personal_fit": fit_analysis.model_dump()
            }

        except Exception as e:
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

    with mlflow.start_run(run_name="resume_optimizer_node", nested=True):

        resume = load_resume()

        prompt_context = {
            "resume": resume,
            "job_description": state["job_description"],
            "company_name": state["company_name"],
            "job_role": state["job_role"],
            "company_eval": state["company_eval"],
            "personal_fit": state["personal_fit"],
        }

        user_prompt = resume_user_prompt(prompt_context)
        
        messages = [
            SystemMessage(content=RESUME_ATS_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        # Get LLM configured for structured ResumeSuggestions output
        structured_llm = get_resume_suggestions_llm()

        try:
            # LLM returns validated ResumeSuggestions object
            suggestions = await structured_llm.ainvoke(messages)

            mlflow.log_metric(
                "resume_improvements",
                len(suggestions.improved_bullets)
            )

            return {
                "resume_suggestions": suggestions.model_dump()
            }

        except Exception as e:
            mlflow.log_param("resume_optimizer_error", str(e))
            raise RuntimeError(
                f"Resume optimization failed: {e}"
            )