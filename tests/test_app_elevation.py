from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import GPX_DIR, app


@pytest.fixture
def client():
    return TestClient(app)


def test_track_stats_returns_elevation_gain(client):
    sample = next(GPX_DIR.glob("*.gpx"))
    response = client.get(f"/api/tracks/{sample.name}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == sample.name
    assert isinstance(data["name"], str)
    assert data["elevation_gain_m"] is not None
    assert data["elevation_gain_m"] > 0


def test_track_stats_missing_file(client):
    response = client.get("/api/tracks/does-not-exist.gpx/stats")
    assert response.status_code == 404


def test_track_stats_without_elevation(client, tmp_path, monkeypatch):
    gpx = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test">
  <trk><name>Flat</name><trkseg>
    <trkpt lat="60.0" lon="10.0"/>
    <trkpt lat="60.001" lon="10.001"/>
  </trkseg></trk>
</gpx>
"""
    monkeypatch.setattr("app.main.GPX_DIR", tmp_path)
    path = tmp_path / "flat.gpx"
    path.write_text(gpx, encoding="utf-8")

    response = client.get("/api/tracks/flat.gpx/stats")
    assert response.status_code == 200
    assert response.json() == {
        "filename": "flat.gpx",
        "name": "Flat",
        "elevation_gain_m": None,
    }
