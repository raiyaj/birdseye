<!-- omit in toc -->
## Contents
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
  - [Methods that evaluate Queries and return results](#methods-that-evaluate-queries-and-return-results)
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
  - [Aggregate functions](#aggregate-functions)
- [Query-related tools](#query-related-tools)
  - [Q objects](#q-objects)
  - [F objects](#f-objects)

## Main interface
All of ods_explore's functionality can be accessed with an instance of `opendatasoft.Opendatasoft`.

### _class_ opendatasoft.Opendatasoft
`opendatasoft.Opendatasoft(subdomain='data', base_url=None, session=None, api_key=None, lang='en', timezone='UTC')`

* `subdomain`: A subdomain used to create the base API URL, useful if the data portal being accessed is hosted on [opendatasoft.com](https://opendatasoft.com/), eg. https://{subdomain}.opendatasoft.com.
* `base_url`: A custom base API URL.
* `session`: A `request.Session` object with which to make API calls.
* `api_key`: An Opendatasoft API key (to be attached to the session object), for accessing private datasets. [Read more on generating API keys.](https://help.opendatasoft.com/apis/ods-explore-v2/#section/Authentication/Finding-and-generating-API-keys)
* `lang`: The language used to format strings. One of: `en`, `fr`, `nl`, `pt`, `it`, `ar`, `de`, `es`, `ca`, `eu`, `sv`
* `timezone`: The timezone applied to datetime fields, [as defined by the Unicode CLDR project](https://github.com/unicode-org/cldr/blob/main/common/bcp47/timezone.xml).

<!-- omit in toc -->
#### `base_url`
The resolved base API URL.

<!-- omit in toc -->
#### `catalog`
An instance of `query.CatalogQuery`: the too-level querying interface, as described below.

<!-- omit in toc -->
#### `session`
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

### Methods that evaluate Queries and return results
#### get
#### count
#### exists
#### iterator
#### all
#### dataframe
#### first
#### last
#### aggregate

### Field lookups

### Aggregate functions

## Query-related tools
### Q objects
### F objects