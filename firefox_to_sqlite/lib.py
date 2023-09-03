import configparser
import json
import os
import sys
from datetime import datetime
from enum import Enum

# from devtools import debug
from pathlib import Path
from typing import NamedTuple, Sequence


class FirefoxProfileStatus(Enum):
    """Profile status"""

    INIT = "created, never used"
    ACTIVE = "active, in use"
    BROKEN = "broken, something doesn't seem quite right"


class Places(NamedTuple):
    last_modified: datetime | None
    size: int | None
    db: Path


class FirefoxProfile:
    """
    FirefoxProfile
    """

    def __init__(self, path: Path, is_default: bool = False) -> None:
        self.path = path
        self.name = self.path.name
        self.is_default = is_default

    def __str__(self):
        return f"{self.name}: {self.status().value}"

    def places(self) -> Places:
        db = self.path / "places.sqlite"
        # Places = NamedTuple(
        #     "Places",
        #     [("last_modified", datetime | None), ("size", int | None), ("db", Path)],
        # )
        try:
            modified_ts = db.stat().st_mtime
            return Places(datetime.fromtimestamp(modified_ts), db.stat().st_size, db)
        except FileNotFoundError:
            return Places(None, None, db)

    def status(self) -> FirefoxProfileStatus:
        try:
            t = self.path / "times.json"
            times = json.loads(t.read_text())
        except FileNotFoundError:
            return FirefoxProfileStatus.BROKEN

        if not times["firstUse"]:
            return FirefoxProfileStatus.INIT

        if self.places().db.is_file():  # type: ignore[attr-defined]
            return FirefoxProfileStatus.ACTIVE
        # Assume broken if we get here
        return FirefoxProfileStatus.BROKEN


class FirefoxProfileException(Exception):
    """Source Exception"""


class Install(NamedTuple):
    name: str
    last_used_profile: FirefoxProfile


class Firefox:
    """docstring for Firefox"""

    def __init__(self, data_store: Path) -> None:
        self.data_store = data_store
        self.profile_path = data_store / "Profiles"

    def installs(self) -> Sequence[Install]:
        # Return cache if available
        if hasattr(self, "_installs"):
            return self._installs  # type:ignore[has-type]

        install_config = self.data_store / "installs.ini"
        # Install = NamedTuple(
        #     "Install", [("name", str), ("last_used_profile", FirefoxProfile)]
        # )

        if not install_config.is_file():
            raise FileNotFoundError(f"Install config ({install_config}) not found")

        config = configparser.ConfigParser()
        config.read(install_config)

        self._installs: list[Install] = []
        for i in config.sections():
            last_used_profile = FirefoxProfile(self.data_store / config[i]["Default"])
            self._installs.append(Install(i, last_used_profile))

        return self._installs

    def profiles(self) -> list[FirefoxProfile]:
        # Return cache if available
        if hasattr(self, "_profiles"):
            return self._profiles  # type:ignore[has-type]

        profile_config = self.data_store / "profiles.ini"
        config = configparser.ConfigParser()
        config.read(profile_config)

        if not profile_config.is_file():
            # TODO: Workout profile discovery, if config is unavailable, from walking
            # Profiles
            raise FileNotFoundError(f"Profile config ({profile_config}) not found")

        self._profiles = []
        for section in config.sections():
            if section.startswith("Profile"):
                path = Path(config[section]["Path"])
                is_relative = config.getboolean(section, "IsRelative")
                # TODO: Not sure about the meaing of Default in profiles.ini.
                # Load it when it's there. Maybe traipse through the Firefox source one
                # day.
                is_default = config.getboolean(section, "Default", fallback=False)

                if is_relative:
                    path = self.data_store / path

                self._profiles.append(FirefoxProfile(path=path, is_default=is_default))

        return self._profiles

    def profile_from_name(self, name):
        return FirefoxProfile(self.profile_path / name)

    def profile_largest(self) -> FirefoxProfile:
        # FIXME: Two databases could be the same size
        profiles_size = {p.places().size: p for p in self.profiles() if p.places().size}
        return profiles_size[max(profiles_size)]  # type:ignore[type-var]

    def profile_most_recent(self) -> FirefoxProfile:
        # FIXME: Two databases could have the same modification time
        profiles = {
            p.places().last_modified: p
            for p in self.profiles()
            if p.places().last_modified
        }
        return profiles[max(profiles)]  # type:ignore[type-var]


def firefox_data_store() -> Path:
    if sys.platform.startswith("darwin"):
        return Path.home() / "Library/Application Support/Firefox"
    elif sys.platform.startswith("linux"):
        return Path.home() / ".mozilla/firefox"
    elif sys.platform.startswith("win"):
        return Path(os.getenv("APPDATA")) / r"Mozilla\Firefox"
    else:
        raise FirefoxToSqliteException(
            f"Firefox data directory unknown for {sys.platform}!"
        )


class FirefoxToSqliteException(Exception):
    """Source Exception"""
