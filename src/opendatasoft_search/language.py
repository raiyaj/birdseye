import json
import re
from typing import NewType, Union


KEYWORDS = [
  'and',
  'as',
  'asc',
  'avg',
  'by',
  'count',
  'date_format',
  'day',
  'dayofweek',
  'desc',
  'equi',
  'false',
  'group',
  'hour',
  'or',
  'limit',
  'lower',
  'max',
  'millisecond',
  'min',
  'minute',
  'month',
  'not',
  'null',
  'quarter',
  'range',
  'second',
  'select',
  'sum',
  'top',
  'true',
  'upper',
  'where',
  'year'
]


## Literals ##

Date = NewType('Date', str)
Geometry = NewType('Geometry', str)
String = NewType('String', str)

def date(date: str) -> Date:
  """
  Date literal
  :param date: An ISO 8601 or YYYY/MM/DD formatted date
  """
  return f"date'{date}'"

def geom(geometry: Union[str, dict]) -> Geometry:
  """
  Geometry literal
  :param geometry: A WKT/WKB or GeoJSON geometry expression
  """
  geometry = json.dumps(geometry) if isinstance(geometry, dict) else geometry
  return f"geom'{geometry}'"

def str(string: str) -> String:
  """
  String literal
  :param string: String
  """
  # If string is a Date or Geometry literal, return unchanged
  if re.match(r"^date'.*'$", string) or re.match(r"^geom'.*'$", string):
    return string
  return f'"{string}"'


## Scalar functions ##


## Filter functions ##

def range():
  pass
