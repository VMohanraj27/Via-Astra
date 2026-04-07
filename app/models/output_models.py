from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


# ---- COMPANY EVALUATION MODELS ----

class CompanyMetric(BaseModel):
    """Evaluation result for a specific company metric."""
    
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        description="Name of the evaluation metric (e.g., 'AI & Data Footprint')"
    )

    score: float = Field(
        description="Score from 1 to 5 evaluating the company performance"
    )

    description: str = Field(
        description="Detailed description of what this metric evaluates"
    )

    evidence: List[str] = Field(
        description="List of evidence points supporting the score"
    )

    implication: str = Field(
        description="What this score means for the candidate's career"
    )

    risks: List[str] = Field(
        description="Potential risk factors associated with this metric"
    )

    sources: List[str] = Field(
        description="List of source links or citations supporting the evaluation"
    )


class TechnologyStack(BaseModel):
    """Technology used by the company."""
    
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        description="Technology or tool name"
    )

    evidence: str = Field(
        description="Evidence of the company using this technology"
    )

    relevance: str = Field(
        description="How relevant this technology is to the applied role"
    )


class CompanyMetadata(BaseModel):
    """Basic company information."""
    
    model_config = ConfigDict(extra="forbid")

    company_name: str = Field(
        description="Name of the company"
    )

    company_website: str = Field(
        description="Company website URL"
    )

    industry: str = Field(
        description="Industry or sector the company operates in"
    )

    listing_status: str = Field(
        description="Whether company is public or private"
    )

    headquarters: str = Field(
        description="Location of company headquarters"
    )

    founded: str = Field(
        description="Year company was founded"
    )

    countries: str = Field(
        description="Number of countries company operates in"
    )

    india_cities: str = Field(
        description="Indian cities where company has offices"
    )


class CompanyEvaluation(BaseModel):
    """Complete company evaluation for the HTML report."""
    
    model_config = ConfigDict(extra="forbid")

    # Company Info
    metadata: CompanyMetadata = Field(
        description="Basic company information"
    )

    role_applied: str = Field(
        description="Job role the candidate applied for"
    )

    # Evaluation scores
    overall_score: int = Field(
        description="Overall company fit score (1-100)"
    )

    # Metrics
    company_metrics: List[CompanyMetric] = Field(
        description="Evaluation results for all company assessment metrics"
    )

    # Technology
    technology_stack: List[TechnologyStack] = Field(
        description="Technologies used by the company relevant to the role"
    )


# ---- RESUME & PERSONAL FIT MODELS ----

class InterviewQuestions(BaseModel):
    """Interview preparation questions organized by category."""
    
    model_config = ConfigDict(extra="forbid")

    business: List[str] = Field(
        description="Business and strategy related questions"
    )

    ml: List[str] = Field(
        description="Machine learning specific questions"
    )

    system_design: List[str] = Field(
        description="System design interview questions"
    )

    mlops: List[str] = Field(
        description="MLOps and deployment related questions"
    )

    behavioral: List[str] = Field(
        description="Behavioral and culture fit questions"
    )


class ResumeRecommendation(BaseModel):
    """Resume improvement recommendation."""
    
    model_config = ConfigDict(extra="forbid")

    gap: str = Field(
        description="The skill or keyword gap being addressed"
    )

    before: str = Field(
        description="Current resume content or statement"
    )

    after: str = Field(
        description="Improved/optimized resume content"
    )

    impact: str = Field(
        description="Impact of this improvement on ATS/hiring"
    )


class PersonalFit(BaseModel):
    """Personal fit assessment for candidate-company alignment."""
    
    model_config = ConfigDict(extra="forbid")

    personal_fit_score: float = Field(
        description="Overall personal fit score (1-100)"
    )

    strengths_match: List[str] = Field(
        description="Areas where the candidate strongly matches the role"
    )

    skill_gaps: List[str] = Field(
        description="Skills or experiences that the candidate lacks for the role"
    )

    career_growth_assessment: str = Field(
        description="Assessment of learning and growth opportunities"
    )

    final_recommendation: str = Field(
        description="Final recommendation on whether to pursue this opportunity"
    )


class ResumeSuggestions(BaseModel):
    """Resume optimization and interview preparation."""
    
    model_config = ConfigDict(extra="forbid")

    resume_alignment_score: int = Field(
        description="Resume alignment score with job description (1-100)"
    )

    resume_gaps: List[str] = Field(
        description="Gaps in resume compared to job requirements"
    )

    resume_recommendations: List[ResumeRecommendation] = Field(
        description="Specific recommendations for resume improvement"
    )

    interview_questions: InterviewQuestions = Field(
        description="Interview questions organized by category"
    )


# ---- FINAL REPORT MODEL ----

class Recommendation(BaseModel):
    """Final recommendation for the opportunity."""
    
    model_config = ConfigDict(extra="forbid")

    decision: str = Field(
        description="Recommendation decision (e.g., 'Strong Apply', 'Apply', 'Consider', 'Skip')"
    )

    reason: str = Field(
        description="Reasoning behind the recommendation"
    )


class CompanyFitReport(BaseModel):
    """Complete company assessment report combining all evaluations."""
    
    model_config = ConfigDict(extra="forbid")

    generated_date: str = Field(
        description="Date the report was generated"
    )

    # Company evaluation
    company_evaluation: CompanyEvaluation = Field(
        description="Company assessment results"
    )

    # Personal fit
    personal_fit: PersonalFit = Field(
        description="Personal fit assessment"
    )

    # Resume suggestions
    resume_suggestions: ResumeSuggestions = Field(
        description="Resume optimization and interview prep"
    )

    # Final recommendation
    recommendation: Recommendation = Field(
        description="Final recommendation on the opportunity"
    )