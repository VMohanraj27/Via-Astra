import logging
import asyncio
from pathlib import Path
from typing import Dict, Any
import mlflow
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.llm_service import get_llm_service
from app.repositories.research_repository import ResearchRepository
from app.llm.prompts import (
    COMPANY_EVAL_SYSTEM_PROMPT,
    PERSONAL_FIT_SYSTEM_PROMPT,
    RESUME_INTERVIEW_SYSTEM_PROMPT,
    RECOMMENDATION_SYSTEM_PROMPT,
    company_eval_user_prompt,
    personal_fit_user_prompt,
    resume_interview_user_prompt,
    recommendation_user_prompt,
)
from app.models.output_models import (
    CompanyEvaluation,
    PersonalFit,
    ResumeSuggestions,
    CompanyFitReport,
    Recommendation,
)
from datetime import datetime

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Service layer for company assessment evaluation.
    Orchestrates research, evaluation, and output generation.
    """
    
    @staticmethod
    def load_resume() -> str:
        """Load sanitized master resume."""
        return Path("knowledge/resume_master.md").read_text()
    
    @staticmethod
    def load_framework() -> str:
        """Load company assessment framework."""
        return Path("knowledge/company_assessment_framework.md").read_text()
    
    @staticmethod
    async def get_research(company: str, role: str, salary: str) -> Dict[str, Any]:
        """
        Get company research from repository (async).
        
        Args:
            company: Company name
            role: Job role
            salary: Salary expectation
            
        Returns:
            Research results
        """
        logger.info(f"EvaluationService: Getting research for {company}")
        
        with mlflow.start_run(run_name="research", nested=True):
            research_results = await ResearchRepository.get_research(company, role, salary)
            
            num_metrics = len(research_results)
            total_results = sum(len(results) for results in research_results.values())
            
            mlflow.log_metric("research_metrics_collected", num_metrics)
            mlflow.log_metric("research_total_results", total_results)
            
            logger.info(f"EvaluationService: Research complete - {num_metrics} metrics, {total_results} results")
        
        return research_results
    
    @staticmethod
    async def evaluate_company(
        company_name: str,
        company_url: str,
        job_role: str,
        salary_expectation: str,
        research_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate company against framework (asynchronous).
        Uses asyncio.to_thread() to prevent blocking on LLM calls.
        
        Args:
            company_name: Company name
            company_url: Company website
            job_role: Job role
            salary_expectation: Salary expectation
            research_results: Research data from Tavily
            
        Returns:
            Company evaluation results
        """
        logger.info(f"EvaluationService: Evaluating company {company_name}")
        
        with mlflow.start_run(run_name="company_evaluation", nested=True):
            mlflow.log_param("company", company_name)
            mlflow.log_param("role", job_role)
            
            framework = EvaluationService.load_framework()
            
            prompt_context = {
                "company_name": company_name,
                "company_url": company_url,
                "job_role": job_role,
                "salary_expectation": salary_expectation,
                "framework": framework,
                "research": research_results,
            }
            
            user_prompt = company_eval_user_prompt(prompt_context)
            
            messages = [
                SystemMessage(content=COMPANY_EVAL_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            llm_service = get_llm_service()
            structured_llm = llm_service.get_company_eval_llm()
            
            logger.info(f"EvaluationService: Invoking LLM for company evaluation")
            # Run blocking LLM call in thread pool to prevent blocking event loop
            evaluation = await asyncio.to_thread(structured_llm.invoke, messages)
            
            mlflow.log_metric("company_metrics_evaluated", len(evaluation.company_metrics))
            logger.info(f"EvaluationService: Company evaluation complete")
        
        return evaluation.model_dump()
    
    @staticmethod
    async def evaluate_personal_fit(
        company_name: str,
        job_role: str,
        job_description: str,
        salary_expectation: str,
        company_eval: Dict[str, Any],
        research_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate personal fit with company (asynchronous).
        Uses asyncio.to_thread() to prevent blocking on LLM calls.
        
        Args:
            company_name: Company name
            job_role: Job role
            job_description: Job description
            salary_expectation: Salary expectation
            company_eval: Company evaluation results
            research_results: Research data
            
        Returns:
            Personal fit results
        """
        logger.info(f"EvaluationService: Evaluating personal fit for {company_name}")
        
        with mlflow.start_run(run_name="personal_fit_evaluation", nested=True):
            mlflow.log_param("company", company_name)
            
            framework = EvaluationService.load_framework()
            resume = EvaluationService.load_resume()
            
            prompt_context = {
                "company_name": company_name,
                "job_role": job_role,
                "job_description": job_description,
                "salary_expectation": salary_expectation,
                "framework": framework,
                "resume": resume,
                "company_eval": company_eval,
                "research": research_results,
            }
            
            user_prompt = personal_fit_user_prompt(prompt_context)
            
            messages = [
                SystemMessage(content=PERSONAL_FIT_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            llm_service = get_llm_service()
            structured_llm = llm_service.get_personal_fit_llm()
            
            logger.info(f"EvaluationService: Invoking LLM for personal fit")
            # Run blocking LLM call in thread pool to prevent blocking event loop
            fit = await asyncio.to_thread(structured_llm.invoke, messages)
            
            logger.info(f"EvaluationService: Personal fit evaluation complete")
        
        return fit.model_dump()
    
    @staticmethod
    async def suggest_resume_improvements(
        company_name: str,
        job_role: str,
        job_description: str,
        company_eval: Dict[str, Any],
        personal_fit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate resume improvement suggestions (asynchronous).
        Uses asyncio.to_thread() to prevent blocking on LLM calls.
        
        Args:
            company_name: Company name
            job_role: Job role
            job_description: Job description
            company_eval: Company evaluation results
            personal_fit: Personal fit results
            
        Returns:
            Resume suggestions
        """
        logger.info(f"EvaluationService: Generating resume suggestions for {job_role}")
        
        with mlflow.start_run(run_name="resume_optimization", nested=True):
            mlflow.log_param("company", company_name)
            mlflow.log_param("role", job_role)
            
            resume = EvaluationService.load_resume()
            
            prompt_context = {
                "company_name": company_name,
                "job_role": job_role,
                "job_description": job_description,
                "resume": resume,
                "company_eval": company_eval,
                "personal_fit": personal_fit,
            }
            
            user_prompt = resume_interview_user_prompt(prompt_context)
            
            messages = [
                SystemMessage(content=RESUME_INTERVIEW_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            llm_service = get_llm_service()
            structured_llm = llm_service.get_resume_suggestions_llm()
            
            logger.info(f"EvaluationService: Invoking LLM for resume suggestions")
            # Run blocking LLM call in thread pool to prevent blocking event loop
            suggestions = await asyncio.to_thread(structured_llm.invoke, messages)
            
            logger.info(f"EvaluationService: Resume suggestions complete")
        
        return suggestions.model_dump()
    
    @staticmethod
    async def generate_recommendation(
        company_name: str,
        job_role: str,
        company_score: int,
        personal_fit_score: int,
        resume_score: int,
        company_eval: Dict[str, Any],
        personal_fit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate final recommendation based on all evaluations (asynchronous).
        Uses asyncio.to_thread() to prevent blocking on LLM calls.
        
        Args:
            company_name: Company name
            job_role: Job role
            company_score: Overall company score (1-100)
            personal_fit_score: Personal fit score (1-100)
            resume_score: Resume alignment score (1-100)
            company_eval: Company evaluation data
            personal_fit: Personal fit evaluation data
            
        Returns:
            Recommendation results
        """
        logger.info(f"EvaluationService: Generating recommendation for {company_name}")
        
        with mlflow.start_run(run_name="recommendation_generation", nested=True):
            mlflow.log_param("company", company_name)
            mlflow.log_param("role", job_role)
            mlflow.log_metric("company_score", company_score)
            mlflow.log_metric("personal_fit_score", personal_fit_score)
            mlflow.log_metric("resume_score", resume_score)
            
            prompt_context = {
                "company_name": company_name,
                "role": job_role,
                "company_score": company_score,
                "personal_fit_score": personal_fit_score,
                "resume_score": resume_score,
                "company_strengths": str(company_eval.get("company_metrics", [])),
                "personal_fit_summary": str(personal_fit),
                "career_goals": "AI/ML Engineering Excellence",
            }
            
            user_prompt = recommendation_user_prompt(prompt_context)
            
            messages = [
                SystemMessage(content=RECOMMENDATION_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            llm_service = get_llm_service()
            structured_llm = llm_service.get_recommendation_llm()
            
            logger.info(f"EvaluationService: Invoking LLM for recommendation")
            # Run blocking LLM call in thread pool to prevent blocking event loop
            recommendation = await asyncio.to_thread(structured_llm.invoke, messages)
            
            logger.info(f"EvaluationService: Recommendation generation complete")
        
        return recommendation.model_dump()
    
    @staticmethod
    def generate_final_report(
        company_name: str,
        generated_date: str,
        company_eval: CompanyEvaluation,
        personal_fit: PersonalFit,
        resume_suggestions: ResumeSuggestions,
        recommendation: Recommendation
    ) -> CompanyFitReport:
        """
        Aggregate all evaluations into a complete company fit report.
        
        Args:
            company_name: Company name
            generated_date: Report generation date
            company_eval: Company evaluation object
            personal_fit: Personal fit evaluation object
            resume_suggestions: Resume suggestions object
            recommendation: Final recommendation object
            
        Returns:
            Complete CompanyFitReport
        """
        logger.info(f"EvaluationService: Generating final report for {company_name}")
        
        report = CompanyFitReport(
            generated_date=generated_date,
            company_evaluation=company_eval,
            personal_fit=personal_fit,
            resume_suggestions=resume_suggestions,
            recommendation=recommendation
        )
        
        logger.info(f"EvaluationService: Final report generated successfully")
        
        return report
