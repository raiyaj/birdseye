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
Field = NewType('Field', str)
Geometry = NewType('Geometry', str)
String = NewType('String', str)

def date(date: str) -> Date:
  """
  Date literal
  :param date: An ISO 8601 or YYYY/MM/DD formatted date
  """
  return f"date'{date}'"

def field(field: str) -> Field:
  return (
    f'`{field}`'
    if field in KEYWORDS or field.isdigit()
    else field
  )

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


## Filter functions (use with the `inarea` field lookup) ##

def circle(
  center: Geometry,
  radius: Union[int, float],
  unit: str = Unit.METERS
) -> str:
  """
  Limit results to a geographical area defined by a circle.
  :param center: Center of the circle 
  :param radius: Radius of the circle
  :param unit: Radius units
  """
  return f'distance({{}}, {center}, {radius}{unit})'

def geometry(area: Geometry, mode: str = Set.WITHIN) -> str:
  """
  Limit results to a geographical area, based on a given set mode (for use with
  a geo_shape field).
  :param area: Geographical area
  :param mode: Set mode that defines how the geo_shape field is compared with
    the geographical area
  """
  return f'geometry({{}}, {area}, {mode})'

def polygon(area: Geometry) -> str:
  """
  Limit results to a geographical area (for use with a geo_point field).
  :param area: Geographical area
  """
  return f'polygon({{}}, {area})'


## Ranges ##

def drange():
  pass

def srange():
  pass
