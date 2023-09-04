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
            firefox_db = Database(db)
            # Disable WAL
            firefox_db.disable_wal()
            # Enable full-text search for moz_places
            # FIXME: OperationalError('no such table: moz_places')
            # firefox_db.table("moz_places").enable_fts(["url", "title", "description"])
            # Add views
            for view in VIEWS:
                firefox_db.create_view(view, VIEWS[view])
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


VIEWS = {
    "history": """
select
  h.id,
  h.visit_date as visit_epoch_us,
  h.visit_type,
  h.session,
  h.source,
  h.place_id,
  p.origin_id,
  p.url,
  p.title
from
  moz_historyvisits h
  left join moz_places p on p.id = h.place_id
order by
  visit_date desc
""",
    "bookmarks": """
select * from moz_bookmarks
""",
    "downloads": """
select
  a.id,
  a.place_id,
  a.dateAdded as date_added_epoch_us,
  a.lastModified as date_modified_epoch_us,
  a.content as file,
  p.url as source_url
from
  moz_annos a
  left join moz_places p  on p.id = a.place_id
where a.anno_attribute_id = (select id from moz_anno_attributes where name == 'downloads/destinationFileURI')
""",  # noqa: E501
}


if __name__ == "__main__":
    app()
