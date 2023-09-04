# Usage

## Views

:::{note}
Firefox stores timestamps (epoch) with a micro-second resolution. Timestamp
fields are annotated with `epoch_us`.
:::

### bookmarks

```sql

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
