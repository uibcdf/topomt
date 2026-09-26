import json
import sys
import warnings
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.get_topography import get_topography
from topomt.provider_output import ProviderRun
from topomt.third_party.pycasta.library import _protein_atom_indices_from_pdb

UPSTREAM_ROOT = Path('/home/diego/repos@others/pycasta/src/pycasta')
BOUND_DIR = UPSTREAM_ROOT / 'data' / 'bounded'


def test_pycasta_atom_mapping_skips_interleaved_hetatm(tmp_path):
    original_lines = (BOUND_DIR / '2pk4.pdb').read_text().splitlines()
    protein_lines = [line for line in original_lines if line.startswith('ATOM  ')][:2]
    ligand_line = next(line for line in original_lines if line.startswith('HETATM'))
    input_pdb = tmp_path / 'interleaved.pdb'
    input_pdb.write_text('\n'.join([ligand_line, *protein_lines]) + '\n')
    protein_coords = np.asarray(
        [
            [float(line[start : start + 8]) for start in (30, 38, 46)]
            for line in protein_lines
        ]
    )

    mapped = _protein_atom_indices_from_pdb(
        input_pdb, np.asarray([10, 20, 30]), protein_coords
    )
    assert mapped.tolist() == [20, 30]


def test_pycasta_atom_mapping_rejects_coordinate_mismatch(tmp_path):
    line = next(
        line
        for line in (BOUND_DIR / '2pk4.pdb').read_text().splitlines()
        if line.startswith('ATOM  ')
    )
    input_pdb = tmp_path / 'one_atom.pdb'
    input_pdb.write_text(line + '\n')

    with pytest.raises(ValueError, match='coordinate order'):
        _protein_atom_indices_from_pdb(
            input_pdb, np.asarray([10]), np.asarray([[0.0, 0.0, 0.0]])
        )


def _load_upstream_pycasta():
    if not UPSTREAM_ROOT.exists():
        pytest.skip('local pycasta upstream mirror is not available')

    if str(UPSTREAM_ROOT) not in sys.path:
        sys.path.insert(0, str(UPSTREAM_ROOT))

    import run_analysis  # noqa: PLC0415

    return run_analysis


def _pocket_features(topography):
    return sorted(
        topography.get_features(by='type', value='pocket'),
        key=lambda pocket: pocket.score,
        reverse=True,
    )


def test_pycasta_provider_library_matches_upstream_reference_for_2pk4(tmp_path):
    run_analysis = _load_upstream_pycasta()
    pdb_path = BOUND_DIR / '2pk4.pdb'
    upstream = run_analysis.process_pdb(str(pdb_path))

    provider_topography = tmt.third_party.pycasta.get_topography(
        str(pdb_path),
        backend='library',
        upstream_root=str(UPSTREAM_ROOT),
    )
    provider_pockets = _pocket_features(provider_topography)

    assert len(provider_pockets) == len(upstream['ranked_pockets']) == 1
    assert puw.get_value(provider_pockets[0].volume, to_unit='nm**3') == pytest.approx(
        upstream['pocket_volumes'][0] / 1000.0
    )
    assert provider_pockets[0].score == pytest.approx(upstream['ranking_scores'][0])
    assert provider_pockets[0].score != pytest.approx(
        upstream['pocket_volumes'][0] / 1000.0
    )
    assert puw.get_value(
        provider_pockets[0].depth, to_unit='angstroms'
    ) == pytest.approx(upstream['pocket_depths'][0])
    assert puw.get_value(provider_pockets[0].depth, to_unit='nm') == pytest.approx(
        upstream['pocket_depths'][0] / 10.0
    )
    assert puw.get_value(
        provider_pockets[0].mouth_area, to_unit='angstroms**2'
    ) == pytest.approx(upstream['mouth_area'][0])
    assert puw.get_value(
        provider_pockets[0].mouth_perimeter, to_unit='angstroms'
    ) == pytest.approx(upstream['mouth_perimeter'][0])
    assert len(provider_topography.provider_runs) == 1
    run = next(iter(provider_topography.provider_runs.values()))
    assert run.get_artifact('input/2pk4.pdb') == pdb_path.read_bytes()
    recorded = json.loads(run.get_artifact('output/topomt_returned_result.json'))
    for key in upstream:
        if key != 'pdb_path':
            assert recorded[key] == upstream[key]
    native_names = {name for name, _ in run.artifacts}
    assert 'output/bov1/2pk4.alpha.npz' in native_names
    assert any(
        name.startswith('output/bov1/pocket_pdbs/2pk4/') for name in native_names
    )
    assert any(
        name.startswith('output/bov1/pocket_properties/') for name in native_names
    )
    with np.load(BytesIO(run.get_artifact('output/bov1/2pk4.alpha.npz'))) as alpha:
        assert alpha['protein_coords'].shape[1] == 3
        assert alpha['tetrahedra'].shape[1:] == (4, 3)
    assert run.metadata['configuration']['save_alpha'] is True
    assert run.metadata['configuration']['filter_alpha_by_sasa'] is False
    archive = tmp_path / 'pycasta.zip'
    run.save(archive)
    recovered = ProviderRun.load(archive)
    assert recovered.run_id == run.run_id
    assert recovered.artifacts == run.artifacts
    assert provider_pockets[0].provider_run_id == run.run_id


@pytest.mark.parametrize('pdb_name', ['1stp.pdb', '2ifb.pdb', '1hew.pdb'])
def test_pycasta_provider_reports_each_pocket_descriptor(pdb_name):
    run_analysis = _load_upstream_pycasta()
    pdb_path = BOUND_DIR / pdb_name
    upstream = run_analysis.process_pdb(str(pdb_path))
    topography = tmt.third_party.pycasta.get_topography(
        str(pdb_path), backend='library', upstream_root=str(UPSTREAM_ROOT)
    )
    pockets = sorted(
        topography.get_features(by='type', value='pocket'),
        key=lambda pocket: int(pocket.source_id.split(':')[1]),
    )

    assert len(pockets) == len(upstream['ranked_pockets'])
    for index, pocket in enumerate(pockets):
        assert pocket.provider_tetrahedron_indices == upstream['ranked_pockets'][index]
        assert pocket.score == pytest.approx(upstream['ranking_scores'][index])
        assert puw.get_value(
            pocket.representative_point, to_unit='angstroms'
        ) == pytest.approx(upstream['representative_points'][index])
        assert (
            pocket.provider_validation_method == upstream['validation_methods'][index]
        )
        assert pocket.external_measurements[
            'representative_point'
        ].original_value == pytest.approx(upstream['representative_points'][index])
        assert puw.get_value(pocket.volume, to_unit='angstroms**3') == pytest.approx(
            upstream['pocket_volumes'][index]
        )
        for name, source in (
            ('depth', 'pocket_depths'),
            ('mouth_area', 'mouth_area'),
            ('mouth_perimeter', 'mouth_perimeter'),
        ):
            assert puw.get_value(getattr(pocket, name)) == pytest.approx(
                upstream[source][index] / (100 if name == 'mouth_area' else 10)
            )
            assert pocket.external_measurements[name].original_value == pytest.approx(
                upstream[source][index]
            )


def test_get_topography_pycasta_routes_without_digest_warnings(monkeypatch):
    provider_module = __import__(
        'topomt.third_party.pycasta.api',
        fromlist=['get_topography'],
    )

    def fake_provider(molecular_system, **kwargs):
        return tmt.Topography(molecular_system=molecular_system)

    monkeypatch.setattr(provider_module, 'get_topography', fake_provider)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        topo = get_topography(
            tmt.demo['TcTIM']['1tcd.pdb'],
            method='pycasta',
            implementation='wrapper',
            upstream_root='/tmp/pycasta',
        )

    assert isinstance(topo, tmt.Topography)
    assert not any(
        type(item.message).__name__ == 'DigestNotDigestedWarning' for item in caught
    )
