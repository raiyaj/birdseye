import logging
import requests
from typing import Any

logger = logging.getLogger(__package__)


class OpendatasoftCore:
  def __init__(
    self, base_url: str, timezone: str, session: requests.Session, source: str
  ) -> None:
    self.base_url = base_url
    self.timezone = timezone
    self.session = session
    self.source = source

  @property
  def api_url(self) -> str:
    return f'{self.base_url}/api/v2/{self.source}'

  def build_query_parameters(self, **kwargs: Any) -> str:
    parameters = [
      f'&{key}={str(value)}'
      for key, value in kwargs.items()
      if value is not None
    ]
    if parameters:
      parameters[0] = '?' + parameters[0][1:]
    return ''.join(parameters)

  def build_url(self, *args: str) -> str:
    return '/'.join([self.api_url, *args])

  def get(self, url: str) -> requests.Response:
    response = self.session.get(url)
    logger.info(f'GET {url} {response.status_code}')
    return response
