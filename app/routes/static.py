from app import app


@app.route("/about/")
def about():
    return app.render("about")
