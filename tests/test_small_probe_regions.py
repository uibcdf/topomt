"""Covered-cycle winding separates independently counted free face regions."""

import copy

import numpy as np
import pytest

from devtools.verify_small_probe_boundary import build_face_certificate
from devtools.verify_small_probe_regions import build_face_regions, verify_face_regions

TRIANGLE = np.array([[0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [0.0, 4.0, 0.0]])
CENTERS = np.array([[1.0, 1.0, 0.0]])


def certificate():
    convex = build_face_certificate(TRIANGLE, CENTERS, 1.2)
    regions = build_face_regions(TRIANGLE, CENTERS, 1.2, convex)
    return convex, regions


def test_winding_witnesses_exhaust_two_free_components_without_production_geometry():
    convex, regions = certificate()
    result = verify_face_regions(TRIANGLE, CENTERS, 1.2, convex, regions)
    assert result['free_components'] == 2
    assert result['localization'] == 'resolved'
    assert len({tuple(row['winding_signature']) for row in regions['regions']}) == 2


@pytest.mark.parametrize(
    'damage', ['missing', 'duplicate', 'blocked', 'label', 'cycle']
)
def test_false_or_incomplete_localization_is_rejected(damage):
    convex, regions = certificate()
    damaged = copy.deepcopy(regions)
    if damage == 'missing':
        damaged['regions'].pop()
    elif damage == 'duplicate':
        damaged['regions'][1] = copy.deepcopy(damaged['regions'][0])
    elif damage == 'blocked':
        damaged['regions'][0]['barycentric_weights'] = [0.5, 0.25, 0.25]
    elif damage == 'label':
        damaged['regions'][0]['winding_signature'][0] ^= 1
    else:
        damaged['cycles'][0][0] = 999
    with pytest.raises(ValueError):
        verify_face_regions(TRIANGLE, CENTERS, 1.2, convex, damaged)


def test_frozen_two_region_face_needs_more_than_a_coarse_grid():
    import json
    from pathlib import Path

    from devtools.verify_small_probe_boundary import _model

    case = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/closed_shell'
    )
    data = case / 'artifacts/small_probe_boundary_v1'
    centers, radius, tolerance, *_ = _model(
        case / 'artifacts/closed_shell_v1/input.json', data / 'protocol.json'
    )
    certificate = json.loads((data / 'certificate_candidate.json').read_text())
    row = next(
        row for row in certificate['faces'] if row['atom_indices'] == [18, 31, 39]
    )
    triangle = centers[row['atom_indices']]
    result = build_face_regions(
        triangle, centers, radius, row['convex_intersections'], tolerance=tolerance
    )
    assert (
        verify_face_regions(
            triangle,
            centers,
            radius,
            row['convex_intersections'],
            result,
            tolerance=tolerance,
        )['free_components']
        == 2
    )


@pytest.fixture(scope='module')
def frozen_region_panel():
    from pathlib import Path

    from devtools.verify_small_probe_regions import build_region_certificate

    case = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/closed_shell'
    )
    inputs = case / 'artifacts/closed_shell_v1/input.json'
    protocol = case / 'artifacts/small_probe_boundary_v2/protocol.json'
    prior = case / 'artifacts/small_probe_boundary_v1/certificate_candidate.json'
    certificate = build_region_certificate(inputs, protocol, prior)
    return inputs, protocol, certificate


def test_complete_reference_matches_actual_raw_physical_results(frozen_region_panel):
    from devtools.verify_small_probe_regions import verify_region_certificate
    from tests.test_benchlab_public_topography import public_result

    inputs, protocol, certificate = frozen_region_panel
    verified = verify_region_certificate(inputs, protocol, certificate)
    native = public_result('closed_shell', 0.05)[0].dfnd.raw['boundary_connectivity']
    assert native['status'] == 'resolved'
    assert native['n_patches'] == verified['opening_component_count']
    reference_counts = {
        tuple(row['atom_indices']): len(row['localization']['regions'])
        for row in certificate['faces']
    }
    native_counts = {
        tuple(sorted(row['source_atom_indices'])): len(row['regions'])
        for row in native['surface']['faces']
    }
    assert reference_counts == native_counts


@pytest.mark.parametrize('damage', ['seam', 'assignment', 'region', 'witness'])
def test_global_reference_rejects_incomplete_or_false_region_attachments(
    frozen_region_panel, damage
):
    from devtools.verify_small_probe_regions import verify_region_certificate

    inputs, protocol, certificate = frozen_region_panel
    broken = copy.deepcopy(certificate)
    if damage == 'seam':
        broken['seams'].pop()
    elif damage == 'region':
        row = next(
            row for row in broken['faces'] if len(row['localization']['regions']) > 1
        )
        row['localization']['regions'].pop()
    elif damage == 'witness':
        row = next(row for row in broken['faces'] if row['localization']['regions'])
        row['localization']['regions'][0]['barycentric_weights'] = [1.0, 0.0, 0.0]
    else:
        side = next(
            side
            for seam in broken['seams']
            for connection in seam['connections']
            for side in connection
        )
        side['region_index'] = len(
            broken['faces'][side['face_index']]['localization']['regions']
        )
    with pytest.raises(ValueError):
        verify_region_certificate(inputs, protocol, broken)


def test_all_independent_patches_have_a_common_origin_path_witness(frozen_region_panel):
    from devtools.verify_small_probe_regions import (
        build_origin_paths,
        verify_region_certificate,
    )

    inputs, protocol, certificate = frozen_region_panel
    received = copy.deepcopy(certificate)
    received['origin_paths'] = build_origin_paths(inputs, protocol, certificate)
    verified = verify_region_certificate(inputs, protocol, received)
    assert verified['origin_path_status'] == 'resolved'
    assert (
        verified['origin_connected_patch_count'] == verified['opening_component_count']
    )
    for path in received['origin_paths']:
        path['ray_direction'] = [0.0, 0.0, 0.0]
        break
    with pytest.raises(ValueError):
        verify_region_certificate(inputs, protocol, received)


def test_retained_reference_replays_without_discovery_or_production(monkeypatch):
    import json
    from pathlib import Path

    from devtools import verify_small_probe_regions as reference

    def forbidden(*args, **kwargs):
        raise AssertionError('Retained verification must not discover new witnesses')

    monkeypatch.setattr(reference, 'build_region_certificate', forbidden)
    monkeypatch.setattr(reference, 'build_face_regions', forbidden)
    case = (
        Path(__file__).resolve().parents[1]
        / 'docs/content/benchlab/synthetic/closed_shell'
    )
    folder = case / 'artifacts/small_probe_boundary_v2'
    result = reference.verify_region_certificate(
        case / 'artifacts/closed_shell_v1/input.json',
        folder / 'protocol.json',
        json.loads((folder / 'certificate.json').read_text()),
    )
    retained = json.loads((folder / 'verification.json').read_text())
    assert result == retained
    assert result['opening_component_count'] == 13
    assert result['origin_connected_patch_count'] == 13
