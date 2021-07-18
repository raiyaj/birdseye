import requests


class OpendatasoftCore:
  def __init__(self, opendatasoft_url: str, session: requests.Session) -> None:
    self.opendatasoft_url = opendatasoft_url
    self.session = session
