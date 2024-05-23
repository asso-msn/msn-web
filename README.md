# msn-web

This is the repository for the public website of the French association "Make
Some Noise", a group that acts to make arcade rhythm games more known and
accessible in its region. The group's main activities include sharing
information online and bringing rhythm games setups to meetups and events such
as anime conventions.

## Website's motivation

The website's main objective is making information available publicly that is currently
hard to obtain for someone who is not using social media or chat groups,
including:

- Information about past and future events, games available there, photos
- Information about arcade rhythm games, how to play them, what to buy, etc
- Information about the community, who is where and who plays what
- Information about the publicly available arcade venues

## Contributing

First of all, please consult the [Roadmap][roadmap] to know what features are
currently planned. Then from there:

- If you are a developer, refer to the [#developing](#developing) section and
  submit a PR. If you need help, reach out through GitHub issues or Discord.

- If you are a designer, you can discuss design decisions through GitHub issues.

- You can provide content by editing files in the `data/` directory with better
  information and submit a PR.

- You can submit new features you'd want to see or report bugs through GitHub
  issues.

You can reach us on Discord at https://asso-msn.fr/discord.

## Developing

This project is developped using Python 3.10 and later. The backend
functionality is provided by Flask. Database ORM is provided by SQLAlchemy. We
recommend getting familiar with those first.

### Running locally

If you do not have Python 3.10 or later provided by your OS, we recommend using
[pyenv](https://github.com/pyenv/pyenv). Then `pyenv install 3.10` and `pyenv
shell 3.10` before running the following commands.

Setting up:

```bash
git clone https://github.com/asso-msn/msn-web
cd msn-web
python -m venv .venv
source .venv/bin/activate
# Or if you use Windows:
# .venv\Scripts\activate.bat
pip install -r requirements.txt
```

Running the project in development mode (hot-reload + debug infos):

```bash
flask run --debug
```

Running the project in production mode:

```bash
flask run
```

If you need to bind to a specific port you can use `-p <PORT>`, or to a specific
interface with `-h <IP>`.

### Understanding the code

The entrypoint of the web server is the `app` symbol available in the `app`
module, defined in `app/__init__.py`.

`app/pages` is a collection of Flask routes that serve rendered HTML pages.

`app/services` holds the code for features implementation / "business logic", in
a form that is easy to import and execute, so that it can be imported in `pages`
while only having to add web specific logic on top of it (requests handling,
etc). Data models are defined there.

`app/static` contains static files such as images, CSS and JS.

`app/templates` contains Jinja2 HTML templates to be used by `pages`.

Generic Python helpers are directly added in their own file in the `app`
directory.

`data/` contains static data that can be read programatically. Think of it like
a database. This contains non-sensitive data that can be easily modified through
traditional git flows, allowing for peer reviewing of content etc.


If you need more help, please use GitHub issues or reach out on Discord.


## License

MIT.

[roadmap]: https://github.com/asso-msn/msn-web/milestones?direction=asc&sort=title&state=open
