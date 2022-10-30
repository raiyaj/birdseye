A Python client for [Opendatasoft's Explore API (v2)](https://help.opendatasoft.com/apis/ods-explore-v2/), inspired by the [Django Queryset API](https://docs.djangoproject.com/en/latest/ref/models/querysets/) &nbsp;🐍 📊

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
datasets = ods.catalog.datasets.get()
```

## API docs
See [docs/api.md](/docs/api.md) for detailed documentation of ods_explore classes and usage patterns.
