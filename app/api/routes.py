from fastapi import APIRouter
from app.models.input_models import EvaluationRequest
from app.agents.workflow import build_workflow
from app.utils.markdown_generator import generate_markdown

router = APIRouter()

workflow = build_workflow()


@router.post("/evaluate-company")
async def evaluate_company(request: EvaluationRequest):

    state = request.model_dump()

    result = await workflow.ainvoke(state)

    markdown = generate_markdown(
        result["company_eval"],
        result["personal_fit"],
        result["resume_suggestions"]
    )

    return {
        "report": markdown
    }