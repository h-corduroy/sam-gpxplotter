---
name: run-gpx-catalog
description: Run the GPX Catalog FastAPI app in this repo. Use when the user asks to run, start, serve, launch, or boot the app, the server, the GPX catalog, or app/main.py.
---

# Run GPX Catalog

The app (`app/main.py`) is a FastAPI server that lists `.gpx` files from `gpx_files/`
and renders each as an interactive Folium map.

## Run it

From the repo root:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Serves at http://127.0.0.1:8000. Start it in the background and keep it running.

- First start is slow because matplotlib builds its font cache. Wait for
  `Application startup complete` / `Uvicorn running` before reporting success.
- Use `--reload` during development to auto-restart on code changes.

## If `.venv` is missing or deps aren't installed

```bash
python3 -m venv .venv
.venv/bin/pip install -r app/requirements.txt
.venv/bin/pip install -e .
```

`app/requirements.txt` covers `fastapi` and `uvicorn`; the editable install (`-e .`)
provides the local `gpxplotter` package that `app/main.py` imports.

## Verify it's up

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/   # expect 200
curl -s http://127.0.0.1:8000/api/tracks                          # JSON list of tracks
```

## Endpoints

- `GET /` — catalog UI (`app/static/index.html`)
- `GET /api/tracks` — JSON list of `.gpx` files with display names
- `GET /map/{filename}` — standalone Folium map for one file

## Notes

- The `~/.matplotlib not writable` warning is harmless; matplotlib falls back to a
  temp cache dir. Set `MPLCONFIGDIR` to a writable path to silence it.
- Drop new `.gpx` files into `gpx_files/` and refresh the page to see them.
