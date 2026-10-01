"""ProtOr typing tests for the experimental CASTp3 backend."""

import numpy as np

from topomt.third_party.castp3.core.castp_core import geometry
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


def test_castp3_server_profile_distinguishes_carboxylate_radii():
    groups = np.asarray(['ASP', 'ASP', 'GLU', 'GLU', 'ALA', 'SER', 'TYR', 'ASH'])
    names = np.asarray(['OD1', 'OD2', 'OE1', 'OE2', 'O', 'OG', 'OH', 'OD2'])
    elements = np.full(len(groups), 'O')
    bonds = np.ones(len(groups), dtype=int)

    standard = _protor_radii_for_labels(groups, names, elements, bonds)
    server = geometry._castp3_protor_radii_for_labels(groups, names, elements, bonds)

    np.testing.assert_allclose(standard, [1.42] * 5 + [1.46] * 3)
    np.testing.assert_allclose(server, [1.40] * 4 + [1.42] + [1.46] * 3)


def test_castp3_server_profile_preserves_explicit_radius_overrides(monkeypatch):
    # Profile dispatch must not override an explicit user sphere model.
    from pathlib import Path

    source = (
        Path(__file__).parent.parent
        / 'docs/content/showcase/dfnd/artifacts/regular_tetrahedron_v1/input_castp.pdb'
    )

    def unexpected_typing(*args, **kwargs):
        raise AssertionError('An explicit radius override must bypass typing.')

    monkeypatch.setattr(geometry, '_castp3_protor_radii_for_labels', unexpected_typing)
    result = geometry.build_castp_geometry(
        source, radii_model='castp3_protor', atom_radii_override=np.full(4, 3.1)
    )
    np.testing.assert_allclose(result.atom_radii, 3.1)
