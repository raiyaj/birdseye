import logging
import requests

logger = logging.getLogger(__package__)


class OpendatasoftCore:
  def __init__(
    self, api_url: str, session: requests.Session, timezone: str
  ) -> None:
    self.api_url = api_url
    self.session = session
    self.timezone = timezone

  def build_query_parameters(self, **kwargs) -> str:
    parameters = [
      f'&{key}={str(value)}'
      for key, value in kwargs.items()
      if value is not None
    ]
    if parameters:
      parameters[0] = parameters[0].replace('&', '?')
    return ''.join(parameters)

  def build_url(self, *args) -> str:
    return '/'.join([self.api_url, *args])

  def get(self, url: str) -> requests.Response:
    response = self.session.get(url=url)
    logger.info(f'GET {url} {response.status_code}')
    return response
