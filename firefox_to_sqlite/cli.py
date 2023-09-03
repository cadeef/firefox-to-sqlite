import importlib.metadata
from pathlib import Path
from shutil import copy2
from typing import Annotated, Optional

import typer
from rich import print
from sqlite_utils import Database

from .lib import Firefox, firefox_data_store

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
        typer.Option(
            "--version",
            "-V",
            help="Print version",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    ctx.ensure_object(dict)


@app.command()
def fetch(
    db: Annotated[Path, typer.Argument(help="Destination path for exported database")],
    profile: Annotated[
        Optional[str],
        typer.Option("--profile", "-p", help="Profile to fetch"),
    ] = None,
    data_store: Annotated[
        Path,
        typer.Option("--data-store", "-d", help="Firefox data store directory"),
    ] = firefox_data_store(),
) -> None:
    """
    Fetch and transform the database
    """
    ff = Firefox(data_store)

    if profile:
        p = ff.profile_from_name(profile)

        try:
            copy2(p.places().db, db)
            Database(db).disable_wal()
        except FileNotFoundError:
            print(f":x: {profile}: Places database ({p.places().db}) not found.")
            raise typer.Exit(code=1)

        print(f":white_check_mark: Database saved to {db}")


@app.command("profiles")
def list_profiles(
    data_store: Annotated[
        Path,
        typer.Option("--data-store", "-d", help="Firefox data store directory"),
    ] = firefox_data_store(),
):
    """
    List Firefox profiles
    """
    ff = Firefox(data_store)

    installs = list(ff.installs())

    if len(installs) > 1:
        print("Multiple Firefox installations found:")
        for install in installs:
            print(
                f"\t{install.name}: Last used (default) {install.last_used_profile.name}"  # noqa: E501
            )
    else:
        print(
            f"Last used (default) profile: [bold]{installs[0].last_used_profile.name}[/bold]"  # noqa: E501
        )

    print("\nProfiles:")
    for profile in ff.profiles():
        status = f"[bold]{profile.name}:[/bold] {profile.status().value}"
        if ff.profile_most_recent().name == profile.name:
            status += ", [green]most recent[/green]"
        if ff.profile_largest().name == profile.name:
            status += ", [blue]largest[/blue]"
        print(f"  {status}")


if __name__ == "__main__":
    app()
