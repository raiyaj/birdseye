"""API interface"""

import logging
import requests

from . import auth

logger = logging.getLogger(__package__)


class Opendatasoft:
  """Core Opendatasoft object; stores session info"""

  STR_CATALOG = 'catalog'
  STR_DATA = 'data'
  STR_MONITORING = 'monitoring'
  STR_OPENDATASOFT = 'opendatasoft'
  VALID_SOURCES = [STR_CATALOG, STR_MONITORING, STR_OPENDATASOFT]

  def __init__(
    self,
    data_portal_id: str = STR_DATA,
    base_url: str = None,
    source: str = STR_CATALOG,
    api_key: str = None,
    session: requests.Session = None,
    timezone: str = 'UTC'
  ) -> None:
    """
    :param data_portal_id: Id used to create the base API URL, eg.
      {data_portal_id}.opendatasoft.com. Default: `data`, eg.
      data.opendatasoft.com (the hub for all public datasets in Opendatasoft's
      network)
    :param base_url: Custom domain to override the base API URL created by
      `data_portal_id`
    :param source: Data source to search. Either `catalog`, `monitoring` or
      `opendatasoft`. Default: `catalog`
    :param api_key: API key for restricted datasets
    :param session: A session object with which to make API calls
    :param timezone: Default timezone for datetime fields in queries and
      responses. Default: `UTC`
    """
    if not base_url and not data_portal_id:
      raise ValueError('base_url and data_portal_id cannot both be empty.')
    self.base_url = (
      base_url.strip('/') if base_url else f'{data_portal_id}.opendatasoft.com'
      '/api/v2'
    )
    self.data_portal_id = None if base_url else data_portal_id

    if source not in self.VALID_SOURCES:
      raise ValueError(f'{source} is not a valid data source.')
    elif (
      source == self.STR_OPENDATASOFT
      and base_url
      or data_portal_id != self.STR_DATA
    ):
      logger.warn(
        f'Using a custom base API URL with the {self.STR_OPENDATASOFT} data '
        'source; results will match those of the default base URL.'
      )
    self.source = source      

    self.session = session or requests.Session()
    if api_key:
      self.session.auth = auth.TokenAuth(api_key=api_key)

    self.timezone = timezone
