from app import app
from app.services import igdb as service


@app.cli.group()
def igdb():
    pass


@igdb.command()
def platforms():
    """List all platforms from IGDB"""
    api = service.API()
    result = api.get_platforms(with_name=True)
    result.sort(key=lambda x: x.slug)

    for platform in result:
        print(platform.slug, platform.name)
