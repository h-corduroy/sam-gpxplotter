"""Tests for the FastAPI map catalog endpoints.

This test module verifies the /api/tracks, POST /api/tracks, and /map/{filename}
routes, including upload validation, path traversal protection, and map rendering.
"""
import io
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app, GPX_DIR


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_gpx_content():
    """Return valid minimal GPX XML content for testing uploads."""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test">
  <trk>
    <name>Test Track</name>
    <trkseg>
      <trkpt lat="59.911491" lon="10.757933">
        <ele>25</ele>
        <time>2023-01-01T12:00:00Z</time>
      </trkpt>
      <trkpt lat="59.912491" lon="10.758933">
        <ele>30</ele>
        <time>2023-01-01T12:01:00Z</time>
      </trkpt>
      <trkpt lat="59.913491" lon="10.759933">
        <ele>28</ele>
        <time>2023-01-01T12:02:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""


@pytest.fixture
def empty_gpx_content():
    """Return empty GPX content (no track points) for validation testing."""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test">
  <trk>
    <name>Empty Track</name>
  </trk>
</gpx>"""


class TestIndexRoute:
    """Tests for the root / route."""

    @pytest.mark.api
    def test_index_returns_html(self, client):
        """Verify the root route returns the catalog HTML page."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestListTracksRoute:
    """Tests for GET /api/tracks endpoint."""

    @pytest.mark.api
    def test_list_tracks_returns_json(self, client):
        """Verify /api/tracks returns valid JSON."""
        response = client.get("/api/tracks")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.api
    def test_list_tracks_structure(self, client):
        """Verify the response structure includes filename and name fields."""
        response = client.get("/api/tracks")
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            track = data[0]
            assert "filename" in track
            assert "name" in track
            assert track["filename"].endswith(".gpx")

    @pytest.mark.api
    def test_list_tracks_includes_known_files(self, client):
        """Verify known GPX files in the catalog are listed."""
        response = client.get("/api/tracks")
        data = response.json()
        filenames = [track["filename"] for track in data]
        assert len(filenames) > 0
        assert any(f.endswith(".gpx") for f in filenames)


class TestUploadTrackRoute:
    """Tests for POST /api/tracks upload endpoint."""

    @pytest.mark.api
    def test_upload_valid_gpx(self, client, sample_gpx_content):
        """Verify uploading a valid GPX file succeeds."""
        files = {"file": ("test_upload.gpx", io.BytesIO(sample_gpx_content), "application/gpx+xml")}
        response = client.post("/api/tracks", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test_upload.gpx"
        assert "name" in data
        uploaded_path = GPX_DIR / "test_upload.gpx"
        assert uploaded_path.exists()
        uploaded_path.unlink()

    @pytest.mark.api
    def test_upload_overwrites_existing_file(self, client, sample_gpx_content):
        """Verify uploading a file with the same name overwrites the previous one."""
        files = {"file": ("test_overwrite.gpx", io.BytesIO(sample_gpx_content), "application/gpx+xml")}
        response1 = client.post("/api/tracks", files=files)
        assert response1.status_code == 200
        response2 = client.post("/api/tracks", files=files)
        assert response2.status_code == 200
        uploaded_path = GPX_DIR / "test_overwrite.gpx"
        uploaded_path.unlink(missing_ok=True)

    @pytest.mark.api
    def test_upload_empty_gpx_fails(self, client, empty_gpx_content):
        """Verify uploading GPX with no track points returns 422."""
        files = {"file": ("empty.gpx", io.BytesIO(empty_gpx_content), "application/gpx+xml")}
        response = client.post("/api/tracks", files=files)
        assert response.status_code == 422
        assert "No track points found" in response.json()["detail"]

    @pytest.mark.api
    def test_upload_invalid_xml_fails(self, client):
        """Verify uploading invalid XML returns 422."""
        invalid_content = b"Not valid XML at all"
        files = {"file": ("invalid.gpx", io.BytesIO(invalid_content), "application/gpx+xml")}
        response = client.post("/api/tracks", files=files)
        assert response.status_code == 422

    @pytest.mark.api
    def test_upload_non_gpx_extension_fails(self, client, sample_gpx_content):
        """Verify uploading a file without .gpx extension returns 400."""
        files = {"file": ("test.txt", io.BytesIO(sample_gpx_content), "text/plain")}
        response = client.post("/api/tracks", files=files)
        assert response.status_code == 400
        assert "Not a .gpx file" in response.json()["detail"]

    @pytest.mark.api
    def test_upload_path_traversal_blocked(self, client, sample_gpx_content):
        """Verify path traversal attempts in filename are blocked."""
        files = {"file": ("../../../etc/passwd.gpx", io.BytesIO(sample_gpx_content), "application/gpx+xml")}
        response = client.post("/api/tracks", files=files)
        if response.status_code == 200:
            data = response.json()
            assert data["filename"] == "passwd.gpx"
            uploaded_path = GPX_DIR / "passwd.gpx"
            uploaded_path.unlink(missing_ok=True)


class TestRenderMapRoute:
    """Tests for GET /map/{filename} endpoint."""

    @pytest.mark.api
    def test_render_existing_gpx_returns_html(self, client):
        """Verify /map/{filename} returns HTML for an existing file."""
        gpx_files = list(GPX_DIR.glob("*.gpx"))
        if gpx_files:
            filename = gpx_files[0].name
            response = client.get(f"/map/{filename}")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
            assert b"leaflet" in response.content.lower() or b"folium" in response.content.lower()

    @pytest.mark.api
    def test_render_nonexistent_file_returns_404(self, client):
        """Verify requesting a non-existent file returns 404."""
        response = client.get("/map/nonexistent_file_12345.gpx")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.api
    def test_render_path_traversal_blocked(self, client):
        """Verify path traversal attempts in filename are blocked."""
        response = client.get("/map/../../../etc/passwd.gpx")
        assert response.status_code == 404

    @pytest.mark.api
    def test_render_map_contains_map_elements(self, client):
        """Verify rendered map HTML contains expected Folium/Leaflet elements."""
        gpx_files = list(GPX_DIR.glob("*.gpx"))
        if gpx_files:
            filename = gpx_files[0].name
            response = client.get(f"/map/{filename}")
            content = response.content.decode("utf-8")
            assert "leaflet" in content.lower() or "L.map" in content
            assert "PolyLine" in content or "polyline" in content.lower()

    @pytest.mark.api
    def test_render_applies_custom_styles(self, client):
        """Verify custom MAP_TILE_STYLE is applied to rendered map."""
        gpx_files = list(GPX_DIR.glob("*.gpx"))
        if gpx_files:
            filename = gpx_files[0].name
            response = client.get(f"/map/{filename}")
            content = response.content.decode("utf-8")
            assert "filter: saturate" in content or "leaflet-tile-pane" in content


class TestHelperFunctions:
    """Tests for helper functions in app/main.py."""

    @pytest.mark.unit
    def test_sanitize_gpx_filename_valid(self):
        """Verify sanitize_gpx_filename accepts valid filenames."""
        from app.main import sanitize_gpx_filename
        
        assert sanitize_gpx_filename("test.gpx") == "test.gpx"
        assert sanitize_gpx_filename("my_route.gpx") == "my_route.gpx"
        assert sanitize_gpx_filename("route-123.gpx") == "route-123.gpx"

    @pytest.mark.unit
    def test_sanitize_gpx_filename_strips_path(self):
        """Verify sanitize_gpx_filename extracts basename from paths."""
        from app.main import sanitize_gpx_filename
        
        assert sanitize_gpx_filename("/path/to/file.gpx") == "file.gpx"
        assert sanitize_gpx_filename("../../../file.gpx") == "file.gpx"

    @pytest.mark.unit
    def test_sanitize_gpx_filename_rejects_non_gpx(self):
        """Verify sanitize_gpx_filename rejects files without .gpx extension."""
        from app.main import sanitize_gpx_filename
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            sanitize_gpx_filename("file.txt")
        assert exc_info.value.status_code == 400
        assert "Not a .gpx file" in str(exc_info.value.detail)

    @pytest.mark.unit
    def test_resolve_gpx_path_valid_file(self):
        """Verify resolve_gpx_path returns valid path for existing files."""
        from app.main import resolve_gpx_path
        
        gpx_files = list(GPX_DIR.glob("*.gpx"))
        if gpx_files:
            filename = gpx_files[0].name
            resolved = resolve_gpx_path(filename)
            assert resolved.exists()
            assert resolved.parent == GPX_DIR
            assert resolved.name == filename

    @pytest.mark.unit
    def test_resolve_gpx_path_rejects_nonexistent(self):
        """Verify resolve_gpx_path raises 404 for non-existent files."""
        from app.main import resolve_gpx_path
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            resolve_gpx_path("nonexistent_file_12345.gpx")
        assert exc_info.value.status_code == 404

    @pytest.mark.unit
    def test_resolve_gpx_path_blocks_traversal(self):
        """Verify resolve_gpx_path blocks path traversal attempts."""
        from app.main import resolve_gpx_path
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            resolve_gpx_path("../../../etc/passwd.gpx")
        assert exc_info.value.status_code == 404

    @pytest.mark.unit
    def test_track_display_name_extracts_name(self):
        """Verify track_display_name extracts name from track metadata."""
        from app.main import track_display_name
        
        track_with_name = {"name": ["Morning Run"]}
        assert track_display_name(track_with_name, "fallback") == "Morning Run"
        
        track_with_string_name = {"name": "Evening Ride"}
        assert track_display_name(track_with_string_name, "fallback") == "Evening Ride"

    @pytest.mark.unit
    def test_track_display_name_fallback(self):
        """Verify track_display_name uses fallback when name is missing."""
        from app.main import track_display_name
        
        track_no_name = {}
        assert track_display_name(track_no_name, "fallback.gpx") == "fallback.gpx"
        
        track_empty_name = {"name": [""]}
        assert track_display_name(track_empty_name, "fallback.gpx") == "fallback.gpx"

    @pytest.mark.unit
    def test_pick_metric_prefers_hr(self):
        """Verify pick_metric prefers heart rate when available."""
        from app.main import pick_metric
        
        segment = {
            "hr": [120, 130, 140],
            "velocity-level": [5.0, 5.5, 6.0],
            "elevation": [100, 105, 110]
        }
        assert pick_metric(segment) == "hr"

    @pytest.mark.unit
    def test_pick_metric_fallback_chain(self):
        """Verify pick_metric falls back through velocity-level and elevation."""
        from app.main import pick_metric
        
        segment_velocity = {
            "velocity-level": [5.0, 5.5, 6.0],
            "elevation": [100, 105, 110]
        }
        assert pick_metric(segment_velocity) == "velocity-level"
        
        segment_elevation = {"elevation": [100, 105, 110]}
        assert pick_metric(segment_elevation) == "elevation"

    @pytest.mark.unit
    def test_pick_metric_returns_none_when_empty(self):
        """Verify pick_metric returns None when no metrics available."""
        from app.main import pick_metric
        
        segment_empty = {}
        assert pick_metric(segment_empty) is None
        
        segment_empty_values = {"hr": [], "elevation": None}
        assert pick_metric(segment_empty_values) is None
