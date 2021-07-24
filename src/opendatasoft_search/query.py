from __future__ import annotations

import logging

from . import models

logger = logging.getLogger(__package__)


class QuerySet(models.OpendatasoftCore):
  def __init__(self, *args, **kwargs) -> None:
    self._source = kwargs.pop('source')
    super().__init__(*args, **kwargs)

  def dataset(self, dataset_id: str) -> Dataset:
    queryset_args = [self.base_url, self.timezone, self.session]
    return Dataset(*queryset_args, source=self._source, dataset_id=dataset_id)

  ## API endpoints ##

  def search(self):
    pass

  def aggregate(self):
    pass

  def export(self):
    pass

  def lookup(self):
    pass
  
  def facet(self):
    pass

  def metadata_template(self):
    pass

#   ## ODSQL filters ##

  def select(self):
    pass

  def where(self):
    pass

  def group_by(self):
    pass

  def order_by(self):
    pass

#   ## Facet filters ##

  def refine(self):
    pass

  def exclude(self):
    pass


class Dataset(QuerySet):
  def __init__(self, *args, **kwargs) -> None:
    self._dataset_id = kwargs.pop('dataset_id')
    super().__init__(*args, **kwargs)

#   def _get_path_parts(self, endpoint: str) -> List[str]:
#     path_parts = ['datasets', self.dataset_id]
#     if endpoint in ['search', 'lookup']:
#       path_parts.append('records')
#     return path_parts
