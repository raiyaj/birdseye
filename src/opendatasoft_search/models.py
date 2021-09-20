import logging
import requests
from typing import Any

logger = logging.getLogger(__package__)


class OpendatasoftCore:
  def __init__(
    self, base_url: str, session: requests.Session, source: str
  ) -> None:
    self.base_url = base_url
    self.session = session
    self.source = source

  @property
  def api_url(self) -> str:
    return f'{self.base_url}/api/v2/{self.source}'

  def build_query_parameters(self, **kwargs: Any) -> str:
    """
    Build query parameter string. 
    :param **kwargs: Parameter names and values. If a value is a list, appends a
      separate query parameter for each item.
    """
    parameters = []
    for key, value in kwargs.items():
      if value is None:
        continue
      if not isinstance(value, list):
        value = [value]
      parameters.extend(f'&{key}={item}' for item in value)

    if parameters:
      parameters[0] = '?' + parameters[0][1:]

    return ''.join(parameters)

  def build_url(self, *args: str) -> str:
    return '/'.join([self.api_url, *args])

  def get(self, url: str) -> requests.Response:
    response = self.session.get(url)
    logger.info(f'GET {url} {response.status_code}')
    return response
