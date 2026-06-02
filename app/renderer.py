"""
renderer.py
Beautiful terminal UI using the Rich library.
Handles all display: tables, schema view, errors, welcome screen.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.prompt import Prompt, IntPrompt
from rich.layout import Layout

console = Console()


def show_welcome(db_name: str):
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]🧠 NL2SQL Terminal[/bold cyan]\n"
        f"[dim]Connected to:[/dim] [green]{db_name}[/green]\n"
        "[dim]Type your question in plain English.[/dim]\n"
        "[dim]Commands: [/dim][yellow]:schema[/yellow][dim] | [/dim]"
        "[yellow]:history[/yellow][dim] | [/dim][yellow]:export[/yellow]"
        "[dim] | [/dim][yellow]:quit[/yellow]",
        title="[bold]Welcome[/bold]",
        border_style="cyan",
    ))


def show_schema(schema: dict):
    console.print("\n[bold cyan]📋 Database Schema[/bold cyan]\n")
    for table_name, columns in schema.items():
        table = Table(
            title=f"[bold]{table_name}[/bold]",
            box=box.ROUNDED,
            border_style="dim cyan",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Column", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        for col_name, col_type in columns:
            table.add_row(col_name, col_type)
        console.print(table)
        console.print()


def show_generated_sql(sql: str, warnings: list[str]):
    """Display the generated SQL with syntax highlighting."""
    console.print()
    if warnings:
        for w in warnings:
            console.print(f"  [yellow]{w}[/yellow]")
    syntax = Syntax(sql, "sql", theme="monokai", line_numbers=False, padding=(1, 2))
    console.print(Panel(syntax, title="[bold]Generated SQL[/bold]", border_style="yellow"))


def show_results(result: dict):
    """Display query results as a rich table."""
    if not result["success"]:
        console.print(f"\n  [bold red]❌ SQL Error:[/bold red] {result['error']}\n")
        return

    rows = result["rows"]
    columns = result["columns"]

    if not rows:
        console.print("\n  [dim]No rows returned.[/dim]\n")
        return

    table = Table(
        box=box.SIMPLE_HEAD,
        border_style="dim",
        show_header=True,
        header_style="bold white",
        row_styles=["", "dim"],
    )
    for col in columns:
        table.add_column(col, style="cyan", overflow="fold")

    for row in rows[:50]:  # Limit display to 50 rows
        table.add_row(*[str(row.get(col, "")) for col in columns])

    console.print(table)

    count = result["row_count"]
    shown = min(count, 50)
    console.print(
        f"  [dim]Showing {shown} of {count} row(s)[/dim]\n"
    )


def show_clarification(clarification: dict) -> str:
    """Show clarification options and get user choice."""
    console.print(f"\n  [yellow]❓ {clarification['question']}[/yellow]")
    for i, option in enumerate(clarification["options"], 1):
        console.print(f"     [{i}] {option}")
    choice = IntPrompt.ask(
        "  Enter number",
        choices=[str(i) for i in range(1, len(clarification["options"]) + 1)],
    )
    return clarification["options"][int(choice) - 1]


def show_history(history: list[dict]):
    """Show past queries in this session."""
    if not history:
        console.print("\n  [dim]No history yet.[/dim]\n")
        return
    console.print("\n[bold cyan]📜 Query History[/bold cyan]\n")
    for i, entry in enumerate(history, 1):
        console.print(f"  [dim]{i}.[/dim] [white]{entry['question']}[/white]")
        console.print(f"     [dim]{entry['sql']}[/dim]\n")


def show_error(msg: str):
    console.print(f"\n  [bold red]Error:[/bold red] {msg}\n")


def get_input(prompt_text: str = "") -> str:
    return console.input(f"\n[bold green]>[/bold green] ")