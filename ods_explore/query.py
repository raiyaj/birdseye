from __future__ import annotations

from copy import deepcopy
import random
from typing import Any, Dict, List, NewType, Optional, Tuple, Union
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
    self._annotations = {}

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
      field_name = self._annotations.get(field_name, field_name)
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

  def annotate(self, annotations: dict) -> Q:
    self._annotations = annotations
    return self


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

  def __init__(
    self,
    format: Dict[str, str],
    **kwargs
  ) -> None:
    """
    :param format: Dictionary of default format options
      :lang str: Language used to format strings (for example, in the
        `date_format` method)
      :timezone str: Timezone applied to datetime fields in queries and
        responses
    """
    self.format = {
      'lang': format.get('lang', 'fr'),
      'timezone': format.get('timezone', 'UTC')
    }
    super().__init__(**kwargs)

    self._select = []
    self._where = []
    self._group_by = []
    self._order_by = ''
    self._refine = []
    self._exclude = []
    self._annotations = {}

  def _clone(self) -> Query:
    return deepcopy(self)

  @property
  def decoded_url(self) -> str:
    return urllib.parse.unquote_plus(self.url())

  def url(self, **kwargs: Any) -> str:
    return self.build_url(
      self.base_path,
      self.build_querystring(
        select=self._select,
        where=self._where,
        group_by=self._group_by,
        order_by=self._order_by,
        refine=self._refine,
        exclude=self._exclude,
        **self.format,
        **kwargs
      )
    )

  ## Fetch results ##

  def get(self, **kwargs: Any) -> dict:
    return super().get(self.url(**kwargs))

  def count(self) -> int:
    return self.get()['total_count']

  def exists(self) -> bool:
    return self.count() > 0

  def all(self, chunk_size: int = 100) -> List:
    """
    Returns all results as a list
    :param chunk_size: Number of results to fetch in each Opendatasoft API call
    """
    return list(self.iterator(chunk_size=chunk_size))

  def iterator(self, chunk_size: int = 100) -> dict:
    """
    Returns results as an iterator
    :param chunk_size: Number of results to fetch in each Opendatasoft API call
    """
    count = offset = 0
    key, klass = (
        ('dataset', models.Dataset)
        if isinstance(self, CatalogQuery)
        else ('record', models.Record)
      )
    key_plural = f'{key}s'

    while offset <= count:
      results = self.get(limit=chunk_size, offset=offset)
      count = results['total_count']
      items = results[key_plural]
      offset += len(items)

      if len(items) == 0:
        break

      for item in items:
        yield klass(**item[key])

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
    expressions = []
    for expression in [*args, Q(**kwargs)]:
      if isinstance(expression, Q):
        expression.annotate(self._annotations)
        expressions.append(expression.odsql)
      else:
        expressions.append(expression)

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
    Select fields to return. Each argument is an expression to which the
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

  def annotate(self, **kwargs: str) -> Query:
    """
    Annotate this query with the given labels and expressions (a scalar function
    such as `length()`), so that they may be referenced in subsequent chained
    methods. Note: this does not annotate items in the returned results; to do
    so, use `select()`.
    """
    self._annotations.update(kwargs)
    return self

  def group_by(self, *args: str, **kwargs: Any) -> Query:
    pass

  def order_by(self, *args: str) -> Query:
    """
    Specify the order of results.
    :param args: Field names, aggregation functions, or `?` to order results
      randomly
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
  """
  Interface for the Catalog API. Queries are made via self.datasets or
  self.dataset().
  """

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self.datasets = DatasetsQuery(
      base_url=self.base_url,
      session=self.session,
      format=self.format
    )

  def dataset(self, dataset_id: str) -> DatasetQuery:
    return DatasetQuery(
      dataset_id=dataset_id,
      base_url=self.base_url,
      session=self.session,
      format=self.format
    )


class DatasetsQuery(Query):
  many = True
  base_path = 'datasets'


class DatasetQuery(Query):
  """Interface for the Dataset API"""
  many = False

  def __init__(self, dataset_id: str, **kwargs) -> None:
    super().__init__(**kwargs)
    self.dataset_id = dataset_id
    self.records = RecordsQuery(
      dataset_id=dataset_id,
      base_url=self.base_url,
      session=self.session,
      format=self.format
    )

  @property
  def base_path(self):
    return f'datasets/{self.dataset_id}'
    

  def record(self, record_id: str) -> RecordQuery:
    return RecordQuery(
      dataset_id=self.dataset_id,
      record_id=record_id,
      base_url=self.base_url,
      session=self.session,
      format=self.format
    )


class RecordsQuery(Query):
  many = True

  def __init__(self, dataset_id: str, **kwargs) -> None:
    super().__init__(**kwargs)
    self.dataset_id = dataset_id
  
  @property
  def base_path(self):
    return f'datasets/{self.dataset_id}/records'


class RecordQuery(Query):
  many = False

  def __init__(self, dataset_id: str, record_id: str, **kwargs) -> None:
    super().__init__(**kwargs)
    self.dataset_id = dataset_id
    self.record_id = record_id

  @property
  def base_path(self):
    return f'datasets/{self.dataset_id}/records/{self.record_id}'
