"""API interface"""

import requests

from . import auth


class Opendatasoft:
  """Core Opendatasoft object; stores session info."""

  def __init__(
    self,
    data_portal_id: str = 'data',
    base_url: str = None,
    api_key: str = None,
    session: requests.Session = None,
    timezone: str = 'UTC'
  ) -> None:
    """
    :param data_portal_id: Id used to create the base API URL, eg.
      {data_portal_id}.opendatasoft.com. Default: `data`
    :param base_url: Custom domain to override the base API URL created by
      `data_portal_id`
    :param api_key: API key for restricted datasets
    :param session: A session object with which to make API calls
    :param timezone: Default timezone for datetime fields in queries and
      responses. Default: `UTC`
    """
    if base_url:
      self.base_url = base_url.strip('/')
      self.data_portal_id = None
    else:
      self.base_url = f'{data_portal_id}.opendatasoft.com'
      self.data_portal_id = data_portal_id
    self.base_url += '/api/v2'
  
    self.session = session or requests.Session()
    if api_key:
      self.session.auth = auth.TokenAuth(api_key)

    self.timezone = timezone
