"""Original AlphaSpace2 binds both submitted inputs to their MolSysMT sources."""

import copy
import json
import zipfile
from importlib.metadata import distribution
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest
from depdigest.core import decorator as dependency_decorator

import topomt as tmt
from devtools.provider_handoff import prepare_reference_source
from tests.methods.fpocket4.test_chemical_context import _with_states
from tests.methods.fpocket4.test_input_preparation import _pdb_frame
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun
from topomt.third_party.alphaspace2 import library
from topomt.third_party.pdb_context import (
    reference_chemical_context,
    source_input_context,
    validate_source_input_context,
)


@pytest.fixture
def source(tmp_path):
    path = tmp_path / 'seed.pdb'
    path.write_text(_pdb_frame() + 'END\n')
    return msm.convert(path, to_form='molsysmt.MolSys')


def forbidden(*args, **kwargs):
    pytest.fail('Original input or engine work preceded source admission.')


@pytest.mark.parametrize('role', ['receptor', 'binder'])
@pytest.mark.parametrize(
    'inventory,reference,selector,message',
    [
        ('two', 0, 1, 'nonreference'),
        ('two', None, 'reference', 'ambiguous'),
        ('absent', 0, 'reference', 'absent'),
        ('empty', None, 'reference', 'zero chemical states'),
    ],
)
def test_reference_admission_precedes_any_export(
    source, role, inventory, reference, selector, message, monkeypatch
):
    invalid = _with_states(source, inventory=inventory, reference=reference)
    monkeypatch.setattr(dependency_decorator, 'check_dependency', lambda *a, **k: None)
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    monkeypatch.setattr(library, 'import_upstream_module', forbidden)
    options = (
        {'chemical_state': selector}
        if role == 'receptor'
        else {'binder': invalid, 'binder_chemical_state': selector}
    )
    with pytest.raises(ValueError, match=message):
        tmt.get_provider_output(
            invalid if role == 'receptor' else source, method='alphaspace2', **options
        )


def test_nonzero_references_export_existing_charges_without_preparing(
    source, monkeypatch
):
    receptor = _with_states(source, reference=1)
    binder = _with_states(source, reference=1)
    msm.set(receptor, element='atom', formal_charge=[1] * 4, chemical_state=1)
    msm.set(binder, element='atom', formal_charge=[-1] * 4, chemical_state=1)
    before = [
        copy.deepcopy(
            msm.convert(
                s.chemical_states, to_form='molsysmt.ChemicalStatesDict'
            ).to_dict()
        )
        for s in (receptor, binder)
    ]
    prepare = library.prepare_wrapper_input_pdb
    observed = []

    class ObservedBothExports(Exception):
        pass

    def observe(value, **options):
        path, indices = prepare(value, **options)
        rows = [r for r in path.read_text().splitlines() if r.startswith('ATOM')]
        observed.append([r[78:80] for r in rows])
        if value is binder:
            raise ObservedBothExports
        return path, indices

    monkeypatch.setattr(dependency_decorator, 'check_dependency', lambda *a, **k: None)
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', observe)
    monkeypatch.setattr(library, 'import_upstream_module', forbidden)
    with pytest.raises(ObservedBothExports):
        tmt.get_provider_output(
            receptor,
            method='alphaspace2',
            chemical_state=1,
            binder=binder,
            binder_chemical_state=np.int64(1),
        )
    assert observed == [['1+'] * 4, ['1-'] * 4]
    for value, expected in zip((receptor, binder), before):
        assert value.chemical_states.reference_chemical_state_index == 1
        np.testing.assert_equal(
            msm.convert(
                value.chemical_states, to_form='molsysmt.ChemicalStatesDict'
            ).to_dict(),
            expected,
        )


@pytest.mark.parametrize('role', ['receptor', 'binder'])
@pytest.mark.parametrize('damage', ['row_map', 'coordinates', 'models', 'serials'])
def test_submitted_context_is_validated_before_original_import(
    source, role, damage, monkeypatch
):
    pytest.importorskip('mdtraj')
    pytest.importorskip('alphaspace2')
    binder = msm.copy(source)
    prepare = library.prepare_wrapper_input_pdb

    def corrupt(value, **options):
        path, indices = prepare(value, **options)
        if (value is source) == (role == 'receptor'):
            if damage == 'row_map':
                indices = indices[::-1]
            elif damage == 'coordinates':
                text = path.read_text()
                lines = text.splitlines()
                first = next(i for i, r in enumerate(lines) if r.startswith('ATOM'))
                lines[first] = lines[first][:30] + f'{9.0:8.3f}' + lines[first][38:]
                path.write_text('\n'.join(lines) + '\n')
            elif damage == 'serials':
                lines = path.read_text().splitlines()
                atom_rows = [i for i, r in enumerate(lines) if r.startswith('ATOM')]
                i, j = atom_rows[:2]
                lines[j] = lines[j][:6] + lines[i][6:11] + lines[j][11:]
                path.write_text('\n'.join(lines) + '\n')
            else:
                text = path.read_text()
                path.write_text(
                    'MODEL        1\n'
                    + text
                    + 'ENDMDL\nMODEL        2\n'
                    + text
                    + 'ENDMDL\n'
                )
        return path, indices

    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', corrupt)
    monkeypatch.setattr(library, 'import_upstream_module', forbidden)
    with pytest.raises(
        ValueError, match='coordinates|one input coordinate frame|serials'
    ):
        tmt.get_provider_output(source, method='alphaspace2', binder=binder)


@pytest.mark.parametrize('role', ['receptor', 'binder'])
def test_loaded_coordinates_cannot_reorder_source_rows(source, role, monkeypatch):
    md = pytest.importorskip('mdtraj')
    pytest.importorskip('alphaspace2')
    original = md.load
    calls = []

    def corrupt(*args, **kwargs):
        value = original(*args, **kwargs)
        calls.append(value)
        if len(calls) == (1 if role == 'receptor' else 2):
            value.xyz = value.xyz[:, ::-1, :].copy()
        return value

    monkeypatch.setattr(md, 'load', corrupt)
    monkeypatch.setattr(library, 'import_upstream_module', forbidden)
    with pytest.raises(ValueError, match='loaded coordinates'):
        tmt.get_provider_output(source, method='alphaspace2', binder=msm.copy(source))


@pytest.fixture(scope='module')
def profile(tmp_path_factory):
    # Ordinary optional-engine tests may skip; an explicitly selected original
    # profile must still use the real installed 0.1.2 distribution without a mirror.
    alpha = pytest.importorskip('alphaspace2')
    installed = distribution('alphaspace2')
    assert installed.version == '0.1.2'
    assert (
        Path(alpha.__file__).resolve()
        == Path(installed.locate_file('alphaspace2/__init__.py')).resolve()
    )
    folder = tmp_path_factory.mktemp('alphaspace2_context')
    archive = Path(tmt.__file__).parent / 'data/CASTpFold_server/2pk4.zip'
    with zipfile.ZipFile(archive) as z:
        path = folder / '2pk4.pdb'
        path.write_bytes(z.read('2pk4.pdb'))
    base, selected = prepare_reference_source(path)
    receptor = _with_states(base, reference=1)
    binder = _with_states(base, reference=0)
    ligand = msm.select(binder, selection='group_name=="ACA"')
    return receptor, binder, selected, ligand


@pytest.fixture(scope='module')
def outputs(profile):
    receptor, binder, selected, ligand = profile
    results = []
    for policy in (['nm', 'ps', 'radians'], ['pm', 'fs', 'radians']):
        local_receptor, local_binder = msm.copy(receptor), msm.copy(binder)
        with puw.context(standard_units=policy):
            output = tmt.get_provider_output(
                local_receptor,
                method='alphaspace2',
                selection=np.array(selected[::-1]),
                structure_indices=np.array([1]),
                chemical_state=1,
                binder=local_binder,
                binder_selection=np.array(ligand[::-1]),
                binder_structure_indices=0,
                binder_chemical_state=0,
                min_vertices=1,
            )
        results.append((output, local_receptor, local_binder))
    return results


@pytest.mark.parametrize('index', [0, 1])
def test_original_run_retains_independent_source_contexts(
    profile, outputs, index, tmp_path
):
    _, _, selected, ligand = profile
    output, receptor, binder = outputs[index]
    expected_receptor = source_input_context(receptor, 1)
    expected_binder = source_input_context(binder, 0)
    metadata = output.run.metadata
    assert output.pockets and metadata['distribution_version'] == '0.1.2'
    assert metadata['chemical_state_context'] == reference_chemical_context(
        receptor, 1, provider='AlphaSpace2'
    )
    assert metadata['binder']['chemical_state_context'] == reference_chemical_context(
        binder, 0, provider='AlphaSpace2'
    )
    assert metadata['selected_atom_indices'] == selected
    assert metadata['binder']['selected_atom_indices'] == sorted(ligand)
    assert (
        metadata['structure_indices'] == [1]
        and metadata['binder']['structure_indices'] == 0
    )
    captured_receptor = json.loads(
        output.run.get_artifact(metadata['source_context_artifact'])
    )
    captured_binder = json.loads(
        output.run.get_artifact(metadata['binder']['source_context_artifact'])
    )
    validate_source_input_context(receptor, captured_receptor, 1)
    validate_source_input_context(binder, captured_binder, 0)
    assert captured_receptor['atom_attributes'] == expected_receptor['atom_attributes']
    assert captured_binder['atom_attributes'] == expected_binder['atom_attributes']
    for context, indices in [
        (metadata, selected),
        (metadata['binder'], sorted(ligand)),
    ]:
        rows = [
            r
            for r in output.run.get_artifact(
                context.get('input_artifact', metadata['receptor_input_artifact'])
            )
            .decode()
            .splitlines()
            if r.startswith(('ATOM  ', 'HETATM'))
        ]
        assert context['atom_serial_to_index'] == {
            str(int(r[6:11])): i for r, i in zip(rows, indices)
        }
    protocol = metadata['output_protocol']
    assert protocol['artifact'] == 'output/topomt_snapshot.json'
    assert protocol['units']['_alpha_xyz'] == 'angstroms'
    assert protocol['units']['_alpha_space'] == 'angstroms**3'
    assert protocol['units']['_beta_scores'] == 'unspecified'
    output.run.save(tmp_path / 'original.zip')
    assert ProviderRun.load(tmp_path / 'original.zip') == output.run
    frozen = output.run.metadata
    changed = receptor
    msm.set(
        changed,
        coordinates=msm.get(changed, structure_indices=1, coordinates=True)
        + puw.quantity([[[1.0, 0.0, 0.0]]], 'nm'),
        structure_indices=1,
    )
    msm.set(changed, element='atom', formal_charge=1, chemical_state=1)
    msm.set(
        binder,
        coordinates=msm.get(binder, structure_indices=0, coordinates=True)
        + puw.quantity([[[0.0, 1.0, 0.0]]], 'nm'),
        structure_indices=0,
    )
    msm.set(binder, element='atom', formal_charge=1, chemical_state=0)
    assert output.run.metadata == frozen
    assert (
        json.loads(
            output.run.get_artifact(metadata['binder']['source_context_artifact'])
        )
        == captured_binder
    )
    assert (
        json.loads(output.run.get_artifact(metadata['source_context_artifact']))
        == captured_receptor
    )


def test_original_fields_and_physical_geometry_agree_across_unit_policies(outputs):
    first, second = [item[0] for item in outputs]
    assert first.run.get_artifact(
        'output/topomt_snapshot.json'
    ) == second.run.get_artifact('output/topomt_snapshot.json')
    assert [p.source_id for p in first.pockets] == [p.source_id for p in second.pockets]
    for a, b in zip(first.pockets, second.pockets):
        assert a.atom_indices == b.atom_indices and a.atom_role == b.atom_role
        assert set(a.geometries) == set(b.geometries)
        for name in a.geometries:
            left, right = a.geometries[name], b.geometries[name]
            np.testing.assert_allclose(
                left.points_nm, right.points_nm, rtol=0, atol=1e-12
            )
            if left.radii_nm is not None:
                np.testing.assert_allclose(
                    left.radii_nm, right.radii_nm, rtol=0, atol=1e-12
                )
