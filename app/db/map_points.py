import enum
from enum import Enum

from . import Column, Id, Table, column


class MapPoint(Table, Id):
    class Type(Enum):
        City = enum.auto()
        Department = enum.auto()
        Country = enum.auto()

    name: Column[str] = column(unique=True)
    type: Column[Type]
    longitude: Column[float]
    latitude: Column[float]

    def __str__(self):
        return self.name
