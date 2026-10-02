import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import numpy as np
import pytest

from devtools.castp.audit_castp3_flow import (
    _match_bulbs,
    _minimum_reachable_sinks,
    audit_flow_archive,
)


def test_minimum_reachable_sink_preserves_finite_branch_against_exterior():
    # Node 0 can reach both finite sink 2 and the exterior marker 3.
    successors = [[1, 3], [2], [], []]
    ranks = [1, 2, 5]
    result = _minimum_reachable_sinks(successors, ranks, infinity=3)
    np.testing.assert_array_equal(result, [2, 2, 2])
    assert successors == [[1, 3], [2], [], []]


def test_minimum_reachable_sink_selects_lowest_terminal_rank():
    result = _minimum_reachable_sinks([[1, 2], [], [], []], [1, 8, 6], 3)
    np.testing.assert_array_equal(result, [2, 1, 2])


def test_minimum_reachable_sink_keeps_hull_only_paths_exterior():
    result = _minimum_reachable_sinks([[1], [2], []], [1, 3], 2)
    np.testing.assert_array_equal(result, [2, 2])


def test_minimum_reachable_sink_rejects_unresolved_cycles():
    with pytest.raises(ValueError, match='cycle'):
        _minimum_reachable_sinks([[1], [0], []], [1, 1], 2)


def test_bulb_matching_requires_empty_compatible_four_atom_support():
    coordinates = np.asarray(
        [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]
    ) * np.sqrt(5 / 3)
    geometry = SimpleNamespace(
        atom_coordinates=coordinates,
        atom_radii=np.full(4, 2.0),
        solvent_radius=1.4,
        mesh=SimpleNamespace(
            simplex_centers=np.zeros((1, 3)),
            simplex_atom_indices=np.asarray([[0, 1, 2, 3]]),
        ),
    )
    bulbs = [[{'c': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'r': 1.0}]]
    result = _match_bulbs(geometry, bulbs, np.asarray([11, 12, 13, 14]))
    match = result[0]['bulbs'][0]
    assert match['compatible']
    assert match['simplex'] == 0
    assert match['contact_serials'] == [11, 12, 13, 14]

    geometry.atom_coordinates = np.vstack([coordinates, np.zeros(3)])
    geometry.atom_radii = np.full(5, 2.0)
    result = _match_bulbs(geometry, bulbs, np.asarray([11, 12, 13, 14, 15]))
    assert not result[0]['bulbs'][0]['compatible']
    assert result[0]['bulbs'][0]['simplex'] is None

    # A fifth contact cannot identify a unique tetrahedral support from the
    # printed sphere alone; nearest-center lookup must not invent that identity.
    geometry.atom_coordinates[-1] = [np.sqrt(5), 0, 0]
    result = _match_bulbs(geometry, bulbs, np.asarray([11, 12, 13, 14, 15]))
    assert not result[0]['bulbs'][0]['compatible']
    assert result[0]['bulbs'][0]['simplex'] is None


def test_1stp_flow_audit_separates_bulb_geometry_from_final_atom_reporting():
    from topomt.third_party.castp3.core.castp_core import components

    original = components._compute_pocket_depths
    archive = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1stp.zip'
    )
    result = audit_flow_archive(archive)
    assert components._compute_pocket_depths is original
    minimum = result['variants']['minimum_reachable']
    assert minimum['geometry_validated_oracle_count'] == 9
    assert minimum['geometry_exact_count'] == minimum['geometry_native_count'] == 9
    assert all(row['exact'] for row in minimum['bulb_regions'])
    assert all(
        row['passed'] for row in minimum['component_vertex_memberships'].values()
    )
    # Reconstructing the bulb regions alone does not validate the current
    # attached-face atom-export rules or aggregate mouth records.
    assert not minimum['atom_memberships']['pocket']['passed']
    assert not minimum['atom_memberships']['mouth']['passed']
    target = next(row for row in result['bulbs'] if row['server_id'] == 3)
    support = next(bulb for bulb in target['bulbs'] if 592 in bulb['contact_serials'])
    assert support['compatible']
    trace = next(
        row for row in result['flow_trace'] if row['simplex'] == support['simplex']
    )
    assert trace['maximum_depth'] == result['infinity_marker']
    assert trace['minimum_depth'] != result['infinity_marker']


def test_pinned_flow_panel_keeps_source_identity_and_reporting_regressions():
    repository = Path(__file__).resolve().parents[3]
    report = json.loads(
        (
            repository
            / 'devguide/castp/artifacts/flow_audit_2026_10_02_1stp_controls.json'
        ).read_text()
    )
    assert report['complete']
    expected = {'1stp', '1crn', '1rop', '2pk4', '3phv', '1ifb', '1hew'}
    assert set(report['requested_cases']) == expected
    assert {case['case'] for case in report['cases']} == expected
    assert len(report['cases']) == len(expected)
    for case in report['cases']:
        archive = repository / 'topomt/data/CASTpFold_server' / f'{case["case"]}.zip'
        assert (
            case['archive_sha256'] == hashlib.sha256(archive.read_bytes()).hexdigest()
        )
        with ZipFile(archive) as source:
            pdb = next(name for name in source.namelist() if name.endswith('.pdb'))
            assert case['pdb_sha256'] == hashlib.sha256(source.read(pdb)).hexdigest()
        assert case['policy']['diagnostic_only']
        assert case['policy']['radii_model'] == 'castp3_protor'
        assert case['policy']['probe_radius_angstrom'] == 1.4
        assert all(
            bulb['compatible'] for region in case['bulbs'] for bulb in region['bulbs']
        )
        minimum = case['variants']['minimum_reachable']
        assert minimum['geometry_passed']
        assert minimum['geometry_oracle_region_count'] == len(case['bulbs'])
        assert (
            minimum['geometry_exact_count']
            == minimum['geometry_native_count']
            == len(case['bulbs'])
        )
        assert all(row['exact'] for row in minimum['bulb_regions'])
        assert all(
            row['passed'] for row in minimum['component_vertex_memberships'].values()
        )
    assert (
        sum(
            len(region['bulbs']) for case in report['cases'] for region in case['bulbs']
        )
        == 689
    )
    for policy, geometry, pockets, mouths in [
        ('maximum', 40, 28, 33),
        ('minimum_reachable', 50, 25, 23),
    ]:
        variants = [case['variants'][policy] for case in report['cases']]
        assert sum(row['geometry_exact_count'] for row in variants) == geometry
        assert (
            sum(row['atom_memberships']['pocket']['exact_count'] for row in variants)
            == pockets
        )
        assert (
            sum(row['atom_memberships']['mouth']['exact_count'] for row in variants)
            == mouths
        )
