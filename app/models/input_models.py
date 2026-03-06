from pydantic import BaseModel, Field, ConfigDict
from typing import List


class EvaluationRequest(BaseModel):
    company_name: str = Field(description="name of the input company")
    company_url: str = Field(description="input company url")
    job_role: str = Field(description="job role applying for")
    job_description: str = Field(description="Job description")
    salary_expectation: str = Field(description="Salary expectation")

    model_config = ConfigDict(extra="forbid")