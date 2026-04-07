import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

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
        overall_score = company_eval.get("overall_score", 0)
        
        md = f"""# Section I: Company Assessment

## Company Overview
- **Company Name**: {company_name}
- **Website**: [{company_url}]({company_url})
- **Job Role Applied**: {role_applied}
- **Overall Score**: {overall_score}/100

---

## Assessment Metrics

"""
        
        # Support both old and new field names
        company_metrics = company_eval.get("company_metrics", company_eval.get("evaluation_metrics", []))
        
        for i, metric in enumerate(company_metrics, 1):
            # Support both old (metric_name, reasoning, citations) and new (name, description, evidence, implication, risks, sources) field names
            metric_name = metric.get("name", metric.get("metric_name", "Unknown Metric"))
            score = metric.get("score", 0)
            description = metric.get("description", metric.get("reasoning", "No description provided"))
            evidence = metric.get("evidence", [])
            implication = metric.get("implication", "")
            risks = metric.get("risks", [])
            sources = metric.get("sources", metric.get("citations", []))
            
            # Determine rank based on score (adjust for 1-5 or 1-10 scale)
            if score >= 4:
                rank = "High" if score <= 5 else "Excellent"
            elif score >= 3:
                rank = "Medium" if score <= 5 else "Good"
            else:
                rank = "Low"
            
            md += f"""### {i}. {metric_name}

**Score**: {score}/5

**Description**: {description}

"""
            
            if evidence:
                md += "**Evidence**:\n"
                for item in evidence:
                    md += f"- {item}\n"
                md += "\n"
            
            if implication:
                md += f"**Career Implication**: {implication}\n\n"
            
            if risks:
                md += "**Risk Factors**:\n"
                for risk in risks:
                    md += f"- {risk}\n"
                md += "\n"
            
            if sources:
                md += "**Sources & References**:\n"
                for source in sources:
                    if isinstance(source, dict):
                        source_title = source.get("source_title", "Unknown")
                        source_link = source.get("source_link", "#")
                        md += f"- [{source_title}]({source_link})\n"
                    else:
                        # Handle string sources
                        md += f"- {source}\n"
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
        # Support both old and new field names
        resume_alignment_score = resume_suggestions.get(
            "resume_alignment_score", 
            resume_suggestions.get("alignment_score", 65)
        )
        resume_gaps = resume_suggestions.get("resume_gaps", [])
        resume_recommendations = resume_suggestions.get("resume_recommendations", [])
        
        # Fallback to old field names if new ones not available
        missing_keywords = resume_suggestions.get("missing_keywords", [])
        improved_bullets = resume_suggestions.get("improved_bullets", [])
        
        md = f"""---

# Section III: Resume Alignment & Interview Prep

## Job Role & Description

**Position**: {job_role}

**Description Summary**: 
{job_description[:500]}...

---

## Resume Alignment Score

**Alignment Score**: {resume_alignment_score}/100

Your resume has {'strong' if resume_alignment_score >= 75 else 'moderate' if resume_alignment_score >= 60 else 'limited'} alignment with the job description. Following the recommendations below can significantly improve your chances.

---

## Identified Gaps

The following gaps have been identified between your resume and the job requirements:

"""
        
        if resume_gaps:
            for gap in resume_gaps:
                md += f"- {gap}\n"
        elif missing_keywords:
            md += "**Missing Keywords/Skills**:\n"
            for keyword in missing_keywords:
                md += f"- {keyword}\n"
        else:
            md += "- No significant gaps identified\n"
        
        md += """

---

## Resume Improvement Recommendations

"""
        
        if resume_recommendations:
            for i, rec in enumerate(resume_recommendations, 1):
                gap = rec.get("gap", "")
                before = rec.get("before", "")
                after = rec.get("after", "")
                impact = rec.get("impact", "")
                
                md += f"""### Recommendation {i}: {gap}

**Current (Before)**:
```
{before}
```

**Improved (After)**:
```
{after}
```

**Impact**: {impact}

"""
        elif improved_bullets:
            md += "**Improved Resume Bullet Points**:\n"
            for i, bullet in enumerate(improved_bullets, 1):
                md += f"{i}. {bullet}\n"
        else:
            md += "- Your resume is well-aligned with the job requirements\n"
        
        md += """

---

## Interview Preparation

"""
        
        # Add interview questions if available
        interview_questions = resume_suggestions.get("interview_questions", {})
        if interview_questions:
            if interview_questions.get("business"):
                md += "### Business & Strategy Questions\n"
                for q in interview_questions.get("business", []):
                    md += f"- {q}\n"
                md += "\n"
            
            if interview_questions.get("ml"):
                md += "### Machine Learning Questions\n"
                for q in interview_questions.get("ml", []):
                    md += f"- {q}\n"
                md += "\n"
            
            if interview_questions.get("system_design"):
                md += "### System Design Questions\n"
                for q in interview_questions.get("system_design", []):
                    md += f"- {q}\n"
                md += "\n"
            
            if interview_questions.get("mlops"):
                md += "### MLOps & Deployment Questions\n"
                for q in interview_questions.get("mlops", []):
                    md += f"- {q}\n"
                md += "\n"
            
            if interview_questions.get("behavioral"):
                md += "### Behavioral Questions\n"
                for q in interview_questions.get("behavioral", []):
                    md += f"- {q}\n"
                md += "\n"
        
        return md
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


class HTMLGenerator:
    """
    Generates HTML reports from Jinja2 template.
    Renders CompanyFitReport data into HTML format using report_template.html.
    """
    
    @staticmethod
    def generate(
        report_data: Dict[str, Any],
        template_path: str = "report_template.html"
    ) -> str:
        """
        Generate HTML report from Jinja2 template.
        
        Args:
            report_data: Complete report data (from CompanyFitReport.model_dump())
            template_path: Path to Jinja2 HTML template (relative to project root)
            
        Returns:
            Rendered HTML string
            
        Raises:
            FileNotFoundError: If template file not found
            Exception: If template rendering fails
        """
        logger.info(f"Generating HTML report from template: {template_path}")
        logger.info(f"Generating the HTML reports from data", report_data)
        
        try:
            # Get absolute path to template
            template_file = Path(template_path)
            if not template_file.is_absolute():
                # If relative, assume relative to project root
                template_file = Path.cwd() / template_path
            
            if not template_file.exists():
                raise FileNotFoundError(f"Template file not found: {template_file}")
            
            # Setup Jinja2 environment
            template_dir = template_file.parent
            template_name = template_file.name
            
            env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(['html', 'xml'])
            )
            
            # Load and render template
            template = env.get_template(template_name)
            
            # Flatten nested structures for template access
            flattened_data = HTMLGenerator._flatten_report_data(report_data)
            
            html = template.render(**flattened_data)
            
            logger.info(f"HTML report generated successfully ({len(html)} characters)")
            return html
        
        except FileNotFoundError as e:
            logger.error(f"Template file error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _flatten_report_data(report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten nested report data for Jinja2 template access.
        
        Converts nested structures like:
        {
          "company_evaluation": {
            "metadata": {...},
            "company_metrics": [...]
          }
        }
        
        To flat structure:
        {
          "company_name": "...",
          "company_metrics": [...],
          ...
        }
        
        Args:
            report_data: Nested report data
            
        Returns:
            Flattened dictionary
        """
        flattened = {}
        
        # Add generated_date
        flattened["generated_date"] = report_data.get("generated_date", "")
        
        # Flatten company_evaluation
        company_eval = report_data.get("company_evaluation", {})
        if company_eval:
            metadata = company_eval.get("metadata", {})
            flattened.update({
                "company_name": metadata.get("company_name", ""),
                "company_website": metadata.get("company_website", ""),
                "industry": metadata.get("industry", ""),
                "listing_status": metadata.get("listing_status", ""),
                "headquarters": metadata.get("headquarters", ""),
                "founded": metadata.get("founded", ""),
                "countries": metadata.get("countries", ""),
                "india_cities": metadata.get("india_cities", ""),
                "role_applied": company_eval.get("role_applied", ""),
                "overall_score": company_eval.get("overall_score", 0),
                "company_metrics": company_eval.get("company_metrics", []),
                "technology_stack": company_eval.get("technology_stack", []),
            })
        
        # Flatten personal_fit
        personal_fit = report_data.get("personal_fit", {})
        if personal_fit:
            flattened.update({
                "personal_fit_score": personal_fit.get("personal_fit_score", 0),
                "personal_fit_summary": f"Score: {personal_fit.get('personal_fit_score', 0)}/100",
                "personal_fit_strengths": personal_fit.get("strengths_match", []),
                "personal_fit_gaps": personal_fit.get("skill_gaps", []),
            })
        
        # Flatten resume_suggestions
        resume_sug = report_data.get("resume_suggestions", {})
        if resume_sug:
            flattened.update({
                "resume_alignment_score": resume_sug.get("resume_alignment_score", 0),
                "resume_gaps": resume_sug.get("resume_gaps", []),
                "resume_recommendations": resume_sug.get("resume_recommendations", []),
                "interview_questions": resume_sug.get("interview_questions", {
                    "business": [],
                    "ml": [],
                    "system_design": [],
                    "mlops": [],
                    "behavioral": []
                }),
            })
        
        # Flatten recommendation
        recommendation = report_data.get("recommendation", {})
        if recommendation:
            flattened.update({
                "recommendation": {
                    "decision": recommendation.get("decision", ""),
                    "reason": recommendation.get("reason", ""),
                }
            })
        
        return flattened
    
    @staticmethod
    def export_html(html_content: str, output_path: str) -> None:
        """
        Export HTML content to file.
        
        Args:
            html_content: Rendered HTML string
            output_path: Path where to save HTML file
        """
        logger.info(f"Exporting HTML report to: {output_path}")
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')
        
        logger.info(f"HTML report exported successfully ({output_file.stat().st_size} bytes)")
