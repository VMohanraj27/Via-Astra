import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import mlflow
from app.models.input_models import EvaluationRequest
from app.services.evaluation_service import EvaluationService
from app.utils.report_generator import MarkdownGenerator
from app.utils.pdf_exporter import PDFExporter

logger = logging.getLogger(__name__)

router = APIRouter()

# Output directory for reports
REPORTS_DIR = Path("reports")


@router.post("/evaluate-company")
async def evaluate_company(request: EvaluationRequest):
    """
    Evaluate company and generate comprehensive assessment report.
    Returns both markdown and PDF formats.
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
            
            # Step 1: Research
            logger.info("[CONTROLLER] Step 1: Gathering research data...")
            research_results = await EvaluationService.get_research(
                request.company_name,
                request.job_role,
                request.salary_expectation
            )
            
            # Step 2: Company Evaluation
            logger.info("[CONTROLLER] Step 2: Evaluating company...")
            company_eval = EvaluationService.evaluate_company(
                request.company_name,
                request.company_url,
                request.job_role,
                request.salary_expectation,
                research_results
            )
            
            # Step 3: Personal Fit
            logger.info("[CONTROLLER] Step 3: Evaluating personal fit...")
            personal_fit = EvaluationService.evaluate_personal_fit(
                request.company_name,
                request.job_role,
                request.job_description,
                request.salary_expectation,
                company_eval,
                research_results
            )
            
            # Step 4: Resume Suggestions
            logger.info("[CONTROLLER] Step 4: Generating resume suggestions...")
            resume_suggestions = EvaluationService.suggest_resume_improvements(
                request.company_name,
                request.job_role,
                request.job_description,
                company_eval,
                personal_fit
            )
            
            # Step 5: Generate Reports
            logger.info("[CONTROLLER] Step 5: Generating reports...")
            markdown = MarkdownGenerator.generate(
                company_eval,
                personal_fit,
                resume_suggestions,
                request.company_url,
                request.company_name,
                request.job_description,
                request.job_role
            )
            
            # Export to files
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_company_name = "".join(c for c in request.company_name if c.isalnum() or c in (' ', '-')).strip()
            
            md_path = REPORTS_DIR / f"{safe_company_name}_{timestamp}.md"
            pdf_path = REPORTS_DIR / f"{safe_company_name}_{timestamp}.pdf"
            
            PDFExporter.export_markdown(markdown, md_path)
            PDFExporter.export(markdown, pdf_path, f"{request.company_name} - Assessment Report")
            
            logger.info(f"[CONTROLLER] Reports generated:")
            logger.info(f"  - Markdown: {md_path}")
            logger.info(f"  - PDF: {pdf_path}")
            
            mlflow.log_artifact(str(md_path))
            mlflow.log_artifact(str(pdf_path))
            
            logger.info("=" * 80)
            logger.info("[CONTROLLER] /evaluate-company completed successfully")
            logger.info("=" * 80)

            return {
                "status": "success",
                "company": request.company_name,
                "role": request.job_role,
                "report_markdown": markdown,
                "report_files": {
                    "markdown": str(md_path),
                    "pdf": str(pdf_path)
                }
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
        if filename.endswith('.pdf'):
            media_type = "application/pdf"
        elif filename.endswith('.md'):
            media_type = "text/markdown"
        else:
            media_type = "application/octet-stream"
        
        return FileResponse(file_path, media_type=media_type, filename=filename)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CONTROLLER] Error downloading report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))