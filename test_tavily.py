"""
Isolated test file for Tavily parallel research queries.
This file tests the Tavily search functionality independently.
"""

import asyncio
import json
import sys
import logging
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging for the test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.research.parallel_research import run_company_research
from app.research.research_queries import build_queries


async def test_simple_query():
    """Test a single simple Tavily query"""
    print("=" * 80)
    print("TEST 1: Testing a single Tavily query")
    print("=" * 80)
    
    from app.research.tavily_client import tavily_client_connection
    
    try:
        query = "Google artificial intelligence initiatives"
        print(f"\nQuery: {query}")
        print("Searching...\n")
        
        response = await tavily_client_connection.search(
            query=query,
            include_answer="advanced",
            search_depth="advanced",
            include_raw_content="markdown"
        )
        
        print("Response received!")
        print(f"Response keys: {response.keys()}")
        print(f"\nAnswer: {response.get('answer', 'N/A')[:200]}...")
        print(f"Number of results: {len(response.get('results', []))}")
        
        # Print first result details
        if response.get('results'):
            first_result = response['results'][0]
            print(f"\nFirst result:")
            print(f"  Title: {first_result.get('title', 'N/A')}")
            print(f"  URL: {first_result.get('url', 'N/A')}")
            print(f"  Content preview: {first_result.get('content', 'N/A')[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_metric_query():
    """Test queries for a single metric"""
    print("\n" + "=" * 80)
    print("TEST 2: Testing multiple queries for a single metric")
    print("=" * 80)
    
    from app.research.parallel_research import run_metric_queries
    
    try:
        company = "Google"
        queries = [
            f"{company} artificial intelligence initiatives",
            f"{company} machine learning platform or AI products",
            f"{company} generative AI strategy"
        ]
        
        print(f"\nCompany: {company}")
        print(f"Queries to run ({len(queries)}):")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
        
        print("\nRunning metric queries in parallel...\n")
        responses = await run_metric_queries(queries)
        
        print(f"Received {len(responses)} responses")
        for i, response in enumerate(responses, 1):
            print(f"\nResponse {i}:")
            print(f"  Answer: {response.get('answer', 'N/A')[:150]}...")
            print(f"  Results count: {len(response.get('results', []))}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_company_research():
    """Test the full company research workflow"""
    print("\n" + "=" * 80)
    print("TEST 3: Testing full company research workflow")
    print("=" * 80)
    
    try:
        company = "Google"
        role = "Software Engineer"
        salary = "50000-100000 USD"
        
        print(f"\nCompany: {company}")
        print(f"Role: {role}")
        print(f"Salary: {salary}")
        
        # First, let's see what queries will be built
        queries = build_queries(company, role, salary)
        print(f"\nTotal metrics to research: {len(queries)}")
        total_queries = sum(len(q) for q in queries.values())
        print(f"Total queries to run: {total_queries}")
        
        print("\nQueries by metric:")
        for metric, metric_queries in queries.items():
            print(f"  {metric}: {len(metric_queries)} queries")
        
        print("\nRunning full company research (this may take a while)...\n")
        results = await run_company_research(company, role, salary)
        
        print("=" * 80)
        print("RESEARCH COMPLETE")
        print("=" * 80)
        
        print(f"\nResults by metric:")
        for metric, metric_results in results.items():
            print(f"\n{metric}:")
            print(f"  Results received: {len(metric_results)}")
            if metric_results:
                for i, result in enumerate(metric_results[:1], 1):  # Show first result only
                    answer = result.get('answer', 'N/A')
                    print(f"  Result {i} answer: {answer[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TAVILY PARALLEL RESEARCH - ISOLATED TEST")
    print("=" * 80 + "\n")
    
    # Test 1: Single query
    test1_passed = await test_simple_query()
    
    # Test 2: Metric queries
    if test1_passed:
        test2_passed = await test_metric_query()
    else:
        print("\n⚠️ Skipping Test 2 - Test 1 failed")
        test2_passed = False
    
    # Test 3: Full workflow
    if test2_passed:
        response = input("\n\nWould you like to run Test 3 (full company research)? This may take several minutes. (y/n): ")
        if response.lower() == 'y':
            test3_passed = await test_full_company_research()
        else:
            test3_passed = None
            print("Skipping Test 3")
    else:
        print("\n⚠️ Skipping Test 3 - Test 2 failed")
        test3_passed = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Test 1 (Single Query): {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Test 2 (Metric Queries): {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    if test3_passed is not None:
        print(f"Test 3 (Full Research): {'✓ PASSED' if test3_passed else '✗ FAILED'}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
