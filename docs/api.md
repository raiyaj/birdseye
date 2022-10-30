<!-- omit in toc -->
## Contents
- [Main interface](#main-interface)
  - [_`class`_ `opendatasoft.`__`Opendatasoft`__`(subdomain='data', base_url=None, session=None, api_key=None, lang='en', timezone='UTC')`](#class-opendatasoftopendatasoftsubdomaindata-base_urlnone-sessionnone-api_keynone-langen-timezoneutc)
  - [Making queries](#making-queries)
    - [Catalog queries](#catalog-queries)
    - [Dataset queries](#dataset-queries)
    - [Record queries](#record-queries)
- [Query API](#query-api)
  - [Methods that return new Queries](#methods-that-return-new-queries)
    - [`filter()`](#filter)
    - [`exclude()`](#exclude)
    - [`select()`](#select)
    - [`annotate()`](#annotate)
    - [`order_by()`](#order_by)
    - [`refine()`](#refine)
    - [`ignore()`](#ignore)
  - [Methods that evaluate queries and return results](#methods-that-evaluate-queries-and-return-results)
    - [`get()`](#get)
    - [`count()`](#count)
    - [`exists()`](#exists)
    - [`iterator()`](#iterator)
    - [`all()`](#all)
    - [`dataframe()`](#dataframe)
    - [`first()`](#first)
    - [`last()`](#last)
    - [`aggregate()`](#aggregate)

## Main interface
All of ods_explore's functionality can be accessed with an instance of `opendatasoft.Opendatasoft`. Queries are made using its `catalog` property.

### _`class`_ `opendatasoft.`__`Opendatasoft`__`(subdomain='data', base_url=None, session=None, api_key=None, lang='en', timezone='UTC')`

Parameters:
* _subdomain_ - A subdomain used to create the base API URL, useful if the data portal being accessed is hosted on [opendatasoft.com](https://opendatasoft.com/), eg. https://{subdomain}.opendatasoft.com.
* _base_url_ - A custom base API URL.
* _session_ - A `request.Session` object with which to make API calls.
* _api_key_ - An Opendatasoft API key (to be attached to the session object), for accessing private datasets. [Read more on generating API keys.](https://help.opendatasoft.com/apis/ods-explore-v2/#section/Authentication/Finding-and-generating-API-keys)
* _lang_ - The language used to format strings. One of: `en`, `fr`, `nl`, `pt`, `it`, `ar`, `de`, `es`, `ca`, `eu`, `sv`
* _timezone_ - The timezone applied to datatime fields, [as defined by the Unicode CLDR project](https://github.com/unicode-org/cldr/blob/main/common/bcp47/timezone.xml).

<!-- omit in toc -->
#### __base_url__

<!-- omit in toc -->
#### __catalog__

<!-- omit in toc -->
#### __session__

### Making queries

#### Catalog queries

#### Dataset queries

#### Record queries

## Query API
### Methods that return new Queries
#### `filter()`
#### `exclude()`
#### `select()`
#### `annotate()`
#### `order_by()`
#### `refine()`
#### `ignore()`

### Methods that evaluate queries and return results
#### `get()`
#### `count()`
#### `exists()`
#### `iterator()`
#### `all()`
#### `dataframe()`
#### `first()`
#### `last()`
#### `aggregate()`
