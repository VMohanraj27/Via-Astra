import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import mlflow
from datetime import datetime
from app.models.input_models import EvaluationRequest
from app.models.output_models import (
    CompanyEvaluation, PersonalFit, ResumeSuggestions, Recommendation, CompanyFitReport
)
from app.services.evaluation_service import EvaluationService
from app.utils.report_generator import MarkdownGenerator, HTMLGenerator
from app.agents.workflow import build_workflow

logger = logging.getLogger(__name__)

router = APIRouter()

# Output directory for reports
REPORTS_DIR = Path("reports")


@router.post("/evaluate-company")
async def evaluate_company(request: EvaluationRequest):
    """
    Evaluate company and generate comprehensive assessment report.
    Returns HTML and markdown formats.
    """
    
    logger.info("=" * 80)
    logger.info("[CONTROLLER] /evaluate-company endpoint called")
    logger.info(f"[CONTROLLER] Company: {request.company_name}, Role: {request.job_role}")
    logger.info("=" * 80)

    try:
        with mlflow.start_run(run_name=f"assessment_{request.company_name}", nested=False):
            mlflow.log_params({
                "company": request.company_name,
                "role": request.job_role,
                "url": request.company_url
            })
            
            # Initialize state for LangGraph workflow
            logger.info("[CONTROLLER] Initializing LangGraph workflow...")
            initial_state = {
                "company_name": request.company_name,
                "company_url": request.company_url,
                "job_role": request.job_role,
                "job_description": request.job_description,
                "salary_expectation": request.salary_expectation,
                "research_results": {},
                "company_eval": {},
                "personal_fit": {},
                "resume_suggestions": {},
                "recommendation": {},
                "final_report": {},
            }
            
            # Execute LangGraph workflow (6-node pipeline)
            logger.info("[CONTROLLER] Executing LangGraph workflow (research → company_eval → personal_fit → resume_opt → recommendation → report_generation)...")
            workflow = build_workflow()
            logger.info("Workflow is build successfully!!")
            final_state = await workflow.ainvoke(initial_state)
            
            # Extract results from final state
            logger.info("[CONTROLLER] Extracting results from workflow...")
            research_results = final_state.get("research_results", {})
            company_eval_dict = final_state.get("company_eval", {})
            personal_fit_dict = final_state.get("personal_fit", {})
            resume_suggestions_dict = final_state.get("resume_suggestions", {})
            recommendation_dict = final_state.get("recommendation", {})
            final_report_dict = final_state.get("final_report", {})
            
            # Convert dicts to Pydantic models for type safety
            company_eval = CompanyEvaluation(**company_eval_dict)
            personal_fit = PersonalFit(**personal_fit_dict)
            resume_suggestions = ResumeSuggestions(**resume_suggestions_dict)
            recommendation = Recommendation(**recommendation_dict)
            company_fit_report = CompanyFitReport(**final_report_dict)
            
            # Step 2: Generate Reports in Multiple Formats
            logger.info("[CONTROLLER] Step 2: Generating report files...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_company_name = "".join(c for c in request.company_name if c.isalnum() or c in (' ', '-')).strip()
            
            # Create versioned folder structure: reports/{CompanyName}/v{version}/
            company_dir = REPORTS_DIR / safe_company_name
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine version number by counting existing version folders
            existing_versions = [d for d in company_dir.iterdir() if d.is_dir() and d.name.startswith('v')]
            version_number = len(existing_versions) + 1
            version_dir = company_dir / f"v{version_number}"
            version_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"[CONTROLLER] Created version folder: {version_dir}")
            logger.info(f"[CONTROLLER] Version: v{version_number}")
            
            # Generate Markdown (from dict format for compatibility)
            markdown = MarkdownGenerator.generate(
                company_eval_dict,
                personal_fit_dict,
                resume_suggestions_dict,
                request.company_url,
                request.company_name,
                request.job_description,
                request.job_role
            )
            
            # Generate HTML (from CompanyFitReport) - use new template
            html = HTMLGenerator.generate(
                company_fit_report.model_dump(),
                "report_template.html"
            )
            
            # Step 3: Export Files
            logger.info("[CONTROLLER] Step 3: Exporting files...")
            
            md_path = version_dir / f"{safe_company_name}_{timestamp}.md"
            html_path = version_dir / f"{safe_company_name}_{timestamp}.html"
            
            # Export files (pass Path objects directly, not strings)
            # Export markdown
            md_path.parent.mkdir(parents=True, exist_ok=True)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            # Export HTML
            HTMLGenerator.export_html(html, html_path)
            
            logger.info(f"[CONTROLLER] Reports generated:")
            logger.info(f"  - HTML: {html_path}")
            logger.info(f"  - Markdown: {md_path}")
            
            # Log artifacts to MLflow
            mlflow.log_artifact(str(md_path))
            mlflow.log_artifact(str(html_path))
            
            # Log final scores
            mlflow.log_metric("company_score", company_eval.overall_score)
            mlflow.log_metric("personal_fit_score", int(personal_fit.personal_fit_score))
            mlflow.log_metric("resume_alignment_score", resume_suggestions.resume_alignment_score)
            
            logger.info("=" * 80)
            logger.info("[CONTROLLER] /evaluate-company completed successfully (LangGraph workflow)")
            logger.info("=" * 80)

            return {
                "status": "success",
                "company": request.company_name,
                "role": request.job_role,
                "scores": {
                    "company_score": company_eval.overall_score,
                    "personal_fit_score": int(personal_fit.personal_fit_score),
                    "resume_alignment_score": resume_suggestions.resume_alignment_score,
                },
                "recommendation": {
                    "decision": recommendation.decision,
                    "reason": recommendation.reason,
                },
                "report_files": {
                    "html": str(html_path),
                    "markdown": str(md_path)
                },
                "report_html": html  # Include HTML in response for immediate rendering
            }
        
    except Exception as e:
        logger.error("[CONTROLLER] Error during evaluation", exc_info=True)
        mlflow.log_param("error", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{filename}")
async def download_report(filename: str):
    """
    Download generated report file.
    """
    try:
        file_path = REPORTS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report file not found")
        
        logger.info(f"[CONTROLLER] Downloading report: {filename}")
        
        # Determine media type
        if filename.endswith('.md'):
            media_type = "text/markdown"
        elif filename.endswith('.html'):
            media_type = "text/html"
        else:
            media_type = "application/octet-stream"
        
        return FileResponse(file_path, media_type=media_type, filename=filename)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CONTROLLER] Error downloading report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))