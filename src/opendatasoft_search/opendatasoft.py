from __future__ import annotations

import logging
import requests

from . import auth
from . import models
from . import query

logger = logging.getLogger(__package__)


class Opendatasoft(models.OpendatasoftCore):
  def __init__(
    self,
    subdomain: str = 'data',
    base_url: str = None,
    timezone: str = 'UTC',
    session: requests.Session = None,
    api_key: str = None
  ) -> None:
    """
    :param subdomain: Subdomain used to create the base API URL,
      eg. https://{subdomain}.opendatasoft.com. Default: `data`, (the hub for
      all public datasets in Opendatasoft's network)
    :param base_url: Custom base API URL
    :param timezone: Default timezone applied to datetime fields in queries and
      responses. Default: `UTC`
    :param session: A session object with which to make API calls
    :param api_key: Opendatasoft API key for accessing private datasets
    """
    if not subdomain and not base_url:
      raise ValueError('`subdomain` and `base_url` cannot both be empty.')
    base_url = (
      base_url.strip('/')
      if base_url
      else f'https://{subdomain}.opendatasoft.com'
    )
    super().__init__(base_url, timezone, session or requests.Session())
    if api_key:
      self.login(api_key)

    queryset_args = [self.base_url, self.timezone, self.session]
    self.catalog = query.QuerySet(*queryset_args, source='catalog')
    self.monitoring = query.QuerySet(*queryset_args, source='monitoring')
    self.opendatasoft = query.QuerySet(*queryset_args, source='opendatasoft')

  def login(self, api_key: str) -> Opendatasoft:
    """Login to an Opendatasoft domain to access private datasets."""
    self.session.auth = auth.TokenAuth(api_key)
    return self
