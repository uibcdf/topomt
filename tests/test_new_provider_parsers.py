"""Small protocol fixtures protect original semantics without optional engines."""

import importlib

import numpy as np
import pytest

from topomt.provider_output import ProviderRun


def captured(tmp_path, provider, files):
    source = tmp_path / 'input.pdb'
    source.write_text('REMARK Parser fixture only\n')
    results = tmp_path / 'results'
    results.mkdir()
    for name, data in files.items():
        path = results / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)
    return ProviderRun.capture(
        provider, 'library' if provider == 'pykvfinder' else 'cli', source, results
    )


def grid_line(serial=1, label='KAA', x=1.0, cluster=1):
    return f'HETATM{serial:5d}  H   {label:3s} A{cluster:4d}    {x:8.3f}{2.0:8.3f}{3.0:8.3f}  1.00  0.00           H\n'


def test_pykvfinder_grid_and_descriptors_keep_definitions(tmp_path):
    run = captured(
        tmp_path,
        'pykvfinder',
        {
            'results.toml': '[PARAMETERS]\nSTEP=0.6\n[RESULTS.VOLUME]\nKAA=2.16\n[RESULTS.AREA]\nKAA=1.5\n[RESULTS.RESIDUES]\nKAA=[["10","A","ALA"]]\n',
            'cavities.pdb': grid_line(),
        },
    )
    output = importlib.import_module(
        'topomt.third_party.pykvfinder.parser'
    ).parse_output(run)
    assert output.pockets == () and len(output.cavities) == 1
    record = output.cavities[0]
    assert record.source_id == 'KAA' and record.atom_indices is None
    np.testing.assert_allclose(
        record.geometries['grid_points'].points_nm, [[0.1, 0.2, 0.3]]
    )
    assert record.measurements['volume'].original_value == 2.16
    assert record.measurements['volume'].original_unit == 'angstroms**3'
    assert record.fields['RESIDUES'] == [['10', 'A', 'ALA']]


def test_pykvfinder_empty_requires_explicit_success(tmp_path):
    parser = importlib.import_module('topomt.third_party.pykvfinder.parser')
    run = captured(
        tmp_path,
        'pykvfinder',
        {'results.toml': '[RESULTS.VOLUME]\n[RESULTS.AREA]\n', 'cavities.pdb': ''},
    )
    assert parser.parse_output(run).records == ()
    with pytest.raises(ValueError, match='results.toml'):
        parser.parse_output(
            ProviderRun.capture(
                'pykvfinder', 'library', tmp_path / 'input.pdb', tmp_path / 'missing'
            )
        )


def caver_csv(*, missing_axis=False):
    header = 'Snapshot, Tunnel cluster, Tunnel, Throughput, Cost, Bottleneck radius, Average R error bound, Max. R error bound, Bottleneck R error bound, Curvature, Length, , Axis, Values...\n'
    axes = {
        'X': '1,2',
        'Y': '2,3',
        'Z': '3,4',
        'R': '0.5,0.7',
        'distance': '0,1',
        'length': '0,1',
    }
    if missing_axis:
        del axes['Z']
    return header + ''.join(
        f'input.pdb,1,2,0.8,1.0,0.5,-,-,-,1.1,4.0,,{axis},{values}\n'
        for axis, values in axes.items()
    )


def test_caver_ordered_profiles_are_channels(tmp_path):
    run = captured(tmp_path, 'caver', {'analysis/tunnel_profiles.csv': caver_csv()})
    output = importlib.import_module('topomt.third_party.caver.parser').parse_output(
        run
    )
    assert output.pockets == () and len(output.channels) == 1
    record = output.channels[0]
    assert record.atom_indices is None
    geometry = record.geometries['centerline']
    np.testing.assert_allclose(geometry.points_nm, [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]])
    np.testing.assert_allclose(geometry.radii_nm, [0.05, 0.07])
    assert record.measurements['length'].original_value == 4.0
    assert record.measurements['bottleneck_radius'].original_value == 0.5
    assert record.fields['profiles']['distance']['unit'] == 'angstroms'


def test_caver_rejects_incomplete_axes(tmp_path):
    run = captured(
        tmp_path,
        'caver',
        {'analysis/tunnel_profiles.csv': caver_csv(missing_axis=True)},
    )
    with pytest.raises(ValueError, match='axes'):
        importlib.import_module('topomt.third_party.caver.parser').parse_output(run)


def test_ghecom_clusters_use_models_not_grid_value_residue_numbers(tmp_path):
    text = (
        'REMARK  Ncluster 2\nREMARK  grid_width 1.000\n#REMARK CLUSTER[1] NVOXEL 1\n#REMARK CLUSTER[2] NVOXEL 1\nMODEL        1\n'
        + grid_line(label='GRD', cluster=64)
        + 'ENDMDL\nMODEL        2\n'
        + grid_line(label='GRD', cluster=64, x=4.0)
        + 'ENDMDL\n'
    )
    run = captured(tmp_path, 'ghecom', {'pockets.pdb': text})
    output = importlib.import_module('topomt.third_party.ghecom.parser').parse_output(
        run
    )
    assert [r.source_id for r in output.pockets] == ['1', '2']
    assert output.pockets[1].geometries['grid_points'].points_nm[0][0] == 0.4


def test_p2rank_sites_are_not_closed_pockets(tmp_path):
    run = captured(
        tmp_path,
        'p2rank',
        {
            'input.pdb_predictions.csv': 'name,rank,score,probability,sas_points,surf_atoms,center_x,center_y,center_z,residue_ids,surf_atom_ids\npocket1,1,2.4,0.8,10,2,1,2,3,A_10,1 3\n'
        },
    )
    output = importlib.import_module('topomt.third_party.p2rank.parser').parse_output(
        run
    )
    assert output.pockets == () and len(output.sites) == 1
    site = output.sites[0]
    assert site.atom_indices is None
    assert site.fields['surf_atom_ids'] == '1 3'
    assert site.measurements['probability'].original_value == 0.8
    np.testing.assert_allclose(
        site.geometries['predicted_center'].points_nm, [[0.1, 0.2, 0.3]]
    )


@pytest.mark.parametrize(
    'provider,files',
    [
        (
            'pykvfinder',
            {
                'results.toml': '[RESULTS.VOLUME]\nKAA=nan\n[RESULTS.AREA]\nKAA=1.0\n',
                'cavities.pdb': grid_line(),
            },
        ),
        (
            'p2rank',
            {
                'input.pdb_predictions.csv': 'name,rank,score,probability,sas_points,surf_atoms,center_x,center_y,center_z,residue_ids,surf_atom_ids\na,1,2,1.2,1,1,0,0,0,A_1,1\n'
            },
        ),
    ],
)
def test_malformed_original_results_are_not_empty_success(tmp_path, provider, files):
    run = captured(tmp_path, provider, files)
    with pytest.raises(ValueError):
        importlib.import_module(f'topomt.third_party.{provider}.parser').parse_output(
            run
        )


@pytest.mark.parametrize(
    'provider,files',
    [
        ('ghecom', {'pockets.pdb': 'REMARK Ncluster 0\nREMARK grid_width 1.0\n'}),
        (
            'caver',
            {'analysis/tunnel_profiles.csv': caver_csv().splitlines(keepends=True)[0]},
        ),
        (
            'p2rank',
            {
                'input.pdb_predictions.csv': 'name,rank,score,probability,sas_points,surf_atoms,center_x,center_y,center_z,residue_ids,surf_atom_ids\n'
            },
        ),
    ],
)
def test_explicit_empty_original_results_are_valid(tmp_path, provider, files):
    run = captured(tmp_path, provider, files)
    assert (
        importlib.import_module(f'topomt.third_party.{provider}.parser')
        .parse_output(run)
        .records
        == ()
    )
