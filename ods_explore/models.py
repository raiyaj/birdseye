import logging
import requests
from typing import Any, NamedTuple
import urllib.parse

logger = logging.getLogger(__package__)


class OpendatasoftCore:
  """Core API interface"""

  def __init__(
    self, base_url: str, session: requests.Session, resource: str = 'catalog',
  ) -> None:
    self.base_url = base_url
    self.session = session
    self.resource = resource

  @property
  def api_url(self) -> str:
    return f'{self.base_url}/api/v2/{self.resource}'

  def build_querystring(self, **kwargs: Any) -> str:
    """
    Build a url-encoded querystring. 
    :param **kwargs: Parameter keys and values. If a value is a sequence,
      generates a separate query parameter for each element of the value
      sequence.
    """
    parameters = {
      key: value
      for key, value in kwargs.items()
      if value is not None
    }
    return f'?{urllib.parse.urlencode(parameters, doseq=True)}'

  def build_url(self, *args: str) -> str:
    return '/'.join([self.api_url, *args])

  def get(self, url: str) -> requests.Response:
    response = self.session.get(url)
    logger.info(f'GET {urllib.parse.unquote_plus(url)} {response.status_code}')
    return response.json()


class Dataset(NamedTuple):
  pass


class Record(NamedTuple):
  pass


class Facet(NamedTuple):
  pass


class Attachment(NamedTuple):
  pass
