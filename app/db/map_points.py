import enum
from enum import Enum

from . import Column, Id, Table, column


class MapPoint(Table, Id):
    class Type(Enum):
        City = enum.auto()
        Region = enum.auto()
        Country = enum.auto()

    name: Column[str] = column(unique=True)
    type: Column[Type]
    longitude: Column[float]
    latitude: Column[float]
