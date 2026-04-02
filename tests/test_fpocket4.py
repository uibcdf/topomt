import importlib
from pathlib import Path
import shutil
import tempfile

import numpy as np
import pytest
import topomt as tmt
import molsysmt as msm
from topomt import pyunitwizard as puw

from topomt.methods.fpocket4 import (
    ASPH_MAX_SIZE_NM,
    ASPH_MIN_SIZE_NM,
    PRECISION_TOLERANCE_NM,
    UPSTREAM_KEEP_HETATM_GROUP_NAMES,
    _get_upstream_like_bfactor_statistics,
    _prepare_receptor,
    fpocket4,
)
from topomt.wrappers.fpocket.integration import load_topography_from_fpocket_output
from topomt.wrappers.fpocket.parser import _parse_pqr_charge_and_radius, parse_fpocket_output
from topomt.wrappers.fpocket.runner import run_fpocket


REPO_ROOT = Path(__file__).resolve().parents[1]
FP_3LKF_PDB = REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF.pdb'
FP_3LKF_OUT = REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF_out'
FP_1TCD_PDB = REPO_ROOT / 'topomt' / 'wrappers' / 'fpocket' / '1tcd.pdb'
FP_1TCD_OUT = REPO_ROOT / 'topomt' / 'wrappers' / 'fpocket' / '1tcd_out'

PDB_PARITY_SYSTEMS = [
    ('1TCD.pdb', Path(tmt.demo['TcTIM']['1TCD.pdb'])),
    ('1ATP.pdb', Path(tmt.demo['fpocket']['1ATP.pdb'])),
    ('1CEN.pdb', Path(tmt.demo['fpocket']['1CEN.pdb'])),
    ('1GG0.pdb', Path(tmt.demo['fpocket']['1GG0.pdb'])),
    ('1N57.pdb', Path(tmt.demo['fpocket']['1N57.pdb'])),
    ('1YCR.pdb', Path(tmt.demo['fpocket']['1YCR.pdb'])),
    ('2GI9.pdb', Path(tmt.demo['fpocket']['2GI9.pdb'])),
    ('2H05.pdb', Path(tmt.demo['fpocket']['2H05.pdb'])),
    ('3LKF.pdb', Path(tmt.demo['fpocket']['3LKF.pdb'])),
    ('E15ALA.pdb', Path(tmt.demo['fpocket']['E15ALA.pdb'])),
]

DEEP_VALIDATION_FPPOCKET_CASES = [
    ('2HGR.pdb', Path(tmt.demo['fpocket']['2HGR.pdb'])),
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

TOPOMT_PARITY_SYSTEMS = [
    ('1ATP.pdb', Path(tmt.demo['fpocket']['1ATP.pdb'])),
    ('1CEN.pdb', Path(tmt.demo['fpocket']['1CEN.pdb'])),
    ('1GG0.pdb', Path(tmt.demo['fpocket']['1GG0.pdb'])),
    ('1N57.pdb', Path(tmt.demo['fpocket']['1N57.pdb'])),
    ('1YCR.pdb', Path(tmt.demo['fpocket']['1YCR.pdb'])),
    ('2GI9.pdb', Path(tmt.demo['fpocket']['2GI9.pdb'])),
    ('2H05.pdb', Path(tmt.demo['fpocket']['2H05.pdb'])),
    ('3LKF.pdb', Path(tmt.demo['fpocket']['3LKF.pdb'])),
    ('E15ALA.pdb', Path(tmt.demo['fpocket']['E15ALA.pdb'])),
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


def test_parse_fpocket_output_keeps_full_precision_of_vert_radius_for_1tcd():

    pocket_vert = FP_1TCD_OUT / 'pockets' / 'pocket1_vert.pqr'
    with pocket_vert.open() as file_handle:
        first_atom_line = next(
            line for line in file_handle if line.startswith(('ATOM  ', 'HETATM'))
        )

    charge, radius = _parse_pqr_charge_and_radius(first_atom_line)

    assert charge == pytest.approx(0.0, abs=1.0e-8)
    assert radius == pytest.approx(3.92, abs=1.0e-8)


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


def _best_native_matches_by_atom_indices(native_topography, wrapper_topography):
    matches = []
    used_native = set()

    for wrapper_feature_id in wrapper_topography:
        wrapper_atoms = set(wrapper_topography[wrapper_feature_id].atom_indices)
        best_match = None

        for native_feature_id in native_topography:
            if native_feature_id in used_native:
                continue

            native_atoms = set(native_topography[native_feature_id].atom_indices)
            intersection = len(wrapper_atoms & native_atoms)
            union = len(wrapper_atoms | native_atoms)
            jaccard = intersection / union if union else 1.0

            candidate = (
                wrapper_feature_id,
                native_feature_id,
                intersection,
                jaccard,
                len(wrapper_atoms),
                len(native_atoms),
            )
            if best_match is None or (intersection, jaccard) > (
                best_match[2],
                best_match[3],
            ):
                best_match = candidate

        used_native.add(best_match[1])
        matches.append(best_match)

    return matches


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


@pytest.mark.skipif(shutil.which('fpocket') is None, reason='fpocket not available')
@pytest.mark.parametrize(
    ('label', 'source_pdb'),
    DEEP_VALIDATION_FPPOCKET_CASES,
    ids=[item[0] for item in DEEP_VALIDATION_FPPOCKET_CASES],
)
@pytest.mark.skip(reason='large-system deep-validation case kept outside the routine battery')
def test_fpocket4_deep_validation_cases(label, source_pdb):

    topography = fpocket4(source_pdb)

    with tempfile.TemporaryDirectory(prefix='topomt_test_fpocket4_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        local_pdb = tmpdir / source_pdb.name
        shutil.copy2(source_pdb, local_pdb)
        output_dir = run_fpocket(local_pdb, workdir=tmpdir)
        reference = load_topography_from_fpocket_output(local_pdb, local_pdb, output_dir)

    _assert_topographies_match(topography, reference)


def test_fpocket4_native_implementation_does_not_require_wrapper(monkeypatch):
    fpocket4_module = importlib.import_module('topomt.methods.fpocket4')

    def fail_if_called(*args, **kwargs):
        raise AssertionError('wrapper path should not be used by the native implementation')

    monkeypatch.setattr(fpocket4_module, 'get_topography_with_fpocket', fail_if_called)

    topography = fpocket4(FP_3LKF_PDB, implementation='native')

    assert len(topography) > 0


def test_fpocket4_argdigest_normalizes_structure_indices_for_native_path(monkeypatch):
    captured = {}
    fpocket4_module = importlib.import_module('topomt.methods.fpocket4')

    def fake_build_native_state(**kwargs):
        captured.update(kwargs)
        return 'native-state'

    def fake_native_topography_from_state(state, **kwargs):
        return state, kwargs

    monkeypatch.setattr(fpocket4_module, '_build_native_state', fake_build_native_state)
    monkeypatch.setattr(
        fpocket4_module,
        '_native_topography_from_state',
        fake_native_topography_from_state,
    )

    result = fpocket4(
        'dummy',
        structure_indices=0,
        implementation='native',
    )

    assert captured['structure_indices'] == 0
    assert result == ('native-state', {})


def test_fpocket4_native_prepare_receptor_keeps_b_factors_for_1atp():

    receptor, atom_indices, coordinates_nm, atom_types, atom_radii_nm, atom_electronegativities, atom_b_factors = _prepare_receptor(
        Path(tmt.demo['fpocket']['1ATP.pdb']),
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )

    assert receptor is not None
    assert atom_b_factors is not None
    assert len(atom_indices) == len(coordinates_nm) == len(atom_types) == len(atom_radii_nm) == len(atom_electronegativities) == len(atom_b_factors)


def test_fpocket4_native_prepare_receptor_excludes_water_and_ions_for_3lkf():

    receptor, atom_indices, coordinates_nm, atom_types, atom_radii_nm, atom_electronegativities, atom_b_factors = _prepare_receptor(
        FP_3LKF_PDB,
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )

    group_names = np.array(msm.get(receptor, element='atom', group_name=True), dtype=object)
    molecule_types = np.array(msm.get(receptor, element='atom', molecule_type=True), dtype=object)

    assert receptor is not None
    assert len(atom_indices) == len(coordinates_nm) == len(atom_types) == len(atom_radii_nm) == len(atom_electronegativities)
    assert 'H' not in set(atom_types.tolist())
    assert not {'HOH', 'WAT', 'TIP'} & set(group_names.tolist())
    assert not {'water', 'ion'} & set(molecule_types.tolist())
    assert 'PC' not in set(group_names.tolist())


def test_fpocket4_native_prepare_receptor_keeps_whitelisted_small_molecule_for_e15ala():

    receptor, atom_indices, coordinates_nm, atom_types, atom_radii_nm, atom_electronegativities, atom_b_factors = _prepare_receptor(
        Path(tmt.demo['fpocket']['E15ALA.pdb']),
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )

    group_names = np.array(msm.get(receptor, element='atom', group_name=True), dtype=object)

    assert receptor is not None
    assert 'HEO' in set(group_names.tolist())


def test_fpocket4_native_prepare_receptor_matches_upstream_input_count_for_e15ala():

    receptor, atom_indices, coordinates_nm, atom_types, atom_radii_nm, atom_electronegativities, atom_b_factors = _prepare_receptor(
        Path(tmt.demo['fpocket']['E15ALA.pdb']),
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )

    assert receptor is not None
    assert len(atom_indices) == 1026


def test_fpocket4_native_prepare_receptor_excludes_non_whitelisted_small_molecules_for_1atp():

    receptor, atom_indices, coordinates_nm, atom_types, atom_radii_nm, atom_electronegativities, atom_b_factors = _prepare_receptor(
        Path(tmt.demo['fpocket']['1ATP.pdb']),
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )

    group_names = set(np.array(msm.get(receptor, element='atom', group_name=True), dtype=object).tolist())

    assert receptor is not None
    assert 'ATP' not in group_names
    assert 'MN' not in group_names


def test_fpocket4_native_prepare_receptor_excludes_po4_for_1gg0():

    receptor, atom_indices, coordinates_nm, atom_types, atom_radii_nm, atom_electronegativities, atom_b_factors = _prepare_receptor(
        Path(tmt.demo['fpocket']['1GG0.pdb']),
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )

    group_names = set(np.array(msm.get(receptor, element='atom', group_name=True), dtype=object).tolist())

    assert receptor is not None
    assert 'PO4' not in group_names


def test_fpocket4_native_prepare_receptor_keeps_pc_when_requested_explicitly():

    receptor, atom_indices, coordinates_nm, atom_types, atom_radii_nm, atom_electronegativities, atom_b_factors = _prepare_receptor(
        FP_3LKF_PDB,
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
        include_group_names={'PC'},
    )

    group_names = set(np.array(msm.get(receptor, element='atom', group_name=True), dtype=object).tolist())

    assert receptor is not None
    assert 'PC' in group_names


def test_fpocket4_upstream_keep_hetatm_whitelist_contains_expected_examples():

    assert 'HEO' in UPSTREAM_KEEP_HETATM_GROUP_NAMES
    assert 'PC3' in UPSTREAM_KEEP_HETATM_GROUP_NAMES
    assert 'PC' not in UPSTREAM_KEEP_HETATM_GROUP_NAMES
    assert 'PO4' not in UPSTREAM_KEEP_HETATM_GROUP_NAMES
    assert 'ATP' not in UPSTREAM_KEEP_HETATM_GROUP_NAMES


def test_fpocket4_upstream_like_bfactor_statistics_follow_fpocket_semantics_for_1gg0():

    molecular_system = Path(tmt.demo['fpocket']['1GG0.pdb'])
    _, _, _, _, _, _, atom_b_factors = _prepare_receptor(
        molecular_system,
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )

    average_b_factor, min_b_factor, max_b_factor = _get_upstream_like_bfactor_statistics(
        molecular_system
    )

    assert atom_b_factors is not None
    assert average_b_factor == pytest.approx(float(np.mean(atom_b_factors)), abs=1.0e-12)
    assert min_b_factor == pytest.approx(0.0, abs=1.0e-12)
    assert max_b_factor == pytest.approx(float(np.max(atom_b_factors)), abs=1.0e-12)


def test_fpocket4_alpha_size_thresholds_leave_upstream_precision_margin():

    assert ASPH_MIN_SIZE_NM - PRECISION_TOLERANCE_NM == pytest.approx(0.3399, abs=1.0e-8)
    assert ASPH_MAX_SIZE_NM + PRECISION_TOLERANCE_NM == pytest.approx(0.6201, abs=1.0e-8)


@pytest.mark.parametrize(
    'source_pdb',
    [
        Path(tmt.demo['fpocket']['1GG0.pdb']),
        Path(tmt.demo['fpocket']['1N57.pdb']),
    ],
    ids=['1GG0', '1N57'],
)
def test_fpocket4_native_recovers_wrapper_pockets_ignoring_order(source_pdb):

    wrapper_topography = fpocket4(source_pdb, implementation='wrapper')
    native_topography = fpocket4(source_pdb, implementation='native')

    matches = _best_native_matches_by_atom_indices(native_topography, wrapper_topography)

    assert len(matches) == len(wrapper_topography)
    assert len(native_topography) >= len(wrapper_topography)
    assert all(match[3] == pytest.approx(1.0, abs=1.0e-12) for match in matches)


def test_fpocket4_native_matches_audited_count_for_3lkf():

    native_topography = fpocket4(FP_3LKF_PDB, implementation='native')

    assert len(native_topography) == 18


def test_fpocket4_native_exports_geometric_fields_as_quantities_for_3lkf():

    native_topography = fpocket4(FP_3LKF_PDB, implementation='native')
    pocket = native_topography['POC-1']

    assert puw.is_quantity(pocket.center)
    assert puw.is_quantity(pocket.volume)
    assert puw.is_quantity(pocket.convex_hull_volume)
    assert puw.is_quantity(pocket.mean_alpha_sphere_radius)
    assert puw.is_quantity(pocket.alpha_sphere_centers)
    assert puw.is_quantity(pocket.alpha_sphere_radii)
    assert puw.get_value(pocket.center, to_unit='nm').shape == (3,)
    assert puw.get_value(pocket.alpha_sphere_centers, to_unit='nm').shape[1] == 3


@pytest.mark.parametrize(
    ('label', 'source_pdb'),
    TOPOMT_PARITY_SYSTEMS,
    ids=[item[0] for item in TOPOMT_PARITY_SYSTEMS],
)
def test_fpocket4_topomt_matches_native_pockets_ignoring_order(label, source_pdb):

    native_topography = fpocket4(source_pdb, implementation='native')
    topomt_topography = fpocket4(source_pdb, implementation='topomt')

    matches = _best_native_matches_by_atom_indices(topomt_topography, native_topography)

    assert len(matches) == len(native_topography)
    assert len(topomt_topography) == len(native_topography)
    if label == '3LKF.pdb':
        assert all(match[3] >= 0.95 for match in matches)
    else:
        assert all(match[3] == pytest.approx(1.0, abs=1.0e-12) for match in matches)
