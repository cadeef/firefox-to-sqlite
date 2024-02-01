# Usage

## Full-text Search

Full-text search (across url, title, description) is enabled for the `moz_places` table.

## Views

:::{note}
Firefox stores timestamps (epoch) with a micro-second resolution. Timestamp
columns are annotated with `epoch_us`. You can output more human readable timestamps
with `datetime(<COLUMN> /1000000, 'unixepoch')`.

For instance:

```sql
select
  id,
  datetime(visit_epoch_us /1000000, 'unixepoch') as visit_ts,
from
  history
```

:::

### bookmarks

- id
- date_added_epoch_us
- last_modified_epoch_us
- bookmark_title
- place_id
- origin_id
- url
- title

```sql
select
  b.id,
  b.dateAdded as date_added_epoch_us,
  b.lastModified as last_modified_epoch_us,
  b.title as bookmark_title,
  b.fk as place_id,
  p.origin_id,
  p.url,
  p.title
from
  moz_bookmarks b
  left join moz_places p on p.id = b.fk
order by
  b.dateAdded desc
```

### downloads

#### Columns

- id
- place_id
- date_added_epoch_us
- date_modified_epoch_us
- file
- source_url

```sql
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
```

### history

#### Columns

- id
- visit_epoch_us
- visit_type
- session
- source
- place_id
- origin_id
- url
- title

```sql
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
```
