import asyncio
from typing import Dict, List
from .tavily_client import tavily_client_connection
from .research_queries import build_queries


async def run_query(query: str):

    try:

        response = await tavily_client_connection.search(
            query=query,
            include_answer="advanced",
            search_depth="advanced",
            include_raw_content="markdown"
        )

        return response

    except Exception as e:

        return {"error": str(e), "query": query}


async def run_metric_queries(queries: List[str]):

    tasks = [run_query(q) for q in queries]

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    cleaned = []

    for r in responses:

        if isinstance(r, Exception):
            continue

        cleaned.append(r)

    return cleaned


async def run_company_research(company: str, role: str, salary: str):

    query_map = build_queries(company, role, salary)

    results: Dict[str, List] = {}

    tasks = {}

    for metric, queries in query_map.items():

        tasks[metric] = asyncio.create_task(
            run_metric_queries(queries)
        )

    for metric, task in tasks.items():

        results[metric] = await task

    return results