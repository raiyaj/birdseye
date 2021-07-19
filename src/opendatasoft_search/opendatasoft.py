import logging
import requests

from . import auth
from . import models
from . import query

logger = logging.getLogger(__package__)


class Opendatasoft(models.OpendatasoftCore):
  DEFAULT_SUBDOMAIN = 'data'
  VALID_SOURCES = ['catalog', 'monitoring', 'opendatasoft']

  def __init__(
    self,
    subdomain: str = DEFAULT_SUBDOMAIN,
    url: str = None,
    source: str = 'catalog',
    timezone: str = 'UTC',
    session: requests.Session = None,
    api_key: str = None
  ) -> None:
    """
    :param subdomain: Subdomain used to create the base API URL,
      eg. https://{subdomain}.opendatasoft.com. Default: `data`,
      eg. data.opendatasoft.com (the hub for all public datasets in
      Opendatasoft's network)
    :param url: Custom base API URL
    :param source: Data source to search. Either `catalog`, `monitoring` or
      `opendatasoft`. Default: `catalog`
    :param timezone: Default timezone applied to datetime fields in queries and
      responses. Default: `UTC`
    :param session: A session object with which to make API calls
    :param api_key: Opendatasoft API key for accessing private datasets
    """
    if not subdomain and not url:
      raise ValueError('`subdomain` and `url` cannot both be empty.')
    if source not in self.VALID_SOURCES:
      raise ValueError(f'{source} is not a valid data source.')
    if (
      source == 'opendatasoft'
      and (url or subdomain != self.DEFAULT_SUBDOMAIN)
    ):
      logger.warn(
        f'Using a custom base API URL with the `opendatasoft` data source; '
        'results will match those of the default base URL.'
      )

    api_url = (
      f"{url.strip('/') if url else f'https://{subdomain}.opendatasoft.com'}"
      f'/api/v2/{source}'
    )
    super().__init__(api_url, session or requests.Session(), timezone)
    if api_key:
      self.login(api_key=api_key)

  def login(self, api_key: str) -> None:
    """
    Login to an Opendatasoft domain to access private datasets.
    :param api_key: API key
    """
    self.session.auth = auth.TokenAuth(api_key=api_key)

  def query(self, dataset_id: str = None) -> query.QuerySet:
    """
    Query datasets or records sourced in an Opendatasoft domain.
    :param dataset_id: Id of a dataset in which to query records
    """
    core_args = [self.api_url, self.session, self.timezone]
    if dataset_id:
      return query.Dataset(*core_args, dataset_id=dataset_id)
    return query.Catalog(*core_args)
