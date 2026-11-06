"""Original CASTp payload discovery preserves bytes and rejects ambiguity."""

import stat
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import numpy as np
import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun

DATA = Path(tmt.__file__).parent / 'data'
CASTP3 = DATA / 'CASTp_3.0_server/1tcd.zip'
CASTPFOLD = DATA / 'CASTpFold_server/1psn.zip'
NESTED = 'download/processed/'
SUFFIXES = ('.poc', '.pocInfo', '.mouth', '.mouthInfo', '.pdb')


def members(path):
    with ZipFile(path) as archive:
        return [(name, archive.read(name)) for name in archive.namelist()]


def materialize(tmp_path, rows, route, *, reverse=False):
    rows = list(reversed(rows)) if reverse else rows
    if route == 'zip':
        path = tmp_path / 'download.zip'
        with ZipFile(path, 'w', compression=ZIP_DEFLATED) as archive:
            for name, data in rows:
                archive.writestr(name, data)
        return {'zip_file': path}
    path = tmp_path / 'directory'
    path.mkdir()
    for name, data in rows:
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return {'dir_path': path}


def load(**options):
    return tmt.get_provider_output(method='castp', backend='files', **options)


def same_value(actual, expected):
    if not isinstance(expected, (str, bytes, dict, set)) and puw.is_quantity(expected):
        assert puw.get_unit(actual) == puw.get_unit(expected)
        np.testing.assert_allclose(
            puw.get_value(actual, to_unit=puw.get_unit(expected)),
            puw.get_value(expected),
            rtol=0,
            atol=1e-12,
        )
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            same_value(actual[key], expected[key])
    elif isinstance(expected, (float, np.floating)):
        np.testing.assert_equal(actual, expected)
    else:
        assert actual == expected


def assert_references(output, originals, prefix):
    referenced = set()
    for record in output.records:
        for key, value in record.fields.items():
            if key.endswith('source_artifact'):
                referenced.add(value)
        for measurement in record.measurements.values():
            assert measurement.run_id == output.run.run_id
            referenced.add(measurement.source_artifact)
    assert referenced
    for name in referenced:
        assert name.startswith('output/' + prefix)
        relative = name.removeprefix('output/' + prefix)
        assert output.run.get_artifact(name) == originals[relative]


@pytest.fixture(
    scope='module', params=[CASTP3, CASTPFOLD], ids=['castp3', 'castpfold-jobid']
)
def original_case(request):
    path = request.param
    return path, dict(members(path)), load(zip_file=path)


@pytest.mark.parametrize('route', ['zip', 'directory'])
@pytest.mark.parametrize('reverse', [False, True])
def test_nested_original_payload_preserves_records_and_exact_artifact_provenance(
    original_case, tmp_path, route, reverse
):
    _, originals, baseline = original_case
    options = materialize(
        tmp_path,
        [(NESTED + n, b) for n, b in originals.items()],
        route,
        reverse=reverse,
    )
    output = load(**options)
    assert [r.source_id for r in output.records] == [
        r.source_id for r in baseline.records
    ]
    assert len(output.pockets) == len(baseline.pockets) > 0
    for actual, expected in zip(output.records, baseline.records, strict=True):
        for name in (
            'record_kind',
            'atom_indices',
            'atom_labels',
            'atom_role',
            'parent_source_ids',
        ):
            assert getattr(actual, name) == getattr(expected, name)
        assert actual.fields.keys() == expected.fields.keys()
        for name, expected_value in expected.fields.items():
            if name == 'provider_run_id':
                assert actual.fields[name] == output.run.run_id
            elif name.endswith('source_artifact'):
                assert actual.fields[
                    name
                ] == 'output/' + NESTED + expected_value.removeprefix('output/')
            elif name != 'external_measurements':
                same_value(actual.fields[name], expected_value)
        assert actual.measurements.keys() == expected.measurements.keys()
        for name, expected_measurement in expected.measurements.items():
            measured = actual.measurements[name]
            for attribute in (
                'original_value',
                'original_unit',
                'source_field',
                'definition',
                'issue_url',
                'status',
            ):
                same_value(
                    getattr(measured, attribute),
                    getattr(expected_measurement, attribute),
                )
            same_value(measured.value, expected_measurement.value)
        assert actual.geometries.keys() == expected.geometries.keys()
        for name, expected_geometry in expected.geometries.items():
            geometry = actual.geometries[name]
            assert geometry.kind == expected_geometry.kind
            assert geometry.definition == expected_geometry.definition
            np.testing.assert_allclose(
                geometry.points_nm, expected_geometry.points_nm, rtol=0, atol=1e-12
            )
            assert geometry.radii_nm == expected_geometry.radii_nm
    for name, data in originals.items():
        assert output.run.get_artifact('output/' + NESTED + name) == data
    assert_references(output, originals, NESTED)
    bundle = tmp_path / 'retained.zip'
    output.run.save(bundle)
    restored = ProviderRun.load(bundle)
    assert restored.run_id == output.run.run_id
    assert restored.artifacts == output.run.artifacts


@pytest.mark.parametrize('prefix', ['', NESTED], ids=['flat', 'nested'])
def test_info_only_directory_preserves_unknown_membership(tmp_path, prefix):
    name, data = next((n, b) for n, b in members(CASTP3) if n.endswith('.pocInfo'))
    output = load(**materialize(tmp_path, [(prefix + name, data)], 'directory'))
    assert len(output.records) == len(output.pockets) == 78
    assert output.input_coordinates is None
    assert all(
        r.atom_indices is None and r.atom_labels is None and r.geometries == {}
        for r in output.pockets
    )
    assert_references(output, {name: data}, prefix)
    bundle = tmp_path / 'info-only.zip'
    output.run.save(bundle)
    restored = ProviderRun.load(bundle)
    assert (
        restored.run_id == output.run.run_id
        and restored.artifacts == output.run.artifacts
    )


@pytest.mark.parametrize('prefix', ['', NESTED], ids=['flat', 'nested'])
@pytest.mark.parametrize('suffix', ['.pocInfo', '.mouthInfo'])
def test_header_only_result_is_known_empty_and_retained(tmp_path, prefix, suffix):
    name, data = next((n, b) for n, b in members(CASTP3) if n.endswith(suffix))
    header = next(line for line in data.splitlines() if line.strip()) + b'\n'
    output = load(**materialize(tmp_path, [(prefix + name, header)], 'directory'))
    assert output.records == output.pockets == ()
    assert output.run.get_artifact('output/' + prefix + name) == header


@pytest.mark.parametrize('route', ['zip', 'directory'])
@pytest.mark.parametrize('suffix', ['.pocInfo', '.mouthInfo'])
def test_zero_byte_measurement_table_is_not_a_known_empty_result(
    tmp_path, route, suffix
):
    options = materialize(tmp_path, [('1tcd' + suffix, b'')], route)
    with pytest.raises(ValueError):
        load(**options)


@pytest.mark.parametrize('content', ['empty', 'pdb-only', 'readme-only'])
def test_directory_without_result_artifacts_is_rejected(tmp_path, content):
    rows = []
    if content == 'pdb-only':
        rows = [(n, b) for n, b in members(CASTP3) if n.endswith('.pdb')]
    elif content == 'readme-only':
        rows = [('README.txt', b'No scientific result artifacts.\n')]
    with pytest.raises(ValueError):
        load(**materialize(tmp_path, rows, 'directory'))


@pytest.mark.parametrize('route', ['zip', 'directory'])
@pytest.mark.parametrize('suffix', SUFFIXES)
def test_multiple_candidates_for_one_artifact_kind_are_rejected(
    tmp_path, route, suffix
):
    rows = members(CASTP3)
    name, data = next((n, b) for n, b in rows if n.endswith(suffix))
    if suffix == '.pdb':
        # A matching core-family PDB legitimately outranks unrelated auxiliary
        # PDBs. Ambiguity is real when neither of two structures matches it.
        rows = [(n, b) for n, b in rows if not n.endswith('.pdb')]
        rows.extend([('first_unmatched.pdb', data), ('second_unmatched.pdb', data)])
    else:
        rows.append(('second/' + name, data))
    with pytest.raises(ValueError):
        load(**materialize(tmp_path, rows, route))


@pytest.mark.parametrize('route', ['zip', 'directory'])
@pytest.mark.parametrize('suffix', SUFFIXES[:-1])
def test_incoherent_result_stems_are_rejected(tmp_path, route, suffix):
    rows = [
        ('different' + suffix if n.endswith(suffix) else n, b)
        for n, b in members(CASTP3)
    ]
    with pytest.raises(ValueError):
        load(**materialize(tmp_path, rows, route))


@pytest.mark.parametrize('combination', ['zip-dir', 'zip-individual', 'dir-individual'])
def test_archive_directory_and_individual_routes_are_mutually_exclusive(
    tmp_path, combination
):
    directory = materialize(tmp_path, members(CASTP3), 'directory')['dir_path']
    options = {
        'zip-dir': {'zip_file': CASTP3, 'dir_path': directory},
        'zip-individual': {
            'zip_file': CASTP3,
            'pocInfo_file': directory / '1tcd.pocInfo',
        },
        'dir-individual': {'dir_path': directory, 'pdb_file': directory / '1tcd.pdb'},
    }[combination]
    with pytest.raises(ValueError):
        load(**options)


def test_duplicate_zip_member_names_are_rejected(tmp_path):
    path = tmp_path / 'duplicate.zip'
    rows = members(CASTP3)
    with ZipFile(path, 'w') as archive:
        for name, data in rows:
            archive.writestr(name, data)
        with pytest.warns(UserWarning, match='Duplicate name'):
            archive.writestr(*rows[0])
    with pytest.raises(ValueError):
        load(zip_file=path)


@pytest.mark.parametrize(
    'name',
    [
        '../escape.txt',
        '/absolute.txt',
        'download//README.txt',
        'download\\README.txt',
        'download/./README.txt',
        'C:/job.pocInfo',
    ],
)
def test_unsafe_or_noncanonical_zip_member_paths_are_rejected(tmp_path, name):
    options = materialize(
        tmp_path, [*members(CASTP3), (name, b'ambiguous path')], 'zip'
    )
    with pytest.raises(ValueError, match='archive path'):
        load(**options)


def test_zip_member_nul_is_rejected_using_original_untruncated_name(tmp_path):
    placeholder = 'download/extra_marker.txt'
    options = materialize(
        tmp_path, [*members(CASTP3), (placeholder, b'unchanged payload')], 'zip'
    )
    path = options['zip_file']
    original, corrupted = (
        placeholder.encode(),
        placeholder.replace('_', '\0', 1).encode(),
    )
    raw = path.read_bytes()
    assert len(original) == len(corrupted) and raw.count(original) == 2
    path.write_bytes(raw.replace(original, corrupted))
    with ZipFile(path) as archive:
        assert any(info.orig_filename != info.filename for info in archive.infolist())
    with pytest.raises(ValueError, match='archive path'):
        load(**options)


def test_zip_symlink_entries_are_rejected(tmp_path):
    path = tmp_path / 'symlink.zip'
    with ZipFile(path, 'w') as archive:
        for name, data in members(CASTP3):
            archive.writestr(name, data)
        entry = ZipInfo('download/linked.txt')
        entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(entry, '../1tcd.pdb')
    with pytest.raises(ValueError):
        load(zip_file=path)


@pytest.mark.parametrize(
    'aliases',
    [
        ('notes/README.txt', 'Notes/details.txt'),
        ('notes/README.txt', 'notes/readme.txt'),
    ],
)
def test_zip_case_aliases_cannot_change_retained_artifact_identity(tmp_path, aliases):
    rows = [*members(CASTP3), *((name, b'original bytes') for name in aliases)]
    options = materialize(tmp_path, rows, 'zip')
    with pytest.raises(ValueError, match='[Aa]liased CASTp archive path'):
        load(**options)


@pytest.mark.parametrize('route', ['zip', 'directory'])
def test_original_empty_mouth_file_remains_present_and_valid(tmp_path, route):
    original = DATA / 'CASTpFold_server/1crn.zip'
    rows = members(original)
    name, empty = next((n, b) for n, b in rows if n.endswith('.mouth'))
    assert empty == b''
    output = load(**materialize(tmp_path, [(NESTED + n, b) for n, b in rows], route))
    assert len(output.records) == len(output.pockets) == 1
    assert output.pockets[0].fields['n_mouths'] == 0
    assert output.run.get_artifact('output/' + NESTED + name) == empty


def test_explicit_individual_files_can_have_custom_names(tmp_path):
    argument_names = ('.poc', '.pocInfo', '.mouth', '.mouthInfo', '.pdb')
    arguments = ('poc_file', 'pocInfo_file', 'mouth_file', 'mouthInfo_file', 'pdb_file')
    originals, options = {}, {}
    for index, (suffix, argument) in enumerate(
        zip(argument_names, arguments, strict=True)
    ):
        _, data = next((n, b) for n, b in members(CASTP3) if n.endswith(suffix))
        name = f'custom-{index}{suffix}'
        path = tmp_path / name
        path.write_bytes(data)
        originals[name] = data
        options[argument] = path
    output = load(**options)
    assert len(output.records) == 120 and len(output.pockets) == 78
    assert_references(output, originals, '')


@pytest.mark.parametrize('route', ['zip', 'directory'])
def test_matching_family_pdb_is_selected_and_auxiliary_pdb_is_retained(tmp_path, route):
    rows = members(CASTP3)
    _, data = next((n, b) for n, b in rows if n.endswith('.pdb'))
    auxiliary = 'fpocket/1tcd_out/pockets/pocket1_atm.pdb'
    output = load(**materialize(tmp_path, [*rows, (auxiliary, data)], route))
    assert len(output.records) == 120 and len(output.pockets) == 78
    assert output.run.get_artifact('output/' + auxiliary) == data
    assert_references(output, dict(rows), '')


def test_packaged_demo_retains_auxiliary_fpocket_files_without_ambiguity():
    directory = DATA / 'TcTIM/CASTp_1tcd'
    output = load(dir_path=directory)
    assert len(output.records) == 120 and len(output.pockets) == 78
    for path in directory.rglob('*'):
        if path.is_file():
            name = 'output/' + path.relative_to(directory).as_posix()
            assert output.run.get_artifact(name) == path.read_bytes()
    originals = {
        path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()
    }
    assert_references(output, originals, '')


def test_nested_original_zip_is_discovered_without_flattening(tmp_path):
    path = tmp_path / 'download.zip'
    with ZipFile(CASTP3) as source, ZipFile(path, 'w') as target:
        for name in reversed(source.namelist()):
            target.writestr('download/processed/' + name, source.read(name))
    output = tmt.get_provider_output(method='castp', backend='files', zip_file=path)
    assert len(output.pockets) == 78
    assert len(output.records) == 120
    with ZipFile(CASTP3) as source:
        for name in source.namelist():
            assert output.run.get_artifact(
                'output/download/processed/' + name
            ) == source.read(name)
