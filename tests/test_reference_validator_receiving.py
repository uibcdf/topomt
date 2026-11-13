"""A real frozen model is decoded through the owning quantity codec."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from devtools.reference_validator.model import Model
from devtools.reference_validator.producer import partition
from devtools.reference_validator.receiving import freeze_tetrahedron
from devtools.reference_validator.verify import verify

ROOT = Path(__file__).resolve().parents[1]
INPUT = (
    ROOT
    / 'docs/content/benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.json'
)


def test_real_tetrahedron_has_an_exact_negative_control_and_roundtrip():
    model = freeze_tetrahedron(INPUT, probe_angstroms=1.7)
    assert len(model.atoms) == 4
    assert model.interpretation == 'received_binary64_nm'
    assert Model.from_record(json.loads(json.dumps(model.to_record()))) == model
    early = verify(model, partition(model, max_depth=10, max_leaves=1024))
    assert early['topology_complete'] is False
    checked = verify(model, partition(model, max_depth=18, max_leaves=1024))
    assert checked['n_components'] == 0 and checked['topology_complete']


def test_receiving_does_not_replace_a_general_hull_with_a_box():
    shell = (
        ROOT
        / 'docs/content/benchlab/synthetic/closed_shell/artifacts/closed_shell_v1/input.json'
    )
    with pytest.raises(ValueError, match='four'):
        freeze_tetrahedron(shell, probe_angstroms=1.4)


def test_damaged_quantity_record_is_rejected(tmp_path):
    from pyunitwizard.record import RecordError

    value = json.loads(INPUT.read_text())
    value['coordinates']['values'][0][0] += 1
    damaged = tmp_path / 'damaged.json'
    damaged.write_text(json.dumps(value))
    with pytest.raises(RecordError):
        freeze_tetrahedron(damaged, probe_angstroms=1.4)


def test_cli_freezes_a_reusable_exact_model(tmp_path):
    destination = tmp_path / 'model.json'
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'devtools.reference_validator',
            'freeze-tetrahedron',
            str(INPUT),
            str(destination),
            '--probe-angstroms',
            '1.7',
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    model = Model.from_record(json.loads(destination.read_text()))
    assert json.loads(result.stdout)['model_sha256'] == model.digest


def test_pilot_captures_replayable_proofs_with_actual_resource_limits(tmp_path):
    protocol = ROOT / 'devguide/evidence/reference_validator_p0_v1/protocol.json'
    output = tmp_path / 'receiving'
    script = """
import os, resource, sys
from pathlib import Path
os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
from devtools.reference_validator.capture import capture
capture(Path(sys.argv[1]), Path(sys.argv[2]))
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(protocol), str(output)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads((output / 'receipt.json').read_text())
    assert len(receipt['models']) == 10
    assert receipt['address_space_limit_bytes'] == 2 * 1024**3
    for name, expected in receipt['files'].items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == expected
    for row in receipt['models']:
        model = Model.from_record(
            json.loads((output / f'{row["id"]}.model.json').read_text())
        )
        cert = json.loads((output / f'{row["id"]}.certificate.json').read_text())
        report = verify(model, cert)
        assert report['n_components'] == row['n_components']
    # Evidence is append-only, including retained unresolved results.
    rerun = subprocess.run(
        [sys.executable, '-c', script, str(protocol), str(output)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert rerun.returncode != 0
