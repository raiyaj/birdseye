import requests


class TokenAuth(requests.AuthBase):
  """API key authentication"""

  def __init__(self, api_key: str) -> None:
    self.api_key = api_key
  
  def __call__(self, request: requests.Request) -> requests.Request:
    request.headers['Authorization'] = f'Apikey {self.api_key}'
    return request
