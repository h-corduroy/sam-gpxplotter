---
name: review-map-render
description: Visually verify the GPX Catalog app by loading a track in a browser and screenshotting the rendered map. Use when the user asks to verify, check, screenshot, or visually confirm a route map, the catalog UI, or any change to app/main.py or app/static/index.html.
---

# Review Map Render

Self-verify UI work on the GPX Catalog app: boot the server, drive a real browser to a
track, and capture a screenshot so the rendered map can be inspected — not just the code.

## 1. Make sure the app is running

Start it with the `run-gpx-catalog` skill if it isn't already. Confirm it's up:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/   # expect 200
```

## 2. Pick a track to verify

List available files and choose one (prefer a data-rich track like `ruten.gpx`, and
also spot-check a sparser file to exercise fallbacks):

```bash
curl -s http://127.0.0.1:8000/api/tracks
```

## 3. Drive the browser

Use the browser tools (`cursor-ide-browser` MCP):

1. `browser_navigate` to `http://127.0.0.1:8000/` (omit `position` to keep focus).
2. `browser_lock` (action `lock`) before interacting.
3. `browser_snapshot` to get the accessibility tree, then `browser_click` the track
   button in the left list (items carry a `data-filename` attribute).
4. The map renders inside the `#map` iframe. Iframe contents aren't directly
   accessible, so to verify the map body, also navigate directly to the standalone
   render and screenshot that:
   - `browser_navigate` to `http://127.0.0.1:8000/map/<filename>`.
5. `browser_take_screenshot` to capture the rendered route (this attaches an image you
   can actually inspect).
6. `browser_lock` (action `unlock`) when finished.

## 4. What to check

- The route line is drawn and visible against the desaturated basemap.
- Color-by-metric legend appears for files with `hr` / `velocity-level` / `elevation`;
  a plain line for files without.
- Any new panel / stat card / overlay you added is present and populated.
- No JavaScript errors — check via `browser_cdp` with `Runtime.evaluate` or
  `Log.enable` if the page looks wrong.

## 5. Report

Embed the screenshot in your response and state which file(s) you verified. If
something is missing or broken, capture the screenshot and the console output before
attempting a fix.
