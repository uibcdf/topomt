"""Archive-wide analytical comparisons retain mismatches and duplicate identity."""

from pathlib import Path

from devtools.castp.audit_castp3_void_measurements import (
    audit_archive_voids,
    compare_void_measurements,
)


def _void(serials, area=2.0):
    return {
        'atom_serials': serials,
        'area_sa': area,
        'area_ms': 3.0,
        'volume_sa': 4.0,
        'volume_ms': 5.0,
    }


def test_void_audit_keeps_membership_and_measure_failures_separate():
    report = compare_void_measurements(
        [_void([1, 2]), _void([3, 4])],
        [_void([1, 2], area=2.002), _void([5, 6])],
    )
    assert report['exact_memberships'] == 1
    assert report['passed_measures'] == 3
    assert report['failed_measures'] == 1
    assert report['missing_memberships'] == [[3, 4]]
    assert report['extra_memberships'] == [[5, 6]]
    assert not report['passed']
    assert report['measures'][0]['unit'] == 'angstrom**2'


def test_void_audit_does_not_collapse_duplicate_memberships():
    report = compare_void_measurements(
        [_void([1, 2]), _void([1, 2])], [_void([1, 2]), _void([1, 2])]
    )
    assert report['oracle_voids'] == report['native_voids'] == 2
    assert report['exact_memberships'] == 2
    assert report['ambiguous_memberships'] == [[1, 2]]
    assert report['passed_measures'] == report['failed_measures'] == 0
    assert not report['passed']


def test_void_audit_uses_absolute_server_rounding_allowance():
    assert compare_void_measurements([_void([1])], [_void([1], 2.00049)])['passed']
    assert not compare_void_measurements([_void([1])], [_void([1], 2.00051)])['passed']


def test_pinned_crambin_void_matches_all_four_server_measures():
    archive = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1crn.zip'
    )
    result = audit_archive_voids(archive)
    assert result['oracle_voids'] == result['native_voids'] == 1
    assert result['exact_memberships'] == 1
    assert result['passed_measures'] == 4
    assert result['failed_measures'] == 0
    assert result['passed']


def test_pinned_1cge_audit_retains_missing_voids_in_parity_denominator():
    """Track #85 honestly until all seven archived voids are reproduced."""
    archive = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1cge.zip'
    )
    result = audit_archive_voids(archive)
    assert result['oracle_voids'] == 7
    assert result['native_voids'] == result['exact_memberships'] == 4
    assert len(result['missing_memberships']) == 3
    assert result['passed_measures'] == 16
    assert result['failed_measures'] == 0
    assert not result['passed']
