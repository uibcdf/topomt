import re
import shutil
from pathlib import Path

import pytest

import topomt as tmt
from topomt import pyunitwizard as puw

REPO_ROOT = Path(__file__).resolve().parents[3]
FP_3LKF_PDB = REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF.pdb'
FP_3LKF_OUT = REPO_ROOT / 'topomt' / 'data' / 'fpocket4' / 'sample' / '3LKF_out'
FP_1TCD_DIR = REPO_ROOT / 'topomt' / 'third_party' / 'fpocket' / 'testdata'


def _read_original_info_fields(report):
    reported = {}
    pocket_id = None
    for line in report.splitlines():
        match = re.fullmatch(r'Pocket\s+(\d+)\s*:', line.strip())
        if match:
            pocket_id = int(match.group(1))
            reported[pocket_id] = {}
        elif ':' in line and pocket_id is not None:
            label, value = line.strip().split(':', 1)
            reported[pocket_id][label.strip()] = float(value.strip())
    return reported


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

    assert len(topography.provider_runs) == 1
    run = next(iter(topography.provider_runs.values()))
    assert pocket.provider_run_id == run.run_id
    assert len(run.artifacts) == 1 + sum(
        path.is_file() for path in FP_3LKF_OUT.rglob('*')
    )
    assert run.get_artifact('input/3LKF.pdb') == FP_3LKF_PDB.read_bytes()
    assert (
        run.get_artifact('output/3LKF_info.txt')
        == (FP_3LKF_OUT / '3LKF_info.txt').read_bytes()
    )
    assert pocket.provider_raw_fields['Proportion of polar atoms'] == pytest.approx(
        35.135
    )
    for name, expected, issue in (
        ('total_sasa', 235.646, 20),
        ('polar_sasa', 102.807, 21),
        ('apolar_sasa', 132.839, 22),
    ):
        measurement = pocket.external_measurements[name]
        assert puw.get_value(
            measurement.value, to_unit='angstroms**2'
        ) == pytest.approx(expected)
        assert puw.get_value(
            getattr(pocket, name), to_unit='angstroms**2'
        ) == pytest.approx(expected)
        assert measurement.original_value == pytest.approx(expected)
        assert measurement.original_unit == 'angstroms**2'
        assert measurement.source_artifact == 'output/3LKF_info.txt'
        assert measurement.run_id == run.run_id
        assert measurement.issue_url.endswith(f'/issues/{issue}')


def test_fpocket_info_field_inventory_and_source_precision():
    topography = tmt.third_party.fpocket.load_topography(
        FP_3LKF_PDB, pdb_file=FP_3LKF_PDB, output_dir=FP_3LKF_OUT
    )
    pocket = topography['POC-1']
    expected = {
        'score': ('Score', 33.993, '1', None),
        'druggability_score': ('Druggability Score', 0.401, '1', None),
        'n_alpha_spheres': ('Number of Alpha Spheres', 76, '1', None),
        'total_sasa': ('Total SASA', 235.646, 'angstroms**2', 20),
        'polar_sasa': ('Polar SASA', 102.807, 'angstroms**2', 21),
        'apolar_sasa': ('Apolar SASA', 132.839, 'angstroms**2', 22),
        'volume': ('Volume', 645.303, 'angstroms**3', None),
        'local_hydrophobic_density_score': (
            'Mean local hydrophobic density',
            27.379,
            '1',
            None,
        ),
        'mean_alpha_sphere_radius': (
            'Mean alpha sphere radius',
            3.724,
            'angstroms',
            None,
        ),
        'mean_alpha_sphere_solvent_access': (
            'Mean alp. sph. solvent access',
            0.531,
            '1',
            23,
        ),
        'apolar_alpha_sphere_ratio': (
            'Apolar alpha sphere proportion',
            0.382,
            '1',
            None,
        ),
        'hydrophobicity_score': ('Hydrophobicity score', 22.200, '1', 24),
        'volume_score': ('Volume score', 4.600, '1', 25),
        'polarity_score': ('Polarity score', 5, '1', 26),
        'charge_score': ('Charge score', 1, '1', 27),
        'proportion_polar_atoms': ('Proportion of polar atoms', 35.135, 'percent', 28),
        'alpha_sphere_density': ('Alpha sphere density', 3.535, 'angstroms', None),
        'alpha_sphere_max_distance': (
            'Cent. of mass - Alpha Sphere max dist',
            10.560,
            'angstroms',
            None,
        ),
        'flexibility': ('Flexibility', 0.361, '1', 29),
    }

    assert set(pocket.external_measurements) == set(expected)
    assert pocket.unmapped_provider_fields == {}
    for name, (field, value, unit, issue) in expected.items():
        measurement = pocket.external_measurements[name]
        assert measurement.source_field == field
        assert measurement.source_artifact == 'output/3LKF_info.txt'
        assert measurement.original_value == pytest.approx(value)
        assert measurement.original_unit == unit
        assert measurement.run_id == pocket.provider_run_id
        if unit in {'angstroms', 'angstroms**2', 'angstroms**3'}:
            assert puw.get_value(measurement.value, to_unit=unit) == pytest.approx(
                value
            )
        else:
            assert measurement.value == pytest.approx(value)
        if issue is None:
            assert measurement.issue_url is None
            assert measurement.status == 'topomt_available'
        else:
            assert measurement.issue_url.endswith(f'/issues/{issue}')
            assert measurement.status == 'external_only'

    assert pocket.score == pytest.approx(33.9933)
    assert pocket.external_measurements['score'].original_value == pytest.approx(33.993)
    assert pocket.proportion_polar_atoms == pytest.approx(35.135)
    assert puw.get_value(
        pocket.alpha_sphere_density, to_unit='angstroms'
    ) == pytest.approx(3.535)
    assert puw.get_value(
        pocket.alpha_sphere_max_distance, to_unit='angstroms'
    ) == pytest.approx(10.560)
    assert pocket.flexibility == pytest.approx(0.361)


def test_fpocket_unrecognized_info_field_remains_queryable(tmp_path):
    output_dir = tmp_path / '3LKF_out'
    shutil.copytree(FP_3LKF_OUT, output_dir)
    info_file = output_dir / '3LKF_info.txt'
    info_file.write_text(
        info_file.read_text().replace(
            '\nPocket 2 :', '\tFuture Descriptor : 12.5\n\nPocket 2 :', 1
        )
    )

    topography = tmt.third_party.fpocket.load_topography(
        FP_3LKF_PDB, pdb_file=FP_3LKF_PDB, output_dir=output_dir
    )
    pocket = topography['POC-1']
    run = topography.provider_runs[pocket.provider_run_id]
    assert pocket.unmapped_provider_fields == {'Future Descriptor': 12.5}
    assert run.get_artifact('output/3LKF_info.txt') == info_file.read_bytes()


@pytest.mark.parametrize(
    ('pdb_file', 'output_dir'),
    [
        (FP_3LKF_PDB, FP_3LKF_OUT),
        (FP_1TCD_DIR / '1tcd.pdb', FP_1TCD_DIR / '1tcd_out'),
    ],
)
def test_fpocket_all_reported_scalar_fields_are_mapped(pdb_file, output_dir):
    topography = tmt.third_party.fpocket.load_topography(
        pdb_file, pdb_file=pdb_file, output_dir=output_dir
    )
    assert len(topography) > 0
    for pocket in topography.values():
        assert len(pocket.external_measurements) == 19
        assert pocket.unmapped_provider_fields == {}
        run = topography.provider_runs[pocket.provider_run_id]
        assert all(
            measurement.source_artifact == f'output/{pdb_file.stem}_info.txt'
            and measurement.run_id == run.run_id
            for measurement in pocket.external_measurements.values()
        )


@pytest.mark.parametrize(
    ('pdb_file', 'output_dir'),
    [
        (FP_3LKF_PDB, FP_3LKF_OUT),
        (FP_1TCD_DIR / '1tcd.pdb', FP_1TCD_DIR / '1tcd_out'),
    ],
)
def test_fpocket_reported_measurements_match_original_info_lines(pdb_file, output_dir):
    topography = tmt.third_party.fpocket.load_topography(
        pdb_file, pdb_file=pdb_file, output_dir=output_dir
    )
    run = next(iter(topography.provider_runs.values()))
    report = run.get_artifact(f'output/{pdb_file.stem}_info.txt').decode()
    reported = _read_original_info_fields(report)

    assert len(reported) == len(topography)
    for pocket_id, original_fields in reported.items():
        pocket = topography[f'POC-{pocket_id}']
        measurements = pocket.external_measurements.values()
        assert len(original_fields) == len(measurements) == 19
        assert {item.source_field for item in measurements} == set(original_fields)
        for item in measurements:
            assert item.original_value == original_fields[item.source_field]
            assert item.run_id == run.run_id


@pytest.mark.parametrize(
    ('pdb_file', 'output_dir'),
    [
        (FP_3LKF_PDB, FP_3LKF_OUT),
        (FP_1TCD_DIR / '1tcd.pdb', FP_1TCD_DIR / '1tcd_out'),
    ],
)
def test_fpocket_global_spheres_match_ordered_pocket_spheres(pdb_file, output_dir):
    topography = tmt.third_party.fpocket.load_topography(
        pdb_file, pdb_file=pdb_file, output_dir=output_dir
    )
    run = next(iter(topography.provider_runs.values()))

    def sphere_lines(artifact):
        return [
            line
            for line in run.get_artifact(artifact).decode().splitlines()
            if line.startswith(('ATOM  ', 'HETATM'))
        ]

    global_lines = sphere_lines(f'output/{pdb_file.stem}_pockets.pqr')
    pocket_lines = [
        line
        for pocket in topography.values()
        for line in sphere_lines(pocket.alpha_sphere_source_artifact)
    ]
    assert len(global_lines) == len(pocket_lines)
    assert len(global_lines) == sum(
        pocket.n_alpha_spheres for pocket in topography.values()
    )
    assert [line[:6] + line[11:] for line in global_lines] == [
        line[:6] + line[11:] for line in pocket_lines
    ]
    if pdb_file.stem == '1tcd':
        assert [line[6:11] for line in global_lines] != [
            line[6:11] for line in pocket_lines
        ]


def test_fpocket_alpha_sphere_records_keep_original_ids_types_and_charges():
    topography = tmt.third_party.fpocket.load_topography(
        FP_3LKF_PDB, pdb_file=FP_3LKF_PDB, output_dir=FP_3LKF_OUT
    )
    pocket = topography['POC-1']
    source_name = 'output/pockets/pocket0_vert.pqr'
    run = topography.provider_runs[pocket.provider_run_id]
    assert (
        run.get_artifact(source_name)
        == (FP_3LKF_OUT / 'pockets' / 'pocket0_vert.pqr').read_bytes()
    )
    assert pocket.alpha_sphere_source_artifact == source_name
    assert pocket.alpha_sphere_ids[:4] == [4031, 4031, 9775, 11953]
    assert pocket.alpha_sphere_types[:4] == ['POL', 'POL', 'POL', 'APOL']
    assert pocket.alpha_sphere_charges[:4].tolist() == [0.0, 0.0, 0.0, 0.0]
    assert pocket.alpha_sphere_radii[:4].tolist() == pytest.approx(
        [3.70, 3.79, 3.64, 3.47]
    )
    assert len(pocket.alpha_sphere_ids) == pocket.n_alpha_spheres


@pytest.mark.parametrize(
    ('pdb_file', 'output_dir'),
    [
        (FP_3LKF_PDB, FP_3LKF_OUT),
        (FP_1TCD_DIR / '1tcd.pdb', FP_1TCD_DIR / '1tcd_out'),
    ],
)
def test_fpocket_contact_atoms_preserve_source_order_and_mapping(pdb_file, output_dir):
    topography = tmt.third_party.fpocket.load_topography(
        pdb_file, pdb_file=pdb_file, output_dir=output_dir
    )
    source_serial_to_index = {
        int(line[6:11]): index
        for index, line in enumerate(
            line
            for line in pdb_file.read_text().splitlines()
            if line.startswith(('ATOM  ', 'HETATM'))
        )
    }
    for pocket in topography.values():
        run = topography.provider_runs[pocket.provider_run_id]
        serials = [
            int(line[6:11])
            for line in run.get_artifact(pocket.atom_source_artifact)
            .decode()
            .splitlines()
            if line.startswith(('ATOM  ', 'HETATM'))
        ]
        expected_indices = [source_serial_to_index[serial] for serial in serials]
        assert pocket.provider_atom_serials == serials
        assert pocket.provider_atom_indices == expected_indices
        assert pocket.unmapped_atom_serials == []
        assert pocket.atom_indices == sorted(expected_indices)


def test_fpocket_unmatched_atom_serial_is_exposed(tmp_path):
    output_dir = tmp_path / '3LKF_out'
    shutil.copytree(FP_3LKF_OUT, output_dir)
    atom_file = output_dir / 'pockets' / 'pocket0_atm.pdb'
    lines = atom_file.read_text().splitlines(keepends=True)
    atom_line_index = next(
        index for index, line in enumerate(lines) if line.startswith('ATOM  ')
    )
    original_line = lines[atom_line_index]
    lines[atom_line_index] = original_line[:6] + '99999' + original_line[11:]
    atom_file.write_text(''.join(lines))

    topography = tmt.third_party.fpocket.load_topography(
        FP_3LKF_PDB, pdb_file=FP_3LKF_PDB, output_dir=output_dir
    )
    pocket = topography['POC-1']
    assert pocket.provider_atom_serials[0] == 99999
    assert pocket.provider_atom_indices[0] is None
    assert pocket.unmapped_atom_serials == [99999]
    assert len(pocket.atom_indices) == len(pocket.provider_atom_serials) - 1
    run = topography.provider_runs[pocket.provider_run_id]
    assert run.get_artifact(pocket.atom_source_artifact) == atom_file.read_bytes()


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
    run = next(iter(provider_topography.provider_runs.values()))
    assert run.backend == 'cli'
    assert run.metadata['executable_name'] == 'fpocket'
    assert len(run.metadata['executable_sha256']) == 64
    assert run.metadata['extra_args'] == []
    assert run.get_artifact('input/3LKF.pdb') == FP_3LKF_PDB.read_bytes()
    reported = _read_original_info_fields(
        run.get_artifact('output/3LKF_info.txt').decode()
    )
    assert len(reported) == len(provider_topography)
    for pocket_id, original_fields in reported.items():
        measurements = provider_topography[
            f'POC-{pocket_id}'
        ].external_measurements.values()
        assert len(original_fields) == len(measurements) == 19
        for item in measurements:
            assert item.original_value == original_fields[item.source_field]


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
