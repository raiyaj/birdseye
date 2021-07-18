import logging
import requests

from . import auth
from . import models
from . import query

logger = logging.getLogger(__package__)


class Opendatasoft(models.OpendatasoftCore):
  STR_CATALOG = 'catalog'
  STR_DATA = 'data'
  STR_MONITORING = 'monitoring'
  STR_OPENDATASOFT = 'opendatasoft'
  VALID_SOURCES = [STR_CATALOG, STR_MONITORING, STR_OPENDATASOFT]

  def __init__(
    self,
    subdomain: str = STR_DATA,
    url: str = None,
    source: str = STR_CATALOG,
    session: requests.Session = None,
  ) -> None:
    """
    :param subdomain: Supdomain used to create the base API URL, eg.
      {subdomain}.opendatasoft.com. Default: `data`, eg. data.opendatasoft.com
      (the hub for all public datasets in Opendatasoft's network)
    :param url: Custom base API URL
    :param source: Data source to search. Either `catalog`, `monitoring` or
      `opendatasoft`. Default: `catalog`
    :param session: A session object with which to make API calls
    """
    if not subdomain and not url:
      raise ValueError('`subdomain` and `url` cannot both be empty.')
    if source not in self.VALID_SOURCES:
      raise ValueError(f'{source} is not a valid data source.')
    if source == self.STR_OPENDATASOFT and url or subdomain != self.STR_DATA:
      logger.warn(
        f'Using a custom base API URL with the {self.STR_OPENDATASOFT} data '
        'source; results will match those of the default base URL.'
      )

    opendatasoft_url = (
      url.strip('/') if url else f'{subdomain}.opendatasoft.com'
      f'/api/v2/{source}'
    )
    super().__init__(opendatasoft_url, session or requests.Session())

  def login(self, api_key: str) -> None:
    """
    Login to an Opendatasoft domain to access private datasets.
    :param api_key: API key
    """
    self.session.auth = auth.TokenAuth(api_key=api_key)

  def query(self, dataset_id: str = None) -> query.QuerySet:
    """
    Query datasets (or records, if given a `dataset_id`) sourced in the
    Opendatasoft domain
    :param dataset_id: Id of a dataset in which to query records
    """
    opendatasoft_args = [self.opendatasoft_url, self.session]
    if dataset_id:
      return query.Dataset(*opendatasoft_args, dataset_id=dataset_id)
    return query.Catalog(*opendatasoft_args)
