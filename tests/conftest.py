import configparser
import datetime
import json
from pathlib import Path

import pytest

# from devtools import debug
from sqlite_utils import Database

# @pytest.fixture
# def data_store_random(tmp_path, faker):
#     state = {}

#     # 5 profiles
#     state["profiles"] = {}
#     profiles = [
#         f"{faker.bothify(text='#??###?#')}.{faker.domain_word()}" for _ in range(5)
#     ]
#     for profile in profiles:
#         state["profiles"][profile] = {}

#     # 2 installs
#     state["installs"] = {}
#     installs = [faker.bothify(text="??#####?#???#?##?") for _ in range(2)]
#     for install in installs:
#         state["installs"][install] = {}
#         state["installs"][install]["profile"] = faker.random_element(elements=profiles)  # noqa: E501

#     generate_environment(tmp_path, state)

#     return tmp_path, state


@pytest.fixture
def data_store_complex(tmp_path):
    state = {
        "profiles": {
            "6Fz604Y8.faulkner-howard": {
                "times_created": datetime.datetime(2023, 4, 14, 5, 47, 48),
                "times_first_use": datetime.datetime(2023, 8, 19, 0, 53, 2),
                "places_exists": True,
            },
            "3YI440T9.martin": {
                "times_created": datetime.datetime(2023, 4, 22, 1, 44, 9),
                "times_first_use": None,
            },
            "3Wg824N2.archer-patel": {
                "times_created": datetime.datetime(2023, 7, 3, 6, 33, 2),
                "times_first_use": datetime.datetime(2023, 8, 25, 23, 24, 50),
                "places_exists": True,
            },
            "5xs633W9.collins": {},
            "4Xk582E3.ramos-perry": {"places_exists": True},
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
                "places_exists": True,
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

    # Profiles
    profiles_ini = configparser.ConfigParser()
    profile_cnt = 0
    for p in profiles:
        profile_path = profiles_path / p
        profile = profiles[p]

        # Create profile dir
        profile_path.mkdir(parents=True)

        # Config section for profiles.ini
        profiles_ini[f"Profile{profile_cnt}"] = {
            "Name": p.split(".")[1],
            "IsRelative": "1",
            "Path": f"Profiles/{p}",
        }
        profile_cnt += 1

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
        if "places_exists" in profile:
            # TODO: Create database with places.sqlite schema
            db = Database(profile_path / "places.sqlite")
            db.enable_wal()

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
