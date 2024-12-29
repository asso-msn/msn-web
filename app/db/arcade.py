from . import Column, Table, column, relation


class Arcade(Table):
    slug: Column[str] = column(primary_key=True)
    name: Column[str]
    longitude: Column[float]
    latitude: Column[float]
    street_address: Column[str]
    city: Column[str]
    region: Column[str]

    games = relation(
        "ArcadeGame", back_populates="arcade", cascade="all, delete-orphan"
    )
