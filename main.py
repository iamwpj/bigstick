#!/usr/bin/env python3
import click
from pathlib import Path
from importlib import import_module

evals = {"foo": "A generic evaluation", "bar": "A more specific one."}


@click.group()
def cli():
    """Run Something"""


@cli.command("run")
@click.option(
    "--evaluation",
    help="Select an evaluation to run. Use 'list' to see options.",
)
def run_eval(evaluation):
    """Run the provided evaluation with --evaluation."""

    import_module(name=f"{evaluation}")


@cli.command("list")
def list_evals():
    """List all available evals."""
    click.echo("Available evals:")
    [click.echo(f"   - {x}: {evals[x]}") for x in list(evals.keys())]


if __name__ == "__main__":
    cli()
