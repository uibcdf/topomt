"""ProtOr typing tests for the experimental CASTp3 backend."""

import numpy as np

from topomt.third_party.castp3.core.castp_core.geometry import (
    _infer_protor_type_for_atom,
    _protor_radii_for_labels,
)


def test_castp3_protor_type_table_covers_standard_and_variant_residues():
    assert _infer_protor_type_for_atom('ARG', 'NH1', 'N', 1) == 'N3H2'
    assert _infer_protor_type_for_atom('TYR', 'OH', 'O', 1) == 'O2H1'
    assert _infer_protor_type_for_atom('TRP', 'NE1', 'N', 2) == 'N3H1'
    assert _infer_protor_type_for_atom('MET', 'SD', 'S', 2) == 'S2H0'
    assert _infer_protor_type_for_atom('CYS', 'SG', 'S', 1) == 'S2H1'
    assert _infer_protor_type_for_atom('CYX', 'SG', 'S', 2) == 'S2H0'
    assert _infer_protor_type_for_atom('ASH', 'OD2', 'O', 1) == 'O2H1'
    assert _infer_protor_type_for_atom('LYN', 'NZ', 'N', 1) == 'N3H2'


def test_castp3_protor_type_handles_backbone_and_histidine_aliases():
    assert _infer_protor_type_for_atom('GLY', 'CA', 'C', 3) == 'C4H2'
    assert _infer_protor_type_for_atom('ALA', 'N', 'N', 2) == 'N3H1'
    assert _infer_protor_type_for_atom('PRO', 'N', 'N', 3) == 'N3H0'
    assert _infer_protor_type_for_atom('ALA', 'OXT', 'O', 1) == 'O2H1'
    assert _infer_protor_type_for_atom('HSD', 'ND1', 'N', 2) == 'N3H1'
    assert _infer_protor_type_for_atom('HSE', 'NE2', 'N', 2) == 'N3H1'
    assert _infer_protor_type_for_atom('HSP', 'ND1', 'N', 2) == 'N3H1'


def test_castp3_protor_radii_follow_table_before_element_fallback():
    radii = _protor_radii_for_labels(
        np.asarray(['ARG', 'TYR', 'CYX', 'HSD', 'UNK', 'UNK'], dtype=object),
        np.asarray(['NH1', 'OH', 'SG', 'ND1', 'XX', 'SD'], dtype=object),
        np.asarray(['N', 'O', 'S', 'N', 'C', 'S'], dtype=object),
        np.asarray([1, 1, 2, 2, 3, 1], dtype=int),
    )

    assert radii[0] == 1.64
    assert radii[1] == 1.46
    assert radii[2] == 1.77
    assert radii[3] == 1.64
    assert radii[4] == 1.88
    assert radii[5] == 1.77
