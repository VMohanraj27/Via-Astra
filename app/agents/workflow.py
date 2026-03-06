from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import research_node, company_eval_node, personal_fit_node, resume_node


def build_workflow():

    builder = StateGraph(AgentState)

    builder.add_node("research", research_node)
    builder.add_node("company_eval", company_eval_node)
    builder.add_node("personal_fit", personal_fit_node)
    builder.add_node("resume_opt", resume_node)

    builder.set_entry_point("research")

    builder.add_edge("research", "company_eval")
    builder.add_edge("company_eval", "personal_fit")
    builder.add_edge("personal_fit", "resume_opt")
    builder.add_edge("resume_opt", END)

    graph = builder.compile()

    return graph