import typing as t


class Pager:
    items_total: int = 0
    index: int = 0
    pages_total: int = 0
    pages_current: int = 1

    def __init__(
        self,
        iterable: t.Iterable,
        total: int = None,
        page: int = 1,
        per_page: int = 10,
    ):
        self.iterable = iterable
        self.items_total = total or len(iterable)
        self.per_page = per_page
        self.pages_current = page
        self.pages_total = (self.items_total // self.per_page) + bool(
            self.items_total % self.per_page
        )
        self.index = self.per_page * (self.pages_current - 1)

    def get_page(self, page: int):
        cls = type(self)
        return cls(
            self.iterable,
            total=self.items_total,
            page=page,
            per_page=self.per_page,
        )

    @property
    def has_next(self) -> bool:
        return self.pages_current < self.pages_total

    @property
    def has_prev(self) -> bool:
        return self.pages_current > 1

    @property
    def next(self):
        if not self.has_next:
            return None
        return self.pages_current + 1

    @property
    def prev(self):
        if not self.has_prev:
            return None
        return self.pages_current - 1

    @property
    def items(self):
        start_pos = self.per_page * (self.pages_current - 1)
        end_pos = start_pos + self.per_page
        return self.iterable[start_pos:end_pos]

    @property
    def index_in_page(self) -> int:
        return self.index - (self.per_page * (self.pages_current - 1))

    @property
    def pages(self) -> t.Iterator[int]:
        return range(1, self.pages_total + 1)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.items[self.index_in_page]
        except IndexError:
            raise StopIteration
        self.index += 1
        return result

    @classmethod
    def get_from_request(cls, *args, **kwargs):
        import flask

        page = flask.request.args.get("page", 1, type=int)
        return cls(*args, page=page, **kwargs)

    @classmethod
    def get_url(cls, page):
        import flask
        from furl import furl

        url = furl(flask.request.url)
        url.args["page"] = page
        return url.url
