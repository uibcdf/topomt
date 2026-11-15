"""Retained volume requests and bounds never hide unmet original precision."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from devtools.reference_validator.model import Model, decode_scalar, record_digest
from devtools.reference_validator.region_volume import load_region_bundle
from devtools.reference_validator.verify.region_volume import check_region_volume
from devtools.reference_validator.volume_request import VolumeRequest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_region_volume_v1'


def _read(path):
    return json.loads(path.read_text())


def _jobs():
    for job in _read(BASE / 'plan.json')['jobs']:
        protocol = ROOT / job['protocol']
        assert hashlib.sha256(protocol.read_bytes()).hexdigest() == job['sha256']
        yield job, protocol.parent, _read(protocol)


def test_every_frozen_volume_protocol_has_complete_saved_receiving():
    jobs = list(_jobs())
    assert len(jobs) == 29
    assert sum(j['category'] == 'original' for j, _, _ in jobs) == 19
    for _, folder, spec in jobs:
        execution = _read(folder / 'execution.json')
        receipt = _read(folder / 'receiving/receipt.json')
        assert execution['exit_code'] == 0
        assert execution['stop_reason'] is None
        assert execution['receiving_status'] == 'completed'
        assert receipt['source_revision'] == execution['source_revision']
        assert receipt['model_sha256'] == record_digest(spec['model'])
        assert len(execution['cpu_affinity']) == 1
        assert execution['resource_policy']['address_space_limit_bytes'] == 2 * 1024**3
        assert all(s['host']['safe'] for s in execution['host_samples'])
        assert (
            hashlib.sha256((folder / 'execution.log').read_bytes()).hexdigest()
            == execution['log_sha256']
        )
        assert (
            receipt['protocol_sha256']
            == execution['protocol_sha256']
            == hashlib.sha256((folder / 'protocol.json').read_bytes()).hexdigest()
        )
        for relative, digest in execution['files'].items():
            assert (
                hashlib.sha256((folder / relative).read_bytes()).hexdigest() == digest
            )
        for relative, digest in receipt['files'].items():
            assert (
                hashlib.sha256(
                    (folder / 'receiving' / relative).read_bytes()
                ).hexdigest()
                == digest
            )


def test_original_precision_dispositions_match_both_constraints_for_every_region():
    original = 0
    for job, folder, spec in _jobs():
        if job['category'] != 'original':
            continue
        original += 1
        receipt = _read(folder / 'receiving/receipt.json')
        request = VolumeRequest.from_record(receipt['request'])
        assert spec['k'] == receipt['k'] == 24
        assert request.relative == Fraction(1, 2**24)
        assert request.absolute_nm3 > 0
        result = _read(ROOT / receipt['steps'][-1]['verification'])
        assert result['topology_complete'] is True
        assert result['volume_enclosure_status'] == 'resolved'
        total_ok = request.satisfied(
            decode_scalar(result['volume_lower']), decode_scalar(result['volume_upper'])
        )
        region_ok = []
        for row in result['regions']:
            lower, upper = map(decode_scalar, [row['lower'], row['upper']])
            accepted = request.satisfied(lower, upper)
            assert (row['precision_status'] == 'resolved') == accepted
            region_ok.append(accepted)
        assert (result['total_precision_status'] == 'resolved') == total_ok
        assert (result['precision_status'] == 'resolved') == (
            total_ok and all(region_ok)
        )
        if not result['regions']:
            assert result['volume_lower'] == result['volume_upper'] == ['0', '1']
            assert result['precision_status'] == 'resolved'
        else:
            assert result['precision_status'] == 'unresolved'
    assert original == 19


def test_analytic_ladder_is_checked_but_tiny_regions_are_not_removed():
    for k in [8, 16, 24, 32]:
        folder = BASE / f'controls/contained_ball_k{k}/receiving/leaves_1'
        model = Model.from_record(_read(folder / 'model.json'))
        cert = load_region_bundle(folder, model)
        result = check_region_volume(model, cert)
        assert result['precision_status'] == 'resolved'
        assert len(result['regions']) == 1
        assert result['regions'][0]['lower'] == result['volume_lower']
    tiny = _read(
        BASE / 'controls/tiny_eight_corners/receiving/leaves_512/verification.json'
    )
    assert len(tiny['regions']) == 8
    assert all(decode_scalar(r['upper']) > 0 for r in tiny['regions'])
    assert tiny['precision_status'] == 'unresolved'


def test_original_saved_refinement_retains_lineage_and_nested_bounds():
    from devtools.reference_validator.verify.region_volume import (
        check_volume_transition,
    )

    folder = BASE / 'refinement/regular_tetrahedron_1_4/receiving'
    previous = None
    widths = []
    for ceiling in [1, 8, 64, 512, 4096]:
        step = folder / f'leaves_{ceiling}'
        model = Model.from_record(_read(step / 'model.json'))
        cert = load_region_bundle(step, model)
        result = check_region_volume(model, cert)
        assert result['n_components'] == 1
        assert result['precision_status'] == 'unresolved'
        if previous is not None:
            assert (
                check_volume_transition(model, previous, cert)['lineage_status']
                == 'checked'
            )
        previous = cert
        widths.append(
            decode_scalar(result['volume_upper'])
            - decode_scalar(result['volume_lower'])
        )
    assert all(b <= a for a, b in zip(widths, widths[1:]))
    assert widths[-1] < widths[0]
