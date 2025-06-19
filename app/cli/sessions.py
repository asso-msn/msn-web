from app import app


@app.cli.group()
def sessions():
    pass


@sessions.command()
def clear():
    with app.session() as s:
        s.query(app.session_interface.sql_session_model).delete()
        s.commit()
