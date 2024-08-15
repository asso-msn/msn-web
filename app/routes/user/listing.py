from app import app
from app.db import User
from app.paging import Pager


@app.get("/users/")
def users():
    with app.session() as s:
        query = s.query(User).filter_by(hide_in_list=False)
        pager = Pager.get_from_request(query, per_page=20, total=query.count())
        return app.render("users/listing", pager=pager)
