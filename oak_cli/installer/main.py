import typer

app = typer.Typer()


@app.command(
    "fundamentals",
    help="""
    Installs non-python fundamental dependencies like git, docker, docker-compose, etc.
    on the current machine.
    """,
)
def install_fundamentals(verbose: bool = False) -> None:
    print("Todo")
