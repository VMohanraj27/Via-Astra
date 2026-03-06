from pydantic import BaseModel, Field, ConfigDict
from typing import List


class Citation(BaseModel):
    """Reference source used for evaluation."""

    model_config = ConfigDict(extra="forbid")

    source_title: str = Field(
        description="Title of the research source"
    )

    source_link: str = Field(
        description="URL of the source used for citation"
    )


class MetricEvaluation(BaseModel):
    """Evaluation result for a specific company metric."""

    model_config = ConfigDict(extra="forbid")

    metric_name: str = Field(
        description="Name of the evaluation metric"
    )

    score: int = Field(
        description="Score from 1 to 10 evaluating the company performance for the metric"
    )

    reasoning: str = Field(
        description="Detailed explanation for the score based on research evidence"
    )

    citations: List[Citation] = Field(
        description="List of sources supporting the evaluation"
    )


class CompanyEvaluation(BaseModel):

    model_config = ConfigDict(extra="forbid")

    company_name: str = Field(
        description="Name of the company being evaluated"
    )

    role_applied: str = Field(
        description="Job role the candidate applied for"
    )

    evaluation_metrics: List[MetricEvaluation] = Field(
        description="Evaluation results for all company assessment metrics"
    )


class PersonalFit(BaseModel):

    model_config = ConfigDict(extra="forbid")

    personal_fit_score: float = Field(
        description="Overall personal fit score from 1 to 10"
    )

    strengths_match: List[str] = Field(
        description="Areas where the candidate strongly matches the role"
    )

    skill_gaps: List[str] = Field(
        description="Skills that the candidate lacks for the role"
    )


class ResumeSuggestions(BaseModel):

    model_config = ConfigDict(extra="forbid")

    missing_keywords: List[str] = Field(
        description="Important ATS keywords missing in the resume"
    )

    improved_bullets: List[str] = Field(
        description="Improved resume bullet points optimized for ATS"
    )