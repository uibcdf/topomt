"""Real original-engine structural controls; chemical receiving is separate."""

import tempfile
import zipfile
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun


@pytest.fixture(scope='module')
def original():
    try:
        installed = distribution('pocketeer')
    except PackageNotFoundError:
        pytest.skip('optional original Pocketeer distribution is not installed')
    import pocketeer

    if (
        Path(pocketeer.__file__).resolve()
        != Path(installed.locate_file('pocketeer/__init__.py')).resolve()
    ):
        pytest.skip('source checkout shadows installed Pocketeer; use a fresh process')
    return pocketeer, installed


@pytest.fixture(scope='module')
def source_profile(original):
    with tempfile.TemporaryDirectory() as folder:
        pdb = Path(folder) / '2pk4.pdb'
        archive = Path(tmt.__file__).parent / 'data/CASTpFold_server/2pk4.zip'
        with zipfile.ZipFile(archive) as files:
            pdb.write_bytes(files.read('2pk4.pdb'))
        source = msm.convert(pdb, to_form='molsysmt.MolSys')
        coordinates = puw.get_value(msm.get(source, coordinates=True), to_unit='nm')
        second = msm.copy(source)
        msm.set(
            second,
            coordinates=msm.get(second, coordinates=True)
            + puw.quantity([0.2, -0.1, 0.3], 'nm'),
        )
        msm.append_structures(
            source, msm.convert(second, to_form='molsysmt.Structures')
        )
        # An explicit partial atom selection exercises source indices with a gap;
        # it is a structural control, not chemical or receptor qualification.
        selected = np.delete(np.arange(coordinates.shape[1]), coordinates.shape[1] // 3)
    assert not pdb.exists()
    return source, selected, coordinates


def detect(source, selected):
    return tmt.get_provider_output(
        source,
        method='pocketeer',
        selection=selected[::-1],
        structure_indices=1,
        r_min=puw.quantity(300, 'pm'),
        r_max=puw.quantity(0.6, 'nm'),
        sasa_threshold=puw.quantity(0.2, 'nm**2'),
    )


@pytest.fixture(scope='module')
def reference_output(source_profile):
    source, selected, _ = source_profile
    with puw.context(standard_units=['nm', 'ps', 'radians']):
        return detect(msm.copy(source), selected)


def scientific_artifacts(run):
    # MolSysMT's PDB exporter includes wall-clock HEADER/REMARK text. Compare
    # scientific rows and original outputs without rewriting retained bytes or IDs.
    return {
        name: tuple(
            line
            for line in data.splitlines()
            if not line.startswith((b'HEADER', b'REMARK   1 Created by MolSysMT'))
        )
        if name.startswith('input/')
        else data
        for name, data in run.artifacts
    }


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_selected_frame_matches_original_and_survives_bundle_recovery(
    original, source_profile, reference_output, tmp_path, policy
):
    upstream, installed = original
    seed, selected, coordinates = source_profile
    source = msm.copy(seed)
    # This seed carries a crystallographic box: angle standardization needs an
    # explicit dimensionless angular standard as well as length and time.
    with puw.context(standard_units=[*policy, 'radians']):
        result = detect(source, selected)
        assert result.run.metadata == reference_output.run.metadata
        assert scientific_artifacts(result.run) == scientific_artifacts(
            reference_output.run
        )
        assert result.pockets
        assert result.run.metadata['selected_atom_indices'] == selected.tolist()
        assert result.run.metadata['structure_indices'] == 1
        assert result.run.metadata['version'] == upstream.__version__
        assert result.run.metadata['distribution_version'] == installed.version
        input_name = next(
            name for name, _ in result.run.artifacts if name.startswith('input/')
        )
        retained = tmp_path / 'submitted.pdb'
        retained.write_bytes(result.run.get_artifact(input_name))
        expected = upstream.find_pockets(
            upstream.load_structure(str(retained)), **result.run.metadata['parameters']
        )
        assert [r.source_id for r in result.pockets] == [
            f'pocketeer:{p.pocket_id}' for p in expected
        ]
        filtered = np.array(result.run.metadata['filtered_input_atom_indices'])
        for actual, reference in zip(result.pockets, expected):
            assert actual.atom_role == 'pocket_residue_atoms'
            assert actual.atom_indices == tuple(
                selected[np.flatnonzero(reference.mask)]
            )
            assert actual.fields['alpha_sphere_defining_atom_indices'] == [
                selected[filtered[s.atom_indices]].tolist() for s in reference.spheres
            ]
            assert puw.get_value(
                actual.geometries['alpha_spheres'].coordinates, to_unit='angstroms'
            ) == pytest.approx(np.array([s.center for s in reference.spheres]))
            assert actual.measurements['volume'].original_value == reference.volume
        saved = tmp_path / 'original.zip'
        result.run.save(saved)
        restored = ProviderRun.load(saved)
        assert restored == result.run
        msm.set(
            source,
            coordinates=puw.quantity(
                np.zeros_like(
                    puw.get_value(msm.get(source, coordinates=True), to_unit='nm')
                ),
                'nm',
            ),
        )
    np.testing.assert_allclose(
        puw.get_value(result.input_coordinates, to_unit='nm'),
        coordinates[0] + [0.2, -0.1, 0.3],
        rtol=0,
        atol=1e-12,
    )
    assert ProviderRun.load(saved).metadata == result.run.metadata
