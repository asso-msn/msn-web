import dataclasses
import enum
from dataclasses import dataclass
from datetime import datetime

import arrow

from app import config, data


@dataclass
class Event:
    """
    File format: data/events/YYYY-MM-DD-template-name.yml
    """

    class Type(enum.Enum):
        MEETUP = enum.auto()
        CONVENTION = enum.auto()

        def __str__(self):
            return self.name.lower()

    name: str
    dates: list[str] = None
    start_time: int = None
    end_time: int = None
    nightly: bool = False
    template: str = None
    type: Type = None  # TODO: Load from string
    hero: str = None
    location: str = None
    description: str = None
    games: list[str] = dataclasses.field(default_factory=list)
    links: dict[str, str] = dataclasses.field(default_factory=dict)

    templates = data.load("events_templates")

    @classmethod
    def from_data_file(cls, key, value):
        value = value or {}
        date = "-".join(key.split("-")[:3])
        date = datetime.fromisoformat(date)
        template = key.split("-")[3]
        name = " ".join(key.split("-")[4:]).replace("-", " ").title()
        value.setdefault("name", name)
        value.setdefault("dates", [date])
        value.setdefault("template", template)
        return cls(**value)

    @property
    def date(self):
        if not self.dates:
            return None
        return self.dates[0]

    @property
    def time_range(self):
        def display(value):
            hours = value // 100
            minutes = value % 100
            if minutes:
                return f"{hours}h{minutes:02}"
            return f"{hours}h"

        if not self.start_time:
            return None
        if not self.end_time:
            return display(self.start_time)
        return f"{display(self.start_time)} - {display(self.end_time)}"

    @property
    def arrow(self):
        if not self.date:
            return None
        return arrow.get(self.date)

    @property
    def relative_time(self):
        return (
            self.arrow and self.arrow.humanize(locale=config.LANG).capitalize()
        )

    @property
    def day_name(self):
        return self.arrow and self.arrow.format("dddd", locale=config.LANG)

    @property
    def day_number(self):
        if len(self.dates) > 1:
            start = self.arrow.format("D")
            end = arrow.get(self.dates[-1]).format("D")
            return f"{start} - {end}"

        return self.arrow and self.arrow.format("D")

    @property
    def days_span(self):
        return len(self.dates) - 1

    @property
    def month(self):
        return self.arrow and self.arrow.format("MMM", locale=config.LANG)

    def load_template(self):
        template = self.templates.get(self.template)
        if template:
            for key, value in template.items():
                if not getattr(self, key):
                    setattr(self, key, value)

    @property
    def is_past(self):
        return self.arrow and self.arrow < arrow.now()

    def __post_init__(self):
        self.load_template()


def get_events():
    results = [
        Event.from_data_file(key, event)
        for key, event in data.load("events", flat=True).items()
    ]

    results.sort(key=lambda x: x.arrow)
    return results


def get_future_events():
    results = get_events()
    results = [event for event in results if not event.is_past]
    return results


def get_past_events():
    results = get_events()
    results = [event for event in results if event.is_past]
    results.sort(key=lambda x: x.arrow, reverse=True)
    return results
