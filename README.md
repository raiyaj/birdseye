A Python client for [Opendatasoft's Explore API (v2)](https://help.opendatasoft.com/apis/ods-explore-v2/). ods-explore provides a querying interface inspired by the [Django Queryset API](https://docs.djangoproject.com/en/latest/ref/models/querysets/), which converts queries to the [Opendatasoft Query Language ODSQL](https://help.opendatasoft.com/apis/ods-explore-v2/#section/Opendatasoft-Query-Language-(ODSQL)) internally. &nbsp;🐍 📊

<!-- omit in toc -->
## Contents
- [Installation](#installation)
- [Getting started](#getting-started)
- [API docs](#api-docs)

## Installation
```py
pip install ods_explore
```

## Getting started
```py
from ods_explore.opendatasoft import Opendatasoft

ods = Opendatasoft(subdomain='documentation-resources')

# get datasets in a catalog
ods.catalog.datasets.get()

# get one dataset
ods.catalog.dataset('doc-geonames-cities-5000').get()

# get records in a dataset
ods.catalog.dataset('doc-geonames-cities-5000').records.get()

# get the least-populated cities only
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .records
  .filter(population__lt=500)
  .get()
)

# get one record
(
  ods
  .catalog
  .dataset('doc-geonames-cities-5000')
  .record('24eec8bff4f5b55afdeeeacb326167ed6b1e933a')
  .get()
)
```

## API docs
See [docs/api.md](/docs/api.md) for detailed documentation of ods_explore classes and usage patterns.
