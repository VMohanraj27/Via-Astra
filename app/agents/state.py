from typing import TypedDict, Dict, List


class AgentState(TypedDict):

    company_name: str
    company_url: str
    job_role: str
    job_description: str
    salary_expectation: str

    research_results: Dict[str, List]

    company_eval: dict
    personal_fit: dict
    resume_suggestions: dict