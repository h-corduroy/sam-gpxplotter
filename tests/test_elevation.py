import tempfile
import unittest
from pathlib import Path

import numpy as np

from gpxplotter import (
    compute_elevation_gain,
    gpx_elevation_gain,
    read_gpx_file,
    track_elevation_gain,
)


class ElevationGainTests(unittest.TestCase):
    def test_compute_elevation_gain_sums_positive_deltas(self):
        elevation = np.array([100.0, 110.0, 105.0, 120.0])
        self.assertEqual(compute_elevation_gain(elevation), 25.0)

    def test_compute_elevation_gain_handles_missing_data(self):
        self.assertIsNone(compute_elevation_gain(None))
        self.assertEqual(compute_elevation_gain([]), 0.0)
        self.assertEqual(compute_elevation_gain([250.0]), 0.0)

    def test_track_elevation_gain_sums_segments(self):
        track = {
            "segments": [
                {"elevation-up": 100.0},
                {"elevation-up": 50.0},
            ]
        }
        self.assertEqual(track_elevation_gain(track), 150.0)

    def test_track_elevation_gain_returns_none_without_elevation(self):
        track = {"segments": [{"lat": [1.0], "lon": [2.0]}]}
        self.assertIsNone(track_elevation_gain(track))

    def test_gpx_elevation_gain_from_minimal_gpx(self):
        gpx = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test"
  xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Test climb</name>
    <trkseg>
      <trkpt lat="63.0" lon="9.0"><ele>100</ele></trkpt>
      <trkpt lat="63.1" lon="9.1"><ele>130</ele></trkpt>
      <trkpt lat="63.2" lon="9.2"><ele>120</ele></trkpt>
      <trkpt lat="63.3" lon="9.3"><ele>150</ele></trkpt>
    </trkseg>
  </trk>
</gpx>
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gpx", delete=False
        ) as tmp:
            tmp.write(gpx)
            path = tmp.name

        try:
            self.assertEqual(gpx_elevation_gain(path), 60.0)
            track = next(read_gpx_file(path))
            self.assertEqual(track["segments"][0]["elevation-up"], 60.0)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_gpx_elevation_gain_returns_none_without_elevation(self):
        gpx = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test"
  xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <trkseg>
      <trkpt lat="63.0" lon="9.0"></trkpt>
      <trkpt lat="63.1" lon="9.1"></trkpt>
    </trkseg>
  </trk>
</gpx>
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gpx", delete=False
        ) as tmp:
            tmp.write(gpx)
            path = tmp.name

        try:
            self.assertIsNone(gpx_elevation_gain(path))
        finally:
            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
