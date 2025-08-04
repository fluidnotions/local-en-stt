"""Console script for local_en_stt."""

import typer
from rich.console import Console

from local_en_stt import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for local_en_stt."""
    console.print("Replace this message by putting your code into "
               "local_en_stt.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
