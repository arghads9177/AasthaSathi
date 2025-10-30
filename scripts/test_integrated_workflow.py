#!/usr/bin/env python3
"""
Test integrated workflow with various query types.

Tests:
1. API-only queries (branches, schemes, members, accounts)
2. RAG-only queries (policies, procedures)
3. Hybrid queries (combining API data with knowledge base)
4. Error handling and fallback scenarios
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from agents.integrated_agent import get_integrated_agent, reset_integrated_agent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


def print_result(query: str, result: dict):
    """Print formatted result with rich styling."""
    console.print("\n" + "=" * 80)
    console.print(Panel(f"[bold cyan]Query:[/bold cyan] {query}", border_style="cyan"))
    
    # Routing info
    console.print(f"\n[bold green]🧭 Routing Decision:[/bold green] {result['datasource']}")
    console.print(f"[dim]{result['routing_reasoning']}[/dim]")
    
    # Execution path
    console.print(f"\n[bold yellow]📍 Execution Path:[/bold yellow] {' → '.join(result['execution_path'])}")
    
    # Stats
    console.print(f"\n[bold magenta]📊 Stats:[/bold magenta]")
    console.print(f"  • API used: {'✓' if result['api_used'] else '✗'}")
    console.print(f"  • Documents retrieved: {result['num_retrieved']}")
    console.print(f"  • Relevant documents: {result['num_relevant']}")
    console.print(f"  • Retry count: {result['retry_count']}")
    
    # Sources
    if result['sources']:
        console.print(f"\n[bold blue]📚 Sources Used:[/bold blue]")
        for source in result['sources'][:5]:  # Limit to 5
            console.print(f"  • {source}")
    
    # Answer
    console.print(f"\n[bold green]💬 Answer:[/bold green]")
    console.print(Panel(Markdown(result['answer']), border_style="green"))
    
    console.print("=" * 80)


def test_api_queries():
    """Test API-only queries."""
    console.print("\n[bold white on blue] TEST 1: API-ONLY QUERIES [/bold white on blue]")
    
    agent = get_integrated_agent()
    
    queries = [
        "List all branches in Patna",
        "What savings schemes are available?",
        "How many members joined in January 2025?",
        "Show me all SB accounts opened in 2024",
        "What is the available balance for account number 12345?"
    ]
    
    for query in queries:
        result = agent.query(query)
        print_result(query, result)


def test_rag_queries():
    """Test RAG-only queries."""
    console.print("\n[bold white on blue] TEST 2: RAG-ONLY QUERIES [/bold white on blue]")
    
    agent = get_integrated_agent()
    
    queries = [
        "What are the membership eligibility criteria?",
        "Explain the loan application process",
        "What documents are required for opening an account?",
        "What are the interest rates for fixed deposits?"
    ]
    
    for query in queries:
        result = agent.query(query)
        print_result(query, result)


def test_hybrid_queries():
    """Test hybrid queries combining API and RAG."""
    console.print("\n[bold white on blue] TEST 3: HYBRID QUERIES [/bold white on blue]")
    
    agent = get_integrated_agent()
    
    queries = [
        "Show me all RD schemes and explain how recurring deposits work",
        "List branches in Gaya and tell me what services they offer",
        "How many members joined last month and what are the membership benefits?",
        "What loan schemes are available and what is the eligibility criteria?"
    ]
    
    for query in queries:
        result = agent.query(query)
        print_result(query, result)


def test_conversation_flow():
    """Test conversational queries with follow-ups."""
    console.print("\n[bold white on blue] TEST 4: CONVERSATION FLOW [/bold white on blue]")
    
    agent = get_integrated_agent()
    session_id = "test_session_001"
    
    conversation = [
        "What savings schemes do you offer?",
        "What is the interest rate for the first scheme?",
        "How can I open an account?",
        "Are there any branches in Patna?"
    ]
    
    chat_history = []
    
    for query in conversation:
        result = agent.query(
            query,
            session_id=session_id,
            chat_history=chat_history
        )
        print_result(query, result)
        chat_history = result['chat_history']


def test_error_scenarios():
    """Test error handling and edge cases."""
    console.print("\n[bold white on blue] TEST 5: ERROR SCENARIOS [/bold white on blue]")
    
    agent = get_integrated_agent()
    
    queries = [
        "What is the weather today?",  # Out of scope
        "",  # Empty query
        "xyz123abc",  # Gibberish
        "Balance for account 99999999999"  # Non-existent account
    ]
    
    for query in queries:
        result = agent.query(query)
        print_result(query, result)


def run_all_tests():
    """Run all test suites."""
    console.print("\n[bold white on red] 🚀 INTEGRATED WORKFLOW TESTS 🚀 [/bold white on red]\n")
    
    try:
        test_api_queries()
        test_rag_queries()
        test_hybrid_queries()
        test_conversation_flow()
        test_error_scenarios()
        
        console.print("\n[bold green]✅ All tests completed![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        raise


if __name__ == "__main__":
    # Reset agent to start fresh
    reset_integrated_agent()
    
    # Run all tests
    run_all_tests()
