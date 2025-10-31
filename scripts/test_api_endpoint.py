#!/usr/bin/env python3
"""
Simple test script for the API endpoint.

Tests the /api/v1/query endpoint with sample queries.
"""

import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON

console = Console()

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{API_BASE_URL}/api/v1/query"


def test_query(query_text: str, description: str):
    """Test a single query."""
    console.print(f"\n[bold cyan]Test: {description}[/bold cyan]")
    console.print(f"[dim]Query: {query_text}[/dim]")
    
    # Prepare request
    payload = {
        "query": query_text,
        "include_sources": True,
        "include_metadata": True
    }
    
    try:
        # Send request
        console.print("[yellow]Sending request...[/yellow]")
        response = requests.post(API_ENDPOINT, json=payload, timeout=60)
        
        # Check status
        if response.status_code == 200:
            result = response.json()
            
            # Display results
            console.print("\n[bold green]✓ Success![/bold green]")
            console.print(f"Route: [cyan]{result['datasource']}[/cyan]")
            console.print(f"Session ID: [dim]{result['session_id']}[/dim]")
            
            # Answer
            console.print(Panel(
                result['answer'],
                title="[bold green]Answer[/bold green]",
                border_style="green"
            ))
            
            # Metadata
            if result.get('metadata'):
                console.print("\n[bold]Metadata:[/bold]")
                console.print(JSON(json.dumps(result['metadata'], indent=2)))
            
            # Sources
            if result.get('sources'):
                console.print(f"\n[bold]Sources:[/bold] {', '.join(result['sources'][:3])}")
            
        else:
            console.print(f"[bold red]✗ Error: {response.status_code}[/bold red]")
            console.print(response.text)
            
    except requests.exceptions.ConnectionError:
        console.print("[bold red]✗ Connection Error: Is the API server running?[/bold red]")
        console.print("[yellow]Start the server with: uvicorn api.main:app --reload[/yellow]")
    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")


def main():
    """Run all tests."""
    console.print("\n[bold white on blue] API ENDPOINT TESTS [/bold white on blue]\n")
    
    # Check if API is running
    try:
        health_response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        if health_response.status_code == 200:
            console.print("[green]✓ API is running[/green]\n")
        else:
            console.print("[red]✗ API health check failed[/red]\n")
            return
    except:
        console.print("[bold red]✗ API is not running![/bold red]")
        console.print("[yellow]Start the server with:[/yellow]")
        console.print("[cyan]uvicorn api.main:app --reload[/cyan]\n")
        return
    
    # Test queries
    tests = [
        ("List all branches in Patna", "API Query - Branch Search"),
        ("What savings schemes are available?", "API Query - Scheme Search"),
        ("How do I open an account?", "RAG Query - Procedure"),
        ("Show me all RD schemes and explain how they work", "Hybrid Query - Combined")
    ]
    
    for query, description in tests:
        test_query(query, description)
        console.print("\n" + "=" * 80)
    
    console.print("\n[bold green]✅ All tests completed![/bold green]\n")


if __name__ == "__main__":
    main()
