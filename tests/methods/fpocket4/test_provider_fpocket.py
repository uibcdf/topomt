from pathlib import Path
import shutil
import tempfile

import pytest
import topomt as tmt
from topomt import pyunitwizard as puw


REPO_ROOT = Path(__file__).resolve().parents[3]
FP_3LKF_PDB = REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF.pdb'
FP_3LKF_OUT = REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF_out'


def test_fpocket_provider_load_topography_from_files():
    topography = tmt.third_party.fpocket.load_topography(
        FP_3LKF_PDB,
        pdb_file=FP_3LKF_PDB,
        output_dir=FP_3LKF_OUT,
    )

    assert len(topography) == 7
    pocket = topography['POC-1']
    assert pocket.source == 'fpocket'
    assert pocket.source_id == 'fpocket:1'
    assert pocket.score == pytest.approx(33.9933, abs=1.0e-4)


@pytest.mark.skipif(shutil.which('fpocket') is None, reason='fpocket not available')
def test_fpocket_provider_cli_matches_direct_wrapper_path():
    provider_topography = tmt.third_party.fpocket.get_topography(
        FP_3LKF_PDB,
        backend='cli',
    )
    wrapper_topography = tmt.third_party.fpocket.get_topography(
        FP_3LKF_PDB,
        backend='wrapper',
    )

    assert list(provider_topography) == list(wrapper_topography)
    assert len(provider_topography) == len(wrapper_topography)


def test_fpocket_provider_native_and_topomt_route():
    native_topography = tmt.third_party.fpocket.get_topography(
        FP_3LKF_PDB,
        backend='native',
    )
    topomt_topography = tmt.third_party.fpocket.get_topography(
        FP_3LKF_PDB,
        backend='topomt',
    )

    assert len(native_topography) > 0
    assert len(topomt_topography) > 0
    assert puw.is_quantity(native_topography['POC-1'].volume)
    assert puw.is_quantity(topomt_topography['POC-1'].volume)
