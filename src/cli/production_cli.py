#!/usr/bin/env python3
"""
Production CLI for ThingWorx Coding Agent
Supports Thing, Mashup, and App generation with local LLM
"""

import sys
import json
import os
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generator_local import LocalSpecGenerator, GenerationError
from src.executor import Executor, MashupExecutor, AppExecutor, ExecutionError
from src.rag import LocalRAGEngine
from src.llm import OllamaClient


console = Console()


@click.group()
@click.version_option(version="2.0.0-local")
def cli():
    """ThingWorx Coding Agent - Production Edition with Local LLM"""
    pass


@cli.command()
@click.argument("prompt")
@click.option("--output", "-o", help="Output file path (default: auto-generated)")
@click.option("--no-rag", is_flag=True, help="Disable RAG context injection")
def build(prompt: str, output: str, no_rag: bool):
    """
    Build a complete ThingWorx entity from a prompt
    
    Examples:
        twx-agent build "Create a Temperature Sensor Thing with GetTemperature service"
        twx-agent build "Build a Dashboard mashup with temperature chart"
        twx-agent build "Create an IoT Monitoring App with 3 dashboards"
    """
    try:
        console.print(f"[bold blue]Building from prompt:[/bold blue] {prompt}\n")
        
        # Check Ollama status
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        
        client = OllamaClient(base_url=ollama_url, model=ollama_model)
        
        if not client.is_available():
            console.print(f"[bold red]✗ Ollama not available at {ollama_url}[/bold red]")
            console.print("Please start Ollama: ollama serve")
            sys.exit(1)
        
        console.print(f"[green]✓ Ollama available[/green] ({ollama_model})\n")
        
        # Generate spec
        generator = LocalSpecGenerator(
            ollama_url=ollama_url,
            model=ollama_model,
            use_rag=not no_rag
        )
        
        console.print("[bold]Generating specification...[/bold]")
        spec = generator.generate(prompt)
        
        # Save spec
        if not output:
            timestamp = spec["metadata"]["generated_at"].replace(":", "-").replace(".", "-")
            output = f"artifacts/specs/spec_{timestamp}.json"
        
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(spec, f, indent=2)
        
        console.print(f"[green]✓ Spec saved to:[/green] {output_path}\n")
        
        # Show summary
        console.print("[bold]Specification Summary:[/bold]")
        console.print(f"  Actions: {len(spec['actions'])}")
        
        for idx, action in enumerate(spec['actions'], 1):
            console.print(f"  {idx}. {action['type']}: {action.get('description', 'N/A')}")
        
        console.print(f"\n[bold cyan]Next steps:[/bold cyan]")
        console.print(f"  1. Review: cat {output_path}")
        console.print(f"  2. Execute: twx-agent execute {output_path}")
        
    except GenerationError as e:
        console.print(f"[bold red]✗ Generation failed:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Show planned actions without executing")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def execute(spec_file: str, dry_run: bool, yes: bool):
    """
    Execute a specification file
    
    Examples:
        twx-agent execute artifacts/specs/spec_2025-01-08.json --dry-run
        twx-agent execute artifacts/specs/spec_2025-01-08.json -y
    """
    try:
        # Load spec
        with open(spec_file, 'r') as f:
            spec = json.load(f)
        
        console.print(f"[bold blue]Executing specification:[/bold blue] {spec_file}\n")
        
        # Show actions
        console.print("[bold]Actions to execute:[/bold]")
        for idx, action in enumerate(spec['actions'], 1):
            console.print(f"  {idx}. {action['type']}: {action.get('description', 'N/A')}")
        
        console.print()
        
        if dry_run:
            console.print("[yellow]DRY RUN - No actions will be executed[/yellow]")
            return
        
        # Confirm
        if not yes:
            confirm = click.confirm("Execute these actions?", default=False)
            if not confirm:
                console.print("[yellow]Execution cancelled[/yellow]")
                return
        
        # Execute
        executor = Executor()
        result = executor.execute_spec(spec, dry_run=False)
        
        if result["status"] == "success":
            console.print(f"\n[bold green]✓ Execution successful![/bold green]")
            console.print(f"  Actions executed: {result['actions_executed']}")
            console.print(f"  Log file: {result.get('log_file', 'N/A')}")
        else:
            console.print(f"\n[bold red]✗ Execution failed[/bold red]")
            console.print(f"  Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.option("--rebuild", is_flag=True, help="Rebuild knowledge base")
def rag(rebuild: bool):
    """
    Manage RAG knowledge base
    
    Examples:
        twx-agent rag --rebuild
        twx-agent rag
    """
    try:
        kb_path = Path(".kb_local")
        
        if rebuild or not kb_path.exists():
            console.print("[bold blue]Building knowledge base...[/bold blue]\n")
            
            engine = LocalRAGEngine()
            docs_dir = Path("docs")
            
            if not docs_dir.exists():
                console.print("[bold red]✗ docs/ directory not found[/bold red]")
                sys.exit(1)
            
            engine.build(docs_dir)
            console.print("\n[green]✓ Knowledge base built successfully[/green]\n")
        
        # Show stats
        engine = LocalRAGEngine()
        stats = engine.stats()
        
        if stats.get("status") == "empty":
            console.print("[yellow]Knowledge base is empty[/yellow]")
            console.print("Run: twx-agent rag --rebuild")
            return
        
        console.print("[bold]Knowledge Base Statistics:[/bold]\n")
        
        table = Table()
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Chunks", str(stats["total_chunks"]))
        table.add_row("Total Files", str(stats["total_files"]))
        table.add_row("Vocabulary Size", str(stats["vocabulary_size"]))
        
        for chunk_type, count in stats["chunk_types"].items():
            table.add_row(f"  {chunk_type.title()} Chunks", str(count))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--top-k", "-k", type=int, default=3, help="Number of results")
def query(query: str, top_k: int):
    """
    Query the knowledge base
    
    Examples:
        twx-agent query "How to create a service?"
        twx-agent query "Mashup widgets" -k 5
    """
    try:
        kb_path = Path(".kb_local")
        
        if not kb_path.exists():
            console.print("[bold red]✗ Knowledge base not found[/bold red]")
            console.print("Run: twx-agent rag --rebuild")
            sys.exit(1)
        
        engine = LocalRAGEngine()
        results = engine.query(query, top_k=top_k)
        
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        console.print(f"[bold green]Found {len(results)} results:[/bold green]\n")
        
        for idx, result in enumerate(results, 1):
            relevance = result["relevance"]
            relevance_color = "green" if relevance > 0.5 else "yellow" if relevance > 0.3 else "white"
            
            title = f"Result {idx}: {result['file']} - {result['section']} (Score: {relevance:.3f})"
            
            content_preview = result["content"][:300]
            if len(result["content"]) > 300:
                content_preview += "..."
            
            panel = Panel(
                content_preview,
                title=title,
                border_style=relevance_color,
                expand=False
            )
            console.print(panel)
            console.print()
        
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
def status():
    """
    Show system status
    
    Examples:
        twx-agent status
    """
    try:
        console.print("[bold blue]ThingWorx Coding Agent - System Status[/bold blue]\n")
        
        # Check Ollama
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        
        client = OllamaClient(base_url=ollama_url, model=ollama_model)
        ollama_available = client.is_available()
        
        console.print(f"[bold]Ollama LLM:[/bold]")
        console.print(f"  URL: {ollama_url}")
        console.print(f"  Model: {ollama_model}")
        console.print(f"  Status: {'[green]✓ Available[/green]' if ollama_available else '[red]✗ Not available[/red]'}")
        
        if ollama_available:
            models = client.list_models()
            console.print(f"  Models: {', '.join(models) if models else 'None'}")
        
        console.print()
        
        # Check RAG
        kb_path = Path(".kb_local")
        rag_available = kb_path.exists()
        
        console.print(f"[bold]RAG Knowledge Base:[/bold]")
        console.print(f"  Status: {'[green]✓ Built[/green]' if rag_available else '[yellow]⚠ Not built[/yellow]'}")
        
        if rag_available:
            engine = LocalRAGEngine()
            stats = engine.stats()
            console.print(f"  Chunks: {stats['total_chunks']}")
            console.print(f"  Files: {stats['total_files']}")
        
        console.print()
        
        # Check ThingWorx connection
        from src.config import get_config, ConfigError
        
        try:
            config = get_config()
            console.print(f"[bold]ThingWorx Connection:[/bold]")
            console.print(f"  URL: {config.base_url}")
            console.print(f"  AppKey: {'[green]✓ Configured[/green]' if config.app_key else '[red]✗ Not configured[/red]'}")
        except ConfigError as e:
            console.print(f"[bold]ThingWorx Connection:[/bold]")
            console.print(f"  [red]✗ Not configured[/red]")
            console.print(f"  Error: {e}")
        
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
