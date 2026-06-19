"""FastAPI app: a local catalog of GPX files rendered as Folium maps.

Routes:
    GET /                 -> the catalog UI (static HTML page).
    GET /api/tracks       -> JSON list of available GPX files.
    POST /api/tracks      -> upload a GPX file into the catalog.
    GET /map/{filename}   -> standalone Folium map HTML for one GPX file.
"""
import tempfile
from pathlib import Path

import branca.colormap as cm
import folium
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.theme import (
    MAP_BACKGROUND_COLOR,
    PLAIN_ROUTE_COLOR,
    PORTFOLIO_ROUTE_COLORS,
    ROUTE_OUTLINE_COLOR,
    css_variables,
    portfolio_colors_json,
)
from gpxplotter import (
    add_segment_to_map,
    create_folium_map,
    read_gpx_file,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
# Local catalog folder. Drop .gpx files in here and refresh the page.
GPX_DIR = (BASE_DIR.parent / "gpx_files").resolve()

# Metrics we know how to color a track by, in order of preference. Files
# without these (e.g. no heart-rate data) fall back to a plain line.
PREFERRED_METRICS = ("hr", "velocity-level", "elevation")

ROUTE_COLORMAP = cm.LinearColormap(
    colors=list(PORTFOLIO_ROUTE_COLORS),
    vmin=0,
    vmax=1,
)
PLAIN_ROUTE_STYLE = {"color": PLAIN_ROUTE_COLOR, "weight": 5}
ROUTE_OUTLINE_STYLE = {
    "color": ROUTE_OUTLINE_COLOR,
    "weight": 12,
    "opacity": 1,
}

# Desaturate basemap tiles only; overlays (route, markers) stay in other panes.
MAP_TILE_STYLE = f"""
<style>
html, body {{ background: {MAP_BACKGROUND_COLOR}; }}
.leaflet-tile-pane {{
  filter: saturate(0.4) brightness(1.05);
}}
.leaflet-overlay-pane {{
  filter: saturate(1.2);
}}
</style>
"""

INDEX_TEMPLATE = (STATIC_DIR / "index.html").read_text()


def render_index_html() -> str:
    """Inject shared theme tokens into the catalog UI template."""
    html = INDEX_TEMPLATE.replace("/*__THEME_VARS__*/", css_variables())
    return html.replace(
        "/*__PORTFOLIO_COLORS__*/[]",
        portfolio_colors_json(),
    )


app = FastAPI(title="GPX Catalog")


def sanitize_gpx_filename(name: str) -> str:
    """Return a safe basename for a GPX file inside GPX_DIR."""
    filename = Path(name).name
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    if not filename.lower().endswith(".gpx"):
        raise HTTPException(status_code=400, detail="Not a .gpx file")
    return filename


def resolve_gpx_path(filename: str) -> Path:
    """Resolve a requested filename to a safe path inside GPX_DIR.

    Guards against path traversal: the candidate must be a plain ``.gpx``
    file that resolves to a direct child of GPX_DIR.
    """
    safe_name = sanitize_gpx_filename(filename)
    candidate = (GPX_DIR / safe_name).resolve()
    if candidate.parent != GPX_DIR or not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return candidate


def track_display_name(track: dict, fallback: str) -> str:
    """Pull a human-friendly name out of a parsed track."""
    name = track.get("name")
    # read_gpx_file stores the <name> tag contents as a list of strings.
    if isinstance(name, (list, tuple)):
        name = next((part for part in name if part), None)
    if isinstance(name, str) and name.strip():
        return name.strip()
    return fallback


def track_entry_for_path(path: Path) -> dict:
    """Build a catalog list entry for one GPX file on disk."""
    display = path.stem
    try:
        for track in read_gpx_file(str(path)):
            display = track_display_name(track, path.stem)
            break
    except Exception:
        pass
    return {"filename": path.name, "name": display}


def has_track_points(path: str) -> bool:
    """Return True if the GPX file contains at least one segment with points."""
    for track in read_gpx_file(path):
        for segment in track.get("segments", []):
            if segment.get("latlon"):
                return True
    return False


def pick_metric(segment: dict):
    """Choose a metric to color the route by, or None for a plain line."""
    for metric in PREFERRED_METRICS:
        values = segment.get(metric)
        if values is not None and len(values) > 0:
            return metric
    return None


def add_outlined_segment(the_map, segment, **kwargs):
    """Draw a dark casing under the route so it reads on the basemap."""
    folium.PolyLine(segment["latlon"], **ROUTE_OUTLINE_STYLE).add_to(the_map)
    add_segment_to_map(the_map, segment, **kwargs)


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(render_index_html())


@app.get("/api/tracks")
def list_tracks():
    """List GPX files in the catalog, with a display name for each."""
    return [
        track_entry_for_path(path)
        for path in sorted(GPX_DIR.glob("*.gpx"))
    ]


@app.post("/api/tracks")
async def upload_track(file: UploadFile = File(...)):
    """Upload a GPX file into the catalog, overwriting same-named files."""
    filename = sanitize_gpx_filename(file.filename or "")
    content = await file.read()

    with tempfile.NamedTemporaryFile(
        dir=GPX_DIR, suffix=".gpx", delete=False
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        if not has_track_points(str(tmp_path)):
            raise HTTPException(
                status_code=422, detail="No track points found in file"
            )
        entry = track_entry_for_path(tmp_path)
        dest = GPX_DIR / filename
        tmp_path.replace(dest)
        entry["filename"] = filename
        return entry
    except HTTPException:
        tmp_path.unlink(missing_ok=True)
        raise
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Invalid GPX file")


@app.get("/map/{filename}", response_class=HTMLResponse)
def render_map(filename: str) -> HTMLResponse:
    """Render the route(s) from one GPX file onto an interactive map."""
    path = resolve_gpx_path(filename)

    the_map = create_folium_map(tiles="openstreetmap")
    drew_segment = False
    for track in read_gpx_file(str(path)):
        for segment in track.get("segments", []):
            if not segment.get("latlon"):
                continue
            metric = pick_metric(segment)
            if metric:
                add_outlined_segment(
                    the_map,
                    segment,
                    color_by=metric,
                    cmap=ROUTE_COLORMAP,
                    line_options={"weight": 6},
                )
            else:
                add_outlined_segment(
                    the_map,
                    segment,
                    line_options=PLAIN_ROUTE_STYLE,
                )
            drew_segment = True

    if not drew_segment:
        raise HTTPException(
            status_code=422, detail="No track points found in file"
        )

    html = the_map.get_root().render()
    html = html.replace("</head>", MAP_TILE_STYLE + "</head>", 1)
    return HTMLResponse(html)
