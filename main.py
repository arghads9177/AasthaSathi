#!/usr/bin/env python3
"""
AasthaSathi - Main Application Entry Point

This is the main entry point for the AasthaSathi AI Assistant.
Run this file to start the application.
"""

import sys
import logging
from pathlib import Path
from uuid import uuid4

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from core.config import get_settings
from agents.integrated_agent import get_integrated_agent

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings/errors for cleaner output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


def print_welcome():
    """Print welcome message."""
    console.print("\n" + "=" * 80)
    console.print(Panel.fit(
        "[bold cyan]🙏 AasthaSathi - AI Assistant[/bold cyan]\n"
        "[dim]Aastha Co-operative Credit Society Ltd.[/dim]",
        border_style="cyan"
    ))
    console.print("=" * 80)
    
    console.print("\n[bold green]Features:[/bold green]")
    console.print("  • 🏦 Real-time banking data (branches, schemes, members, accounts)")
    console.print("  • 📚 Knowledge base queries (policies, procedures, guidelines)")
    console.print("  • 🔄 Hybrid queries (combining API + Knowledge Base)")
    console.print("  • 💬 Conversational interface with chat history")
    
    console.print("\n[bold yellow]Commands:[/bold yellow]")
    console.print("  • [cyan]exit[/cyan] or [cyan]quit[/cyan] - Exit the application")
    console.print("  • [cyan]help[/cyan] - Show example queries")
    console.print("  • [cyan]clear[/cyan] - Start new conversation")
    
    console.print("=" * 80 + "\n")


def print_help():
    """Print example queries."""
    console.print("\n[bold cyan]📖 Example Queries:[/bold cyan]")
    
    console.print("\n[bold yellow]API Queries (Real-time Data):[/bold yellow]")
    console.print("  • List all branches in Patna")
    console.print("  • What savings schemes are available?")
    console.print("  • How many members joined in January 2025?")
    console.print("  • Show me all SB accounts opened in 2024")
    
    console.print("\n[bold yellow]RAG Queries (Knowledge Base):[/bold yellow]")
    console.print("  • What are the membership eligibility criteria?")
    console.print("  • Explain the loan application process")
    console.print("  • What documents are required for opening an account?")
    
    console.print("\n[bold yellow]Hybrid Queries (Combined):[/bold yellow]")
    console.print("  • Show me all RD schemes and explain how they work")
    console.print("  • List branches in Gaya and their services")
    console.print("  • What loan schemes are available and eligibility criteria?\n")


def print_response(result: dict):
    """Print formatted response."""
    # Routing info
    console.print(f"\n[dim]🧭 Route: {result['datasource']} | "
                  f"Path: {' → '.join(result['execution_path'][:3])}...[/dim]")
    
    # Answer
    console.print(Panel(
        Markdown(result['answer']),
        border_style="green",
        title="[bold green]💬 Answer[/bold green]",
        title_align="left"
    ))
    
    # Sources (compact view)
    if result['sources']:
        sources_preview = result['sources'][:3]
        sources_text = "\n".join([f"  • {s}" for s in sources_preview])
        if len(result['sources']) > 3:
            sources_text += f"\n  [dim]... and {len(result['sources']) - 3} more[/dim]"
        console.print(f"\n[dim]📚 Sources:[/dim]\n{sources_text}")


def main():
    """Main application entry point."""
    try:
        # Load configuration
        settings = get_settings()
        
        # Print welcome
        print_welcome()
        
        # Initialize agent
        with console.status("[bold cyan]Initializing agent..."):
            agent = get_integrated_agent()
        console.print("[bold green]✓[/bold green] Agent ready!\n")
        
        # Session management
        session_id = str(uuid4())
        chat_history = []
        
        # Main interaction loop
        while True:
            try:
                # Get user input
                user_query = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                # Handle commands
                if user_query.lower() in ['exit', 'quit', 'q']:
                    console.print("\n[bold cyan]👋 Thank you for using AasthaSathi![/bold cyan]\n")
                    break
                
                if user_query.lower() == 'help':
                    print_help()
                    continue
                
                if user_query.lower() == 'clear':
                    session_id = str(uuid4())
                    chat_history = []
                    console.print("\n[bold green]✓[/bold green] New conversation started\n")
                    continue
                
                if not user_query.strip():
                    continue
                
                # Process query
                with console.status("[bold cyan]Processing..."):
                    result = agent.query(
                        user_query=user_query,
                        session_id=session_id,
                        chat_history=chat_history
                    )
                
                # Update chat history
                chat_history = result.get('chat_history', [])
                
                # Print response
                print_response(result)
                
            except KeyboardInterrupt:
                console.print("\n\n[bold cyan]👋 Goodbye![/bold cyan]\n")
                break
            except Exception as e:
                console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
                logging.error(f"Error processing query: {str(e)}", exc_info=True)
    
    except Exception as e:
        console.print(f"\n[bold red]❌ Startup Error: {str(e)}[/bold red]")
        if "API_KEY" in str(e) or "api_key" in str(e):
            console.print("\n[bold yellow]💡 Configuration Required:[/bold yellow]")
            console.print("  1. Ensure .env file exists with required API keys")
            console.print("  2. Set OPENAI_API_KEY or GOOGLE_API_KEY")
            console.print("  3. Set BANKING_AUTH_KEY for API access")
        sys.exit(1)


if __name__ == "__main__":
    main()

