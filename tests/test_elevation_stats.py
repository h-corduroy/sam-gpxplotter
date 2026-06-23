import numpy as np
import pytest

from gpxplotter import elevation_gain, elevation_loss, read_gpx_file
from gpxplotter.gpxread import elevation_gain as elevation_gain_direct


@pytest.mark.parametrize(
    "elevations, expected",
    [
        ([], 0.0),
        ([100.0], 0.0),
        ([100.0, 110.0, 105.0], 10.0),
        ([100.0, np.nan, 120.0], 0.0),
        ([100.0, 110.0, np.nan, 130.0], 10.0),
    ],
)
def test_elevation_gain(elevations, expected):
    assert elevation_gain(elevations) == pytest.approx(expected)
    assert elevation_gain_direct(elevations) == pytest.approx(expected)


def test_elevation_loss_matches_negative_descents():
    elevations = [100.0, 90.0, 95.0, 80.0]
    assert elevation_loss(elevations) == pytest.approx(-25.0)


def test_read_gpx_file_sets_segment_elevation_up():
    for track in read_gpx_file("gpx_files/ruten.gpx"):
        for segment in track["segments"]:
            assert segment["elevation-up"] == pytest.approx(
                elevation_gain(segment["elevation"])
            )
            assert len(segment["elevation"]) == len(segment["lat"])
            return
