import logging
import requests
from typing import Any, List, NamedTuple
import urllib.parse

from . import exceptions
from .language import Date

logger = logging.getLogger(__name__)


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
      if value not in ['', None]
    }
    return f'?{urllib.parse.urlencode(parameters, doseq=True)}'

  def build_url(self, *args: str) -> str:
    return '/'.join([self.api_url, *args])

  def get(self, url: str) -> requests.Response:
    try:
      response = self.session.get(url)
    except (
      requests.exceptions.ConnectionError,
      requests.exceptions.Timeout
    ) as ex:
      raise exceptions.ConnectionError(ex)
    except requests.exceptions.RequestException as ex:
      raise exceptions.TransportError(ex)

    logger.info(f'GET {urllib.parse.unquote_plus(url)} {response.status_code}')
    if response.status_code != 200:
      raise exceptions.error_for(response)

    return response.json()


class Dataset(NamedTuple):
  attachments: List[dict]
  data_visible: bool
  dataset_id: str
  dataset_uid: str
  features: List
  fields: List[dict]
  has_records: bool
  metas: dict
  visibility: str

  def __str__(self) -> str:
    return f'<Dataset: {self.dataset_id}>'


class Record(NamedTuple):
  id: str
  fields: dict
  size: int
  timestamp: Date

  def __str__(self) -> str:
    return f'<Record: {self.id}>'


class Facet(NamedTuple):
  pass


class Attachment(NamedTuple):
  pass
