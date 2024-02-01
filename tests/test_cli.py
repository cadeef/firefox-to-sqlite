import importlib.metadata

import pytest
import typer

# from devtools import debug
from sqlite_utils import Database
from typer.testing import CliRunner

from firefox_to_sqlite.cli import APP_NAME, main

app = typer.Typer()
app.command()(main)
cli = CliRunner()


def test_no_command():
    """
    Ensure app runs without command, but fails to help
    """
    result = cli.invoke(app)
    assert result.exit_code == 0


def test_version():
    """
    Ensure app returns version specified in pyproject.toml
    """
    result = cli.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert importlib.metadata.version(APP_NAME) in result.stdout


@pytest.mark.parametrize(
    "profile,success",
    (
        ("6Fz604Y8.faulkner-howard", True),
        ("2zF468G4.stephens-medina", False),
    ),
)
def test_get_profile(data_store_simple, profile, success):
    """
    Ensure database copy & transformations are successful
    """
    data_store_path, _ = data_store_simple
    db = data_store_path / "test.db"
    result = cli.invoke(
        app,
        ["--data-store", data_store_path, "--profile", profile, "--output", str(db)],
    )

    ff_db = Database(db)
    if success:
        assert db.is_file()
        # WAL disabled
        assert ff_db.journal_mode == "delete"
        # Views exist
        assert "downloads" in ff_db.view_names()
        assert "history" in ff_db.view_names()
        assert "bookmarks" in ff_db.view_names()
        # FTS enabled
        assert ff_db["moz_places"].detect_fts() is not None
        assert result.exit_code == 0
        assert "Database saved" in result.stdout
    else:
        assert result.exit_code == 1


def test_profiles(data_store_complex):
    data_store_path, state = data_store_complex
    result = cli.invoke(app, ["--data-store", data_store_path])

    # TODO: Flesh out legit tests
    assert result.exit_code == 0
    assert all(p in result.stdout for p in state["profiles"])
