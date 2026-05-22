from collections import Counter

from devtools.castp.compare_castp3_oracles import (
    DEFAULT_SELECTION,
    ParityRow,
    _atom_id_lookup,
    atom_ids_from_castp_labels,
    compare_atom_id_sets,
    compare_castp3_oracle_zip,
    native_atom_id_sets,
    render_markdown_table,
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
    assert Counter(atom_sets['mouth']) != Counter([
        frozenset({10, 20}),
        frozenset({20, 30}),
    ])


def test_render_markdown_table():
    table = render_markdown_table([
        ParityRow(
            pdb_id='3phv',
            feature_type='mouth',
            oracle_count=11,
            native_count=11,
            exact_count=11,
        )
    ])

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
