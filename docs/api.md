# Query API Reference

<!-- omit in toc -->
## Contents
- [Query API Reference](#query-api-reference)
  - [Main interface](#main-interface)
    - [_class_ opendatasoft.Opendatasoft](#class-opendatasoftopendatasoft)
    - [Making queries](#making-queries)
      - [Catalog queries](#catalog-queries)
      - [Dataset queries](#dataset-queries)
      - [Record queries](#record-queries)
  - [Query API](#query-api)
    - [Methods that return new Queries](#methods-that-return-new-queries)
      - [filter](#filter)
      - [exclude](#exclude)
      - [select](#select)
      - [annotate](#annotate)
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
    - [Field lookups](#field-lookups)
      - [contains](#contains)
      - [exact](#exact)
      - [gt](#gt)
      - [gte](#gte)
      - [lt](#lt)
      - [lte](#lte)
      - [gt](#gt-1)
      - [in](#in)
      - [inarea](#inarea)
      - [inrange](#inrange)
      - [isnull](#isnull)
    - [Aggregate functions](#aggregate-functions)
      - [avg](#avg)
      - [count](#count-1)
      - [envelope](#envelope)
      - [max](#max)
      - [medium](#medium)
      - [min](#min)
      - [percentile](#percentile)
      - [sum](#sum)
  - [Query-related tools](#query-related-tools)
    - [Q objects](#q-objects)
    - [F objects](#f-objects)

## Main interface
All of ods_explore's functionality can be accessed with an instance of `opendatasoft.Opendatasoft`.

### _class_ opendatasoft.Opendatasoft
`opendatasoft.Opendatasoft(subdomain='data', base_url=None, session=None, api_key=None, lang='en', timezone='UTC')`

* `subdomain` - A subdomain used to create the base API URL, useful if the data portal being accessed is hosted on [opendatasoft.com](https://opendatasoft.com/), eg. https://{subdomain}.opendatasoft.com.
* `base_url` - A custom base API URL.
* `session` - A `request.Session` object with which to make API calls.
* `api_key` - An Opendatasoft API key (to be attached to the session object), for accessing private datasets. [Read more on generating API keys.](https://help.opendatasoft.com/apis/ods-explore-v2/#section/Authentication/Finding-and-generating-API-keys)
* `lang` - The language used to format strings. One of: `en`, `fr`, `nl`, `pt`, `it`, `ar`, `de`, `es`, `ca`, `eu`, `sv`
* `timezone` - The timezone applied to datetime fields, [as defined by the Unicode CLDR project](https://github.com/unicode-org/cldr/blob/main/common/bcp47/timezone.xml).

`base_url` \
The resolved base API URL.

`catalog` \
An instance of `query.CatalogQuery`, the top-level querying interface, as described below.

`session` \
The session object.

&nbsp;
### Making queries

#### Catalog queries

#### Dataset queries

#### Record queries

&nbsp;
## Query API
### Methods that return new Queries
#### filter
#### exclude
#### select
#### annotate
#### order_by
#### refine
#### ignore

&nbsp;
### Methods that evaluate Queries and return something _other_ than a Query
#### get
#### count
`count()` \
Returns an integer representing the number of catalog items matching the query. 
```py
# Returns the number of datasets in a catalog
ods.catalog.datasets.count()

# Returns the number of records in the dataset 'doc-geonames-cities-5000'
ods.catalog.dataset('doc-geonames-cities-5000').records.count()

# Returns the number of records whose country code is 'CA'
ods.catalog.datasets('doc-geonames-cities-5000').records.filter(country_code='CA').count()
```
`count()` calls `get(limit=0)` behind the scenes, so you should use `count()` instead of loading all items into Python objects - unless you need them in memory anyway, in which case calling `len()` is faster as it avoids an extra API call.
#### exists
#### iterator
#### all
#### dataframe
#### first
#### last
#### aggregate

&nbsp;
### Field lookups
#### contains
#### exact
#### gt
#### gte
#### lt
#### lte
#### gt
#### in
#### inarea
#### inrange
#### isnull

&nbsp;
### Aggregate functions
#### avg
#### count
#### envelope
#### max
#### medium
#### min
#### percentile
#### sum

&nbsp;
## Query-related tools
### Q objects
### F objects