# Back-End-Development-Songs

Flask REST API completed from the IBM Skills Network course template.

## Environment setup

The course Cloud IDE can initialize Python 3.9 with `bash bin/setup.sh` and
its `backend-songs-venv` environment. This implementation
was also verified locally with Python 3.12 and the pinned requirements.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export MONGODB_SERVICE=127.0.0.1:27018
pytest -v
gunicorn --bind 127.0.0.1:3000 app:app
```

## API

`GET /health`, `GET /count`, `GET /song`,
`GET /song/<id>`, `POST /song`,
`PUT /song/<id>`, and `DELETE /song/<id>`.

MongoDB settings are provided through `MONGODB_SERVICE`, optional `MONGODB_PORT`,
`MONGODB_USERNAME` and `MONGODB_PASSWORD`. Seed data is inserted only into an empty
collection. Credentials are never printed.
