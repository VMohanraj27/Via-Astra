import logging
from fastapi import APIRouter
from app.models.input_models import EvaluationRequest
from app.agents.workflow import build_workflow
from app.utils.markdown_generator import generate_markdown

logger = logging.getLogger(__name__)

router = APIRouter()

workflow = build_workflow()


@router.post("/evaluate-company")
async def evaluate_company(request: EvaluationRequest):
    
    logger.info("=" * 80)
    logger.info("[API] /evaluate-company endpoint called")
    logger.info(f"[API] Company: {request.company_name}, Role: {request.job_role}")
    logger.info("=" * 80)

    try:
        state = request.model_dump()
        logger.debug(f"[API] Input state keys: {list(state.keys())}")

        logger.info("[API] Invoking workflow...")
        result = await workflow.ainvoke(state)
        logger.info("[API] Workflow completed successfully")

        logger.info("[API] Generating markdown report...")
        markdown = generate_markdown(
            result["company_eval"],
            result["personal_fit"],
            result["resume_suggestions"]
        )
        logger.info(f"[API] Report generated, length: {len(markdown)}")

        logger.info("=" * 80)
        logger.info("[API] /evaluate-company completed successfully")
        logger.info("=" * 80)

        return {
            "report": markdown
        }
        
    except Exception as e:
        logger.error("[API] Error during evaluation", exc_info=True)
        raise