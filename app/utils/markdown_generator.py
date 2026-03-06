def generate_markdown(company_eval, personal_fit, resume):

    md = f"""

# Company Fit Assessment

{company_eval}

---

# Personal Fit

{personal_fit}

---

# Resume Optimization

{resume}
"""

    return md