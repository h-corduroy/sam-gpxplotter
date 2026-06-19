---
name: gpx-feature-workflow
description: House workflow for shipping a feature in the gpxplotter repo. Use when adding, changing, or extending a feature that touches the gpxplotter library and/or the FastAPI catalog app (app/main.py, app/static/index.html), or when the user asks to "add a feature", "ship", or "implement" something in this repo.
---

# GPX Feature Workflow

This repo has two layers that usually change together:

- **Library** — `gpxplotter/` (parsing in `gpxread.py`, plotting in `mplplotting.py`,
  maps in `folium_map.py`). Pure, importable, no web concerns.
- **App** — `app/main.py` (FastAPI routes) and `app/static/index.html` (single-page UI
  that calls `/api/tracks` and embeds `/map/{filename}`).

Follow this checklist so every feature lands consistently.

## 1. Understand before editing

- Confirm what segment data is available. `read_gpx_file` yields tracks; each track
  has `segments`, and segments expose keys like `latlon`, `elevation`, `hr`,
  `velocity-level`, and time data. Don't assume a key exists — many real files lack
  `hr` or timestamps.
- Compute derived values (distance, elevation gain, grade) in the **library layer**,
  not inside a route handler. Keep `app/main.py` thin.

## 2. Implement in the right layer

- New computation or rendering helpers go in `gpxplotter/` and get exported via
  `gpxplotter/__init__.py` if the app needs them.
- New data the UI needs is exposed through a JSON route in `app/main.py`. Reuse the
  existing safety helpers (`sanitize_gpx_filename`, `resolve_gpx_path`) for anything
  that takes a filename — never build a path from user input directly.
- UI changes go in `app/static/index.html`. Match the existing neo-brutalist style
  (2px black borders, hard box-shadows, the pastel `PORTFOLIO_COLORS` palette from
  `app/theme.py`). Color tokens are served as `/theme.css`; keep map route colors in
  `app/main.py` aligned with that module.

## 3. Handle missing data gracefully

- A file with no `elevation`, no `hr`, or no timestamps must still render. Degrade to
  a sensible default rather than raising. Mirror the existing `pick_metric` fallback
  pattern in `app/main.py`.

## 4. Verify it actually works

- Run the app using the `run-gpx-catalog` skill.
- Verify the new behavior in the browser with the `review-map-render` skill: load a
  real track from `gpx_files/` and screenshot the result. Don't report a UI feature
  done until you've seen it render.
- Test against more than one file — at minimum one with rich data (`ruten.gpx`) and
  one sparser file — to exercise the fallbacks.

## 5. Review before declaring done

- Run linters / `ReadLints` on every file you touched and fix what you introduced.
- For changes touching uploads, filenames, or path resolution, request a Bugbot
  review — this is the most security-sensitive surface in the repo.

## 6. Follow-ups worth offloading

Once the feature renders, these are good candidates to hand to a cloud agent or a
follow-up task: add `pytest` coverage for any new route, update `README.md` /
`DEMO.md`, and add a gallery example under `docs/source/gallery/` if a new plot type
was introduced.
