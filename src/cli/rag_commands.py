"""
RAG CLI Commands
Commands for building and querying the knowledge base
"""

import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag import RAGEngine


console = Console()


@click.group()
def rag():
    """RAG (Retrieval-Augmented Generation) commands for knowledge base management"""
    pass


@rag.command()
@click.option(
    "--docs-dir",
    "-d",
    type=click.Path(exists=True),
    default="docs",
    help="Documentation directory to index"
)
@click.option(
    "--kb-dir",
    "-k",
    type=click.Path(),
    default=".kb",
    help="Knowledge base directory"
)
def build(docs_dir: str, kb_dir: str):
    """
    Build knowledge base from documentation
    
    Example:
        twx-agent rag build
        twx-agent rag build --docs-dir docs --kb-dir .kb
    """
    try:
        console.print(f"[bold blue]Building knowledge base...[/bold blue]")
        console.print(f"Documentation directory: {docs_dir}")
        console.print(f"Knowledge base directory: {kb_dir}\n")
        
        docs_path = Path(docs_dir)
        kb_path = Path(kb_dir)
        
        if not docs_path.exists():
            console.print(f"[bold red]✗ Documentation directory not found: {docs_dir}[/bold red]")
            sys.exit(1)
        
        # Build knowledge base
        engine = RAGEngine(kb_dir=kb_path)
        engine.build(docs_path)
        
        # Show statistics
        stats = engine.stats()
        
        console.print(f"\n[bold green]✓ Knowledge base built successfully![/bold green]")
        
        stats_table = Table(title="Knowledge Base Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Chunks", str(stats["total_chunks"]))
        stats_table.add_row("Total Files", str(stats["total_files"]))
        
        for chunk_type, count in stats["chunk_types"].items():
            stats_table.add_row(f"  {chunk_type.title()} Chunks", str(count))
        
        stats_table.add_row("Index File", stats["index_file"])
        stats_table.add_row("Embeddings File", stats["embeddings_file"])
        
        console.print(stats_table)
        
    except Exception as e:
        console.print(f"[bold red]✗ Build failed:[/bold red] {e}")
        sys.exit(1)


@rag.command()
@click.argument("query")
@click.option(
    "--top-k",
    "-k",
    type=int,
    default=5,
    help="Number of results to return"
)
@click.option(
    "--kb-dir",
    type=click.Path(),
    default=".kb",
    help="Knowledge base directory"
)
def query(query: str, top_k: int, kb_dir: str):
    """
    Query the knowledge base
    
    Example:
        twx-agent rag query "How do I create a service?"
        twx-agent rag query "ServiceHelper usage" --top-k 3
    """
    try:
        kb_path = Path(kb_dir)
        
        if not kb_path.exists():
            console.print(f"[bold red]✗ Knowledge base not found. Run 'twx-agent rag build' first.[/bold red]")
            sys.exit(1)
        
        console.print(f"[bold blue]Querying knowledge base...[/bold blue]")
        console.print(f"Query: {query}\n")
        
        # Query knowledge base
        engine = RAGEngine(kb_dir=kb_path)
        results = engine.query(query, top_k=top_k)
        
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        # Display results
        console.print(f"[bold green]Found {len(results)} results:[/bold green]\n")
        
        for idx, result in enumerate(results, 1):
            relevance = result["relevance"]
            relevance_color = "green" if relevance > 0.8 else "yellow" if relevance > 0.6 else "white"
            
            title = f"Result {idx}: {result['file']} - {result['section']} (Relevance: {relevance:.2f})"
            
            content_preview = result["content"][:500]
            if len(result["content"]) > 500:
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
        console.print(f"[bold red]✗ Query failed:[/bold red] {e}")
        sys.exit(1)


@rag.command()
@click.option(
    "--kb-dir",
    type=click.Path(),
    default=".kb",
    help="Knowledge base directory"
)
def stats(kb_dir: str):
    """
    Show knowledge base statistics
    
    Example:
        twx-agent rag stats
    """
    try:
        kb_path = Path(kb_dir)
        
        if not kb_path.exists():
            console.print(f"[bold yellow]Knowledge base not found at {kb_dir}[/bold yellow]")
            console.print("Run 'twx-agent rag build' to create it.")
            return
        
        engine = RAGEngine(kb_dir=kb_path)
        stats_data = engine.stats()
        
        if stats_data.get("status") == "empty":
            console.print("[bold yellow]Knowledge base is empty[/bold yellow]")
            console.print("Run 'twx-agent rag build' to populate it.")
            return
        
        console.print("[bold blue]Knowledge Base Statistics[/bold blue]\n")
        
        stats_table = Table()
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Chunks", str(stats_data["total_chunks"]))
        stats_table.add_row("Total Files", str(stats_data["total_files"]))
        
        for chunk_type, count in stats_data["chunk_types"].items():
            stats_table.add_row(f"  {chunk_type.title()} Chunks", str(count))
        
        stats_table.add_row("Index File", stats_data["index_file"])
        stats_table.add_row("Embeddings File", stats_data["embeddings_file"])
        
        console.print(stats_table)
        
    except Exception as e:
        console.print(f"[bold red]✗ Failed to get stats:[/bold red] {e}")
        sys.exit(1)
