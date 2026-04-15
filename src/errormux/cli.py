"""CLI entry point for ErrorMux."""

import typer

app = typer.Typer(
    name="errormux",
    help="On-demand shell command error explanations",
)


@app.command()
def explain() -> None:
    """Explain the last failed command.

    Stub implementation - real functionality coming in Phase 2.
    """
    typer.echo("[errormux] CLI not implemented yet - coming in Phase 2")


if __name__ == "__main__":
    app()
