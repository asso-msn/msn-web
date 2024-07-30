from app import app, data


@app.route("/about/")
def about():
    # return app.render("page", content=data.markdown("about"))
    return app.render("pages/about")
