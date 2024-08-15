from app import app
from app.paging import Pager
from app.services import events as service


@app.get("/events/")
def events():
    past_events = service.get_past_events()
    pager = Pager.get_from_request(past_events, per_page=5)
    if pager.current > 1:
        future_events = None
    else:
        future_events = service.get_future_events()
    return app.render(
        "events", future_events=future_events, past_events_pager=pager
    )
