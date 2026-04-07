from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    research_node,
    company_eval_node,
    personal_fit_node,
    resume_node,
    recommendation_node,
    report_generation_node,
)


def build_workflow():
    """
    Build the complete LangGraph workflow for company assessment.
    
    Workflow:
    research → company_eval → personal_fit → resume_opt → recommendation → report_generation → END
    """

    builder = StateGraph(AgentState)

    # Add all nodes
    builder.add_node("research", research_node)
    builder.add_node("company_eval", company_eval_node)
    builder.add_node("personal_fit", personal_fit_node)
    builder.add_node("resume_opt", resume_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("report_generation", report_generation_node)

    # Set entry point
    builder.set_entry_point("research")

    # Define edges (workflow path)
    builder.add_edge("research", "company_eval")
    builder.add_edge("company_eval", "personal_fit")
    builder.add_edge("personal_fit", "resume_opt")
    builder.add_edge("resume_opt", "recommendation")
    builder.add_edge("recommendation", "report_generation")
    builder.add_edge("report_generation", END)

    # Compile the graph
    graph = builder.compile()

    return graph