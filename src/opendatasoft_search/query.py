from __future__ import annotations

import logging
from typing import Any, Dict, List

from . import models

logger = logging.getLogger(__package__)


class Query(models.OpendatasoftCore):
  def __init__(self, *args, **kwargs):
    self.timezone = kwargs.pop('timezone')
    super().__init__(*args, **kwargs)

    self._select = []
    self._where = []
    self._group_by = []
    self._order_by = []
    self._refine = []
    self._exclude = []

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
      self.build_query_parameters(
        refine=self._refine,
        exclude=self._exclude,
        offset=offset,
        limit=limit,
        timezone=timezone or self.timezone
      )
    )
    response = self.get(url)
    return response.json()

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
      self.build_query_parameters(
        limit=limit,
        timezone=timezone or self.timezone
      )
    )
    response = self.get(url)
    return response.json()

  def export(self):
    pass

  def lookup(self):
    pass
  
  def facets(self):
    """
    Enumerate facets.
    """

  def metadata_template(self):
    pass

  ## ODSQL filters ##

  def select(self):
    pass

  def where(self):
    pass

  def group_by(self):
    pass

  def order_by(self):
    pass

  ## Facet filters ##

  def refine(self, **kwargs: Any) -> Query:
    """
    Limit results by refining on the given facet values, ANDed together.
    :param **kwargs: Facet lookup parameters.
    """
    self._refine.extend(
      f'{facet_name}:{facet_value}'
      for facet_name, facet_value in kwargs.items()
    )
    return self

  def exclude(self, **kwargs: Any) -> Query:
    """
    Limit results by excluding the given facet values, ANDed together.
    :param **kwargs: Facet lookup parameters, compatible with the `in` lookup
      format. 
    """
    for facet_name, facet_value in kwargs.items():
      if facet_name.endswith('__in'):
        self._exclude.extend(
          f'{facet_name[:-4]}:{item}' for item in facet_value
        )
      else:
        self._exclude.append(f'{facet_name}:{facet_value}')
    return self


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

  def __init__(self, *args, **kwargs) -> None:
    self.dataset_id = kwargs.pop('dataset_id')
    super().__init__(*args, **kwargs)

  def _get_path_parts(self, endpoint: str) -> List[str]:
    path_parts = ['datasets', self.dataset_id]
    if endpoint == 'search':
      path_parts.append('records')
    return path_parts
