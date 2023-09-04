Firefox *to* SQLite is a bit of a misnomer, Firefox stores history, bookmarks, etc. in
SQLite. `firefox-to-sqlite` aims to make it easy to find your Firefox data and provide
straight forward [views](https://firefox-to-sqlite.cade.pro/usage.html#Views) in the
database suitable for easy queries without digging into the database schema.

## Quick Start

### Install

```sh
pipx install firefox-to-sqlite
```

Additional [install](https://firefox-to-sqlite.cade.pro/install.html) options available.

### Select profile

```sh
firefox-to-sqlite profiles
```

### Export

```sh
firefox-to-sqlite fetch --profile <PROFILE> <TARGET_DB_FILE>
```
