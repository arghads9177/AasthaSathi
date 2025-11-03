#!/usr/bin/env python3
"""
Quick API Test Script
Tests various query types through the integrated agent
"""

import sys
from pathlib import Path
from uuid import uuid4

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from agents.integrated_agent import get_integrated_agent

console = Console()


def test_api_query(agent, query: str):
    """Test a single API query."""
    console.print(f"\n{'=' * 80}")
    console.print(f"[bold cyan]Query:[/bold cyan] {query}")
    console.print('=' * 80)
    
    try:
        session_id = str(uuid4())
        result = agent.query(
            user_query=query,
            session_id=session_id,
            chat_history=[]
        )
        
        # Print routing info
        console.print(f"\n[bold green]✓ Route:[/bold green] {result['datasource']}")
        console.print(f"[dim]Path: {' → '.join(result['execution_path'])}")
        console.print(f"API Used: {'Yes' if result['api_used'] else 'No'}")
        console.print(f"Documents: {result['documents_retrieved']}/{result['relevant_documents']}[/dim]")
        
        # Print answer
        console.print(Panel(
            Markdown(result['answer']),
            border_style="green",
            title="💬 Answer",
            title_align="left"
        ))
        
        # Print sources
        if result['sources']:
            console.print(f"\n[bold]📚 Sources:[/bold]")
            for source in result['sources'][:3]:
                console.print(f"  • {source}")
            if len(result['sources']) > 3:
                console.print(f"  [dim]... and {len(result['sources']) - 3} more[/dim]")
        
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run API tests."""
    console.print("\n[bold cyan]🚀 API QUERY TESTS[/bold cyan]\n")
    
    # Initialize agent
    with console.status("[bold cyan]Initializing agent..."):
        agent = get_integrated_agent()
    console.print("[bold green]✓ Agent ready![/bold green]\n")
    
    # Test queries
    test_queries = [
        # API queries
        ("List all branches in Kolkata", "API"),
        ("What savings schemes are available?", "API"),
        ("How many members joined in February 2025?", "API"),
        
        # RAG queries  
        ("What are the membership eligibility criteria?", "RAG"),
        ("Explain the loan application process", "RAG"),
        
        # Hybrid query
        ("Show me all RD schemes and explain how recurring deposits work", "Hybrid"),
    ]
    
    results = []
    for query, expected_type in test_queries:
        console.print(f"\n[bold yellow]Testing {expected_type} Query...[/bold yellow]")
        success = test_api_query(agent, query)
        results.append((query, expected_type, success))
    
    # Summary
    console.print(f"\n\n{'=' * 80}")
    console.print("[bold cyan]📊 TEST SUMMARY[/bold cyan]")
    console.print('=' * 80)
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    console.print(f"\n[bold]Results: {passed}/{total} passed[/bold]")
    
    for query, query_type, success in results:
        status = "✓" if success else "✗"
        color = "green" if success else "red"
        console.print(f"  [{color}]{status}[/{color}] {query_type}: {query[:50]}...")
    
    console.print("\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
