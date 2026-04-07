# Output Structure Alignment Document

**Date**: March 2026  
**Purpose**: Align LLM output structure with HTML report template for intuitive end-user reading

---

## Overview

This document outlines the alignment between:
1. **HTML Report Template** (`report_template.html`)
2. **Sample Data Structure** (`report_sample_data.json`)
3. **LLM Output Models** (`app/models/output_models.py`)
4. **System Prompts** (`app/llm/prompts.py`)

The goal is to ensure LLM outputs align perfectly with the HTML rendering structure for a seamless end-user experience.

---

## 1. HTML Report Structure → Output Models Mapping

### 1.1 Executive Summary Section

**HTML Template Fields:**
```html
- generated_date: Report generation timestamp
- company_name: Name of the company
- company_website: Official website URL
- industry: Business sector/industry
- listing_status: Public/Private
- headquarters: HQ location
- founded: Founding year
- countries: Global presence (e.g., "50+")
- india_cities: Cities with offices in India
```

**Output Model Location:**
```python
class CompanyMetadata(BaseModel):
    company_name: str
    company_website: str
    industry: str
    listing_status: str
    headquarters: str
    founded: str
    countries: str
    india_cities: str

class CompanyEvaluation(BaseModel):
    metadata: CompanyMetadata
    role_applied: str
    overall_score: int  # 1-100
```

**LLM System Prompt Guidance:**
- `COMPANY_EVAL_SYSTEM_PROMPT` → Step 1: Extract Company Metadata
- Instructs LLM to extract these fields from research results

---

### 1.2 Company Metrics Section

**HTML Template Structure:**
```html
For each metric:
  - name: Metric name (e.g., "AI & Data Footprint")
  - score: Numeric score (1-5)
  - description: What the metric evaluates
  - evidence[]: List of supporting evidence points
  - implication: Career implications for the candidate
  - risks[]: Potential risk factors
  - sources[]: Links/references to sources
```

**Output Model:**
```python
class CompanyMetric(BaseModel):
    name: str
    score: float  # 1-5 scale
    description: str
    evidence: List[str]
    implication: str
    risks: List[str]
    sources: List[str]

class CompanyEvaluation(BaseModel):
    company_metrics: List[CompanyMetric]
```

**LLM Scoring System:**
- Old: 1-10 scale (problematic for multi-dimensional display)
- **New: 1-5 scale** (maps cleanly to UI progress bars and readability)

**LLM System Prompt Guidance:**
- `COMPANY_EVAL_SYSTEM_PROMPT` → Step 3: Evaluate Each Metric
- Score: 1-2 (Weak), 3 (Moderate), 4 (Strong), 5 (Exceptional)
- Evidence: 2-3 specific points
- Implication: Career value statement
- Risks: List potential downsides
- Sources: URL references from research

---

### 1.3 Technology Stack Section

**HTML Template Structure:**
```html
For each technology:
  - name: Technology name
  - evidence: How the company uses it
  - relevance: Relevance to the applied role
```

**Output Model:**
```python
class TechnologyStack(BaseModel):
    name: str
    evidence: str
    relevance: str

class CompanyEvaluation(BaseModel):
    technology_stack: List[TechnologyStack]
```

**LLM System Prompt Guidance:**
- `COMPANY_EVAL_SYSTEM_PROMPT` → Step 4: Build Technology Stack
- Filter technologies relevant to the role
- Each entry maps to an HTML table row

---

### 1.4 Resume Tailoring Section

**HTML Template Structure:**
```html
- resume_alignment_score: Alignment percentage (1-100)
- resume_gaps[]: List of specific gaps
- resume_recommendations[]:
    For each recommendation:
      - gap: The gap being addressed
      - before: Current resume content
      - after: Improved content
      - impact: Impact of the improvement
```

**Output Model:**
```python
class ResumeRecommendation(BaseModel):
    gap: str
    before: str
    after: str
    impact: str

class ResumeSuggestions(BaseModel):
    resume_alignment_score: int  # 1-100
    resume_gaps: List[str]
    resume_recommendations: List[ResumeRecommendation]
```

**LLM System Prompt Guidance:**
- `RESUME_INTERVIEW_SYSTEM_PROMPT` → Steps 1-5
- Calculate alignment score based on job description match
- Provide specific, actionable improvements
- Before/After format for clear visualization

---

### 1.5 Interview Preparation Section

**HTML Template Structure:**
```html
interview_questions:
  - business[]: Business & strategy questions
  - ml[]: Machine learning questions
  - system_design[]: System design questions
  - mlops[]: MLOps & deployment questions
  - behavioral[]: Behavioral questions
```

**Output Model:**
```python
class InterviewQuestions(BaseModel):
    business: List[str]
    ml: List[str]
    system_design: List[str]
    mlops: List[str]
    behavioral: List[str]

class ResumeSuggestions(BaseModel):
    interview_questions: InterviewQuestions
```

**LLM System Prompt Guidance:**
- `RESUME_INTERVIEW_SYSTEM_PROMPT` → Step 6: Generate Interview Questions
- 2-3 questions per category
- Tailored to specific role and company tech stack
- Fair and role-appropriate difficulty level

---

### 1.6 Final Recommendation Section

**HTML Template Structure:**
```html
recommendation:
  - decision: "Strong Apply" | "Apply" | "Consider" | "Skip"
  - reason: Comprehensive reasoning
```

**Output Model:**
```python
class Recommendation(BaseModel):
    decision: str
    reason: str
```

**LLM System Prompt Guidance:**
- `RECOMMENDATION_SYSTEM_PROMPT`
- Synthesize all scores and factors
- Provide clear, defensible recommendation
- Include key opportunities and risks

---

## 2. Data Flow: Research → LLM → HTML

### Step-by-Step Processing

```
1. RESEARCH PHASE
   ├─ Tavily API searches company
   └─ Results cached in repository
         ↓
2. COMPANY EVALUATION
   ├─ Input: Company research + Assessment framework
   ├─ LLM: COMPANY_EVAL_SYSTEM_PROMPT + company_eval_user_prompt()
   ├─ Output: CompanyEvaluation JSON
   │  - metadata (company details)
   │  - company_metrics[] (evaluation scores)
   │  - technology_stack[] (tech inventory)
   └─ Overall score: aggregated 1-5 metrics → 1-100
         ↓
3. PERSONAL FIT EVALUATION
   ├─ Input: Resume + Job description + Company evaluation
   ├─ LLM: PERSONAL_FIT_SYSTEM_PROMPT + personal_fit_user_prompt()
   └─ Output: PersonalFit JSON
      - personal_fit_score
      - strengths_match[]
      - skill_gaps[]
      - career_growth_assessment
         ↓
4. RESUME & INTERVIEW PREP
   ├─ Input: Resume + Job description + Prior evaluations
   ├─ LLM: RESUME_INTERVIEW_SYSTEM_PROMPT + resume_interview_user_prompt()
   └─ Output: ResumeSuggestions JSON
      - resume_alignment_score
      - resume_gaps[]
      - resume_recommendations[]
      - interview_questions{}
         ↓
5. FINAL RECOMMENDATION
   ├─ Input: All scores + Assessment summaries
   ├─ LLM: RECOMMENDATION_SYSTEM_PROMPT + recommendation_user_prompt()
   └─ Output: Recommendation JSON
      - decision
      - reason
         ↓
6. REPORT GENERATION
   ├─ Combine all outputs + timestamp
   └─ Render HTML using report_template.html
```

---

## 3. Scoring System Changes

### Old System (1-10 scale)
- **Problem**: Hard to display progressively, requires normalization
- **Fields**: metric_name, score, reasoning, citations

### New System (1-5 scale)
- **Advantage**: Maps cleanly to progress bar visualization
- **Overall score**: Normalized to 1-100 for readability
- **Fields**: name, score, description, evidence[], implication, risks[], sources[]

**Conversion Formula:**
```
Overall Score = (Sum of metric scores / Max possible score) × 100
             = (Sum of 1-5 scores / (number_of_metrics × 5)) × 100

Example: 4 metrics with average score 3.5/5
       = (3.5 × 4 / 20) × 100 = 70/100
```

---

## 4. Prompt Alignment Details

### COMPANY_EVAL_SYSTEM_PROMPT
**Alignment Changes:**
- ✅ Step 1: Extract company metadata (new requirement)
- ✅ Step 3: Explicit 1-5 scoring with definitions
- ✅ Step 4: Build technology stack section
- ✅ Step 5: Compute overall score using formula
- ✅ Output format: JSON matching CompanyEvaluation schema

### PERSONAL_FIT_SYSTEM_PROMPT
**Alignment Changes:**
- ✅ Scoring: Changed to 1-100 scale for clarity
- ✅ Output fields match PersonalFit schema exactly
- ✅ Focus on career growth assessment

### RESUME_INTERVIEW_SYSTEM_PROMPT
**New Prompt (previously RESUME_ATS_SYSTEM_PROMPT)**
- ✅ Renamed to reflect dual purpose (resume + interview)
- ✅ Added interview question categories
- ✅ Before/After format for resume improvements
- ✅ Output matches ResumeSuggestions schema

### RECOMMENDATION_SYSTEM_PROMPT
**New Prompt**
- ✅ Synthesizes all evaluations
- ✅ Decision categories: "Strong Apply", "Apply", "Consider", "Skip"
- ✅ Clear reasoning combining multiple factors

---

## 5. Implementation Checklist

### Models ✅
- [x] CompanyMetadata
- [x] CompanyMetric  
- [x] CompanyEvaluation (updated with new structure)
- [x] PersonalFit (updated to match output)
- [x] ResumeSuggestions (updated with new fields)
- [x] InterviewQuestions
- [x] ResumeRecommendation
- [x] Recommendation
- [x] CompanyFitReport (complete report model)

### Prompts ✅
- [x] COMPANY_EVAL_SYSTEM_PROMPT (updated)
- [x] PERSONAL_FIT_SYSTEM_PROMPT (updated)
- [x] RESUME_INTERVIEW_SYSTEM_PROMPT (renamed from RESUME_ATS)
- [x] RECOMMENDATION_SYSTEM_PROMPT (new)
- [x] company_eval_user_prompt() (enhanced)
- [x] personal_fit_user_prompt() (enhanced)
- [x] resume_interview_user_prompt() (renamed)
- [x] recommendation_user_prompt() (new)

### Services ✅
- [x] LLMService updated with new model methods
- [x] gemini_client.py updated with new model imports/functions
- [x] EvaluationService updated to use new prompts
- [x] evaluation_metrics → company_metrics field reference

---

## 6. HTML Template Integration

### Template Variables Expected

**From CompanyEvaluation.metadata:**
```
{{ company_name }}
{{ company_website }}
{{ industry }}
{{ listing_status }}
{{ headquarters }}
{{ founded }}
{{ countries }}
{{ india_cities }}
{{ role_applied }}
{{ overall_score }}
```

**From CompanyEvaluation.company_metrics:**
```
{% for metric in company_metrics %}
  {{ metric.name }}
  {{ metric.score }}
  {{ metric.description }}
  {{ metric.evidence }}
  {{ metric.implication }}
  {{ metric.risks }}
  {{ metric.sources }}
{% endfor %}
```

**From ResumeSuggestions:**
```
{{ resume_alignment_score }}
{{ resume_gaps }}
{% for rec in resume_recommendations %}
  {{ rec.gap }}, {{ rec.before }}, {{ rec.after }}, {{ rec.impact }}
{% endfor %}
{% for questions in interview_questions %}
  business, ml, system_design, mlops, behavioral categories
{% endfor %}
```

**From Recommendation:**
```
{{ recommendation.decision }}
{{ recommendation.reason }}
```

---

## 7. Example Output Structure

See `report_sample_data.json` for a complete example of the expected output structure for the HTML template.

---

## 8. Quality Assurance

### Testing Checklist
- [ ] CompanyEvaluation JSON validates against schema
- [ ] All metadata fields populated from research
- [ ] Metrics score between 1-5
- [ ] Overall score formula produces 1-100 range
- [ ] Evidence items are specific and sourced
- [ ] Technology stack relevant to role
- [ ] Resume improvements are actionable
- [ ] Interview questions are role-appropriate
- [ ] Final recommendation is defensible
- [ ] HTML template renders all fields correctly
- [ ] Progress bars display properly (1-100)

---

## 9. Future Enhancements

- [ ] Add confidence scores to each metric
- [ ] Include salary alignment in recommendations
- [ ] Generate PDF export from HTML
- [ ] Add data visualization charts
- [ ] Support for multiple role applications
- [ ] Batch reporting for multiple companies

---

## Contact & Questions

For questions about this alignment, refer to:
- `app/models/output_models.py` - Data structures
- `app/llm/prompts.py` - System and user prompts
- `report_template.html` - HTML rendering template
- `report_sample_data.json` - Example output data
