import pytest

# from devtools import debug
from firefox_to_sqlite.lib import Firefox


def test_firefoxprofile():
    pass


def test_firefox__profiles(data_store_complex):
    data_store_path, state = data_store_complex
    ff = Firefox(data_store_path)
    profiles = ff.profiles()

    assert len(profiles) == len(state["profiles"])


def test_firefox__installs(data_store_complex):
    data_store_path, state = data_store_complex
    ff = Firefox(data_store_path)
    installs = ff.installs()

    assert len(installs) == len(state["installs"])


def test_firefox__missing_inis(data_store_simple):
    data_store_path, _ = data_store_simple
    ff = Firefox(data_store_path)
    # Remve installs.ini
    installs_ini = data_store_path / "installs.ini"
    installs_ini.unlink()
    profiles_ini = data_store_path / "profiles.ini"
    profiles_ini.unlink()
    with pytest.raises(FileNotFoundError):
        ff.installs()
        ff.profiles()


def test_firefox__profile_from_name(data_store_complex, faker):
    data_store_path, _ = data_store_complex
    ff = Firefox(data_store_path)
    name = f"{faker.bothify(text='#??###?#')}.{faker.domain_word()}"
    profile = ff.profile_from_name(name)

    assert profile.name == name
    assert profile.path == data_store_path / "Profiles" / name


def test_firefox_data_store():
    pass


# @pytest.mark.parametrize(
#     "platform,home,expected",
#     (
#         ("darwin", "/Users/jim", "/Users/jim/Library/Application Support/Firefox"),
#         ("linux", "/home/jim", "/home/jim/.mozilla/firefox"),
#     ),
# )
# def test_firefox_data_path(mocker, platform, home, expected):
#     mocker.patch.object(sys, return_value=platform)
#     mocker.patch("pathlib.Path.home", return_value=Path(home))
#     # os.environ["HOME"] = home
#     assert firefox_data_path() == Path(expected)

# def test_firefox_data_path__windows(mocker):
#     mocker.patch("sys.platform", return_value="windows")
#     os.environ["APPDATA"] = r"C:\Users\jim"
#     assert firefox_data_path() == Path(r"C:\Users\jim\Mozilla\Firefox")
