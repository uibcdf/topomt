"""Independent model and evidence guards for the tetrahedron comparison stage."""

import hashlib
import json
from pathlib import Path

import numpy as np
from pyunitwizard import QuantityRecord

from topomt import pyunitwizard as puw

CASE = (
    Path(__file__).resolve().parents[1]
    / 'docs/content/benchlab/synthetic/regular_tetrahedron'
)
DIRECTORY = CASE / 'artifacts/comparisons_v1'


def scalar(record, field, unit):
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return float(puw.get_value(quantity, to_unit=unit))


def test_tetrahedron_comparison_protocol_preserves_inputs_and_declares_controls():
    protocol = json.loads((DIRECTORY / 'protocol.json').read_text())
    assert protocol['schema'] == 'topomt.benchlab.comparison-protocol/1'
    assert protocol['case_id'] == 'regular_tetrahedron'
    for relative, checksum in protocol['preserved_files'].items():
        assert hashlib.sha256((CASE / relative).read_bytes()).hexdigest() == checksum
    assert (
        protocol['preserved_files']['artifacts/regular_tetrahedron_v1/input.json']
        == '8634f70afdaf21cb8388887f5f80ae73dc36ef4f043198a10b525a93ebde5ce3'
    )
    canonical = (
        (CASE / 'artifacts/regular_tetrahedron_v1/input.pdb').read_bytes().splitlines()
    )
    exported = (CASE / protocol['source_file']).read_bytes().splitlines()
    assert [line[6:] for line in canonical] == [line[6:] for line in exported]
    assert protocol['execute_services'] is False
    assert protocol['workers'] == 1
    runs = protocol['runs']
    assert len(runs) == 14
    assert len({run['id'] for run in runs}) == len(runs)
    for provider in ('pykvfinder', 'ghecom', 'caver', 'mole'):
        selected = [run for run in runs if run['method'] == provider]
        assert selected[0]['scenario'] == 'standard'
        assert selected[0]['id'] == provider + '-standard'
        if provider != 'mole':
            assert [
                scalar(row['probe_label'], 'probe_label', 'angstroms')
                for row in selected[1:]
            ] == [1.2, 1.4, 1.7]
    assert all(run['probe_label'] is None for run in runs if run['method'] == 'mole')


def test_tetrahedron_radius_audit_separates_atomic_models_and_rounding_topology():
    audit = json.loads((DIRECTORY / 'model_audit.json').read_text())
    r_native = scalar(audit['radii']['native']['radius'], 'radius', 'angstroms')
    r_grid = scalar(audit['radii']['pykvfinder']['radius'], 'radius', 'angstroms')
    r_mole = scalar(audit['radii']['mole']['radius'], 'radius', 'angstroms')
    assert (r_native, r_grid, r_mole) == (1.7, 1.66, 1.61)
    assert audit['radii']['pykvfinder']['evidence_mode'] == 'original_read_pdb'
    assert (
        audit['radii']['mole']['evidence_mode'] == 'pinned_source_default_no_override'
    )
    edge = 5.3
    rounded = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ]
    )
    actual_edge = np.linalg.norm(rounded[0] - rounded[1])
    assert edge / np.sqrt(3) - r_grid < 1.4 < actual_edge / np.sqrt(3) - r_grid
    assert edge / np.sqrt(3) - r_native < 1.4 < edge * np.sqrt(6) / 4 - r_native
    assert actual_edge / np.sqrt(3) - r_mole > 1.4
    assert (
        audit['clearance_interpretation']
        == 'Independent ball-model implications, not detector predictions'
    )
