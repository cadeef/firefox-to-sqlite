import importlib.metadata
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print

from .lib import (
    Firefox,
    FirefoxToSqliteException,
    copy_and_transform_db,
    firefox_data_store,
)

APP_NAME = "firefox_to_sqlite"


def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            help="Print version",
        ),
    ] = None,
    profile: Annotated[
        Optional[str],
        typer.Option("--profile", "-p", help="Profile to copy"),
    ] = None,
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Output path for database")
    ] = None,
    data_store: Annotated[
        Optional[Path],
        typer.Option("--data-store", "-d", help="Firefox data store directory"),
    ] = None,
) -> None:
    firefox = get_firefox(data_store)

    if version:
        print(importlib.metadata.version(APP_NAME))
        raise typer.Exit()

    if profile:
        p = firefox.profile_from_name(profile)
        src = p.places().db
        dst = output or Path("./firefox_places.sqlite")

        try:
            copy_and_transform_db(src, dst)
        except FirefoxToSqliteException as e:
            print(f":x: {profile}: {e}")
            raise typer.Exit(code=1)

        print(f":white_check_mark: Database saved to {dst}.")
    else:
        installs = list(firefox.installs())

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
        for p in firefox.profiles():
            status = f"[bold]{p.name}:[/bold] {p.status().value}"
            if firefox.profile_most_recent().name == p.name:
                status += ", [green]most recent[/green]"
            if firefox.profile_largest().name == p.name:
                status += ", [blue]largest[/blue]"
            print(f"  {status}")


def get_firefox(data_store: Optional[Path]) -> Firefox:
    if not data_store:
        data_store = firefox_data_store()
    return Firefox(data_store)


def app():
    typer.run(main)


if __name__ == "__main__":
    # typer.run(main)
    app()
