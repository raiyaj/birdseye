from __future__ import annotations

from copy import deepcopy
import random
from typing import Any, NewType, Optional, Tuple, Union
import urllib.parse

from . import language as lang
from . import models

ODSQL = NewType('ODSQL', str)


class Lookup:
  """Field lookups"""

  CONTAINS = '__contains' 
  EXACT = '__exact'
  GT = '__gt'
  GTE = '__gte'
  LT = '__lt'
  LTE = '__lte'
  IN = '__in'
  INAREA = '__inarea'
  INRANGE = '__inrange'
  ISNULL = '__isnull'

  @classmethod
  def parse(cls, key: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Search for and trim a lookup from a key.
    :param key: Key to parse
    :returns: (trimmed key, lookup)
    """
    lookups = [getattr(cls, attr) for attr in dir(cls) if attr.isupper()]  
    for lookup in lookups:
      if key.endswith(lookup):
        return cls.trim(key, lookup), lookup
    return key, None

  @staticmethod
  def trim(key: str, lookup: str) -> str:
    """
    Trim a lookup from a key.
    :param key: Key to trim
    :param lookup: Lookup to remove
    """
    trimmed = key[:-len(lookup)]
    if not trimmed:
      raise ValueError(f"Invalid lookup parameter '{key}'")
    return trimmed


class Q:
  """
  Represent complex queries using field lookups, which can be combined with
  bitwise boolean operators.
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
    q.raw = f'not {odsql}'
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
      field = lang.fld(field_name)

      # Handle lookups
      expression = None
      if lookup == Lookup.CONTAINS:
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
        expression = ' or '.join(f'{field} = {query}' for query in queries)
        expression = f'({expression})'
      elif lookup == Lookup.INAREA:
        expression = value.format(field)
      elif lookup == Lookup.INRANGE:
        op, query = 'in', value
      elif lookup == Lookup.ISNULL:
        op, query = 'is', f'{"" if value else "not "}null'
      elif isinstance(value, bool):
        op, query = 'is', str(value).lower()
      else:
        op, query = '=', lang.str(value) if isinstance(value, str) else value

      expressions.append(expression or f'{field} {op} {query}')
    return " and ".join(expressions)


class F(str):
  """Represent the value of a field."""

  def __init__(self, field: str) -> None:
    """
    :param field: The field name
    """
    self.field = field

  def __add__(self, other: float) -> str:
    return f'{self.field} + {other}'

  def __sub__(self, other: float) -> str:
    return f'{self.field} - {other}'

  def __mul__(self, other: float) -> str:
    return f'{self.field} * {other}'

  def __truediv__(self, other: float) -> str:
    return f'{self.field} / {other}'


class Query(models.OpendatasoftCore):
  """ORM base class"""

  def __init__(self, **kwargs) -> None:
    self.settings = {
      'lang': kwargs.pop('lang'),
      'timezone': kwargs.pop('timezone')
    }
    super().__init__(**kwargs)

    self._select = []
    self._where = []
    self._group_by = []
    self._order_by = ''
    self._refine = []
    self._exclude = []

  def _clone(self) -> Query:
    return deepcopy(self)

  @property
  def url(self) -> str:
    return self.build_url(
      self.base_path,
      self.build_querystring(
        select=self._select,
        where=self._where,
        group_by=self._group_by,
        order_by=self._order_by,
        refine=self._refine,
        exclude=self._exclude,
        **self.settings
      )
    )

  @property
  def decoded_url(self) -> str:
    return urllib.parse.unquote_plus(self.url)

  ## Fetch results ##

  def get(self) -> dict:
    return super().get(self.url)

  def count(self) -> int:
    return self.get()['total_count']

  def exists(self) -> bool:
    return self.count() > 0

  def aggregate(self, *args, **kwargs) -> dict:
    """
    Returns a dictionary of aggregate values. Each argument specifies a value
    that will be included in the output, and can be defined with a label.
    """
    if not args and not kwargs:
      return {}

    query = self.select(*args, **kwargs)
    results = query.get()

    if results['total_count'] == 0:
      return {}

    resource = None
    if isinstance(self, CatalogQuery):
       resource = 'dataset'
    elif isinstance(self, DatasetQuery):
      resource = 'record'

    return results[f'{resource}s'][0][resource]['fields']

  ## Chainable querying methods ##

  def filter(self, *args: Union[Q, ODSQL], **kwargs: Any) -> Query:
    """
    Return results that match the given filters.
    :param *args: Q expressions or raw ODSQL queries
    :param **kwargs: Field lookups
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

  def exclude(self, *args: Union[Q, ODSQL], **kwargs: Any) -> Query:
    """
    Return results that do not match the given filters.
    :param *args: Q expressions or raw ODSQL queries
    :param **kwargs: Field lookups
    """
    query = self.filter(*args, **kwargs)
    filter_expression = query._where.pop()
    if filter_expression:
      query._where.append(f'not ({filter_expression})')
    return query

  def select(self, *args: Any, **kwargs: Any) -> Query:
    """
    Choose fields to return. Each argument is an expression to which the
    `select` should be limited. Expressions can be fields, strings, numbers, F
    expressions, aggregations, or scalar functions, and can be combined with
    arithmetic operators and defined with labels.
    """
    annotations = (
      f'{value} as {key}'
      for key, value in kwargs.items()
    )
    clone = self._clone()
    clone._select.append(','.join([*args, *annotations]))
    return clone

  def group_by(self, *args: str, **kwargs: Any) -> Query:
    pass

  def order_by(self, *args: str) -> Query:
    """
    """
    if '?' in args:
      self._order_by = f'random({random.randint(0, 1000)})'
      return self

    expressions = (
      f'{arg.lstrip("-")} desc'
      if arg.startswith('-')
      else f'{arg} asc'
      for arg in args
    )
    self._order_by = ','.join(expressions)
    return self

  def refine(self, **kwargs: Any) -> Query:
    """
    Return results that match the given facet values.
    :param **kwargs: Facet parameters
    """
    clone = self._clone()
    clone._refine.extend(f'{key}:{value}' for key, value in kwargs.items())
    return clone

  def ignore(self, **kwargs: Any) -> Query:
    """
    Return results that do not match the given facet values.
    :param **kwargs: Facet parameters, compatible with `in` field lookup
    """
    clone = self._clone()
    for key, value in kwargs.items():
      if key.endswith(Lookup.IN):
        key = Lookup.trim(key, Lookup.IN)
      else:
        value = [value]
      clone._exclude.extend(f'{key}:{item}' for item in value)
    return clone

  ## Not implemented ##

  def export(self):
    raise NotImplementedError()
  
  def facets(self):
    raise NotImplementedError()

  def attachments(self):
    raise NotImplementedError()


class CatalogQuery(Query):
  """Interface for the Catalog API"""

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.base_path = ''
    self.datasets = self._clone()
    self.datasets.many = True
    self.datasets.base_path = 'datasets'

  def dataset(self, dataset_id: str) -> DatasetQuery:
    return DatasetQuery(
      dataset_id=dataset_id,
      base_url=self.base_url,
      session=self.session,
      **self.settings
    )


class DatasetQuery(Query):
  """Interface for the Dataset API"""

  def __init__(self, **kwargs) -> None:
    self.dataset_id = kwargs.pop('dataset_id')
    super().__init__(**kwargs)

    self.base_path = f'datasets/{self.dataset_id}'
    self.records = self._clone()
    self.records.many = True
    self.records.base_path += '/records'

  def record(self, record_id: str) -> RecordQuery:
    return RecordQuery(
      record_id=record_id,
      base_path=self.base_path,
      base_url=self.base_url,
      session=self.session,
      **self.settings
    )


class RecordQuery(Query):
  def __init__(self, **kwargs) -> None:
    self.record_id = kwargs.pop('record_id')
    self.base_path = kwargs.pop('base_path') + f'/records/{self.record_id}'
    super().__init__(**kwargs)
