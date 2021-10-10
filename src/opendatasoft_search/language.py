import json
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

def date(date: str) -> Date:
  """
  :param date: An ISO 8601 or YYYY/MM/DD formatted date
  """
  return f"date'{date}'"

def geom(geometry: Union[str, dict]) -> Geometry:
  """
  :param geometry: A WKT/WKB or GeoJSON geometry expression
  """
  geometry = json.dumps(geometry) if isinstance(geometry, dict) else geometry
  return f"geom'{geometry}'"


## Scalar functions ##


## Filter functions ##

def interval(
  start: Union[int, Date],
  end: Union[int, Date],
  notation: str = '[]'
) -> str:
  """
  """
  return f'{notation[0]}{start}..{end}{notation[1]}'
