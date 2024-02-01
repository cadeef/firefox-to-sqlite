Firefox *to* SQLite is a bit of a misnomer, Firefox stores history, bookmarks, etc. in
SQLite. `firefox-to-sqlite` aims to make it easy to find your Firefox data, provide
straight forward [views](https://firefox-to-sqlite.cade.pro/usage.html#Views) and [full-text
search](https://firefox-to-sqlite.cade.pro/usage.html#full-text-search) suitable for easy
queries without digging into the database schema.

## Quick Start

### Install

```sh
pipx install firefox-to-sqlite
```

Additional [install](https://firefox-to-sqlite.cade.pro/install.html) options available.

### Select profile

```sh
$ firefox-to-sqlite

Last used (default) profile: 3Wg824N2.archer-patel

Profiles:
  6Fz604Y8.faulkner-howard: active, in use
  3YI440T9.martin: created, never used
  3Wg824N2.archer-patel: active, in use, most recent, largest
  5xs633W9.collins: broken, something doesn't seem quite right
```

### Export

```sh
$ firefox-to-sqlite --profile <PROFILE>

✅ Database saved to firefox_places.sqlite
```
