from __future__ import annotations

from copy import deepcopy
import logging
import re
from typing import Any, Dict, Iterable, List, NewType, Union

from . import models

logger = logging.getLogger(__package__)

ODSQL = NewType('ODSQL', str)


class Lookup:
  CONTAINS = '__contains'
  ESCAPE = '__escape'
  GT = '__gt'
  GTE = '__gte'
  LT = '__lt'
  LTE = '__lte'
  IN = '__in'
  INRANGE = '__inrange'
  ISNULL = '__isnull'

  @staticmethod
  def trim(parameter: str) -> str:
    """
    Trim lookup from a given parameter, assuming it ends with a valid lookup.
    """
    return re.search('(.+)__[a-z]+$', parameter).group(1)


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
  def odsql(self):
    """
    """
    filters = []
    for key, value in self.kwargs.items():
      filters.append(f'{key}={value}')
    return 'and'.join(filters)


class Query(models.OpendatasoftCore):
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
  ) -> Dict:
    """
    Search datasets.
    :param offset: Index of the first item to return. Default: 0
    :param limit: Number of items to return. Default: 0
    :param timezone: Timezone applied to datetime fields in queries and
      responses. Default: `UTC`
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

  def aggregate(self, limit: str = None, timezone: str = None) -> Dict:
    """
    Aggregate datasets.
    :param limit: Number of items to return. Default: 0
    :param timezone: Timezone applied to datetime fields in queries and
      responses. Default: `UTC`
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
    """
    Enumerate facets.
    """

  def metadata(self):
    pass

  ## ODSQL filters ##

  def select(self):
    pass

  def where(
    self,
    contains: Union[str, Iterable[str]] = [],
    *args: Union[ODSQL, Q],
    **kwargs: Any
  ) -> Query:
    """
    Filter rows with a combination of `where` expressions.
    :param contains:
    :param args:
    :param kwargs:
    """
    if not isinstance(contains, list):
      contains = [contains]
    filters = (
      arg.odsql
      if isinstance(arg, Q)
      else arg
      for arg in [*contains, *args, Q(**kwargs)]
    )
    self._where.append('and'.join(filters))
    return self._clone()

  def group_by(self):
    pass

  def order_by(self):
    pass

  ## Facet filters ##

  def refine(self, **kwargs: Any) -> Query:
    """
    Limit results by refining on the given facet values, ANDed together.
    :param **kwargs: Facet names and values.
    """
    self._refine.extend(
      f'{key}:{value}'
      for key, value in kwargs.items()
    )
    return self._clone()

  def exclude(self, **kwargs: Any) -> Query:
    """
    Limit results by excluding the given facet values, ANDed together.
    :param **kwargs: Facet names and values, compatible with `in` lookups.
    """
    for key, value in kwargs.items():
      if key.endswith(Lookup.IN):
        self._exclude.extend(
          f'{Lookup.trim(key)}:{item}' for item in value
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
