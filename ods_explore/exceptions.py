# This file is based heavily on the exceptions module in github3.py, by @sigmavirus24.
# https://github.com/sigmavirus24/github3.py/blob/main/src/github3/exceptions.py


class OpendatasoftException(Exception):
  """Base exception class"""
  pass


class TransportError(OpendatasoftException):
  """Catch-all class for exceptions stemming from requests"""
  pass


class ConnectionError(TransportError):
  """Exception for errors in connecting to Opendatasoft"""
  pass


class ResponseError(OpendatasoftException):
  """Base class for exceptions stemming from Opendatasoft responses"""
  
  def __init__(self, response):
    self.status = response.status_code
    json = response.json()
    self.error = json.get('error_code')
    self.message = json.get('message')

  def __str__(self):
    return f'{self.status} {self.error}. {self.message}'


class BadRequestError(ResponseError):
  """Exception for 400 responses."""
  pass


class UnauthorizedError(ResponseError):
  """Exception for 401 responses."""
  pass


class NotFoundError(ResponseError):
  """Exception for 404 responses."""
  pass


class ClientError(ResponseError):
  """Catch-all exception for 4xx responses."""
  pass


class ServerError(ResponseError):
  """Catch-all exception for 5xx responses."""
  pass


error_classes = {
  400: BadRequestError,
  401: UnauthorizedError,
  404: NotFoundError
}

def error_for(response):
  klass = error_classes.get(response.status_code)
  if klass is None:
    if 400 <= response.status_code < 500:
      klass = ClientError
    if 500 <= response.status_code < 600:
      klass = ServerError
  return klass(response)
