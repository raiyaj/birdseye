import json
from typing import NewType, Union


## Literals ##

Date = NewType('Date', str)

def date(date: str) -> Date:
  """
  :param date: An ISO 8601 or YYYY/MM/DD formatted date
  """
  return f"date'{date}'"


Geometry = NewType('Geometry', str)

def geom(geometry: Union[str, dict]) -> Geometry:
  """
  :param geometry: A WKT/WKB or GeoJSON geometry expression
  """
  return f"geom'{geometry if isinstance(geometry, str) else json.dumps(geometry)}'"


## ##
def range(
  start: Union[int, Date],
  end: Union[int, Date],
  notation: str = '[]'
) -> str:
  """
  """
  return f'{notation[0]}{start}..{end}{notation[1]}'
