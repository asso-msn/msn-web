import csv
import logging
from dataclasses import dataclass
from io import StringIO

import requests
from pydantic import BaseModel, Field

from app import ROOT_DIR, app
from app.db import MapPoint

STATIC_DATA_DIR = ROOT_DIR / "static" / "data"


def populate():
    with app.session() as s:
        if (
            not s.query(MapPoint)
            .filter_by(type=MapPoint.Type.Department)
            .count()
        ):
            populate_departments()
    create_regions_topology()


class GeoAPIDepartment(BaseModel):
    name: str = Field(validation_alias="nom")
    code: str


class DataGouvDepartmentGPS(BaseModel):
    code: str  # = Field(validation_alias="Departement")
    north: float  # = Field(validation_alias="Latitude la plus au nord")
    south: float  # = Field(validation_alias="Latitude la plus au sud")
    west: float  # = Field(validation_alias="Longitude la plus à l'ouest")
    east: float  # = Field(validation_alias="Longitude la plus à l'est")

    @property
    def gps(self):
        return [
            (self.north + self.south) / 2,
            (self.west + self.east) / 2,
        ]


@dataclass
class Department:
    name: str
    code: str
    gps: list[float]

    @property
    def display_name(self):
        return f"{self.code} - {self.name}"

    def __str__(self):
        return self.display_name


def get_departments_from_api():
    DEPARTMENTS_LIST_URL = "https://geo.api.gouv.fr/departements"
    DEPARTMENTS_GPS_URL = "https://www.data.gouv.fr/fr/datasets/r/de8e4904-45f6-4a38-b3fc-efb03f8e75bf"  # noqa

    logging.info("Fetching departments from API")
    departments_list = requests.get(DEPARTMENTS_LIST_URL)
    departments_list.raise_for_status()
    logging.info("Done")
    departments_list = [
        GeoAPIDepartment(**entry) for entry in departments_list.json()
    ]

    logging.info("Fetching departments GPS from data gouv dataset")
    departments_gps = requests.get(DEPARTMENTS_GPS_URL)
    departments_gps.raise_for_status()
    logging.info("Done")
    departments_gps = csv.reader(StringIO(departments_gps.text))
    next(departments_gps)  # skip header
    departments_gps = [
        DataGouvDepartmentGPS(
            code=row[0],
            north=float(row[1]),
            south=float(row[2]),
            west=float(row[3]),
            east=float(row[4]),
        )
        for row in departments_gps
    ]
    departments_gps_by_code = {entry.code: entry for entry in departments_gps}

    return [
        Department(
            name=department.name,
            code=department.code,
            gps=departments_gps_by_code[department.code].gps,
        )
        for department in departments_list
        if department.code in departments_gps_by_code
    ]


def create_regions_topology(force=False):
    PATH = STATIC_DATA_DIR / "regions.topojson"
    TOPOLOGY_URL = "https://www.data.gouv.fr/fr/datasets/r/92f37c92-3aae-452c-8af1-c77e6dd590e5"  # noqa

    if PATH.exists() and not force:
        return

    regions = requests.get(TOPOLOGY_URL)
    regions.raise_for_status()

    PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PATH, "w") as f:
        f.write(regions.text)


def populate_departments():
    created = []
    for department in get_departments_from_api():
        with app.session() as s:
            if s.greate(
                MapPoint,
                filter={"name": department.display_name},
                defaults={
                    "type": MapPoint.Type.Department,
                    "longitude": department.gps[1],
                    "latitude": department.gps[0],
                },
            ).created:
                created.append(department)
                logging.info(f"Created {department}")
                s.commit()
    return created
