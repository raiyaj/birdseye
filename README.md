A Python client for [Opendatasoft's Explore API (v2)](https://help.opendatasoft.com/apis/ods-explore-v2/), inspired by the [Django Queryset API](https://docs.djangoproject.com/en/latest/ref/models/querysets/) &nbsp;🐍 📊

## Contents
- [Contents](#contents)
- [Installation](#installation)
- [Getting started](#getting-started)
- [API docs](#api-docs)
- [Usage examples](#usage-examples)
  - [Query datasets](#query-datasets)
  - [Query dataset records](#query-dataset-records)

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
See [doc/api.md](/doc/api.md) for detailed documentation of ods_explore classes.

## Usage examples

### Query datasets

### Query dataset records
