<!-- omit in toc -->
# Query API Reference

<!-- omit in toc -->
## Contents
- [Main interface](#main-interface)
  - [_class_ opendatasoft.Opendatasoft](#class-opendatasoftopendatasoft)
  - [Making queries](#making-queries)
- [Query API](#query-api)
  - [Methods that return new Queries](#methods-that-return-new-queries)
    - [filter](#filter)
    - [exclude](#exclude)
    - [select](#select)
    - [order_by](#order_by)
    - [refine](#refine)
    - [ignore](#ignore)
  - [Methods that evaluate Queries and return something _other_ than a Query](#methods-that-evaluate-queries-and-return-something-other-than-a-query)
    - [get](#get)
    - [count](#count)
    - [exists](#exists)
    - [iterator](#iterator)
    - [all](#all)
    - [dataframe](#dataframe)
    - [first](#first)
    - [last](#last)
    - [aggregate](#aggregate)
  - [Helpers](#helpers)
    - [url](#url)
    - [decoded_url](#decoded_url)
  - [Field lookups](#field-lookups)
    - [contains](#contains)
    - [exact](#exact)
    - [gt](#gt)
    - [gte](#gte)
    - [lt](#lt)
    - [lte](#lte)
    - [in](#in)
    - [inarea](#inarea)
    - [isnull](#isnull)
  - [Aggregation functions](#aggregation-functions)
    - [avg](#avg)
    - [count](#count-1)
    - [envelope](#envelope)
    - [max](#max)
    - [medium](#medium)
    - [min](#min)
    - [percentile](#percentile)
    - [sum](#sum)
- [Query-related tools](#query-related-tools)
  - [Q() objects](#q-objects)
  - [F() objects](#f-objects)
- [Objects](#objects)
  - [Dataset](#dataset)
  - [Record](#record)

## Main interface
All of ods_explore's functionality can be accessed with an instance of `opendatasoft.Opendatasoft`.

### _class_ opendatasoft.Opendatasoft
`ods_explore.opendatasoft.Opendatasoft(subdomain='data', base_url=None, session=None, api_key=None, lang='en', timezone='UTC')`
* `subdomain` - A subdomain used to create the base API URL, useful if the data portal being accessed is hosted on [opendatasoft.com](https://opendatasoft.com/), eg. https://{subdomain}.opendatasoft.com.
* `base_url` - A custom base API URL.
* `session` - A `request.Session` object with which to make API calls.
* `api_key` - An Opendatasoft API key (to be attached to the session object), for accessing private datasets. [Read more on generating API keys.](https://help.opendatasoft.com/apis/ods-explore-v2/#section/Authentication/Finding-and-generating-API-keys)
* `lang` - The language used to format strings. One of: `en`, `fr`, `nl`, `pt`, `it`, `ar`, `de`, `es`, `ca`, `eu`, `sv`
* `timezone` - The timezone applied to datetime fields, [as defined by the Unicode CLDR project](https://github.com/unicode-org/cldr/blob/main/common/bcp47/timezone.xml).

`base_url`

The resolved base API URL.

`catalog`

An instance of `query.CatalogQuery`, the top-level querying interface, as described in [Making queries](#making-queries) below.

`session`

The session object.

### Making queries
All queries are created using the `catalog` attribute of an instance of `opendatasoft.Opendatadoft`. Four key endpoints in the [Catalog API](https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Catalog) and [Dataset API](https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Dataset) are supported:
 - [Query catalog datasets](https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Catalog/operation/getDatasets)
 - [Read one dataset](https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Dataset/operation/getDataset)
 - [Query dataset records](https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Dataset/operation/getRecords)
 - [Read one record](https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Dataset/operation/getRecord)

```py
# query datasets in a catalog
ods.catalog.datasets

# read one dataset
ods.catalog.dataset(dataset_id='doc-geonames-cities-5000')

# query records in a dataset, given its `dataset_id`
ods.catalog.dataset(dataset_id='doc-geonames-cities-5000').records

# read one record, given its `dataset_id` and `record_id`
(
  ods
  .catalog
  .dataset(dataset_id='doc-geonames-cities-5000')
  .record(record_id='24eec8bff4f5b55afdeeeacb326167ed6b1e933a')
)
```

The `datasets`/`records` attributes, and `dataset()`/`record()` methods, all return new instances of `query.DatasetQuery` or `query.RecordQuery`. With these, you can refine your search using any number of [chainable methods](#methods-that-return-new-queries), or retrieve results by calling a [query evaluation method](#methods-that-evaluate-queries-and-return-something-other-than-a-query). 

## Query API
### Methods that return new Queries
Since the methods below return new Queries, they're chainable:
```py
import ods_explore.language as lang

(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .filter(country_code='CA', timezone='America/Vancouver')
  .exclude(population__gt=lang.avg('population'))
  .order_by('name')
)
```
This query adds a filter, exclusion, and ordering to the cities in the `doc-geonames-cities-5000` dataset. The final result contains all Canadian cities in the `America/Vancouver` timezone, except for those whose population is greater than the average population, in alphabetical order by name.

#### filter
`filter(*args, **kwargs)`

Returns a new Query containing objects that match the given lookup parameters. The lookup parameters (`**kwargs`) should be in the format described in [Field lookups](#field-lookups) below. Multiple parameters are joined via AND in the underlying ODSQL expression.

If you need to execute more complex queries (such as parameters joined with OR), you can use [`Q()` objects](#q-objects) or raw OSQQL (`*args`).

#### exclude
`exclude(*args, **kwargs)`

Like [`filter()`](#filter), but returns a new Query containing objects that do _not_ match the given lookup parameters.

#### select
`select(*args, **kwargs)`

Returns a new Query containing objects whose fields are limited to the given expressions. Expressions (`*args`) can be field names, [aggregation functions](#aggregation-functions), scalar functions, or [`F()` objects](#f-objects), and can be combined with arithmetic operators.

To specify custom labels, use named expressions (`**kwargs)`.

```py
import ods_explore.language as lang
from ods_explore.query import F

# the name and population
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .select('name', 'population')
)

# double the population, labelled 'double_population'
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .select(double_population=F('population') * 2)
)
```

#### order_by
`order_by(*args)`

Returns a new Query with a given ordering. To indicate descending order, prepend field names with `-`. To order randomly, use `?`.

```py
# cities in alphabetical order by name
ods.catalog.dataset('doc-geonames-cities-5000').records.order_by('name')

# cities in descending order by population
ods.catalog.dataset('doc-geonames-cities-5000').records.order_by('-population')

# cities in a random order
ods.catalog.dataset('doc-geonames-cities-5000').records.order_by('?')
```

#### refine
`refine(**kwargs)`

Returns a new Query containing objects that match the given facet values (`**kwargs`).

A catalog's available facets and a list of possible values for each facet can be enumerated by directly calling [List facet values](https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Catalog/operation/getDatasetsFacets) in the Explore V2 API. ods_explore does not currently provide an interface for this endpoint.

#### ignore
`ignore(**kwargs)`

Like [`refine()`](#refine), but returns a new Query containing objects that do _not_ match the given facet values (`**kwargs`).

Here, `**kwargs` is compatible with the [`in` field lookup](#in), so you may ignore multiple facet values at once.

&nbsp;
### Methods that evaluate Queries and return something _other_ than a Query

#### get
`get(as_json=False, **kwargs)`

Returns results matched by the query as [objects](#objects), or as dictionaries if `as_json` is `True`. For Queries that read one dataset or one record, a single object is returned, otherwise a list of objects.

Custom querystring parameters (such as `limit` or `offset`) can be added to the underlying API call with `**kwargs`.

#### count
`count()`

Returns the number of results matched by the query. 

#### exists
`exists()`

Returns `True` if the query contains any results, and `False` if not.

#### iterator
`iterator(batch_size=100, as_json=False)`

Returns an iterator over results matched by the query as [objects](#objects), or as dictionaries if `as_json` is `True`.

The number of results to retrieve per API call is adjustable with `batch_size`.

#### all
`all(batch_size=100)`

Returns all results matched by the query as a list of [objects](#objects).

The number of results to retrieve per API call is adjustable with `batch_size`.

#### dataframe
`dataframe(batch_size=100, **kwargs)`

Returns results as a Pandas DataFrame, passing `**kwargs` to the underlying `pandas.json_normalize()` call.

The number of results to retrieve per API call is adjustable with `batch_size`.

#### first
`first()`

Returns the first object matched by the query.

#### last
`last()`

Returns the last object matched by the query.

#### aggregate
`aggregate(*args, **kwargs)`

Returns a dictionary of aggregate values. Expressions (`*args`) are [aggregation functions](#aggregation-functions) that specify a value to be included in the output. To specify custom labels, use named expressions (`**kwargs`).

&nbsp;
### Helpers
The following are attributes and methods of Query instances.

#### url
`url(**kwargs)`

Returns the URL of the underlying API call that the query would make, useful for debugging ods-explore library code.

Custom querystring parameters (such as `limit` or `offset`) can be added to the underlying API call with `**kwargs`.

#### decoded_url
`decoded_url`

Like [`url()`](#url), but returns the decoded URL, with plus signs replaced with spaces and `%xx` escapes replaced with their single-character equivalents.

&nbsp;
### Field lookups
Field lookups are how you specify the core of an ODSQL where clause. Using the key format `<field name>__<field lookup>`, they're passed as keyword arguments to the Query methods [`filter()`](#filter) and [`exclude()`](#exclude), and to [`Q()` objects](#q-objects).

#### contains
Case-insensitive word containment. 
```py
# matches 'La Lima', 'Palos de la Frontera', and 'Shangri-La', but not 'Las Vegas'
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .filter(name__contains='la')
)

# matches 'Santiago de la Peña', 'La Puebla de Almoradiel', and 'Saint-Jean-de-la-Ruelle'
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .filter(name__contains='de la')
)
```

#### exact
Exact match (the default lookup behaviour when no field lookup is used).
```py
ods.catalog.datasets.filter(dataset_id='doc-geonames-cities-5000')

# is equivalent to

ods.catalog.datasets.filter(dataset_id__exact='doc-geonames-cities-5000')
```

#### gt
Greater than.
```py
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .filter(population__gt=500)
)
```

#### gte
Greater than or equal to.

#### lt
Less than.

#### lte
Less than or equal to.

#### in
In a given iterable, usally a list or tuple.
```py
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .filter(country_code__in=['CA', 'FR'])
)
```

#### inarea
In a geographical area (for geo_point fields only).

The literals, helpers, filter functions, and enums described below are provided in the `ods_explore.language` module.

One of the following filter functions that should be used in conjunction with this field lookup. In each case, the first argument is a `Geometry` literal that describes a geographical area. This is created with the `geom(geometry)` helper, where `geometry` is a [WKT/WKB](https://en.wikipedia.org/wiki/Well-known_text) or [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON) geometry expression as a string or dictionary.

`polygon(area)` \
Limit results to a geographical area.

`geometry(area, mode=Set.Within)` \
Limit results to a geographical area, based on a given set mode.

`circle(center, radius, unit=Unit.METERS)` \
Limit results to a geographical area defined by a circle.

#### isnull
Is null (accepts `True` or `False`).

&nbsp;
### Aggregation functions
ods-explore provides the following aggregation functions in the `ods_explore.language` module, which can be provided as arguments to the [`aggregate()` query evaluation method](#aggregate).

#### avg
`avg(field)`

Returns the average value of a numeric field.

#### count
`count(field=None)`

Returns the number of non-null values of a field, or the total number of results matched by the query if no field is provided.

#### envelope
`envelope(field)`

Returns the convex hull (envelope) of a geo_point field.

#### max
`max(field)`

Returns the maximum value of a numeric or date field.

#### medium
`medium(field)`

Returns the median value (50th percentile) of a numeric field.

#### min
`min(field)`

Returns the minimum value of a numeric or date field.

#### percentile
`percentile(field, percentile)`

Returns the nth percentile of a numeric field.

#### sum
`sum(field)`

Returns the sum of all values of a numeric field.

&nbsp;
## Query-related tools
ods-explore provides the following tools in the `ods_explore.query` module.

### Q() objects
A `Q()` object represents an ODSQL condition that can be used in [`filter()`](#filter) and [`exclude()`](#exclude). They make it possible to define and reuse conditions, and can be used to perform complex queries when combined with the logical operators `&` (AND), `|` (OR), and `~` (NOT).

```py
# cities whose population is less than 6000 or greater than 7000
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .filter(Q(population__lt=6000) | Q(population__gt=7000))
)
```

### F() objects
An `F()` object represents the value of an object field, and makes it possible to refer to its value without having to retrieve it from the catalog. They make it possible to define conditions based on field values, and can be combined with the arithmetic operators `+`, `-`, `*`, and `/`.

```py
# select the average elevation (digital elevation model = dem) in meters (the default unit) and in kilometers
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .select(elevation_m='dem', elevation_km=F('dem') / 1000)
)

# cities whose population is less than their average elevation
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .filter(population__lt=F('dem'))
)
```

&nbsp;
## Objects
The following are object representations of Opendatasoft entities, implemented as `typing.NamedTuple`s, that many [query evaluation methods](#methods-that-evaluate-queries-and-return-something-other-than-a-query) return by default.

### Dataset
`ods_explore.models.Dataset(attachments, data_visible dataset_id, dataset_uid, features, fields, has_records, metas, visibility)`
* `attachments` - A list of dictionaries of available file attachments for the dataset.
* `data_visible` - `True` if the caller is authorized to view this dataset, and `False` otherwise.
* `dataset_id` - The dataset id.
* `dataset_uid` - The unique dataset id.
* `features` - A list of available features for the dataset.
* `fields` - A list of dictionaries of field names and associated metadata. 
* `has_records` - `True` if the dataset has at least one record, and `False` otherwise.
* `metas` - Metadata about the dataset, as a dictionary.
* `visibility` - A string indicating whether the dataset is public (`domain`) or private (`restricted`).

### Record
`ods_explore.models.Record(id, fields, size, timestamp)`
* `id` - The record id.
* `fields` - The record data fields, as a dictionary.
* `size` - The record size in bytes.
* `timestamp` - The record's creation time.
