"""Tests for the top-level public surface of topomt.tools."""

import topomt.tools as tools


def test_tools_package_exports_main_subpackages():

    assert tools.__all__ == ['features', 'geometry', 'tessellation']
    assert tools.features is not None
    assert tools.geometry is not None
    assert tools.tessellation is not None


def test_tools_subpackages_expose_expected_helpers():

    assert hasattr(tools.geometry, 'triangle_area')
    assert hasattr(tools.geometry, 'convex_hull_metrics')
    assert hasattr(tools.geometry, 'marching_cubes_union')
    assert hasattr(tools.geometry, 'clip_mesh_with_plane')
    assert hasattr(tools.geometry, 'union_volume_monte_carlo')

    assert hasattr(tools.tessellation, 'analytic_tetra_volume')
    assert hasattr(tools.tessellation, 'mouth_area_from_faces')
    assert hasattr(tools.tessellation, 'representative_points_from_tetra')

    assert hasattr(tools.features.common, 'bounding_metrics')
    assert hasattr(tools.features.common, 'jaccard_overlap_clusters')
    assert hasattr(tools.features.channels, 'cross_section_profile')
    assert hasattr(tools.features.mouths, 'mouth_area_on_plane')
    assert hasattr(tools.features.pockets, 'get_physicochemical_properties')
    assert hasattr(tools.features.pockets, 'simple_ranking')
