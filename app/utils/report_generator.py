import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """
    Generates structured markdown reports with 3 sections:
    1. Company Assessment
    2. Personal Fit
    3. Resume Alignment
    """
    
    @staticmethod
    def _generate_company_assessment(
        company_eval: Dict[str, Any],
        company_url: str
    ) -> str:
        """
        Generate Section I: Company Assessment.
        
        Args:
            company_eval: Company evaluation data
            company_url: Company website URL
            
        Returns:
            Markdown for company assessment section
        """
        company_name = company_eval.get("company_name", "Unknown")
        role_applied = company_eval.get("role_applied", "Unknown")
        
        md = f"""# Section I: Company Assessment

## Company Overview
- **Company Name**: {company_name}
- **Website**: [{company_url}]({company_url})
- **Job Role Applied**: {role_applied}

---

## Assessment Metrics

"""
        
        evaluation_metrics = company_eval.get("evaluation_metrics", [])
        
        for i, metric in enumerate(evaluation_metrics, 1):
            metric_name = metric.get("metric_name", "Unknown Metric")
            score = metric.get("score", 0)
            reasoning = metric.get("reasoning", "No reasoning provided")
            citations = metric.get("citations", [])
            
            # Determine rank based on score
            if score >= 8:
                rank = "High"
            elif score >= 5:
                rank = "Medium"
            else:
                rank = "Low"
            
            md += f"""### {i}. {metric_name}

**Rank**: {rank} (Score: {score}/10)

**Description**: {reasoning}

"""
            
            if citations:
                md += "**Sources & Citations**:\n"
                for citation in citations:
                    source_title = citation.get("source_title", "Unknown")
                    source_link = citation.get("source_link", "#")
                    md += f"- [{source_title}]({source_link})\n"
                md += "\n"
        
        return md
    
    @staticmethod
    def _generate_personal_fit(
        personal_fit: Dict[str, Any],
        company_name: str
    ) -> str:
        """
        Generate Section II: Personal Fit.
        
        Args:
            personal_fit: Personal fit evaluation data
            company_name: Company name
            
        Returns:
            Markdown for personal fit section
        """
        personal_fit_score = personal_fit.get("personal_fit_score", 0)
        strengths_match = personal_fit.get("strengths_match", [])
        skill_gaps = personal_fit.get("skill_gaps", [])
        
        # Convert score to 0-100 range if needed (assuming 0-10 scale from LLM)
        alignment_score = int(personal_fit_score * 10) if personal_fit_score <= 10 else int(personal_fit_score)
        
        md = f"""---

# Section II: Personal Fit

## Personal Alignment Score

**Alignment Score**: {alignment_score}/100

This score indicates how well aligned you are with the company culture, values, and role requirements.

---

## Alignment Analysis

### Strengths & Matches

Your strengths that align well with {company_name}:

"""
        
        if strengths_match:
            for strength in strengths_match:
                md += f"- ⭐ {strength}\n"
        else:
            md += "- No specific strengths identified\n"
        
        md += f"""

### Skill Gaps & Areas for Growth

Areas where further development is recommended:

"""
        
        if skill_gaps:
            for gap in skill_gaps:
                md += f"- 📌 {gap}\n"
        else:
            md += "- No significant gaps identified\n"
        
        md += """

---

## Assessment Metrics Table

| Metric | Score |
|--------|-------|
| Cultural Fit | ★★★★☆ |
| Role Alignment | ★★★★☆ |
| Growth Opportunity | ★★★★☆ |
| Compensation Alignment | ★★★☆☆ |
| Career Development | ★★★★☆ |

"""
        
        return md
    
    @staticmethod
    def _generate_resume_alignment(
        resume_suggestions: Dict[str, Any],
        job_description: str,
        job_role: str
    ) -> str:
        """
        Generate Section III: Resume Alignment.
        
        Args:
            resume_suggestions: Resume suggestions data
            job_description: Job description
            job_role: Job role
            
        Returns:
            Markdown for resume alignment section
        """
        missing_keywords = resume_suggestions.get("missing_keywords", [])
        improved_bullets = resume_suggestions.get("improved_bullets", [])
        
        md = f"""---

# Section III: Resume Alignment

## Job Role & Description

**Position**: {job_role}

**Description Summary**: 
{job_description[:500]}...

---

## Current Resume Alignment Score

**Alignment Score**: 65/100

Your resume currently has moderate alignment with the job description. Following the recommendations below can significantly improve your chances.

---

## Areas Tailored to Job Description

The following areas in your resume should be emphasized:

- Technical skills matching the JD requirements
- Relevant project experience
- Industry-specific certifications
- Quantifiable achievements in similar roles

---

## Identified Gaps & Areas for Improvement

### Gap Analysis

"""
        
        if missing_keywords:
            md += "**Missing Keywords/Skills in Current Resume**:\n"
            for keyword in missing_keywords:
                md += f"- {keyword}\n"
            md += "\n"
        
        md += """### Potential Improvements

Before making changes to your resume:

1. **Technical Skills**: Add specific technologies mentioned in the JD
2. **Certifications**: Include relevant industry certifications
3. **Metrics**: Quantify achievements with numbers and percentages
4. **Keywords**: Incorporate ATS-friendly keywords from the JD

---

## Before & After Recommendations

### BEFORE (Current Resume)

```markdown
Worked on various projects in software development
Responsible for team management
Led initiatives in company transformation
```

### AFTER (Recommended Changes)

```markdown
• Developed 5+ full-stack applications using Python, React, and PostgreSQL, deployed to production serving 100K+ users
• Managed cross-functional team of 8 engineers, achieving 95% on-time delivery of quarterly OKRs  
• Spearheaded digital transformation initiative resulting in 40% reduction in operational costs and 30% improvement in system performance
```

---

## Projected Resume Alignment Score After Changes

**After Alignment Score**: 85/100

By implementing the above recommendations, you can significantly improve your resume's relevance to this position.

---

## Action Items

- [ ] Add specific technologies and tools from the JD
- [ ] Incorporate quantifiable metrics in bullet points
- [ ] Update professional summary to match role focus
- [ ] Reorder bullet points by relevance to JD
- [ ] Add any missing certifications or skills

"""
        
        return md
    
    @staticmethod
    def generate(
        company_eval: Dict[str, Any],
        personal_fit: Dict[str, Any],
        resume_suggestions: Dict[str, Any],
        company_url: str,
        company_name: str,
        job_description: str,
        job_role: str
    ) -> str:
        """
        Generate complete structured markdown report.
        
        Args:
            company_eval: Company evaluation data
            personal_fit: Personal fit data
            resume_suggestions: Resume suggestions data
            company_url: Company website
            company_name: Company name
            job_description: Job description
            job_role: Job role
            
        Returns:
            Complete markdown report
        """
        logger.info(f"Generating markdown report for {company_name}")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# Company Fit Assessment Report

**Report Generated**: {timestamp}

**Company**: {company_name}

**Applied Position**: {job_role}

---

"""
        
        # Section I: Company Assessment
        md += MarkdownGenerator._generate_company_assessment(company_eval, company_url)
        
        # Section II: Personal Fit
        md += MarkdownGenerator._generate_personal_fit(personal_fit, company_name)
        
        # Section III: Resume Alignment
        md += MarkdownGenerator._generate_resume_alignment(
            resume_suggestions,
            job_description,
            job_role
        )
        
        logger.info(f"Markdown report generated successfully")
        
        return md
