"""A real original-engine execution must survive a detached file handoff."""

import os
from pathlib import Path

import pytest

import topomt as tmt
from devtools.qualify_fpocket_handoff import qualify

COMMAND = os.environ.get('TOPOMT_FPOCKET_CMD', 'fpocket')


@pytest.mark.skipif(
    not os.environ.get('TOPOMT_FPOCKET_CMD'),
    reason='source pilot requires an explicit TOPOMT_FPOCKET_CMD and compatible MolSysMT',
)
def test_real_fpocket_handoff_preserves_source_context_and_results(tmp_path):
    source = Path(tmt.__file__).parent / 'data/CASTp_3.0_server/3ptb.pdb'
    destination = tmp_path / 'handoff'
    receipt = qualify(source, COMMAND, destination)
    assert receipt['pocket_count'] > 0
    assert receipt['selection_is_nonconsecutive']
    assert receipt['structure_index'] == 1
    assert receipt['chemical_state']['reference_index'] == 0
    assert all(receipt['checks'].values())
    assert (destination / 'original.zip').is_file()
    assert (destination / 'source.h5msm').is_file()
    assert (destination / 'receipt.json').is_file()
