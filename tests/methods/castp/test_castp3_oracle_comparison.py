import hashlib
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import pytest

from devtools.castp.compare_castp3_oracles import (
    DEFAULT_SELECTION,
    ParityRow,
    _atom_id_lookup,
    atom_ids_from_castp_labels,
    audit_castp3_oracle_zip,
    compare_atom_id_sets,
    compare_castp3_oracle_zip,
    compare_membership_details,
    native_atom_id_sets,
    render_markdown_table,
)
from topomt.io.load_CASTp import (
    _parse_mouth_file,
    _parse_poc_file,
    _parse_poc_info_file,
)


def test_membership_details_preserve_missing_duplicate_and_extra_sets():
    result = compare_membership_details(
        [frozenset({2, 1}), frozenset({4})],
        [frozenset({1, 2}), frozenset({1, 2})],
    )
    assert result == {
        'oracle_count': 2,
        'native_count': 2,
        'exact_count': 1,
        'missing_memberships': [[1, 2]],
        'extra_memberships': [[4]],
        'passed': False,
    }


def test_membership_details_compare_complete_multisets_and_empty_cases():
    for sets in ([], [frozenset({1, 2}), frozenset({1, 2})]):
        result = compare_membership_details(sets, list(reversed(sets)))
        assert result['oracle_count'] == result['native_count'] == len(sets)
        assert result['exact_count'] == len(sets)
        assert result['passed']
        assert not result['missing_memberships']
        assert not result['extra_memberships']


def test_membership_audit_keeps_source_hashes_policy_and_original_indices(
    tmp_path, monkeypatch
):
    from devtools.castp import compare_castp3_oracles as comparison

    pdb = b'ATOM    101  N   GLY A   1       0.000   0.000   0.000  1.00  0.00           N  \nEND\n'
    archive_path = tmp_path / 'synthetic.zip'
    with ZipFile(archive_path, 'w') as archive:
        archive.writestr('synthetic.pdb', pdb)
    monkeypatch.setattr(comparison, '_atom_id_lookup', lambda _path: {0: 101})
    monkeypatch.setattr(
        comparison,
        'native_castp3',
        lambda _path, **_kwargs: (
            [{'feature_type': 'pocket', 'atom_indices': [0], 'mouths': []}],
            None,
        ),
    )
    monkeypatch.setattr(
        comparison,
        'oracle_atom_id_sets',
        lambda _path: {'pocket': [frozenset({101})], 'mouth': []},
    )
    result = audit_castp3_oracle_zip(archive_path, radii_model='castp3_protor')
    assert (
        result['archive_sha256']
        == hashlib.sha256(archive_path.read_bytes()).hexdigest()
    )
    assert result['pdb_sha256'] == hashlib.sha256(pdb).hexdigest()
    assert result['policy']['radii_model'] == 'castp3_protor'
    assert result['policy']['probe_radius'] == {'value': 1.4, 'unit': 'angstrom'}
    assert result['policy']['selection'] == DEFAULT_SELECTION
    assert not result['policy']['probe_limited_depth']
    assert result['policy']['peripheral_atom_expansion_steps'] == 0
    assert result['policy']['alpha_boundary_epsilon_length'] == {
        'value': 0.0,
        'unit': 'angstrom',
    }
    assert result['policy']['alpha_boundary_face_epsilon_rank'] == 0
    assert result['features']['pocket']['exact_count'] == 1
    assert result['passed']


@pytest.mark.parametrize('pdb_id', ['1crn', '1rop', '2pk4', '3phv', '1ifb', '1hew'])
def test_corrected_native_feature_memberships_match_archive_controls(pdb_id):
    archive_path = (
        Path(__file__).resolve().parents[3]
        / 'topomt/data/CASTpFold_server'
        / f'{pdb_id}.zip'
    )
    result = audit_castp3_oracle_zip(archive_path, radii_model='castp3_protor')

    assert result['passed']
    for feature in result['features'].values():
        assert (
            feature['oracle_count'] == feature['native_count'] == feature['exact_count']
        )
        assert not feature['missing_memberships']
        assert not feature['extra_memberships']


@pytest.mark.parametrize('pdb_id,server_id', [('3ptb', 27), ('1bmq', 34)])
def test_corrected_profile_recovers_historical_micro_pockets(
    pdb_id, server_id, tmp_path
):
    archive_path = (
        Path(__file__).resolve().parents[3]
        / 'topomt/data/CASTpFold_server'
        / f'{pdb_id}.zip'
    )
    with ZipFile(archive_path) as archive:
        archive.extractall(tmp_path)
    pocket_labels = _parse_poc_file(next(tmp_path.glob('*.poc')))
    mouth_labels = _parse_mouth_file(next(tmp_path.glob('*.mouth')))
    info = _parse_poc_info_file(next(tmp_path.glob('*.pocInfo')))
    assert info[server_id]['n_mouths'] == 1

    result = audit_castp3_oracle_zip(archive_path, radii_model='castp3_protor')

    for kind, labels in [('pocket', pocket_labels), ('mouth', mouth_labels)]:
        target = sorted(atom_ids_from_castp_labels(labels[server_id]))
        assert target
        assert target not in result['features'][kind]['missing_memberships']


def test_pinned_corrected_membership_panel_is_complete_and_source_identified():
    repository = Path(__file__).resolve().parents[3]
    historical_cases = set(
        '1crn 1rop 2pk4 3phv 8rat 1stp 1rob 2lyz 1ifb 2ifb '
        '1hew 1stn 1hel 1snc 5dfr 1hfc 1brq 1rbp 1hsi 1hiv '
        '1ida 3ptb 3ptn 4phv 2tga 1cge 1a6u 1srf 1mtw 2ctv '
        '1esa 1a6w 1inc 1bmq 1ahc 4ca2 3tms 1djb'.split()
    )
    artifact_root = repository / 'devguide/castp/artifacts'
    void_panel = json.loads(
        (artifact_root / 'void_audit_2026_10_01_prepared_inputs.json').read_text()
    )
    expected_cases = historical_cases | {case['case'] for case in void_panel['cases']}
    report = json.loads(
        (
            artifact_root / 'membership_audit_2026_10_02_corrected_inputs.json'
        ).read_text()
    )
    assert report['complete']
    assert set(report['requested_cases']) == expected_cases
    assert len(report['cases']) == len(expected_cases) == 40
    assert {case['case'] for case in report['cases']} == expected_cases
    for case in report['cases']:
        assert 'error' not in case
        archive_path = (
            repository / 'topomt/data/CASTpFold_server' / f'{case["case"]}.zip'
        )
        assert (
            case['archive_sha256']
            == hashlib.sha256(archive_path.read_bytes()).hexdigest()
        )
        with ZipFile(archive_path) as archive:
            member = next(name for name in archive.namelist() if name.endswith('.pdb'))
            assert (
                case['pdb_sha256'] == hashlib.sha256(archive.read(member)).hexdigest()
            )
        assert case['policy']['radii_model'] == 'castp3_protor'
        assert case['policy']['selection'] == DEFAULT_SELECTION
        assert case['policy']['probe_radius'] == {'value': 1.4, 'unit': 'angstrom'}
        assert not case['policy']['probe_limited_depth']
        assert case['policy']['peripheral_atom_expansion_steps'] == 0
        assert case['policy']['alpha_boundary_epsilon_length'] == {
            'value': 0.0,
            'unit': 'angstrom',
        }
        assert case['policy']['alpha_boundary_face_epsilon_rank'] == 0
        for counts in case['features'].values():
            assert (
                len(counts['missing_memberships'])
                == counts['oracle_count'] - counts['exact_count']
            )
            assert (
                len(counts['extra_memberships'])
                == counts['native_count'] - counts['exact_count']
            )
            assert counts['passed'] == (
                counts['oracle_count']
                == counts['native_count']
                == counts['exact_count']
            )
        assert case['passed'] == all(
            counts['passed'] for counts in case['features'].values()
        )
    for kind, summary in report['summary'].items():
        rows = [case['features'][kind] for case in report['cases']]
        for field in ['oracle_count', 'native_count', 'exact_count']:
            assert summary[field] == sum(row[field] for row in rows)
        assert summary['nonempty_oracle_cases'] == sum(
            row['oracle_count'] > 0 for row in rows
        )
        assert summary['nonempty_cases_fully_exact'] == sum(
            row['passed'] and row['oracle_count'] > 0 for row in rows
        )


def test_atom_ids_from_castp_labels_uses_pdb_atom_id_field():
    labels = {
        '12-CA/ALA/A',
        '7-N/GLY/A',
        '103-OXT/LYS/B',
    }

    assert atom_ids_from_castp_labels(labels) == frozenset({7, 12, 103})


def test_atom_id_lookup_uses_pdb_serials_not_molsysmt_atom_ids(tmp_path):
    pdb_file = tmp_path / 'serials.pdb'
    pdb_file.write_text(
        'ATOM    101  N   GLY A   1       0.000   0.000   0.000  1.00  0.00           N  \n'
        'ATOM    205  CA  GLY A   1       1.000   0.000   0.000  1.00  0.00           C  \n'
        'HETATM  604  O   HOH A   2       2.000   0.000   0.000  1.00  0.00           O  \n'
        'END\n'
    )

    assert _atom_id_lookup(pdb_file) == {0: 101, 1: 205, 2: 604}


def test_atom_id_lookup_respects_parser_alternate_location_removal(tmp_path):
    archive_path = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1rob.zip'
    )
    with ZipFile(archive_path) as archive:
        member = next(name for name in archive.namelist() if name.endswith('.pdb'))
        pdb_file = tmp_path / '1rob.pdb'
        pdb_file.write_bytes(archive.read(member))

    lookup = _atom_id_lookup(pdb_file)

    assert len(lookup) == 1073
    assert lookup[66] == 68
    assert 67 not in lookup.values()


def test_compare_atom_id_sets_counts_exact_multiset_matches():
    oracle_sets = [
        frozenset({1, 2}),
        frozenset({1, 2}),
        frozenset({3}),
    ]
    native_sets = [
        frozenset({1, 2}),
        frozenset({4}),
    ]

    assert compare_atom_id_sets(native_sets, oracle_sets) == (3, 2, 1)


def test_native_atom_id_sets_exports_aggregated_mouth_records():
    records = [
        {
            'feature_type': 'branched_channel',
            'atom_indices': [0, 1, 2],
            'topological_mouths': [
                {'atom_indices': [0, 1]},
                {'atom_indices': [1, 2]},
            ],
            'mouths': [
                {'atom_indices': [0, 1, 2]},
            ],
        }
    ]

    atom_sets = native_atom_id_sets(records, {0: 10, 1: 20, 2: 30})

    assert atom_sets['branched_channel'] == [frozenset({10, 20, 30})]
    assert atom_sets['mouth'] == [frozenset({10, 20, 30})]
    assert Counter(atom_sets['mouth']) != Counter(
        [
            frozenset({10, 20}),
            frozenset({20, 30}),
        ]
    )


def test_render_markdown_table():
    table = render_markdown_table(
        [
            ParityRow(
                pdb_id='3phv',
                feature_type='mouth',
                oracle_count=11,
                native_count=11,
                exact_count=11,
            )
        ]
    )

    assert '| pdb | type | oracle | native | exact |' in table
    assert '| 3phv | mouth | 11 | 11 | 11 |' in table


def test_castp3_oracle_harness_defaults_to_protein_only_selection():
    assert DEFAULT_SELECTION == 'molecule_type in ["protein", "peptide"]'


def test_castp3_oracle_comparison_defaults_to_full_depth():
    defaults = compare_castp3_oracle_zip.__kwdefaults__

    assert defaults['probe_limited_depth'] is False


def test_castp3_oracle_comparison_disables_peripheral_expansion_by_default():
    defaults = compare_castp3_oracle_zip.__kwdefaults__

    assert defaults['peripheral_atom_expansion_steps'] == 0


def test_castp3_oracle_comparison_disables_alpha_boundary_epsilon_by_default():
    defaults = compare_castp3_oracle_zip.__kwdefaults__

    assert defaults['alpha_boundary_epsilon_length'] == 0.0


def test_castp3_oracle_comparison_disables_face_epsilon_by_default():
    defaults = compare_castp3_oracle_zip.__kwdefaults__

    assert defaults['alpha_boundary_face_epsilon_rank'] == 0
