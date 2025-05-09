import click

from app import app, config, data
from app.services import discord, games, gps, igdb, platforms


@app.cli.group()
def seed():
    pass


@seed.command("roles")
def roles_():
    """Create game data files and populate db using existing Discord roles"""
    path = data.resolve("games")
    path.mkdir(exist_ok=True)
    api = discord.API(config.DISCORD_BOT_TOKEN)
    server = api.get_server()
    role_names = [x.name for x in server.roles]
    created = []

    if "=== GAMES ===" in role_names:
        print("Found games section, cutting off previous roles")
        role_names = role_names[role_names.index("=== GAMES ===") + 1 :]
    if "=== Events ===" in role_names:
        print("Found events section, cutting off following roles")
        role_names = role_names[: role_names.index("=== Events ===")]

    game_names = [x.name for x in games.get_all()]
    for name in role_names:
        if name.startswith("-[[ ") and name.endswith(" ]]-"):
            print("Skipping section", name)
            continue

        if name in game_names:
            print("Skipping existing game", name)
            continue

        created.append(name)
        for c in ("!", "/", "'", "@", "."):
            name = name.replace(c, "")
        filename = name.lower()
        print("Creating game data file", filename)
        with open(path / f"{filename}.yml", "w") as f:
            f.write(f"name: {name}\n")

    print("Created", len(created), "games:", *created)


@seed.command("platforms")
@click.argument("slug", required=False)
def platforms_(slug):
    """Update platforms for games using IGDB data"""
    api = igdb.API()
    modified = set()

    if slug:
        games_ = [games.get(slug)]
    else:
        games_ = games.get_all()

    for game in games_:
        print("Looking up platforms for", game.name)
        igdb_platforms = set()

        if game.igdb:
            igdb_games = [api.get_game(slug) for slug in game.igdb]
        else:
            igdb_games = api.get_games(game.name)

        for igdb_game in igdb_games:
            for igdb_platform in igdb_game.platforms:
                platform = platforms.get_by_slug(igdb_platform.slug)

                if not platform:
                    print(
                        "Unknown platform", igdb_platform.slug, "for", game.name
                    )
                    continue

                igdb_platforms.add(platform.name)

        if not igdb_platforms:
            print("No platforms found on IGDB for", game.name)
            continue

        with game.path.open() as f:
            doc = data.yaml.load(f)
        current_platforms = set(doc.get("platforms", []))

        if igdb_platforms.issubset(current_platforms):
            print("No changes for", game.name)
            continue

        modified.add(game.name)
        current_platforms = list(current_platforms.union(igdb_platforms))
        current_platforms.sort()
        doc["platforms"] = current_platforms
        print("Writing data file back for", game.name)
        with game.path.open("w") as f:
            data.yaml.dump(doc, f)

    print("Updated platforms for", len(modified), "games:", *modified)


@seed.command()
@click.argument("slug", required=False)
def dates(slug):
    """Update release dates for games using IGDB data"""
    api = igdb.API()
    modified = set()

    if slug:
        games_ = [games.get(slug)]
    else:
        games_ = games.get_all()

    for game in games_:
        print("Looking up release dates for", game.name)
        igdb_dates = []

        if game.igdb:
            igdb_games = [api.get_game(slug) for slug in game.igdb]
        else:
            igdb_games = api.get_games(game.name)

        for igdb_game in igdb_games:
            if igdb_game.first_release_date:
                igdb_dates.append(igdb_game.first_release_date)

        if not igdb_dates:
            print("No release dates found on IGDB for", game.name)
            continue

        igdb_dates.sort()
        igdb_date = igdb_dates[0]
        igdb_date = igdb_date.year

        with game.path.open() as f:
            doc = data.yaml.load(f)
        current_date = doc.get("start")

        if current_date and current_date <= igdb_date:
            print("No changes for", game.name)
            continue

        modified.add(game.name)
        doc["start"] = igdb_date
        print("Writing data file back for", game.name, "with date", igdb_date)
        with game.path.open("w") as f:
            data.yaml.dump(doc, f)

    print("Updated release dates for", len(modified), "games:", *modified)


@seed.command()
@click.argument("limit", default=10)
def popular(limit):
    """Update popular bool based on Discord roles"""
    api = discord.API(config.DISCORD_BOT_TOKEN)
    members = api.get_members()
    roles_by_id = {role.id: role.name for role in api.get_server().roles}
    roles_count = {}
    for member in members:
        for role_id in member["roles"]:
            role_name = roles_by_id.get(role_id)
            roles_count.setdefault(role_name, 0)
            roles_count[role_name] += 1

    top_roles = []
    for role, _ in sorted(
        roles_count.items(), key=lambda x: x[1], reverse=True
    ):
        if limit == 0:
            break
        game = games.get_by_name(role)
        if not game:
            continue
        top_roles.append(game)
        limit -= 1

    updated = 0
    for game in games.get_all():
        with game.path.open() as f:
            doc = data.yaml.load(f)
        is_popular = game in top_roles
        if doc.get("popular", False) == is_popular:
            continue
        doc["popular"] = is_popular
        with game.path.open("w") as f:
            data.yaml.dump(doc, f)
        print("Updated", game.name, "popularity to", is_popular)
        updated += 1
    print("Updated", updated, "games")


@seed.command("gps")
def gps_():
    """Populate database with departments and countries"""
    created = gps.populate_departments()
    print("Created", len(created), "departments")
    created = gps.populate_countries()
    print("Created", len(created), "countries")


@seed.command("regions")
def regions_():
    """Download regions topology"""
    gps.create_regions_topology(force=True)
    print("Downloaded regions topology")


@seed.command("all")
@click.pass_context
def all_(ctx):
    """Run all seed commands"""
    ctx.invoke(dates)
    ctx.invoke(gps_)
    ctx.invoke(platforms_)
    ctx.invoke(popular)
    ctx.invoke(regions_)
    ctx.invoke(roles_)
