from pathlib import Path
import shutil
import tempfile

import pytest
import topomt as tmt

from topomt.methods.fpocket4 import fpocket4
from topomt.wrappers.fpocket.integration import load_topography_from_fpocket_output
from topomt.wrappers.fpocket.parser import parse_fpocket_output
from topomt.wrappers.fpocket.runner import run_fpocket


REPO_ROOT = Path(__file__).resolve().parents[1]
FP_3LKF_PDB = REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF.pdb'
FP_3LKF_OUT = REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF_out'
FP_1TCD_PDB = REPO_ROOT / 'topomt' / 'wrappers' / 'fpocket' / '1tcd.pdb'
FP_1TCD_OUT = REPO_ROOT / 'topomt' / 'wrappers' / 'fpocket' / '1tcd_out'

PDB_PARITY_SYSTEMS = [
    ('1TCD.pdb', Path(tmt.demo['TcTIM']['1TCD.pdb'])),
    ('1GG0.pdb', Path(tmt.demo['fpocket']['1GG0.pdb'])),
    ('1N57.pdb', Path(tmt.demo['fpocket']['1N57.pdb'])),
    ('2GI9.pdb', Path(tmt.demo['fpocket']['2GI9.pdb'])),
    ('2H05.pdb', Path(tmt.demo['fpocket']['2H05.pdb'])),
    ('3LKF.pdb', Path(tmt.demo['fpocket']['3LKF.pdb'])),
    ('E15ALA.pdb', Path(tmt.demo['fpocket']['E15ALA.pdb'])),
]

BCIF_PARITY_SYSTEMS = [
    (
        '1TCD',
        Path(REPO_ROOT / 'topomt' / 'data' / 'TcTIM' / 'CASTp_1tcd' / '1tcd.pdb'),
        Path(REPO_ROOT / 'topomt' / 'data' / 'TcTIM' / 'CASTp_1tcd' / '1tcd.bcif.gz'),
    ),
    (
        '3LKF',
        Path(REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF.pdb'),
        Path(REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF.bcif.gz'),
    ),
    (
        '1N57',
        Path(REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '1N57.pdb'),
        Path(REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '1N57.bcif.gz'),
    ),
]


def test_parse_fpocket_output_keeps_reported_pocket_ranking_for_3lkf():

    result = parse_fpocket_output(FP_3LKF_PDB, FP_3LKF_OUT)

    assert len(result.pockets) == 7
    assert [pocket.pocket_id for pocket in result.pockets] == [1, 2, 3, 4, 5, 6, 7]
    assert [pocket.file_pocket_id for pocket in result.pockets] == [0, 1, 2, 3, 4, 5, 6]

    first_pocket = result.pockets[0]
    assert first_pocket.score == pytest.approx(33.9933, abs=1.0e-4)
    assert first_pocket.druggability_score == pytest.approx(0.4015, abs=1.0e-4)
    assert first_pocket.n_alpha_spheres == 76
    assert len(first_pocket.atom_serials) == 37
    assert first_pocket.atom_serials[:5] == [1305, 1322, 1311, 1480, 1324]


def test_parse_fpocket_output_extracts_alpha_sphere_geometry_for_1tcd():

    result = parse_fpocket_output(FP_1TCD_PDB, FP_1TCD_OUT)

    assert len(result.pockets) == 23

    first_pocket = result.pockets[0]
    assert first_pocket.pocket_id == 1
    assert first_pocket.file_pocket_id == 1
    assert first_pocket.center is not None
    assert first_pocket.alpha_sphere_centers.shape == (60, 3)
    assert first_pocket.alpha_sphere_radii.shape == (60,)
    assert first_pocket.n_alpha_spheres == 60
    assert first_pocket.volume == pytest.approx(551.2957, abs=1.0e-4)
    assert first_pocket.convex_hull_volume == pytest.approx(93.0196, abs=1.0e-4)
    assert first_pocket.apolar_alpha_sphere_ratio == pytest.approx(0.1333, abs=1.0e-4)


def test_load_topography_from_fpocket_output_maps_atoms_for_3lkf():

    topography = load_topography_from_fpocket_output(FP_3LKF_PDB, FP_3LKF_PDB, FP_3LKF_OUT)

    assert len(topography) == 7

    pocket = topography['POC-1']
    assert pocket.source == 'fpocket'
    assert pocket.source_id == 'fpocket:1'
    assert pocket.score == pytest.approx(33.9933, abs=1.0e-4)
    assert pocket.druggability_score == pytest.approx(0.4015, abs=1.0e-4)
    assert pocket.volume == pytest.approx(645.3032, abs=1.0e-4)
    assert pocket.n_alpha_spheres == 76
    assert len(pocket.atom_indices) == 37
    assert min(pocket.atom_indices) >= 0


def _assert_topographies_match(topography, reference):

    assert list(topography) == list(reference)
    assert len(topography) == len(reference)

    for feature_id in topography:
        pocket = topography[feature_id]
        pocket_ref = reference[feature_id]
        assert pocket.source == 'fpocket'
        assert pocket.source_id == pocket_ref.source_id
        assert pocket.atom_indices == pocket_ref.atom_indices
        assert pocket.score == pytest.approx(pocket_ref.score, abs=1.0e-4)
        assert pocket.druggability_score == pytest.approx(
            pocket_ref.druggability_score, abs=1.0e-4
        )


@pytest.mark.skipif(shutil.which('fpocket') is None, reason='fpocket not available')
@pytest.mark.parametrize(
    ('label', 'source_pdb'),
    PDB_PARITY_SYSTEMS,
    ids=[item[0] for item in PDB_PARITY_SYSTEMS],
)
def test_fpocket4_matches_direct_fpocket_run_for_supported_pdb_inputs(label, source_pdb):

    topography = fpocket4(source_pdb)

    with tempfile.TemporaryDirectory(prefix='topomt_test_fpocket4_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        local_pdb = tmpdir / source_pdb.name
        shutil.copy2(source_pdb, local_pdb)
        output_dir = run_fpocket(local_pdb, workdir=tmpdir)
        reference = load_topography_from_fpocket_output(local_pdb, local_pdb, output_dir)

    _assert_topographies_match(topography, reference)


@pytest.mark.skipif(shutil.which('fpocket') is None, reason='fpocket not available')
@pytest.mark.parametrize(
    ('label', 'source_pdb', 'source_bcif'),
    BCIF_PARITY_SYSTEMS,
    ids=[item[0] for item in BCIF_PARITY_SYSTEMS],
)
def test_fpocket4_matches_pdb_and_bcif_inputs_when_bcif_is_available(
    label,
    source_pdb,
    source_bcif,
):

    if not source_bcif.exists():
        pytest.skip(f'bcif.gz fixture not available for {label}')

    topography_from_pdb = fpocket4(source_pdb)
    topography_from_bcif = fpocket4(source_bcif)

    _assert_topographies_match(topography_from_pdb, topography_from_bcif)
