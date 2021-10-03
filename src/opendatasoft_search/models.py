from datetime import datetime
import logging
import requests
from typing import Any, Dict, NamedTuple
import urllib.parse

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
    logger.info(f'GET {url} {response.status_code}')
    return response.json()


class Dataset(NamedTuple):
  pass


class Record(NamedTuple):
  id: str
  timestamp: datetime
  size: int
  fields: Dict


class Facet(NamedTuple):
  pass


class Metadata(NamedTuple):
  pass
