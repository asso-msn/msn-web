from app import app, data, pdf


def get_games_list():
    series = data.load("games")
    return series.keys()


def get_game(game_id):
    series = data.load("games")
    return series[game_id]


def build_html(game):
    return app.render("game_info_poster", series=game, lang="fr")


def save_pdf(game, dest):
    html = build_html(game)
    pdf.from_html(html, dest)
