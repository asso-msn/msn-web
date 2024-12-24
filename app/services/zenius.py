from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Arcade:
    id: int
    name: str
    longitude: float
    latitude: float
    address: str
    games: list[str]

    @property
    def street_address(self) -> str:
        return self.address.splitlines()[0]

    @property
    def city(self) -> str:
        return self.address.splitlines()[1]

    @property
    def region(self) -> str:
        return self.address.splitlines()[2].split(", ")[0]

    @property
    def zip_code(self) -> str:
        return self.address.splitlines()[2].split(", ")[1]


def get_arcade(id: int) -> Arcade:
    url = f"https://zenius-i-vanisher.com/v5.2/arcade.php?id={id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    arcade_name = soup.find("h1").text

    map_container = soup.find("div", id="map")
    longitude, latitude = map_container["data-lng"], map_container["data-lat"]

    games_container = soup.find("div", id="arcade-games")
    games = []
    for tr in games_container.find_all("tr"):
        if tr.find("th"):
            continue
        game_name = tr.css.select(".top strong")[0].text
        games.append(game_name)

    arcade_summary_container = soup.find("div", id="arcade-summary")
    address = arcade_summary_container.find("p").text

    return Arcade(
        id=id,
        name=arcade_name,
        longitude=longitude,
        latitude=latitude,
        address=address,
        games=games,
    )
