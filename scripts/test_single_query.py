#!/usr/bin/env python3
"""
Test a single query through the integrated workflow.
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

from agents.integrated_agent import get_integrated_agent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


def test_query(query: str):
    """Test a single query."""
    console.print("\n[bold white on blue] 🧪 TESTING SINGLE QUERY [/bold white on blue]\n")
    console.print(Panel(f"[bold cyan]Query:[/bold cyan] {query}", border_style="cyan"))
    
    try:
        agent = get_integrated_agent()
        result = agent.query(query)
        
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
        
        console.print("\n[bold green]✅ Test completed successfully![/bold green]")
        
        return result
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        raise


if __name__ == "__main__":
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "How do I add a new user in MyAastha?"
    
    test_query(query)
