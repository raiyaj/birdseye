from __future__ import annotations

import logging
from typing import Dict, List

from . import models

logger = logging.getLogger(__package__)


class Query(models.OpendatasoftCore):
  def __init__(self, *args, **kwargs) -> None:
    self._source = kwargs['source']
    super().__init__(*args, **kwargs)

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
  
  def facet(self):
    pass

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

  def refine(self):
    pass

  def exclude(self):
    pass


class CatalogQuery(Query):
  """Interface for the Catalog API"""

  def _get_path_parts(self, endpoint: str) -> List[str]:
    if endpoint == 'search':
      return ['datasets']
    return []

  def dataset(self, dataset_id: str) -> DatasetQuery:
    query_args = [self.base_url, self.timezone, self.session]
    return DatasetQuery(*query_args, dataset_id=dataset_id, source=self._source)


class DatasetQuery(Query):
  """Interface for the Dataset API"""

  def __init__(self, *args, **kwargs) -> None:
    self._dataset_id = kwargs.pop('dataset_id')
    super().__init__(*args, **kwargs)

  def _get_path_parts(self, endpoint: str) -> List[str]:
    path_parts = ['datasets', self._dataset_id]
    if endpoint == 'search':
      path_parts.append('records')
    return path_parts
