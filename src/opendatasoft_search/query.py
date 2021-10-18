from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, List, NewType, Optional, Tuple, Union

from . import language as lang
from . import models

ODSQL = NewType('ODSQL', str)


class Lookup:
  ## Lookups ##
  CONTAINS = '__contains'  # A field-level and row-level lookup
  EXACT = '__exact'
  GT = '__gt'
  GTE = '__gte'
  LT = '__lt'
  LTE = '__lte'
  IN = '__in'
  INAREA = '__inarea'
  INRANGE = '__inrange'
  ISNULL = '__isnull'

  # Optional prefix for escaping field names
  ESC = '__esc__'

  @classmethod
  def parse(cls, key: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Search for and trim a lookup from a key.
    :param key: Key to parse
    :returns: (trimmed key, lookup)
    """
    if key == cls.CONTAINS:
      return None, cls.CONTAINS  # Row-level CONTAINS

    if key.startswith(cls.ESC):
      key = cls.trim(key, cls.ESC, from_start=True)

    lookups = [getattr(cls, attr) for attr in dir(cls) if attr.isupper()]
    lookups.remove(cls.ESC)
    for lookup in lookups:
      if key.endswith(lookup):
        return cls.trim(key, lookup), lookup

    return key, None

  @staticmethod
  def trim(key: str, lookup: str, from_start: bool = False) -> str:
    """
    Trim a lookup from a key.
    :param key: Key to trim
    :param lookup: Lookup to remove
    :param from_start: Trim from the start of the key
    """
    trimmed = key[len(lookup):] if from_start else key[:-len(lookup)]
    if not trimmed:
      raise ValueError(f"Invalid lookup parameter '{key}'")
    return trimmed


class Q:
  """
  Complex queries using lookups, and combined with bitwise boolean operators
  """

  def __init__(self, **kwargs: Any) -> None:
    """
    :param **kwargs: Lookup parameters
    """
    self.kwargs = kwargs
    self.raw = ''

  def __and__(self, other: Q) -> Q:
    """a & b"""
    q = Q()
    q.raw = f'{self.odsql} and {other.odsql}'
    return q

  def __or__(self, other: Q) -> Q:
    """a | b"""
    q = Q()
    # Include parentheses because `and` has precedence over `or`
    q.raw = f'({self.odsql} or {other.odsql})'
    return q

  def __invert__(self) -> Q:
    """~a"""
    q = Q()
    odsql = self.odsql
    # Include parentheses because inversion may apply to > 1 expression
    if not (odsql.startswith('(') and odsql.endswith(')')):
      odsql = f'({odsql})'
    q.raw = f'not {self.odsql}'
    return q

  @property
  def odsql(self) -> Optional[ODSQL]:
    """
    ODSQL representation of query expressions
    """
    if self.raw:
      return self.raw

    if not self.kwargs:
      return None

    expressions = []
    for key, value in self.kwargs.items():
      field_name, lookup = Lookup.parse(key)

      # Escape field names
      if field_name:
        if field_name in lang.KEYWORDS or field_name.isdigit():
          field_name = f'`{field_name}`'

      # Handle lookups
      expression = None
      if lookup == Lookup.CONTAINS and field_name is None:
        expression = lang.str(value)  # Row-level CONTAINS
      elif lookup == Lookup.CONTAINS:
        op, query = 'like', lang.str(value)
      elif lookup == Lookup.GT:
        op, query = '>', value
      elif lookup == Lookup.GTE:
        op, query = '>=', value
      elif lookup == Lookup.LT:
        op, query = '<', value
      elif lookup == Lookup.LTE:
        op, query = '<=', value
      elif lookup == Lookup.IN:
        queries = (
          lang.str(query)
          if isinstance(query, str)
          else query
          for query in value
        )
        expression = ' or '.join(f'{field_name} = {query}' for query in queries)
        expression = f'({expression})'
      elif lookup == Lookup.INAREA:
        expression = value.format(field_name)
      elif lookup == Lookup.INRANGE:
        op, query = 'in', value
      elif lookup == Lookup.ISNULL:
        op, query = 'is', f'{"" if value else "not "}null'
      elif isinstance(value, bool):
        op, query = 'is', str(value).lower()
      else:
        op, query = '=', lang.str(value) if isinstance(value, str) else value

      expressions.append(expression or f'{field_name} {op} {query}')
    return " and ".join(expressions)


class Query(models.OpendatasoftCore):
  """ORM base class"""

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
      *self._path_parts(endpoint='search'),
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
      *self._path_parts(endpoint='aggregate'),
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
    raise NotImplementedError()

  ## ODSQL filters ##

  def select(self):
    pass

  def where(self, *args: Union[Q, ODSQL], **kwargs: Any) -> Query:
    """
    Filter results.
    :param *args: Q expressions or raw ODSQL queries
    :param **kwargs: Lookup parameters
    """
    expressions = (
      expression.odsql
      if isinstance(expression, Q)
      else expression
      for expression in [*args, Q(**kwargs)]
    )
    clone = self._clone()
    clone._where.append(' and '.join(filter(None, expressions)))
    return clone

  def group_by(self):
    pass

  def order_by(self):
    pass

  ## Facet filters ##

  def refine(self, **kwargs: Any) -> Query:
    """
    Limit results by refining on the given facet values, ANDed together.
    :param **kwargs: Facet parameters
    """
    clone = self._clone()
    clone._refine.extend(f'{key}:{value}' for key, value in kwargs.items())
    return clone

  def exclude(self, **kwargs: Any) -> Query:
    """
    Limit results by excluding the given facet values, ANDed together.
    :param **kwargs: Facet parameters, compatible with `in` lookups
    """
    clone = self._clone()
    for key, value in kwargs.items():
      if key.endswith(Lookup.IN):
        key = Lookup.trim(key, Lookup.IN)
      else:
        value = [value]
      clone._exclude.extend(f'{key}:{item}' for item in value)
    return clone


class CatalogQuery(Query):
  """Interface for the Catalog API"""

  def _path_parts(self, endpoint: str) -> List[str]:
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

  def _path_parts(self, endpoint: str) -> List[str]:
    path_parts = ['datasets', self.dataset_id]
    if endpoint == 'search':
      path_parts.append('records')
    return path_parts
