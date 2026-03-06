# Company Fit Evaluation Agent

AI powered system to evaluate company fit for AI/ML engineers.

## Features

- Company research using Tavily
- Parallel search queries
- LangGraph workflow agents
- Gemini LLM reasoning
- Resume ATS optimization
- MLflow observability
- FastAPI backend

---

# Setup

Install dependencies

pip install -r requirements.txt

---

# Environment Variables

Create .env

TAVILY_API_KEY=xxxx
GOOGLE_API_KEY=xxxx

---

# Run MLflow

mlflow server \
--host 0.0.0.0 \
--port 5000

---

# Start API

python run.py

---

# API Endpoint

POST /evaluate-company

Request Body

{
  "company_name": "JPMorgan",
  "company_url": "https://jpmorgan.com",
  "job_role": "Applied AI Engineer",
  "job_description": "...",
  "salary_expectation": "30 LPA"
}

---

# Output

Returns a markdown report containing

1. Company evaluation
2. Personal fit analysis
3. Resume optimization