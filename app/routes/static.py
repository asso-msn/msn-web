from app import app


@app.route("/about/")
def about():
    og_data = {
        "description": "Tout savoir sur Make Some Noise",
    }
    return app.render("about", title="L'association", og_data=og_data)
