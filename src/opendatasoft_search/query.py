from __future__ import annotations

from copy import deepcopy
import logging
from typing import Any, Iterable, List, NewType, Union

from . import models

logger = logging.getLogger(__package__)

ODSQL = NewType('ODSQL', str)


class Lookup:
  CONTAINS = '__contains'
  ESCAPE = '__escape'
  EXACT = '__exact'
  GT = '__gt'
  GTE = '__gte'
  LT = '__lt'
  LTE = '__lte'
  IN = '__in'
  INRANGE = '__inrange'
  ISNULL = '__isnull'

  @classmethod
  def trim(cls, kwarg_key: str) -> str:
    """
    Trim valid lookup from the end of a key.
    :param kwarg_key: Key to trim
    """
    lookups = [getattr(cls, attr) for attr in dir(cls) if attr.isupper()]
    for lookup in lookups:
      if kwarg_key.endswith(lookup):
        return kwarg_key[:-len(lookup)]
    return kwarg_key


class Q:
  """
  """
  def __init__(
    self,
    contains: Union[str, Iterable[str]] = [],
    **kwargs: Any
  ) -> None:
    """
    """
    self.contains = contains if isinstance(contains, list) else [contains]
    self.kwargs = kwargs

  @property
  def odsql(self) -> str:
    """
    ODSQL representation of query expressions.
    """
    expressions = []
    for query in self.contains:
      expressions.append(f'"{query}"')
    
    has_filter_lookup = True
    for key, value in self.kwargs.items():
      if key.endswith(Lookup.CONTAINS):
        op, query = 'like', f'"{value}"'
      elif key.endswith(Lookup.GT):
        op, query = '>', value
      elif key.endswith(Lookup.GTE):
        op, query = '>=', value
      elif key.endswith(Lookup.LT):
        op, query = '<', value
      elif key.endswith(Lookup.LTE):
        op, query = '<=', value
      elif key.endswith(Lookup.INRANGE):
        op, query = 'in', value
      elif key.endswith(Lookup.ISNULL):
        op, query = 'is', f'{"" if value else "not "}null'
      elif isinstance(value, bool):
        op, query = 'is', str(value).lower()
      else:
        op, query = '=', value
        has_filter_lookup = key.endswith(Lookup.EXACT)

      if has_filter_lookup:
        key = Lookup.trim(kwarg_key=key)
      if key.endswith(Lookup.ESCAPE):
        key = f'`{Lookup.trim(kwarg_key=key)}`'

      expressions.append(f'{key} {op} {query}')
    return ' and '.join(expressions)


class Query(models.OpendatasoftCore):
  """
  """
  def __init__(self, **kwargs) -> None:
    self.timezone = kwargs.pop('timezone')
    super().__init__(**kwargs)

    self._select = []
    self._where = []
    self._group_by = []
    self._order_by = []
    self._refine = []
    self._exclude = []

  def _clone(self) -> Query:
    return deepcopy(self)

  ## API endpoints ##

  def search(
    self,
    offset: int = 0,
    limit: int = 10,
    timezone: str = None
  ) -> dict:
    """
    Search datasets.
    :param offset: Index of the first item to return
    :param limit: Number of items to return
    :param timezone: Timezone applied to datetime fields in queries and
      responses
    """
    url = self.build_url(
      *self._get_path_parts(endpoint='search'),
      self.build_querystring(
        where=self._where,
        refine=self._refine,
        exclude=self._exclude,
        offset=offset,
        limit=limit,
        timezone=timezone or self.timezone
      )
    )
    json = self.get(url)
    return json

  def aggregate(self, limit: str = None, timezone: str = None) -> dict:
    """
    Aggregate datasets.
    :param limit: Number of items to return
    :param timezone: Timezone applied to datetime fields in queries and
      responses
    """
    url = self.build_url(
      *self._get_path_parts(endpoint='aggregate'),
      'aggregates',
      self.build_querystring(
        limit=limit,
        timezone=timezone or self.timezone
      )
    )
    json = self.get(url)
    return json

  def export(self):
    pass

  def lookup(self):
    pass
  
  def facets(self):
    pass

  def metadata(self):
    pass

  ## ODSQL filters ##

  def select(self):
    pass

  def where(
    self,
    raw: ODSQL = None,
    contains: Union[str, Iterable[str]] = [],
    *args: Q,
    **kwargs: Any
  ) -> Query:
    """
    Filter rows.
    :param raw: Raw ODSQL query
    :param contains: Search terms, ANDed together. A wildcard (*) may be added
      at the end of a word.
    :param args:
    :param kwargs:
    """
    expressions = (
      expression.odsql
      if isinstance(expression, Q)
      else expression
      for expression in [raw, Q(contains=contains), *args, Q(**kwargs)]
    )
    self._where.append(' and '.join(filter(None, expressions)))
    return self._clone()

  def group_by(self):
    pass

  def order_by(self):
    pass

  ## Facet filters ##

  def refine(self, **kwargs: Any) -> Query:
    """
    Limit results by refining on the given facet values, ANDed together.
    :param **kwargs: Facet names and values
    """
    self._refine.extend(
      f'{key}:{value}'
      for key, value in kwargs.items()
    )
    return self._clone()

  def exclude(self, **kwargs: Any) -> Query:
    """
    Limit results by excluding the given facet values, ANDed together.
    :param **kwargs: Facet names and values, compatible with `in` lookups
    """
    for key, value in kwargs.items():
      if key.endswith(Lookup.IN):
        self._exclude.extend(
          f'{Lookup.trim(kwarg_key=key)}:{item}' for item in value
        )
      else:
        self._exclude.append(f'{key}:{value}')
    return self._clone()


class CatalogQuery(Query):
  """Interface for the Catalog API"""

  def _get_path_parts(self, endpoint: str) -> List[str]:
    if endpoint == 'search':
      return ['datasets']
    return []

  def dataset(self, dataset_id: str) -> DatasetQuery:
    return DatasetQuery(
      dataset_id=dataset_id,
      base_url=self.base_url,
      session=self.session,
      source=self.source,
      timezone=self.timezone
    )


class DatasetQuery(Query):
  """Interface for the Dataset API"""

  def __init__(self, **kwargs) -> None:
    self.dataset_id = kwargs.pop('dataset_id')
    super().__init__(**kwargs)

  def _get_path_parts(self, endpoint: str) -> List[str]:
    path_parts = ['datasets', self.dataset_id]
    if endpoint == 'search':
      path_parts.append('records')
    return path_parts
