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
  :param string: A string
  """
  # If string is a date or geometry literal, return it unchanged
  if re.match(r"^date'.*'$", string) or re.match(r"^geom'.*'$", string):
    return string
  return f'"{string}"'


## Enums ##

class Set:
  DISJOINT = 'disjoint'
  INTERSECTS = 'intersects'
  WITHIN = 'within'

class Unit:
  MILES = 'mi'
  YARDS = 'yd'
  FEET = 'ft'
  METERS = 'm'
  KILOMETERS = 'km'
  CENTIMETERS = 'cm'
  MILLIMETERS = 'mm'


## Scalar functions ##


## Filter functions ##
## Use with the `inarea` lookup to filter on whether a field is within a
## geographical area.

def circle(
  center: Geometry,
  radius: Union[int, float],
  unit: str = Unit.METERS
) -> str:
  """
  :param center: Center of the circle 
  :param radius: Radius of the circle
  :param unit: Radius units
  """
  return f'distance({{}}, {center}, {radius}{unit})'

def geometry(area: Geometry, mode: str = Set.WITHIN) -> str:
  """
  For comparison with fields of type geo_shape
  :param area: Geographical area
  :param mode: Set mode that defines how the geo_shape field is compared with
    the geographical area
  """
  return f'geometry({{}}, {area}, {mode})'

def polygon(area: Geometry) -> str:
  """
  For comparison with fields of type geo_point
  :param area: Geographical area
  """
  return f'polygon({{}}, {area})'


## Ranges ##

def drange():
  pass

def srange():
  pass
