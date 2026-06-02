"""
main.py
Entry point. Runs the NL2SQL terminal application.

Usage:
    python app/main.py --db databases/sample.db --model model/nl2sql_model
"""

import argparse
import csv
import os
import sys

from schema_loader import SchemaLoader
from nl2sql_engine import NL2SQLEngine
from db_executor import DBExecutor
from clarifier import Clarifier
from renderer import (
    console,
    show_welcome,
    show_schema,
    show_generated_sql,
    show_results,
    show_clarification,
    show_history,
    show_error,
    get_input,
)


def export_results(result: dict, filename: str = "export.csv"):
    """Export last query result to CSV."""
    if not result or not result.get("rows"):
        console.print("  [yellow]Nothing to export.[/yellow]")
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result["columns"])
        writer.writeheader()
        writer.writerows(result["rows"])
    console.print(f"  [green]✅ Exported to {filename}[/green]")


def main():
    parser = argparse.ArgumentParser(description="NL2SQL Terminal")
    parser.add_argument("--db",    default="databases/sample.db",   help="Path to SQLite database")
    parser.add_argument("--model", default="model/nl2sql_model",    help="Path to fine-tuned T5 model")
    args = parser.parse_args()

    # --- Validate paths ---
    if not os.path.exists(args.db):
        print(f"❌ Database not found: {args.db}")
        sys.exit(1)
    if not os.path.exists(args.model):
        print(f"❌ Model not found: {args.model}")
        print("   Run Colab training first and place model in model/nl2sql_model/")
        sys.exit(1)

    # --- Initialize components ---
    schema_loader = SchemaLoader(args.db)
    db_executor   = DBExecutor(args.db)
    clarifier     = Clarifier()
    engine        = NL2SQLEngine(args.model)
    engine.load()

    schema_string = schema_loader.get_schema_string()
    db_name       = schema_loader.get_db_name()

    history       = []
    last_result   = None

    # --- Welcome screen ---
    show_welcome(db_name)

    # --- Main REPL loop ---
    while True:
        try:
            user_input = get_input().strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not user_input:
            continue

        # --- Special commands ---
        if user_input.lower() in (":quit", ":exit", "exit", "quit"):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        elif user_input.lower() == ":schema":
            show_schema(schema_loader.get_schema_display())
            continue

        elif user_input.lower() == ":history":
            show_history(history)
            continue

        elif user_input.lower().startswith(":export"):
            filename = user_input.split(" ")[1] if len(user_input.split(" ")) > 1 else "export.csv"
            export_results(last_result, filename)
            continue

        elif user_input.lower().startswith(":sql "):
            # Direct SQL mode — bypass model
            raw_sql = user_input[5:].strip()
            console.print(f"\n  [dim]Running raw SQL...[/dim]")
            result = db_executor.execute(raw_sql)
            show_results(result)
            last_result = result
            continue

        # --- NL to SQL flow ---
        question = user_input

        # Check if clarification needed
        clarification = clarifier.needs_clarification(question)
        if clarification:
            choice = show_clarification(clarification)
            question = clarifier.refine_question(question, choice)
            console.print(f"  [dim]Refined question: {question}[/dim]")

        # Convert NL → SQL
        try:
            conversion = engine.convert(question, schema_string, db_name)
        except Exception as e:
            show_error(f"Model error: {e}")
            continue

        sql      = conversion["sql"]
        warnings = conversion["warnings"]

        show_generated_sql(sql, warnings)

        # Validate before executing
        is_valid, val_error = db_executor.validate_sql(sql)
        if not is_valid:
            console.print(f"  [red]⚠️  SQL validation failed:[/red] {val_error}")
            console.print(f"  [dim]You can run raw SQL with: :sql <your query>[/dim]")
            continue

        # Execute
        result   = db_executor.execute(sql)
        last_result = result
        show_results(result)

        # Save to history
        history.append({"question": question, "sql": sql})


if __name__ == "__main__":
    main()