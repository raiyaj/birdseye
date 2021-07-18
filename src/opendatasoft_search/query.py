from . import models


class QuerySet(models.OpendatasoftCore):
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

class Dataset(QuerySet):
  def __init__(self, *args, **kwargs) -> None:
    self.dataset_id = kwargs.pop('dataset_id')
    super().__init__(*args, **kwargs)

class Catalog(QuerySet):
  pass
