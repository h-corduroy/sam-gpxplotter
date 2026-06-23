# gpxplotter

[![Documentation Status](https://readthedocs.org/projects/gpxplotter/badge/?version=latest)](https://gpxplotter.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/andersle/gpxplotter/main?filepath=examples%2Fjupyter%2F)

**gpxplotter** is a Python package for reading 
[gpx](https://en.wikipedia.org/wiki/GPS_Exchange_Format)
files and creating simple predefined plots using
[matplotlib](http://matplotlib.org/) 
and maps using
[folium](https://python-visualization.github.io/folium/).

Please see
[https://gpxplotter.readthedocs.io/en/latest/](https://gpxplotter.readthedocs.io/en/latest/)
for the latest documentation and the 
[Binder notebooks](https://mybinder.org/v2/gh/andersle/gpxplotter/main?filepath=examples%2Fjupyter%2F) for examples.

## Installation

```
pip install gpxplotter
```

## Examples

Interactive examples can be explored
via [Binder](https://mybinder.org/v2/gh/andersle/gpxplotter/main?filepath=examples%2Fjupyter%2F).


#### Simple example for showing a track in a map, colored by heart rate

```python

from gpxplotter import read_gpx_file, create_folium_map, add_segment_to_map

the_map = create_folium_map()
for track in read_gpx_file('ruten.gpx'):
    for i, segment in enumerate(track['segments']):
        add_segment_to_map(the_map, segment, color_by='hr')

# To display the map in a Jupyter notebook:
the_map
```

[![map](examples/images/map001.png)](examples/html/map001.html)

### Further examples

Please see the [gallery in the documentation](https://gpxplotter.readthedocs.io/en/latest/auto_examples_maps/index.html)
for further examples.

## Web Application

**gpxplotter** includes a FastAPI-based web application that provides a catalog interface for viewing and managing GPX files as interactive maps.

See [MAP_API.md](MAP_API.md) for complete documentation on the web API, including:
- API endpoints for listing, uploading, and rendering GPX files
- Map customization and styling options
- Security features and validation
- Usage examples in Python, JavaScript, and curl

### Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Run the server
uvicorn app.main:app --reload --port 8000

# Open in browser
open http://localhost:8000
```

## Testing

The project includes comprehensive test coverage for both the library and the web API.

```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=gpxplotter --cov-report=html

# Run specific test categories
pytest -m api          # API endpoint tests
pytest -m unit         # Unit tests
pytest -m integration  # Integration tests
```

See [MAP_API.md](MAP_API.md) for detailed information about the test suite. 
