# GPX Map API Documentation

## Overview

The gpxplotter Map API is a FastAPI-based web application that provides a local catalog for viewing and managing GPX (GPS Exchange Format) files as interactive Folium maps. The API allows you to list available tracks, upload new GPX files, and render routes as beautiful, styled maps.

## Table of Contents

- [Installation](#installation)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
  - [GET /](#get-)
  - [GET /api/tracks](#get-apitracks)
  - [POST /api/tracks](#post-apitracks)
  - [GET /map/{filename}](#get-mapfilename)
- [Map Features](#map-features)
- [Security](#security)
- [Testing](#testing)
- [Examples](#examples)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

Install required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Additionally, for the FastAPI server, install:

```bash
pip install fastapi uvicorn python-multipart
```

## Running the Server

### Development Mode

Run the FastAPI app using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

The server will start at `http://localhost:8000`.

### Production Mode

For production deployments:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Configuration

The API uses these directory paths (configured in `app/main.py`):

- **GPX_DIR**: `gpx_files/` — where GPX files are stored
- **STATIC_DIR**: `app/static/` — serves the catalog UI

To use a different GPX directory, modify `GPX_DIR` in `app/main.py` before starting the server.

## API Endpoints

### GET /

**Description**: Returns the main catalog UI as an HTML page.

**Response**: HTML page with the GPX catalog interface

**Example**:
```bash
curl http://localhost:8000/
```

---

### GET /api/tracks

**Description**: Lists all GPX files in the catalog with their display names.

**Response**:
```json
[
  {
    "filename": "ruten.gpx",
    "name": "Morning Run - Nordmarka"
  },
  {
    "filename": "solstice_ride.gpx",
    "name": "Solstice Ride"
  }
]
```

**Response Fields**:
- `filename` (string): The GPX file name
- `name` (string): Human-readable track name extracted from the GPX `<name>` tag, or the filename stem if no name is found

**Example**:
```bash
curl http://localhost:8000/api/tracks
```

```python
import requests

response = requests.get("http://localhost:8000/api/tracks")
tracks = response.json()

for track in tracks:
    print(f"{track['name']} ({track['filename']})")
```

---

### POST /api/tracks

**Description**: Upload a new GPX file to the catalog. If a file with the same name exists, it will be overwritten.

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**: File upload field named `file`

**Validations**:
- File must have a `.gpx` extension
- File must contain valid GPX XML
- File must have at least one track point (non-empty segments)

**Response** (Success - 200):
```json
{
  "filename": "new_route.gpx",
  "name": "New Route"
}
```

**Response** (Error - 400):
```json
{
  "detail": "Not a .gpx file"
}
```

**Response** (Error - 422):
```json
{
  "detail": "No track points found in file"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/tracks \
  -F "file=@/path/to/your/route.gpx"
```

```python
import requests

with open("route.gpx", "rb") as f:
    files = {"file": ("route.gpx", f, "application/gpx+xml")}
    response = requests.post("http://localhost:8000/api/tracks", files=files)
    print(response.json())
```

---

### GET /map/{filename}

**Description**: Renders an interactive Folium map for the specified GPX file. The map includes the route drawn as a colored line (colored by heart rate, velocity, or elevation if available) with start and end markers.

**Parameters**:
- `filename` (path parameter): The name of the GPX file (e.g., `ruten.gpx`)

**Response**: HTML page containing the interactive Leaflet/Folium map

**Response** (Error - 404):
```json
{
  "detail": "File not found"
}
```

**Response** (Error - 422):
```json
{
  "detail": "No track points found in file"
}
```

**Example**:
```bash
curl http://localhost:8000/map/ruten.gpx > map.html
open map.html  # macOS
# or
xdg-open map.html  # Linux
```

## Map Features

### Visual Styling

The rendered maps use a custom neo-brutalist design with:

- **Desaturated basemap**: Base tiles are filtered to reduce saturation (40%) and slightly brightened
- **Bold route lines**: Routes use a portfolio color palette with high contrast
- **Outlined paths**: Routes have a dark outline for visibility on any background
- **Start/End markers**: Green "Start" and gray "End" markers with distance and time tooltips (if available)

### Route Coloring

Routes are automatically colored by the best available metric, in this priority order:

1. **Heart Rate** (`hr`) — colored gradient based on heart rate zones
2. **Velocity** (`velocity-level`) — speed-based coloring
3. **Elevation** — elevation-based coloring
4. **Plain line** — solid color if no metrics are available

### Color Palette

The portfolio route colors are:
- Purple: `#A090FF`
- Coral: `#FF948C`
- Green: `#7AE88A`
- Yellow: `#D4E878`
- Cyan: `#5ADCCC`
- Pink: `#FF94B0`

## Security

### Path Traversal Protection

All filename inputs are sanitized to prevent path traversal attacks:

- `sanitize_gpx_filename()`: Strips directory components and validates `.gpx` extension
- `resolve_gpx_path()`: Ensures resolved paths are direct children of `GPX_DIR`

**Example blocked attempts**:
- `../../../etc/passwd.gpx` → resolved to `passwd.gpx`
- `/absolute/path/file.gpx` → resolved to `file.gpx`
- `file.txt` → rejected (not a `.gpx` file)

### File Validation

Uploaded files are validated before being saved:

1. Temporary file is created in `GPX_DIR`
2. File is parsed to check for track points
3. If validation passes, file is moved to final location
4. If validation fails, temporary file is deleted

## Testing

### Running Tests

The project includes comprehensive tests for both API routes and library functions.

```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=gpxplotter --cov-report=html

# Run only API tests
pytest -m api

# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration
```

### Test Structure

- `tests/test_api_routes.py`: Tests for FastAPI endpoints
  - Route responses and status codes
  - Upload validation and security
  - Path traversal protection
  - Helper function behavior

- `tests/test_library.py`: Tests for gpxplotter library
  - Map creation with various tile options
  - Segment coloring and styling
  - Marker placement
  - HTML rendering

## Examples

### Example 1: List and Render All Tracks

```python
import requests

# Get all tracks
response = requests.get("http://localhost:8000/api/tracks")
tracks = response.json()

# Render each track
for track in tracks:
    filename = track["filename"]
    print(f"Rendering {track['name']}...")
    
    map_response = requests.get(f"http://localhost:8000/map/{filename}")
    with open(f"output/{filename}.html", "w") as f:
        f.write(map_response.text)
```

### Example 2: Upload Multiple GPX Files

```python
import requests
from pathlib import Path

gpx_folder = Path("my_gpx_files")

for gpx_file in gpx_folder.glob("*.gpx"):
    print(f"Uploading {gpx_file.name}...")
    
    with open(gpx_file, "rb") as f:
        files = {"file": (gpx_file.name, f, "application/gpx+xml")}
        response = requests.post("http://localhost:8000/api/tracks", files=files)
        
        if response.status_code == 200:
            print(f"  ✓ Success: {response.json()['name']}")
        else:
            print(f"  ✗ Failed: {response.json()['detail']}")
```

### Example 3: Embed Map in Iframe

```html
<!DOCTYPE html>
<html>
<head>
    <title>My GPX Route</title>
</head>
<body>
    <h1>My Morning Run</h1>
    <iframe 
        src="http://localhost:8000/map/ruten.gpx" 
        width="100%" 
        height="600" 
        frameborder="0">
    </iframe>
</body>
</html>
```

### Example 4: Using JavaScript Fetch

```javascript
// Fetch track list
async function loadTracks() {
    const response = await fetch('http://localhost:8000/api/tracks');
    const tracks = await response.json();
    
    const trackList = document.getElementById('track-list');
    tracks.forEach(track => {
        const link = document.createElement('a');
        link.href = `/map/${track.filename}`;
        link.textContent = track.name;
        trackList.appendChild(link);
    });
}

// Upload a file
async function uploadGPX(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8000/api/tracks', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        const result = await response.json();
        console.log('Uploaded:', result.name);
    } else {
        const error = await response.json();
        console.error('Upload failed:', error.detail);
    }
}
```

## Advanced Usage

### Custom Map Styling

To customize map appearance, modify the constants in `app/main.py`:

```python
# Portfolio color palette for routes
PORTFOLIO_ROUTE_COLORS = (
    "#A090FF",  # Purple
    "#FF948C",  # Coral
    "#7AE88A",  # Green
    "#D4E878",  # Yellow
    "#5ADCCC",  # Cyan
    "#FF94B0",  # Pink
)

# Plain route style (when no metrics available)
PLAIN_ROUTE_STYLE = {"color": "#5A4AD8", "weight": 5}

# Route outline for visibility
ROUTE_OUTLINE_STYLE = {"color": "#000000", "weight": 12, "opacity": 1}
```

### Using Different Basemap Tiles

The default basemap is OpenStreetMap. To use different tiles, modify the `render_map` function:

```python
the_map = create_folium_map(tiles="cartodb positron")
# or
the_map = create_folium_map(tiles="opentopomap")
```

Available tile options (from `gpxplotter.folium_map.TILES`):
- `openstreetmap`
- `cartodb positron`
- `cartodb voyager`
- `opentopomap`
- `kartverket_topo4` (Norway)
- `esri_worldimagery`
- `cyclosm`

### Programmatic Access to Map Objects

```python
from gpxplotter import read_gpx_file, create_folium_map, add_segment_to_map

# Read GPX file
gpx_path = "gpx_files/ruten.gpx"
the_map = create_folium_map()

for track in read_gpx_file(gpx_path):
    for segment in track['segments']:
        add_segment_to_map(
            the_map, 
            segment, 
            color_by='hr',
            line_options={"weight": 6}
        )

# Save to file
the_map.save("custom_map.html")

# Or get HTML string
html = the_map.get_root().render()
```

## Troubleshooting

### Port Already in Use

If port 8000 is occupied, use a different port:

```bash
uvicorn app.main:app --port 8080
```

### GPX File Not Found

Ensure your GPX files are in the `gpx_files/` directory relative to the project root, or update `GPX_DIR` in `app/main.py`.

### Upload Fails with 422

The GPX file must contain at least one `<trkpt>` element in a `<trkseg>`. Empty GPX files or files with only waypoints will be rejected.

### Map Not Rendering

Check that:
1. The GPX file has valid latitude/longitude coordinates
2. The file contains track segments (not just waypoints or routes)
3. Browser console for JavaScript errors

## Further Reading

- [gpxplotter Library Documentation](https://gpxplotter.readthedocs.io/en/latest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Folium Documentation](https://python-visualization.github.io/folium/)
- [GPX Format Specification](https://www.topografix.com/gpx.asp)
