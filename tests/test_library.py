"""Tests for gpxplotter library functions.

This test module verifies the folium_map.py functions for creating maps,
adding tiles, coloring segments, and adding markers.
"""
import pytest
import folium
import branca.colormap
import numpy as np

from gpxplotter import (
    create_folium_map,
    add_segment_to_map,
    read_gpx_file,
)
from gpxplotter.folium_map import (
    TILES,
    add_tiles_to_map,
    add_all_tiles,
    add_marker_at,
    add_start_top_markers,
    add_colored_line,
)


@pytest.fixture
def sample_segment():
    """Return a sample segment dictionary for testing."""
    return {
        "latlon": [(59.911491, 10.757933), (59.912491, 10.758933), (59.913491, 10.759933)],
        "elevation": np.array([25.0, 30.0, 28.0]),
        "hr": np.array([120, 130, 135]),
        "velocity-level": np.array([5.0, 5.5, 5.2]),
        "distance": np.array([0.0, 120.5, 245.3]),
    }


@pytest.fixture
def sample_segment_no_metrics():
    """Return a segment without heart rate or velocity data."""
    return {
        "latlon": [(59.911491, 10.757933), (59.912491, 10.758933)],
        "elevation": np.array([25.0, 30.0]),
    }


class TestCreateFoliumMap:
    """Tests for create_folium_map function."""

    @pytest.mark.unit
    def test_create_map_default(self):
        """Verify create_folium_map creates a valid Folium map."""
        the_map = create_folium_map()
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_create_map_with_openstreetmap_tiles(self):
        """Verify map can be created with openstreetmap tiles."""
        the_map = create_folium_map(tiles="openstreetmap")
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_create_map_with_cartodb_tiles(self):
        """Verify map can be created with CartoDB tiles."""
        the_map = create_folium_map(tiles="cartodb positron")
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_create_map_with_custom_tiles(self):
        """Verify map can be created with custom tiles from TILES dict."""
        for tile_name in TILES.keys():
            the_map = create_folium_map(tiles=tile_name)
            assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_create_map_with_location(self):
        """Verify map can be created with custom location."""
        the_map = create_folium_map(location=[59.911, 10.758], zoom_start=13)
        assert isinstance(the_map, folium.Map)


class TestAddTilesToMap:
    """Tests for tile management functions."""

    @pytest.mark.unit
    def test_add_tiles_to_map(self):
        """Verify tiles can be added to an existing map."""
        the_map = create_folium_map()
        add_tiles_to_map(the_map, "opentopomap")
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_all_tiles(self):
        """Verify all predefined tiles can be added to a map."""
        the_map = create_folium_map()
        add_all_tiles(the_map)
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_tiles_dict_structure(self):
        """Verify TILES dictionary has correct structure."""
        for tile_name, tile_config in TILES.items():
            assert "name" in tile_config
            assert "tiles" in tile_config
            assert "attr" in tile_config


class TestAddSegmentToMap:
    """Tests for add_segment_to_map function."""

    @pytest.mark.unit
    def test_add_plain_segment(self, sample_segment):
        """Verify a segment can be added without coloring."""
        the_map = create_folium_map()
        add_segment_to_map(the_map, sample_segment, color_by=None, fit_bounds=False)
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_segment_colored_by_hr(self, sample_segment):
        """Verify segment can be colored by heart rate."""
        the_map = create_folium_map()
        add_segment_to_map(the_map, sample_segment, color_by="hr", fit_bounds=False)
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_segment_colored_by_elevation(self, sample_segment):
        """Verify segment can be colored by elevation."""
        the_map = create_folium_map()
        add_segment_to_map(the_map, sample_segment, color_by="elevation", fit_bounds=False)
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_segment_colored_by_velocity(self, sample_segment):
        """Verify segment can be colored by velocity."""
        the_map = create_folium_map()
        add_segment_to_map(
            the_map, sample_segment, color_by="velocity-level", fit_bounds=False
        )
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_segment_with_custom_colormap(self, sample_segment):
        """Verify segment can use a custom colormap."""
        the_map = create_folium_map()
        custom_cmap = branca.colormap.linear.RdYlGn_11
        add_segment_to_map(
            the_map, sample_segment, color_by="hr", cmap=custom_cmap, fit_bounds=False
        )
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_segment_with_line_options(self, sample_segment):
        """Verify segment can be added with custom line options."""
        the_map = create_folium_map()
        line_options = {"weight": 8, "color": "#FF0000"}
        add_segment_to_map(
            the_map, sample_segment, line_options=line_options, fit_bounds=False
        )
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_segment_without_start_end_markers(self, sample_segment):
        """Verify segment can be added without start/end markers."""
        the_map = create_folium_map()
        add_segment_to_map(
            the_map, sample_segment, add_start_end=False, fit_bounds=False
        )
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_segment_with_min_max_values(self, sample_segment):
        """Verify segment coloring respects min/max values."""
        the_map = create_folium_map()
        add_segment_to_map(
            the_map,
            sample_segment,
            color_by="hr",
            min_value=100,
            max_value=150,
            fit_bounds=False,
        )
        assert isinstance(the_map, folium.Map)


class TestAddColoredLine:
    """Tests for add_colored_line function."""

    @pytest.mark.unit
    def test_add_colored_line_hr(self, sample_segment):
        """Verify colored line can be added for heart rate."""
        the_map = create_folium_map()
        add_colored_line(the_map, sample_segment, "hr")
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_colored_line_with_string_cmap(self, sample_segment):
        """Verify colored line works with string colormap name."""
        the_map = create_folium_map()
        add_colored_line(the_map, sample_segment, "hr", cmap="viridis")
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_colored_line_with_colormap_object(self, sample_segment):
        """Verify colored line works with ColorMap object."""
        the_map = create_folium_map()
        cmap = branca.colormap.linear.YlOrRd_09
        add_colored_line(the_map, sample_segment, "hr", cmap=cmap)
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_colored_line_invalid_cmap_raises(self, sample_segment):
        """Verify invalid colormap raises exception."""
        the_map = create_folium_map()
        with pytest.raises(Exception):
            add_colored_line(the_map, sample_segment, "hr", cmap=12345)


class TestMarkerFunctions:
    """Tests for marker-related functions."""

    @pytest.mark.unit
    def test_add_marker_at_start(self, sample_segment):
        """Verify marker can be added at start of segment."""
        the_map = create_folium_map()
        add_marker_at(the_map, sample_segment, 0, "Start")
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_marker_at_end(self, sample_segment):
        """Verify marker can be added at end of segment."""
        the_map = create_folium_map()
        add_marker_at(the_map, sample_segment, -1, "End")
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_marker_with_custom_icon(self, sample_segment):
        """Verify marker can be added with custom icon options."""
        the_map = create_folium_map()
        add_marker_at(
            the_map, sample_segment, 0, "Custom", icon="star", color="red"
        )
        assert isinstance(the_map, folium.Map)

    @pytest.mark.unit
    def test_add_start_top_markers(self, sample_segment):
        """Verify start and end markers can be added together."""
        the_map = create_folium_map()
        add_start_top_markers(the_map, sample_segment)
        assert isinstance(the_map, folium.Map)


class TestMapRendering:
    """Integration tests for rendering complete maps."""

    @pytest.mark.integration
    def test_render_map_html(self, sample_segment):
        """Verify map can be rendered to HTML."""
        the_map = create_folium_map()
        add_segment_to_map(the_map, sample_segment, color_by="hr")
        html = the_map.get_root().render()
        assert isinstance(html, str)
        assert len(html) > 0
        assert "leaflet" in html.lower()

    @pytest.mark.integration
    def test_render_map_with_multiple_segments(self, sample_segment):
        """Verify map can render multiple segments."""
        the_map = create_folium_map()
        add_segment_to_map(the_map, sample_segment, color_by="hr", fit_bounds=False)
        
        segment2 = sample_segment.copy()
        segment2["latlon"] = [(60.0, 11.0), (60.01, 11.01)]
        segment2["hr"] = np.array([140, 145])
        add_segment_to_map(the_map, segment2, color_by="hr", fit_bounds=False)
        
        html = the_map.get_root().render()
        assert isinstance(html, str)
        assert "leaflet" in html.lower()

    @pytest.mark.integration
    def test_render_map_without_metrics(self, sample_segment_no_metrics):
        """Verify map renders correctly when metrics are missing."""
        the_map = create_folium_map()
        add_segment_to_map(the_map, sample_segment_no_metrics, color_by=None)
        html = the_map.get_root().render()
        assert isinstance(html, str)
        assert "leaflet" in html.lower()
