#!/usr/bin/env python3
"""
ThingWorx Coding Agent CLI
Main command-line interface
"""

import json
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generator import SpecGenerator, GenerationError
from src.executor import Executor, ExecutionError
from src.schema import validate_spec_file, ValidationError
from src.guardrails import validate_spec as validate_guardrails, GuardrailViolation
from src.cli.rag_commands import rag


console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """ThingWorx Coding Agent - Automated ThingWorx development with RAG and safety guardrails"""
    pass


# Add RAG commands
cli.add_command(rag)


@cli.command()
@click.argument("prompt")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="artifacts/specs",
    help="Output directory for generated spec"
)
def generate_spec(prompt: str, output: str):
    """
    Generate a specification from a natural language prompt
    
    Example:
        twx-agent generate-spec "Create a Thing called Calculator with an Add service"
    """
    try:
        console.print(f"[bold blue]Generating spec from prompt...[/bold blue]")
        console.print(f"Prompt: {prompt}\n")
        
        # Generate spec
        generator = SpecGenerator()
        output_dir = Path(output)
        spec_file = generator.generate_and_save(prompt, output_dir)
        
        # Validate schema
        console.print("[yellow]Validating against schema...[/yellow]")
        validate_spec_file(spec_file)
        
        # Validate guardrails
        console.print("[yellow]Validating guardrails...[/yellow]")
        with open(spec_file) as f:
            spec = json.load(f)
        validate_guardrails(spec)
        
        # Display result
        console.print(f"[bold green]✓ Spec generated successfully![/bold green]")
        console.print(f"Saved to: {spec_file}\n")
        
        # Show spec preview
        with open(spec_file) as f:
            spec_json = f.read()
        
        syntax = Syntax(spec_json, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Generated Specification", border_style="green"))
        
        # Show actions summary
        table = Table(title="Actions Summary")
        table.add_column("Step", style="cyan")
        table.add_column("Action Type", style="magenta")
        table.add_column("Description", style="white")
        
        for idx, action in enumerate(spec["actions"], 1):
            action_type = action["type"]
            description = action.get("description", "")
            if not description:
                # Generate description from params
                params = action.get("params", {})
                if action_type == "CreateThing":
                    description = f"Create Thing '{params.get('name')}'"
                elif action_type == "EnableThing":
                    description = f"Enable Thing '{params.get('thingName')}'"
                elif action_type == "AddServiceToThing":
                    description = f"Add service '{params.get('serviceName')}' to '{params.get('thingName')}'"
            
            table.add_row(str(idx), action_type, description)
        
        console.print(table)
        
    except GenerationError as e:
        console.print(f"[bold red]✗ Generation failed:[/bold red] {e}")
        sys.exit(1)
    except ValidationError as e:
        console.print(f"[bold red]✗ Validation failed:[/bold red] {e}")
        sys.exit(1)
    except GuardrailViolation as e:
        console.print(f"[bold red]✗ Guardrail violation:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Unexpected error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True))
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show planned actions without executing"
)
def execute_spec(spec_file: str, dry_run: bool):
    """
    Execute a specification file
    
    Example:
        twx-agent execute-spec artifacts/specs/spec_20250108_120000.json
        twx-agent execute-spec spec.json --dry-run
    """
    try:
        spec_path = Path(spec_file)
        
        console.print(f"[bold blue]{'Dry run' if dry_run else 'Executing'} specification...[/bold blue]")
        console.print(f"Spec file: {spec_path}\n")
        
        # Load spec
        with open(spec_path) as f:
            spec = json.load(f)
        
        # Validate schema
        console.print("[yellow]Validating schema...[/yellow]")
        validate_spec_file(spec_path)
        console.print("[green]✓ Schema valid[/green]\n")
        
        # Validate guardrails
        console.print("[yellow]Validating guardrails...[/yellow]")
        validate_guardrails(spec)
        console.print("[green]✓ Guardrails passed[/green]\n")
        
        # Show actions
        table = Table(title="Planned Actions")
        table.add_column("Step", style="cyan")
        table.add_column("Action Type", style="magenta")
        table.add_column("Parameters", style="white")
        
        for idx, action in enumerate(spec["actions"], 1):
            action_type = action["type"]
            params = action.get("params", {})
            params_str = ", ".join(f"{k}={v}" for k, v in list(params.items())[:3])
            if len(params) > 3:
                params_str += "..."
            table.add_row(str(idx), action_type, params_str)
        
        console.print(table)
        console.print()
        
        if dry_run:
            console.print("[yellow]Dry run mode - no actions will be executed[/yellow]")
        else:
            if not click.confirm("Execute these actions?"):
                console.print("[yellow]Execution cancelled[/yellow]")
                return
        
        # Execute
        executor = Executor()
        result = executor.execute_spec(spec, dry_run=dry_run)
        
        # Display result
        if result["status"] == "success":
            console.print(f"[bold green]✓ Execution completed successfully![/bold green]")
        elif result["status"] == "dry_run":
            console.print(f"[bold yellow]✓ Dry run completed![/bold yellow]")
        else:
            console.print(f"[bold red]✗ Execution failed:[/bold red] {result.get('error')}")
        
        console.print(f"\nLog file: {result['log_file']}")
        console.print(f"Actions executed: {result['actions_executed']}")
        
        # Show results table
        if result.get("results"):
            results_table = Table(title="Execution Results")
            results_table.add_column("Step", style="cyan")
            results_table.add_column("Status", style="magenta")
            results_table.add_column("Details", style="white")
            
            for idx, res in enumerate(result["results"], 1):
                status = res.get("status", "unknown")
                status_color = "green" if status == "success" else "yellow" if status == "dry_run" else "red"
                
                details = ""
                if "thing_name" in res:
                    details = f"Thing: {res['thing_name']}"
                if "service_name" in res:
                    details += f", Service: {res['service_name']}"
                
                results_table.add_row(
                    str(idx),
                    f"[{status_color}]{status}[/{status_color}]",
                    details
                )
            
            console.print(results_table)
        
    except ValidationError as e:
        console.print(f"[bold red]✗ Validation failed:[/bold red] {e}")
        sys.exit(1)
    except GuardrailViolation as e:
        console.print(f"[bold red]✗ Guardrail violation:[/bold red] {e}")
        sys.exit(1)
    except ExecutionError as e:
        console.print(f"[bold red]✗ Execution failed:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Unexpected error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True))
def validate(spec_file: str):
    """
    Validate a specification file
    
    Example:
        twx-agent validate artifacts/specs/spec_20250108_120000.json
    """
    try:
        spec_path = Path(spec_file)
        
        console.print(f"[bold blue]Validating specification...[/bold blue]")
        console.print(f"Spec file: {spec_path}\n")
        
        # Load spec
        with open(spec_path) as f:
            spec = json.load(f)
        
        # Validate schema
        console.print("[yellow]Checking schema...[/yellow]")
        validate_spec_file(spec_path)
        console.print("[green]✓ Schema valid[/green]\n")
        
        # Validate guardrails
        console.print("[yellow]Checking guardrails...[/yellow]")
        validate_guardrails(spec)
        console.print("[green]✓ Guardrails passed[/green]\n")
        
        console.print("[bold green]✓ Specification is valid![/bold green]")
        
    except ValidationError as e:
        console.print(f"[bold red]✗ Schema validation failed:[/bold red] {e}")
        sys.exit(1)
    except GuardrailViolation as e:
        console.print(f"[bold red]✗ Guardrail violation:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Validation failed:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
