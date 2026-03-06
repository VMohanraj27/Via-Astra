def build_queries(company: str, role: str, salary: str):

    return {

        "ai_data_footprint": [
            f"{company} artificial intelligence initiatives",
            f"{company} machine learning platform or AI products",
            f"{company} generative AI strategy",
            f"{company} AI research partnerships or innovation labs",
            f"{company} data platform or advanced analytics initiatives"
        ],

        "technology_stack": [
            f"{company} engineering tech stack",
            f"{company} backend architecture technologies",
            f"{company} cloud infrastructure used by {company}",
            f"{company} ML platform or MLOps tools",
            f"{company} developer tooling engineering practices"
        ],

        "core_offerings": [
            f"{company} products and services",
            f"{company} main business model",
            f"{company} key industry verticals",
            f"{company} customers and market segments"
        ],

        "learning_upskilling": [
            f"{company} employee training programs",
            f"{company} engineering learning opportunities",
            f"{company} certification programs employees",
            f"{company} internal learning academy"
        ],

        "company_culture": [
            f"{company} engineering culture blog",
            f"{company} employee reviews culture",
            f"{company} leadership philosophy",
            f"{company} work life balance engineers"
        ],

        "work_structure": [
            f"{company} work hours engineers",
            f"{company} remote or hybrid policy",
            f"{company} client engagement model",
            f"{company} regions and markets served"
        ],

        "role_research": [
            f"{role} responsibilities at {company}",
            f"{company} {role} team responsibilities",
            f"{company} engineering team structure",
            f"{company} AI engineer responsibilities"
        ],

        "salary_assessment": [
            f"{company} {role} salary India",
            f"{company} software engineer salary range",
            f"{company} compensation benefits engineers",
            f"{company} pay scale technology roles"
        ]
    }