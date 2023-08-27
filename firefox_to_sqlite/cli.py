import importlib.metadata
from typing import Annotated, Optional

import typer
from rich import print

APP_NAME = "firefox_to_sqlite"
app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(importlib.metadata.version(APP_NAME))
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    ctx.ensure_object(dict)


if __name__ == "__main__":
    app()
