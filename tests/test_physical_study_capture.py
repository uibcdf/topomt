"""Frozen input/protocol receiving for the physical source checkpoint."""

import json
from pathlib import Path

import pytest

from devtools.benchlab.capture_physical import capture_case

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'docs/content/benchlab/synthetic/regular_tetrahedron'
PROTOCOL = CASE / 'artifacts/physical_refinement_v1/protocol.json'


def test_physical_capture_uses_actual_public_results_and_independent_reference():
    result = capture_case(CASE, PROTOCOL)
    assert result['reference_verification']['opening_component_count'] == 4
    assert [row['physical']['n_patches'] for row in result['queries']] == [4, 0, 0]
    assert [row['feature_types'] for row in result['queries']] == [
        ['percolating'],
        ['void'],
        [],
    ]
    assert (
        result['queries'][0]['physical']['component_associations']['status']
        == 'resolved'
    )


def test_physical_capture_rejects_a_changed_input_identity(tmp_path):
    protocol = json.loads(PROTOCOL.read_text())
    protocol['input_sha256'] = '0' * 64
    path = tmp_path / 'protocol.json'
    path.write_text(json.dumps(protocol))
    with pytest.raises(ValueError, match='input identity'):
        capture_case(CASE, path)


def test_capture_retains_the_selected_study_owner(tmp_path):
    protocol = json.loads(PROTOCOL.read_text())
    protocol['issue'] = 'uibcdf/topomt#76'
    path = tmp_path / 'protocol.json'
    path.write_text(json.dumps(protocol))
    assert capture_case(CASE, path)['issue'] == 'uibcdf/topomt#76'
