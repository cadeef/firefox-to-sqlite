import configparser
import datetime
import json
import os
from pathlib import Path

import pytest
from sqlite_utils import Database


@pytest.fixture
def data_store_complex(tmp_path):
    state = {
        "profiles": {
            "6Fz604Y8.faulkner-howard": {
                "times_created": datetime.datetime(2023, 4, 14, 5, 47, 48),
                "times_first_use": datetime.datetime(2023, 8, 19, 0, 53, 2),
                "places_last_mod": datetime.datetime(2023, 9, 6, 17, 17, 33),
            },
            "3YI440T9.martin": {
                "times_created": datetime.datetime(2023, 4, 22, 1, 44, 9),
                "times_first_use": None,
            },
            "3Wg824N2.archer-patel": {
                "times_created": datetime.datetime(2023, 7, 3, 6, 33, 2),
                "times_first_use": datetime.datetime(2023, 8, 25, 23, 24, 50),
                "places_last_mod": datetime.datetime(2023, 9, 14, 19, 38, 56),
            },
            "5xs633W9.collins": {},
            "4Xk582E3.ramos-perry": {
                "places_last_mod": datetime.datetime(2023, 6, 11, 16, 49, 23)
            },
        },
        "installs": {
            "904671b79a2c4d13cbcb1bf5473fd3ef": {"profile": "6Fz604Y8.faulkner-howard"},
            "6b7234b3eb4ac5a4c73e9910834bd311": {"profile": "3Wg824N2.archer-patel"},
        },
    }
    generate_environment(tmp_path, state)

    return tmp_path, state


@pytest.fixture
def data_store_simple(tmp_path):
    state = {
        "profiles": {
            "6Fz604Y8.faulkner-howard": {
                "times_created": datetime.datetime(2023, 4, 14, 5, 47, 48),
                "times_first_use": datetime.datetime(2023, 8, 19, 0, 53, 2),
                "places_last_mod": datetime.datetime(2023, 9, 11, 16, 22, 33),
            }
        },
        "installs": {
            "904671b79a2c4d13cbcb1bf5473fd3ef": {"profile": "6Fz604Y8.faulkner-howard"}
        },
    }
    generate_environment(tmp_path, state)

    return tmp_path, state


def generate_environment(path: Path, state: dict) -> None:
    installs = state["installs"]
    profiles = state["profiles"]
    profiles_path = path / "Profiles"
    with Path("tests/config/places_schema.sql").open() as f:
        places_schema = f.readlines()

    # Profiles
    profiles_ini = configparser.ConfigParser()
    for index, p in enumerate(profiles):
        profile_path = profiles_path / p
        profile = profiles[p]

        # Create profile dir
        profile_path.mkdir(parents=True)

        # Config section for profiles.ini
        profiles_ini[f"Profile{index}"] = {
            "Name": p.split(".")[1],
            "IsRelative": "1",
            "Path": f"Profiles/{p}",
        }

        # times.json
        if "times_created" in profile and "times_first_use" in profile:
            created = int(profile["times_created"].timestamp()) * 1000
            if profile["times_first_use"]:
                first_use = int(profile["times_first_use"].timestamp()) * 1000
            else:
                first_use = None
            times_json = profile_path / "times.json"
            times_json.write_text(
                json.dumps(
                    {
                        "created": created,
                        "firstUse": first_use,
                    }
                )
            )

        # places.sqlite
        if "places_last_mod" in profile:
            # Create database
            db_file = profile_path / "places.sqlite"
            db = Database(db_file)
            for query in places_schema:
                db.execute(query.rstrip())
            db.enable_wal()
            # Update database timestamp
            ts = profile["places_last_mod"].timestamp()
            os.utime(db_file, times=(ts, ts))

    # Dump out profiles_ini
    profiles_ini_path = path / "profiles.ini"
    with profiles_ini_path.open(mode="w") as f:
        profiles_ini.write(f)

    # Installs
    installs_ini = configparser.ConfigParser()
    for install in installs:
        installs_ini[install] = {
            "Default": Path("Profiles") / installs[install]["profile"],
            "Locked": "1",
        }

    installs_ini_path = path / "installs.ini"
    with installs_ini_path.open(mode="w") as f:
        installs_ini.write(f)
