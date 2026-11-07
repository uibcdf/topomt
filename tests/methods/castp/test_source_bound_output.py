"""CASTp evidence keeps an explicit source correspondence across recovery."""

import copy
import json
import subprocess
import sys
import zipfile
from dataclasses import fields, is_dataclass
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError
from topomt.provider_output import ProviderRun

DATA = Path(tmt.__file__).parent / 'data'


def test_bound_individual_files_preserve_the_callers_explicit_names(
    binding_profile, tmp_path
):
    source, mapping, _ = binding_profile
    options = {}
    with zipfile.ZipFile(DATA / 'CASTp_3.0_server/2pk4.zip') as archive:
        for i, (argument, suffix) in enumerate(
            (
                ('poc_file', '.poc'),
                ('pocInfo_file', '.pocInfo'),
                ('mouth_file', '.mouth'),
                ('mouthInfo_file', '.mouthInfo'),
                ('pdb_file', '.pdb'),
            )
        ):
            path = tmp_path / f'explicit-{i}{suffix}'
            path.write_bytes(archive.read('2pk4' + suffix))
            options[argument] = path
    output = tmt.get_provider_output(
        source,
        method='castp',
        backend='files',
        source_atom_indices=mapping,
        selection=mapping,
        structure_indices=1,
        **options,
    )
    bundle = tmp_path / 'explicit.zip'
    output.run.save(bundle)
    restored = tmt.get_provider_output(
        source, method='castp', backend='files', bundle_file=bundle
    )
    assert restored.run == output.run
    assert [(r.source_id, r.atom_indices) for r in restored.records] == [
        (r.source_id, r.atom_indices) for r in output.records
    ]


SOURCE_FIXTURE = Path(__file__).resolve().parents[2] / 'data/castp_source_binding.zip'
NESTED = 'download/processed/'
POCKET_MEASUREMENTS = (
    ('n_mouths', 3, '1', 'N_mth'),
    ('solvent_accessible_area', 4, 'angstroms**2', 'Area_sa'),
    ('molecular_surface_area', 5, 'angstroms**2', 'Area_ms'),
    ('solvent_accessible_volume', 6, 'angstroms**3', 'Vol_sa'),
    ('molecular_surface_volume', 7, 'angstroms**3', 'Vol_ms'),
    ('length', 8, 'angstroms', 'Lenth'),
    ('surface_triangles_excluding_mouth_count', 9, '1', 'cnr'),
)
MOUTH_MEASUREMENTS = (
    ('n_mouths', 3, '1', 'N_mth'),
    ('solvent_accessible_area', 4, 'angstroms**2', 'Area_sa'),
    ('molecular_surface_area', 5, 'angstroms**2', 'Area_ms'),
    ('solvent_accessible_length', 6, 'angstroms', 'Len_sa'),
    ('molecular_surface_length', 7, 'angstroms', 'Len_ms'),
    ('n_triangles', 8, '1', 'Ntri'),
)


def same(actual, expected):
    if not isinstance(
        expected, (str, bytes, dict, list, tuple, set)
    ) and puw.is_quantity(expected):
        np.testing.assert_allclose(
            puw.get_value(actual, to_unit=puw.get_unit(expected)),
            puw.get_value(expected),
            rtol=0,
            atol=1e-12,
        )
    elif is_dataclass(expected):
        for field in fields(expected):
            same(getattr(actual, field.name), getattr(expected, field.name))
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            same(actual[key], expected[key])
    elif isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected)
        for left, right in zip(actual, expected, strict=True):
            same(left, right)
    elif isinstance(expected, np.ndarray) and expected.dtype.kind not in 'biufc':
        np.testing.assert_equal(actual, expected)
    elif isinstance(expected, (float, np.floating, np.ndarray)):
        np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)
    else:
        assert actual == expected


def snapshot(source):
    return {
        'coordinates_nm': np.asarray(
            puw.get_value(msm.get(source, coordinates=True), to_unit='nm')
        ).copy(),
        'identities': copy.deepcopy(
            msm.get(
                source,
                element='atom',
                output_type='dictionary',
                get_missing_bonds=False,
                atom_id=True,
                atom_name=True,
                atom_type=True,
                group_id=True,
                group_name=True,
                chain_id=True,
            )
        ),
        'chemical_states': copy.deepcopy(
            msm.convert(
                source.chemical_states, to_form='molsysmt.ChemicalStatesDict'
            ).to_dict()
        ),
    }


@pytest.fixture(scope='module')
def binding_profile(tmp_path_factory):
    folder = tmp_path_factory.mktemp('castp-source-profile')
    with zipfile.ZipFile(SOURCE_FIXTURE) as archive:
        source_path = folder / 'source.h5msm'
        source_path.write_bytes(archive.read('source.h5msm'))
        profile = json.loads(archive.read('mapping.json'))
    source = msm.convert(source_path, to_form='molsysmt.MolSys')
    mapping = profile['original_pdb_row_to_source_atom_indices']
    assert msm.get(source, n_atoms=True, n_structures=True) == [747, 2]
    assert len(mapping) == len(set(mapping)) == 745
    assert set(mapping) == set(range(747)) - {1, 3}
    assert mapping != sorted(mapping)
    assert source.chemical_states.reference_chemical_state_index == 0
    return source, mapping, source_path


def bind(source, mapping, archive, **options):
    values = dict(
        source_atom_indices=mapping,
        selection=np.array(mapping[::-1]),
        structure_indices=np.array([1]),
        syntax='MolSysMT',
        chemical_state=0,
        provider_server='castp3',
    )
    values.update(options)
    return tmt.get_provider_output(
        source, method='castp', backend='files', zip_file=archive, **values
    )


def recover(source, bundle, **options):
    return tmt.get_provider_output(
        source, method='castp', backend='files', bundle_file=bundle, **options
    )


@pytest.fixture(scope='module')
def bound_case(binding_profile, tmp_path_factory):
    source, mapping, _ = binding_profile
    folder = tmp_path_factory.mktemp('castp-bound-case')
    nested = folder / 'original.zip'
    original = DATA / 'CASTp_3.0_server/2pk4.zip'
    with zipfile.ZipFile(original) as left, zipfile.ZipFile(nested, 'w') as right:
        originals = {n: left.read(n) for n in left.namelist()}
        for name in reversed(left.namelist()):
            right.writestr(NESTED + name, originals[name])
    before = snapshot(source)
    output = bind(source, mapping, nested)
    same(snapshot(source), before)
    bundle = folder / 'bound.zip'
    output.run.save(bundle)
    return output, bundle, nested, originals


def rewrite(run, folder, mutate):
    metadata, artifacts = run.metadata, dict(run.artifacts)
    mutate(metadata, artifacts)
    for name, data in artifacts.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    inputs = [n for n in artifacts if n.startswith('input/')]
    assert len(inputs) == 1
    changed = ProviderRun.capture(
        run.provider, run.backend, folder / inputs[0], folder / 'output', metadata
    )
    bundle = folder / 'rewritten.zip'
    changed.save(bundle)
    assert ProviderRun.load(bundle) == changed
    assert changed.run_id != run.run_id
    return bundle


def test_original_archive_can_bind_a_declared_source_map_and_recover(tmp_path):
    archive = DATA / 'CASTp_3.0_server/2pk4.zip'
    with zipfile.ZipFile(archive) as original:
        pdb = tmp_path / '2pk4.pdb'
        pdb.write_bytes(original.read('2pk4.pdb'))
    source = msm.convert(pdb, to_form='molsysmt.MolSys', get_missing_bonds=False)
    mapping = list(range(msm.get(source, n_atoms=True)))
    result = tmt.get_provider_output(
        source,
        method='castp',
        backend='files',
        zip_file=archive,
        source_atom_indices=mapping,
    )
    bundle = tmp_path / 'bound.zip'
    result.run.save(bundle)
    recovered = tmt.get_provider_output(
        source, method='castp', backend='files', bundle_file=bundle
    )
    assert recovered.run == result.run
    assert [p.atom_indices for p in recovered.pockets] == [
        p.atom_indices for p in result.pockets
    ]


def test_bound_archive_pdb_loading_never_requests_missing_bond_inference(
    tmp_path, monkeypatch
):
    archive = DATA / 'CASTp_3.0_server/2pk4.zip'
    with zipfile.ZipFile(archive) as original:
        pdb = tmp_path / '2pk4.pdb'
        pdb.write_bytes(original.read('2pk4.pdb'))
    source = msm.convert(pdb, to_form='molsysmt.MolSys', get_missing_bonds=False)
    mapping = list(range(msm.get(source, n_atoms=True)))
    convert = msm.convert
    observed = []

    def guarded(value, *args, **kwargs):
        if isinstance(value, (str, Path)) and Path(value).suffix.lower() == '.pdb':
            observed.append(kwargs.get('get_missing_bonds'))
            if kwargs.get('get_missing_bonds') is not False:
                pytest.fail('Bound archive PDB loading requested bond inference.')
        return convert(value, *args, **kwargs)

    monkeypatch.setattr(msm, 'convert', guarded)
    result = tmt.get_provider_output(
        source,
        method='castp',
        backend='files',
        zip_file=archive,
        source_atom_indices=mapping,
    )
    assert result.pockets
    assert observed and all(value is False for value in observed)


def test_declared_pdb_element_must_match_the_bound_source(tmp_path):
    archive = DATA / 'CASTp_3.0_server/2pk4.zip'
    with zipfile.ZipFile(archive) as original:
        pdb = tmp_path / '2pk4.pdb'
        pdb.write_bytes(original.read('2pk4.pdb'))
    rows = [
        r for r in pdb.read_text().splitlines() if r.startswith(('ATOM  ', 'HETATM'))
    ]
    carbon = next(i for i, row in enumerate(rows) if row[76:78].strip() == 'C')
    source = msm.convert(pdb, to_form='molsysmt.MolSys', get_missing_bonds=False)
    msm.set(source, element='atom', selection=[carbon], atom_type='N')
    with pytest.raises(ValueError, match='element|identity'):
        tmt.get_provider_output(
            source,
            method='castp',
            backend='files',
            zip_file=archive,
            source_atom_indices=list(range(len(rows))),
        )


def assert_raw_witness(output, mapping, originals):
    pdb_name = next(n for n in originals if n.endswith('.pdb'))
    rows = [
        r
        for r in originals[pdb_name].decode().splitlines()
        if r.startswith(('ATOM  ', 'HETATM'))
    ]
    serials = {int(row[6:11]): i for i, row in enumerate(rows)}
    xyz = np.array([[float(row[i : i + 8]) for i in (30, 38, 46)] for row in rows])
    tables, members, labels = {}, {}, {}
    for kind, suffix, member_suffix in (
        ('pocket', '.pocInfo', '.poc'),
        ('mouth_aggregate', '.mouthInfo', '.mouth'),
    ):
        table_name = next(n for n in originals if n.endswith(suffix))
        table = [
            r.split() for r in originals[table_name].decode().splitlines() if r.strip()
        ]
        tables[kind] = {int(row[2]): row for row in table[1:]}
        member_name = next(n for n in originals if n.endswith(member_suffix))
        members[kind], labels[kind] = {}, {}
        for row in originals[member_name].decode().splitlines():
            if not row.strip():
                continue
            identifier, serial = int(row[66:70]), int(row[6:11])
            members[kind].setdefault(identifier, set()).add(serials[serial])
            labels[kind].setdefault(identifier, set()).add(
                f'{serial}-{row[12:16].strip()}/{row[17:20].strip()}/{row[21].strip()}'
            )
    expected_ids = [f'Pocket {i}' for i in sorted(tables['pocket'])]
    expected_ids += [
        f'Mouth {i}'
        for i in sorted(tables['mouth_aggregate'])
        if int(tables['mouth_aggregate'][i][3]) > 0
    ]
    assert [record.source_id for record in output.records] == expected_ids
    for record in output.records:
        identifier = int(record.source_id.split()[-1])
        original = tables[record.record_kind][identifier]
        fields_for_kind = (
            POCKET_MEASUREMENTS
            if record.record_kind == 'pocket'
            else MOUTH_MEASUREMENTS
        )
        assert set(record.measurements) == {name for name, *_ in fields_for_kind}
        assert record.fields['provider_run_id'] == output.run.run_id
        for name, column, unit, original_field in fields_for_kind:
            value = int(original[column]) if unit == '1' else float(original[column])
            measurement = record.measurements[name]
            assert measurement.original_value == pytest.approx(value)
            assert measurement.original_unit == unit
            assert measurement.run_id == output.run.run_id
            table_key = 'poc_info' if record.record_kind == 'pocket' else 'mouth_info'
            assert (
                measurement.source_artifact
                == output.run.metadata['result_artifacts'][table_key]
            )
            prefix = 'pocInfo' if record.record_kind == 'pocket' else 'mouthInfo'
            assert (
                measurement.source_field == f'{prefix}[{identifier}].{original_field}'
            )
            assert measurement.status == 'external_only'
            actual = (
                measurement.value
                if unit == '1'
                else puw.get_value(measurement.value, to_unit=unit)
            )
            assert actual == pytest.approx(value)
            same(record.fields[name], measurement.value)
        expected_members = members[record.record_kind].get(identifier)
        if expected_members is None:
            assert record.atom_indices is None and record.geometries == {}
            continue
        submitted = record.fields['submitted_atom_indices']
        assert len(submitted) == len(set(submitted))
        assert set(submitted) == expected_members
        assert record.atom_indices == tuple(mapping[i] for i in submitted)
        assert set(record.atom_labels) == labels[record.record_kind][identifier]
        np.testing.assert_allclose(
            puw.get_value(
                record.geometries['member_atoms'].coordinates, to_unit='angstroms'
            ),
            xyz[np.asarray(submitted)],
            rtol=0,
            atol=1e-9,
        )
        if record.record_kind == 'mouth_aggregate':
            assert set(record.parent_source_ids) == {f'Pocket {identifier}'}
    return xyz


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_nonmonotonic_source_roundtrip_preserves_all_thirteen_measurements(
    binding_profile, bound_case, tmp_path, policy
):
    source, mapping, _ = binding_profile
    _, _, archive, originals = bound_case
    before = snapshot(source)
    with puw.context(standard_units=[*policy, 'radians']):
        active = copy.deepcopy(puw.configure.report()['standard_units'])
        result = bind(source, mapping, archive)
        xyz = assert_raw_witness(result, mapping, originals)
        assert result.run.metadata['source_atom_indices'] == mapping
        assert result.run.metadata['structure_indices'] == [1]
        assert result.run.metadata['chemical_state_context']['index'] == 0
        np.testing.assert_allclose(
            np.asarray(result.input_points_nm)[mapping] * 10, xyz, rtol=0, atol=1e-9
        )
        assert len(result.input_points_nm) == 747
        for name, data in originals.items():
            assert result.run.get_artifact('output/' + NESTED + name) == data
        assert result.run.get_artifact('input/original.zip') == archive.read_bytes()
        bundle = tmp_path / 'bound.zip'
        result.run.save(bundle)
        recovered = recover(source, bundle)
        assert recovered.run == result.run == ProviderRun.load(bundle)
        same(recovered.records, result.records)
        same(recovered.input_points_nm, result.input_points_nm)
        assert puw.configure.report()['standard_units'] == active
    same(snapshot(source), before)


@pytest.mark.parametrize(
    'damage', ['boolean', 'float', 'duplicate', 'range', 'negative', 'empty', 'nested']
)
def test_bound_map_rejects_invalid_axes(binding_profile, bound_case, damage):
    source, mapping, _ = binding_profile
    bad = list(mapping)
    if damage == 'empty':
        bad = []
    elif damage == 'nested':
        bad = [[i] for i in bad]
    else:
        bad[0] = {
            'boolean': True,
            'float': float(bad[0]),
            'duplicate': bad[1],
            'range': 747,
            'negative': -1,
        }[damage]
    with pytest.raises((ArgumentError, ValueError)):
        bind(source, mapping, bound_case[2], source_atom_indices=bad)


@pytest.mark.parametrize(
    'options',
    [
        {'structure_indices': 0},
        {'structure_indices': [0, 1]},
        {'structure_indices': 'all'},
        {'chemical_state': 1},
        {'chemical_state': True},
        {'chemical_state': None},
    ],
)
def test_bound_frame_and_state_must_describe_the_existing_source(
    binding_profile, bound_case, options
):
    source, mapping, _ = binding_profile
    before = snapshot(source)
    with pytest.raises((ArgumentError, ValueError)):
        bind(source, mapping, bound_case[2], **options)
    same(snapshot(source), before)


def test_coincident_coordinates_cannot_disguise_an_atom_name_map_swap(
    binding_profile, tmp_path
):
    base, mapping, _ = binding_profile
    source = msm.copy(base)
    with zipfile.ZipFile(DATA / 'CASTp_3.0_server/2pk4.zip') as archive:
        originals = {n: archive.read(n) for n in archive.namelist()}
    pdb = next(n for n in originals if n.endswith('.pdb'))
    rows = [
        r
        for r in originals[pdb].decode().splitlines()
        if r.startswith(('ATOM  ', 'HETATM'))
    ]
    assert rows[0][12:16] != rows[1][12:16]
    second_serial, first_coordinates = int(rows[1][6:11]), rows[0][30:54]
    path = tmp_path / 'coincident.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in originals.items():
            if name.endswith(('.pdb', '.poc', '.mouth')):
                lines = data.decode().splitlines()
                lines = [
                    row[:30] + first_coordinates + row[54:]
                    if row.startswith(('ATOM  ', 'HETATM'))
                    and int(row[6:11]) == second_serial
                    else row
                    for row in lines
                ]
                data = ('\n'.join(lines) + '\n').encode()
            archive.writestr(name, data)
    coordinates = msm.get(
        source, selection=[mapping[0]], structure_indices=1, coordinates=True
    )
    msm.set(
        source, selection=[mapping[1]], structure_indices=1, coordinates=coordinates
    )
    swapped = list(mapping)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    with pytest.raises(ValueError, match='identity|atom|residue'):
        bind(source, mapping, path, source_atom_indices=swapped)


@pytest.mark.parametrize(
    'damage', ['selected', 'excluded', 'charge', 'group_name', 'reference']
)
def test_saved_recovery_rejects_changed_full_source(
    binding_profile, bound_case, damage
):
    source, mapping, _ = binding_profile
    changed = msm.copy(source)
    if damage in {'selected', 'excluded'}:
        index = mapping[0] if damage == 'selected' else 1
        xyz = msm.get(changed, selection=[index], structure_indices=1, coordinates=True)
        msm.set(
            changed,
            selection=[index],
            structure_indices=1,
            coordinates=xyz + puw.quantity([[[0.01, 0, 0]]], 'nm'),
        )
        after = msm.get(
            changed, selection=[index], structure_indices=1, coordinates=True
        )
        assert not np.array_equal(
            puw.get_value(after, to_unit='nm'), puw.get_value(xyz, to_unit='nm')
        )
    elif damage == 'charge':
        before_charge = msm.get(
            changed, element='atom', formal_charge=True, chemical_state=0
        )
        charges = [0] * msm.get(changed, n_atoms=True)
        charges[mapping[0]] = 1
        msm.set(changed, element='atom', formal_charge=charges, chemical_state=0)
        after_charge = msm.get(
            changed, element='atom', formal_charge=True, chemical_state=0
        )
        assert before_charge is None and after_charge is not None
        assert after_charge[mapping[0]] == 1
    elif damage == 'group_name':
        group = msm.get(changed, element='atom', selection=[3], group_index=True)
        msm.set(changed, element='group', selection=group, group_name='CHANGED')
        assert (
            msm.get(changed, element='atom', selection=[3], group_name=True)[0]
            == 'CHANGED'
        )
    else:
        payload = msm.convert(
            changed.chemical_states, to_form='molsysmt.ChemicalStatesDict'
        ).to_dict()
        payload['states'].append(copy.deepcopy(payload['states'][0]))
        payload['states'][1]['state_id'] = 'changed-reference'
        payload['reference_chemical_state_index'] = 1
        changed.chemical_states = msm.convert(
            msm.ChemicalStatesDict(payload), to_form='molsysmt.ChemicalStates'
        )
        assert changed.chemical_states.n_chemical_states == 2
        assert changed.chemical_states.reference_chemical_state_index == 1
    with pytest.raises(ValueError):
        recover(changed, bound_case[1])


@pytest.mark.parametrize(
    'damage',
    [
        'protocol_bool',
        'missing_protocol',
        'map_bool',
        'map_float',
        'map_duplicate',
        'map_range',
        'map_swap',
        'selection',
        'frame',
        'frame_bool',
        'state',
        'state_bool',
        'context_coordinates',
        'context_identity',
        'context_unit',
        'context_duplicate_key',
        'reference_path',
        'result_paths',
        'poc_serial',
        'poc_identity',
        'pdb_coordinates',
        'duplicate_table_id',
        'finite_table_change',
        'missing_context',
        'extra_result_family',
    ],
)
def test_rehashed_valid_bundles_reject_inconsistent_bound_evidence(
    binding_profile, bound_case, tmp_path, damage
):
    source, _, _ = binding_profile
    output = bound_case[0]

    def mutate(metadata, artifacts):
        context_name = metadata['source_context_artifact']
        files = metadata['result_artifacts']
        if damage == 'protocol_bool':
            metadata['source_binding_protocol'] = True
        elif damage == 'missing_protocol':
            metadata.pop('source_binding_protocol')
        elif damage.startswith('map_'):
            values = metadata['source_atom_indices']
            if damage == 'map_swap':
                values[0], values[1] = values[1], values[0]
            else:
                values[0] = {
                    'map_bool': True,
                    'map_float': float(values[0]),
                    'map_duplicate': values[1],
                    'map_range': 747,
                }[damage]
        elif damage == 'selection':
            metadata['selection'] = metadata['selection'][:-1]
        elif damage in {'frame', 'frame_bool'}:
            metadata['structure_indices'] = [0 if damage == 'frame' else True]
        elif damage in {'state', 'state_bool'}:
            metadata['chemical_state_context']['index'] = (
                1 if damage == 'state' else False
            )
        elif damage.startswith('context_'):
            context = json.loads(artifacts[context_name])
            if damage == 'context_coordinates':
                context['coordinates']['value'][1][0] += 0.01
            elif damage == 'context_identity':
                context['atom_attributes']['group_name'][3] = 'CHANGED'
            elif damage == 'context_unit':
                context['coordinates']['unit'] = 'pm'
            elif damage == 'context_duplicate_key':
                raw = json.dumps(context, separators=(',', ':'))
                artifacts[context_name] = ('{"n_atoms":0,' + raw[1:]).encode()
                return
            artifacts[context_name] = json.dumps(context).encode()
        elif damage == 'reference_path':
            metadata['reference_pdb_artifact'] = files['poc_info']
        elif damage == 'result_paths':
            files['pdb'] = files['poc_info']
        elif damage == 'missing_context':
            artifacts.pop(context_name)
        elif damage == 'extra_result_family':
            artifacts['output/another.pocInfo'] = artifacts[files['poc_info']]
        elif damage in {'duplicate_table_id', 'finite_table_change'}:
            name = files['poc_info']
            lines = artifacts[name].decode().splitlines()
            if damage == 'duplicate_table_id':
                lines.append(lines[1])
            else:
                values = lines[1].split()
                values[4] = str(float(values[4]) + 1)
                lines[1] = '\t'.join(values)
            artifacts[name] = ('\n'.join(lines) + '\n').encode()
        else:
            name = files['pdb'] if damage == 'pdb_coordinates' else files['poc']
            lines = artifacts[name].decode().splitlines()
            i = next(
                i for i, r in enumerate(lines) if r.startswith(('ATOM  ', 'HETATM'))
            )
            row = lines[i]
            if damage == 'poc_serial':
                row = row[:6] + f'{99999:5d}' + row[11:]
            elif damage == 'poc_identity':
                row = row[:12] + ' XX ' + row[16:]
            else:
                row = row[:30] + f'{float(row[30:38]) + 1:8.3f}' + row[38:]
            lines[i] = row
            artifacts[name] = ('\n'.join(lines) + '\n').encode()

    path = rewrite(output.run, tmp_path / 'changed', mutate)
    with pytest.raises((ArgumentError, ValueError)):
        recover(source, path)


@pytest.mark.parametrize(
    'name',
    [
        'selection',
        'structure_indices',
        'syntax',
        'chemical_state',
        'source_atom_indices',
        'zip_file',
        'provider_metadata',
    ],
)
def test_saved_selectors_cannot_override_bound_context(
    binding_profile, bound_case, name
):
    with pytest.raises(ArgumentError, match=name):
        recover(binding_profile[0], bound_case[1], **{name: None})


def test_saved_server_assertion_cannot_relabel_original_evidence(
    binding_profile, bound_case
):
    with pytest.raises(ValueError, match='server'):
        recover(binding_profile[0], bound_case[1], provider_server='castpfold')


def test_recovered_result_is_detached_from_bundle_and_live_source(
    binding_profile, bound_case, tmp_path
):
    source = msm.copy(binding_profile[0])
    path = tmp_path / 'disposable.zip'
    path.write_bytes(bound_case[1].read_bytes())
    result = recover(source, path)
    points = copy.deepcopy(result.input_points_nm)
    records = copy.deepcopy(result.records)
    path.unlink()
    xyz = msm.get(source, structure_indices=1, coordinates=True)
    msm.set(
        source, structure_indices=1, coordinates=xyz + puw.quantity([10, 0, 0], 'nm')
    )
    same(result.input_points_nm, points)
    same(result.records, records)


def test_submitted_pdb_route_retains_and_recovers_the_raw_server_zip(
    binding_profile, tmp_path
):
    source, mapping, _ = binding_profile
    archive = DATA / 'CASTp_3.0_server/2pk4.zip'
    with zipfile.ZipFile(archive) as raw:
        originals = {n: raw.read(n) for n in raw.namelist()}
    submitted = tmp_path / 'submitted.pdb'
    submitted.write_bytes(originals['2pk4.pdb'])
    before = snapshot(source)
    result = bind(source, mapping, archive, submitted_input_pdb=submitted)
    assert result.run.get_artifact('input/submitted.pdb') == submitted.read_bytes()
    assert (
        result.run.get_artifact('output/raw_server_zip/2pk4.zip')
        == archive.read_bytes()
    )
    assert_raw_witness(result, mapping, originals)
    bundle = tmp_path / 'server-retained.zip'
    result.run.save(bundle)
    recovered = recover(source, bundle)
    assert recovered.run == result.run
    same(recovered.records, result.records)
    same(snapshot(source), before)


def test_rehashed_raw_server_zip_cannot_disagree_with_retained_result_files(
    binding_profile, tmp_path
):
    from io import BytesIO

    source, mapping, _ = binding_profile
    archive = DATA / 'CASTp_3.0_server/2pk4.zip'
    with zipfile.ZipFile(archive) as raw:
        originals = {n: raw.read(n) for n in raw.namelist()}
    submitted = tmp_path / 'submitted.pdb'
    submitted.write_bytes(originals['2pk4.pdb'])
    result = bind(source, mapping, archive, submitted_input_pdb=submitted)

    def mutate(metadata, artifacts):
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w') as changed:
            for name, data in originals.items():
                if name.endswith('.pocInfo'):
                    rows = data.decode().splitlines()
                    values = rows[1].split()
                    values[4] = str(float(values[4]) + 1)
                    rows[1] = '\t'.join(values)
                    data = ('\n'.join(rows) + '\n').encode()
                changed.writestr(name, data)
        artifacts['output/raw_server_zip/2pk4.zip'] = buffer.getvalue()

    changed = rewrite(result.run, tmp_path / 'changed', mutate)
    with pytest.raises(ValueError):
        recover(source, changed)


def test_castpfold_zero_occupancy_rows_keep_fixed_width_identity_and_measurements(
    tmp_path,
):
    archive = DATA / 'CASTpFold_server/1psn.zip'
    with zipfile.ZipFile(archive) as raw:
        originals = {n: raw.read(n) for n in raw.namelist()}
    name = next(n for n in originals if n.endswith('.pdb'))
    pdb = tmp_path / name
    pdb.write_bytes(originals[name])
    rows = [
        r for r in pdb.read_text().splitlines() if r.startswith(('ATOM  ', 'HETATM'))
    ]
    assert any(float(row[54:60]) == 0 for row in rows)
    source = msm.convert(pdb, to_form='molsysmt.MolSys', get_missing_bonds=False)
    mapping = list(range(len(rows)))
    before = snapshot(source)
    result = tmt.get_provider_output(
        source,
        method='castpfold',
        backend='files',
        zip_file=archive,
        source_atom_indices=mapping,
    )
    assert result.pockets and result.run.metadata['server'] == 'castpfold'
    assert_raw_witness(result, mapping, originals)
    bundle = tmp_path / 'fold-bound.zip'
    result.run.save(bundle)
    recovered = recover(source, bundle, provider_server='castpfold')
    assert recovered.run == result.run
    same(recovered.records, result.records)
    same(snapshot(source), before)


def test_fresh_saved_recovery_never_imports_engines_or_contacts_urls(
    binding_profile, bound_case, tmp_path
):
    output = bound_case[0]
    expected = {
        'run_id': output.run.run_id,
        'points': output.input_points_nm,
        'records': [],
    }
    for record in output.records:
        expected['records'].append(
            {
                'source_id': record.source_id,
                'kind': record.record_kind,
                'indices': record.atom_indices,
                'parents': record.parent_source_ids,
                'measurements': {
                    name: {
                        'original_value': m.original_value,
                        'unit': m.original_unit,
                        'field': m.source_field,
                        'artifact': m.source_artifact,
                        'status': m.status,
                        'definition': m.definition,
                    }
                    for name, m in record.measurements.items()
                },
                'geometries': {
                    name: g.points_nm for name, g in record.geometries.items()
                },
            }
        )
    receipt = tmp_path / 'expected.json'
    receipt.write_text(json.dumps(expected, allow_nan=False))
    script = """
import importlib.abc
import json
from pathlib import Path
import socket
import sys
import urllib.request
attempts=[]
probes=[]
interop_imports=[]
roots={'alphaspace2','pocketeer','pycasta','castpfoldpy'}
def audit(event, args):
    if event == 'import' and args[0].split('.')[0] == 'mdtraj':
        interop_imports.append(args[0])
sys.addaudithook(audit)
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'mdtraj':
            probes.append(fullname)
        if fullname.split('.')[0] in roots or fullname.startswith('topomt.third_party.castp.servers') or fullname in {'topomt.third_party.castp.native','topomt.third_party.castp._native_impl'}:
            attempts.append(fullname)
            raise AssertionError('Saved recovery attempted provider execution: '+fullname)
sys.meta_path.insert(0, Block())
def network(*args, **kwargs):
    attempts.append('network')
    raise AssertionError('Saved recovery attempted a URL/network operation')
socket.create_connection=network
socket.socket.connect=network
socket.socket.connect_ex=network
urllib.request.urlopen=network
urllib.request.urlretrieve=network
import numpy as np
import topomt as tmt
from topomt import pyunitwizard as puw
assert not roots.intersection(sys.modules) and 'mdtraj' not in sys.modules
expected=json.loads(Path(sys.argv[3]).read_text())
with puw.context(standard_units=['pm','fs','radians']):
    active=list(puw.configure.report()['standard_units'])
    result=tmt.get_provider_output(sys.argv[1],method='castp',backend='files',bundle_file=sys.argv[2])
    assert result.run.run_id == expected['run_id']
    assert len(result.records) == len(expected['records'])
    np.testing.assert_allclose(result.input_points_nm,expected['points'],rtol=0,atol=1e-12)
    for record,saved in zip(result.records,expected['records'],strict=True):
        assert record.source_id == saved['source_id'] and record.record_kind == saved['kind']
        assert list(record.atom_indices) == saved['indices']
        assert list(record.parent_source_ids) == saved['parents']
        assert set(record.measurements) == set(saved['measurements'])
        for name,measurement in record.measurements.items():
            original=saved['measurements'][name]
            assert measurement.run_id == result.run.run_id
            assert measurement.original_unit == original['unit']
            assert measurement.source_field == original['field']
            assert measurement.source_artifact == original['artifact']
            assert measurement.status == original['status']
            assert measurement.definition == original['definition']
            np.testing.assert_allclose(measurement.original_value,original['original_value'],rtol=0,atol=1e-12)
            value=measurement.value if original['unit']=='1' else puw.get_value(measurement.value,to_unit=original['unit'])
            np.testing.assert_allclose(value,original['original_value'],rtol=0,atol=1e-9)
        assert set(record.geometries) == set(saved['geometries'])
        for name,geometry in record.geometries.items():
            np.testing.assert_allclose(geometry.points_nm,saved['geometries'][name],rtol=0,atol=1e-12)
    assert puw.configure.report()['standard_units'] == active
report={'original_or_network_attempts':attempts,'mdtraj_import_events':interop_imports,'mdtraj_loaded':'mdtraj' in sys.modules,'mdtraj_availability_queries':len(probes)}
assert not attempts and not roots.intersection(sys.modules), report
assert not interop_imports and 'mdtraj' not in sys.modules, report
Path(sys.argv[4]).write_text(json.dumps(report,sort_keys=True))
"""
    diagnostic = tmp_path / 'fresh-recovery.json'
    result = subprocess.run(
        [
            sys.executable,
            '-B',
            '-c',
            script,
            str(binding_profile[2]),
            str(bound_case[1]),
            str(receipt),
            str(diagnostic),
        ],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(diagnostic.read_text())
    assert (
        report['original_or_network_attempts'] == report['mdtraj_import_events'] == []
    )
    assert report['mdtraj_loaded'] is False
