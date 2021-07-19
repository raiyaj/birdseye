from typing import Dict, List

from . import models


class Q:
  """ODSQL query"""
  pass


class QuerySet(models.OpendatasoftCore):
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

  def _get_path_parts(self, endpoint: str) -> List[str]:
    return []

  ## API endpoints ##

  def search(
    self,
    offset: int = 0,
    limit: int = 10,
    include_app_metas: bool = False,
    timezone: str = None
  ) -> Dict:
    """
    Search datasets.
    :param offset: Index of the first item to return. Default: 0
    :param limit: Number of items to return. Default: 0
    :param include_app_metas: Explicitly request application metadata for each
      dataset. Default: False
    :param timezone: Timezone applied to datetime fields in queries and
      responses. Default: `UTC`
    """
    url = self.build_url(
      'datasets',
      *self._get_path_parts(endpoint='search'),
      self.build_query_parameters(
        offset=offset,
        limit=limit,
        include_app_metas=include_app_metas,
        timezone=timezone or self.timezone
      )
    )
    response = self.get(url)
    return response.json()

  def aggregate(self):
    pass

  def export(self):
    pass

  def lookup(self):
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


class Dataset(QuerySet):
  def __init__(self, *args, **kwargs) -> None:
    self.dataset_id = kwargs.pop('dataset_id')
    super().__init__(*args, **kwargs)

  def _get_path_parts(self, endpoint: str) -> List[str]:
    if endpoint == 'search':
      return [self.dataset_id, 'records']


class Catalog(QuerySet):
  ## API endpoints ##
  def metadata_templates(self):
    pass

  def facets(self):
    pass
