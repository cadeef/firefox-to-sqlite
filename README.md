Firefox *to* SQLite is a bit of a misnomer, Firefox stores history, bookmarks, etc. in
SQLite. `firefox-to-sqlite` aims to make it easy to find your Firefox data and provide addtional
context in the database suitable for easy queries.

## Quick Start

### Install

```sh
pipx install firefox-to-sqlite
```

### Select profile

```sh
firefox-to-sqlite profiles
```

### Export

```sh
firefox-to-sqlite fetch --profile <PROFILE> <TARGET_DB_FILE>
```
