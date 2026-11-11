"""Original specialist result protocols, independent of installed executables."""

import importlib
from pathlib import Path

import pytest

from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun

DATA = Path(__file__).parent / 'data/original_local'


def capture(tmp_path, provider, *, empty=False, replace_files=None):
    source = DATA / provider / ('empty_input.pdb' if empty else 'input.pdb')
    output = tmp_path / 'results'
    output.mkdir()
    names = (
        ['stdout.txt', 'profile.sph']
        if provider == 'hole'
        else ['interfaces.txt', 'assemblies.txt']
    )
    for name in names:
        original = DATA / provider / (('empty_' if empty else '') + name)
        (output / name).write_bytes(original.read_bytes())
    for name, content in (replace_files or {}).items():
        (output / name).write_bytes(content)
    return ProviderRun.capture(provider, 'cli', source, output)


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_hole_original_profile_separates_samples_midpoints_and_visual_extensions(
    tmp_path, policy
):
    with puw.context(standard_units=policy):
        result = importlib.import_module('topomt.third_party.hole.parser').parse_output(
            capture(tmp_path, 'hole')
        )
        assert len(result.channels) == 1
        assert result.pockets == result.cavities == result.regions == ()
        record = result.channels[0]
        profile = record.fields['profile']
        assert len(profile['sampled']['radius']['value']) == 67
        assert len(profile['midpoints']['radius']['value']) == 66
        assert profile['sampled']['radius']['unit'] == 'angstroms'
        assert profile['sampled']['coordinate']['value'][0] == -16.5
        assert profile['sampled']['coordinate']['value'][-1] == 16.5
        assert profile['sampled']['radius']['value'][53] == pytest.approx(3.97751)
        assert len(record.geometries['centerline'].points_nm) == 67
        assert record.atom_indices is None
        assert record.measurements['minimum_radius'].original_value == pytest.approx(
            3.97751
        )
        assert puw.get_value(
            record.measurements['minimum_radius'].value, to_unit='angstroms'
        ) == pytest.approx(3.97751)
        assert 'volume' not in record.measurements


@pytest.mark.parametrize('change', ['completion', 'numeric', 'profile', 'version'])
def test_hole_corrupt_or_unfinished_original_output_is_not_empty_success(
    tmp_path, change
):
    original = DATA / 'hole'
    text = (original / 'stdout.txt').read_text()
    sphere = (original / 'profile.sph').read_bytes()
    if change == 'completion':
        text = text.replace('HOLE: normal completion', '')
    elif change == 'numeric':
        text = text.replace('-16.50000     6.91692', '-16.50000          nan')
    elif change == 'profile':
        sphere = sphere.replace(
            b'  -0.019   0.009   0.000', b'  99.000   0.009   0.000'
        )
    else:
        text = text.replace('HOLE release 2.3.1', 'HOLE release 99.0.0')
    with pytest.raises(ValueError):
        importlib.import_module('topomt.third_party.hole.parser').parse_output(
            capture(
                tmp_path,
                'hole',
                replace_files={'stdout.txt': text.encode(), 'profile.sph': sphere},
            )
        )


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_pisa_original_interfaces_keep_two_sides_units_contacts_and_supplied_context(
    tmp_path, policy
):
    with puw.context(standard_units=policy):
        result = importlib.import_module('topomt.third_party.pisa.parser').parse_output(
            capture(tmp_path, 'pisa')
        )
        assert len(result.interfaces) == 1
        assert result.pockets == result.cavities == result.channels == ()
        interface = result.interfaces[0]
        assert interface.source_id == '1'
        assert interface.atom_indices is None
        assert [p['chain_id'] for p in interface.fields['participants']] == ['A', 'B']
        assert interface.fields['contact_counts']['other-bonds'] == 24
        distance = interface.fields['contacts']['other-bonds'][0]['distance']
        assert distance['unit'] == 'angstroms'
        assert distance['value'] == pytest.approx(3.7947331922)
        area = interface.measurements['interface_area']
        assert area.original_value == pytest.approx(125.73203716)
        assert puw.get_value(area.value, to_unit='angstroms**2') == pytest.approx(
            125.73203716
        )
        assert (
            interface.measurements['solvation_energy'].original_unit
            == 'kilocalories/mol'
        )
        assert 'biological' not in interface.fields
        assert result.assembly_measurements[
            'buried_surface_area'
        ].original_value == pytest.approx(251.46407431)
        assert result.assembly_policy == 'supplied_as_is'


def test_pisa_explicit_original_empty_is_evaluated_and_keeps_assembly(tmp_path):
    result = importlib.import_module('topomt.third_party.pisa.parser').parse_output(
        capture(tmp_path, 'pisa', empty=True)
    )
    assert result.interfaces == ()
    assert result.assembly_policy == 'supplied_as_is'
    assert result.assembly_measurements['buried_surface_area'].original_value == 0


@pytest.mark.parametrize(
    'change', ['count', 'energy', 'status', 'participant', 'entity', 'assembly']
)
def test_pisa_missing_or_inconsistent_original_is_not_empty_success(tmp_path, change):
    text = (DATA / 'pisa/interfaces.txt').read_text()
    assembly = (DATA / 'pisa/assemblies.txt').read_bytes()
    if change == 'count':
        text = text.replace(
            '<n_interfaces>1</n_interfaces>', '<n_interfaces>0</n_interfaces>'
        )
    elif change == 'energy':
        text = text.replace('-1.8709236348', 'nan')
    elif change == 'status':
        text = text.replace('<status>Ok</status>', '<status>Error</status>')
    elif change == 'participant':
        text = text.replace('<chain_id>B</chain_id>', '<chain_id>A</chain_id>')
    elif change == 'entity':
        text = '<!DOCTYPE x [<!ENTITY x "payload">]>' + text
    else:
        assembly = b'<pisa_results><status>Ok</status></pisa_results>'
    with pytest.raises(ValueError):
        importlib.import_module('topomt.third_party.pisa.parser').parse_output(
            capture(
                tmp_path,
                'pisa',
                replace_files={
                    'interfaces.txt': text.encode(),
                    'assemblies.txt': assembly,
                },
            )
        )


def test_hole_known_input_data_is_credited_only_when_selected():
    from topomt._ackredit import _references

    plain = _references('hole', 'original', 'test', {'version': '2.3.1'})
    selected = _references(
        'hole',
        'original',
        'test',
        {'version': '2.3.1', 'input_data_references': ['amber_1984']},
    )
    assert not any(entry['item'].get('doi') == '10.1021/ja00315a051' for entry in plain)
    paper = next(
        entry for entry in selected if entry['item'].get('doi') == '10.1021/ja00315a051'
    )
    assert paper['roles'] == ['input_data_reference']
    with pytest.raises(ValueError):
        _references('hole', 'original', 'test', {'input_data_references': ['unknown']})
