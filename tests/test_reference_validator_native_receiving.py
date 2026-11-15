"""Full original negative carriers require exact native/reference Model equality."""

import hashlib
import json
from pathlib import Path

from devtools.reference_validator.model import decode_scalar, record_digest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_native_comparison_v1'


def _read(path):
    return json.loads(path.read_text())


def test_actual_native_arrays_match_reference_before_whole_carrier_exclusion():
    expected = {
        'straight_tube_narrow_dense': (30, 3, 4),
        'straight_tube_wide_sparse': (1, 1, 2),
    }
    for job in _read(BASE / 'qualified_plan.json')['jobs']:
        protocol_path = ROOT / job['protocol']
        assert hashlib.sha256(protocol_path.read_bytes()).hexdigest() == job['sha256']
        spec = _read(protocol_path)
        folder = protocol_path.parent
        receipt = _read(folder / 'receiving/receipt.json')
        native = _read(folder / 'receiving/native_model.json')
        original = _read(ROOT / spec['reference_model'])
        assert native['domain'] == original['domain']
        assert [a['center'] for a in native['atoms']] == [
            a['center'] for a in original['atoms']
        ]
        assert native['probe'] == original['probe']
        assert native['atoms'] != original['atoms']
        assert receipt['original_reference_model_sha256'] == record_digest(original)
        proof = _read(folder / 'receiving/reference_certificate.json')
        target_check = _read(folder / 'receiving/reference_verification.json')
        assert proof['model_sha256'] == record_digest(native)
        assert target_check['topology_complete'] is True
        assert target_check['n_components'] == target_check['n_boundary_patches'] == 0
        assert (
            receipt['reference_origin']
            == 'saved_geometry_candidate_independently_checked_on_actual_native_inputs'
        )
        assert (
            receipt['native_model_sha256']
            == receipt['reference_model_sha256']
            == record_digest(native)
        )
        assert (
            receipt['native_execution']
            == 'fresh_public_receiving_of_canonical_nm_coordinates_and_native_vdw_radii'
        )
        comparison = _read(folder / 'receiving/comparison.json')
        public = _read(folder / 'receiving/native_public.json')['public_observation']
        npoints, ncarriers, npublic = expected[job['name']]
        assert len(comparison['points']) == npoints
        states = [p['point_state'] for p in comparison['points'].values()]
        assert all(state in {'blocked', 'outside_domain'} for state in states)
        assert states.count('outside_domain') == (8 if npoints == 30 else 1)
        assert (
            comparison['reference_region_count']
            == comparison['reference_boundary_patch_count']
            == 0
        )
        assert len(comparison['carriers']) == ncarriers
        assert len(public['public_features']) == npublic
        assert comparison['numerical_model_match'] == 'exact'
        assert comparison['morphology_status'] == 'not_inferred'
        for carrier in public['wet_components']:
            row = comparison['carriers'][carrier['component_id']]
            assert row['source_tetrahedra'] == carrier['tetrahedron_source_support']
            assert row['physical_state'] == 'empty'
            assert row['proof_route'] == 'whole_domain_exclusion'
            assert row['domain_containment'] == 'verified_by_convexity'
        execution = _read(folder / 'execution.json')
        assert execution['exit_code'] == 0 and execution['stop_reason'] is None
        assert len(execution['cpu_affinity']) == 1
        assert execution['resource_policy']['address_space_limit_bytes'] == 2 * 1024**3
        assert all(s['host']['safe'] for s in execution['host_samples'])
        for relative, digest in execution['files'].items():
            assert (
                hashlib.sha256((folder / relative).read_bytes()).hexdigest() == digest
            )
        assert (
            hashlib.sha256((folder / 'execution.log').read_bytes()).hexdigest()
            == execution['log_sha256']
        )


def test_roundtrip_and_radius_differences_remain_explicit_unmatched_history():
    failed = _read(BASE / 'straight_tube_narrow_dense/execution.json')
    assert failed['exit_code'] == 1 and failed['receiving_status'] == 'incomplete'
    assert not (BASE / 'straight_tube_narrow_dense/receiving/comparison.json').exists()
    diagnostic = _read(BASE / 'roundtrip_diagnostic/receiving/diagnostic.json')
    assert diagnostic['canonical_nm_equals_reference'] is True
    assert diagnostic['native_equals_angstrom_round_trip'] is True
    assert diagnostic['changed_coordinate_entries'] == 136
    assert decode_scalar(diagnostic['max_coordinate_difference_nm']) > 0
    assert decode_scalar(diagnostic['max_radius_difference_nm']) > 0
    assert decode_scalar(diagnostic['probe_difference_nm']) == 0
