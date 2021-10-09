from __future__ import annotations

from copy import deepcopy
import logging
from typing import Any, List, NewType, Optional, Tuple, Union

from . import models

logger = logging.getLogger(__package__)

ODSQL = NewType('ODSQL', str)


class Lookup:
  ## Non field lookups ##
  NON_FIELD_CONTAINS = '__contains__'

  ## Meta field lookups ##
  KEYWORD = '__keyword__'

  ## Field lookups ##
  CONTAINS = '__contains'
  EXACT = '__exact'
  GT = '__gt'
  GTE = '__gte'
  LT = '__lt'
  LTE = '__lte'
  IN = '__in'
  INRANGE = '__inrange'
  ISNULL = '__isnull'
  FIELD_LOOKUPS = [CONTAINS, EXACT, GT, GTE, LT, LT, IN, INRANGE, ISNULL]

  @classmethod
  def parse(cls, key: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Search for and trim a lookup from a key.
    :returns: (trimmed key, lookup)
    """
    if key == cls.NON_FIELD_CONTAINS:
      return None, cls.NON_FIELD_CONTAINS

    if key.startswith(cls.KEYWORD):
      key = f'`{cls.trim(key, cls.KEYWORD, trim_start=True)}`'

    for lookup in cls.FIELD_LOOKUPS:
      if key.endswith(lookup):
        return cls.trim(key, lookup), lookup

    return key, None

  @classmethod
  def trim(cls, key: str, lookup: str, trim_start: bool = False) -> str:
    """
    Trim a lookup from a key.
    """
    if trim_start:
      return key[len(lookup):]
    return key[:-len(lookup)]


class Q:
  """
  """
  def __init__(self, **kwargs: Any) -> None:
    self.kwargs = kwargs

  # def __and__(self, other: Q) -> ODSQL:
  #   return f'{self.odsql} and {other.odsql}'

  # def __or__(self, other: Q) -> ODSQL:
  #   return f'{self.odsql} or {other.odsql}'

  # def __invert__(self) -> ODSQL:
  #   return f'not {self.odsql}'

  @property
  def odsql(self) -> str:
    """
    ODSQL representation of query expressions.
    """
    expressions = []
    for key, value in self.kwargs.items():
      field, lookup = Lookup.parse(key)

      # Handle non-field lookups
      if lookup == Lookup.NON_FIELD_CONTAINS:
        expressions.append(f'"{value}"')
        continue

      # Handle field lookups
      query = None
      if lookup == Lookup.CONTAINS:
        op, query = 'like', f'"{value}"'
      elif lookup == Lookup.EXACT:
        op, query = '=', value
      elif lookup == Lookup.GT:
        op, query = '>', value
      elif lookup == Lookup.GTE:
        op, query = '>=', value
      elif lookup == Lookup.LT:
        op, query = '<', value
      elif lookup == Lookup.LTE:
        op, query = '<=', value
      elif lookup == Lookup.IN:
        op, queries, sep = '=', value, ' or '
      elif lookup == Lookup.INRANGE:
        op, query = 'in', value
      elif lookup == Lookup.ISNULL:
        op, query = 'is', f'{"" if value else "not "}null'
      elif isinstance(value, bool):
        op, query = 'is', str(value).lower()
      else:
        op, query = '=', value

      expressions.append(
        f'{field} {op} {query}'
        if query
        else sep.join(f'{field} {op} {query}' for query in queries)
      )

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
    raise NotImplementedError()

  def lookup(self):
    pass
  
  def facets(self):
    pass

  def metadata(self):
    pass

  ## ODSQL filters ##

  def select(self):
    pass

  def where(self, *args: Union[Q, ODSQL], **kwargs: Any) -> Query:
    """
    Filter rows.
    :param contains: Search terms, ANDed together. A wildcard (*) may be added
      at the end of a word.
    :param args: Q expression(s) or a raw ODSQL query
    :param kwargs:
    """
    q_expressions = (
      f'({arg})'
      if isinstance(arg, str) and ' or ' in arg
      else arg
      for arg in args
    )
    expressions = (
      expression.odsql
      if isinstance(expression, Q)
      else expression
      for expression in [*q_expressions, Q(**kwargs)]
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
          f'{Lookup.trim(key, Lookup.IN)}:{item}' for item in value
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
