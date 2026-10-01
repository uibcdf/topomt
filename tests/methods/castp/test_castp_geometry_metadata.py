"""CAST geometry must only request metadata required by its radii policy."""

from pathlib import Path

import numpy as np
import pytest

from topomt.third_party.castp.core.castp_core import geometry as castp_geometry
from topomt.third_party.castp3.core.castp_core import geometry as castp3_geometry

INPUT_ROOT = (
    Path(__file__).resolve().parents[3] / 'docs/content/showcase/dfnd/artifacts'
)


@pytest.mark.parametrize('case', ['regular_tetrahedron', 'closed_shell'])
@pytest.mark.parametrize('radii_model', ['castp_param', 'castp1_pdb2alf', 'override'])
@pytest.mark.parametrize('implementation', [castp_geometry, castp3_geometry])
def test_classical_geometry_does_not_require_chemical_bonds(
    case, radii_model, implementation, monkeypatch
):
    original_get = implementation.msm.get

    def get_without_chemical_typing(*args, **kwargs):
        assert not kwargs.get('n_bonds'), 'Classical CAST does not need bonds.'
        assert not kwargs.get('atom_type'), 'Classical CAST does not need typing.'
        return original_get(*args, **kwargs)

    monkeypatch.setattr(implementation.msm, 'get', get_without_chemical_typing)
    input_path = INPUT_ROOT / f'{case}_v1/input_castp.pdb'
    options = {'radii_model': radii_model}
    expected_radius = 3.2
    if radii_model == 'override':
        n_atoms = sum(
            line.startswith('HETATM') for line in input_path.read_text().splitlines()
        )
        options = {'atom_radii_override': np.full(n_atoms, 3.1)}
        expected_radius = 3.1

    geometry = implementation.build_castp_geometry(input_path, **options)

    assert geometry.mesh.n_simplices > 0
    np.testing.assert_allclose(geometry.atom_radii, expected_radius)


@pytest.mark.parametrize(
    'implementation,radii_model',
    [
        (castp_geometry, 'protor'),
        (castp3_geometry, 'protor'),
        (castp3_geometry, 'castp3_protor'),
    ],
)
def test_protor_connectivity_failure_is_preserved(
    implementation, radii_model, monkeypatch
):
    original_get = implementation.msm.get

    def get_with_unavailable_connectivity(*args, **kwargs):
        if kwargs.get('n_bonds'):
            raise RuntimeError('connectivity unavailable')
        return original_get(*args, **kwargs)

    monkeypatch.setattr(implementation.msm, 'get', get_with_unavailable_connectivity)

    with pytest.raises(RuntimeError, match='connectivity unavailable'):
        implementation.build_castp_geometry(
            INPUT_ROOT / 'regular_tetrahedron_v1/input_castp.pdb',
            radii_model=radii_model,
        )


@pytest.fixture
def protein_with_explicit_hydrogen(tmp_path):
    pdb = tmp_path / 'explicit_hydrogen.pdb'
    labels = [('N', 'N'), ('CA', 'C'), ('C', 'C'), ('O', 'O'), ('H', 'H')]
    points = [(3, 3, 3), (3, -3, -3), (-3, 3, -3), (-3, -3, 3), (12, 0, 0)]
    pdb.write_text(
        ''.join(
            f'ATOM  {index:5d} {name:^4s} ALA A   1    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {element:>2s}  \n'
            for index, ((name, element), (x, y, z)) in enumerate(
                zip(labels, points), start=1
            )
        )
        + 'END\n'
    )
    return pdb


@pytest.mark.parametrize(
    'implementation,radii_model',
    [
        (castp_geometry, 'protor'),
        (castp3_geometry, 'protor'),
        (castp3_geometry, 'castp3_protor'),
    ],
)
def test_protor_geometry_omits_explicit_hydrogen_but_preserves_source_indices(
    implementation, radii_model, protein_with_explicit_hydrogen
):
    geometry = implementation.build_castp_geometry(
        protein_with_explicit_hydrogen, radii_model=radii_model
    )
    assert geometry.atom_indices_map.tolist() == [0, 1, 2, 3]
    assert geometry.atom_coordinates.shape == (4, 3)


def test_protor_hydrogen_selection_preserves_requested_atom_order(
    protein_with_explicit_hydrogen,
):
    geometry = castp3_geometry.build_castp_geometry(
        protein_with_explicit_hydrogen,
        selection=[4, 2, 0, 3, 1],
        radii_model='castp3_protor',
    )
    assert geometry.atom_indices_map.tolist() == [2, 0, 3, 1]


@pytest.mark.parametrize('implementation', [castp_geometry, castp3_geometry])
@pytest.mark.parametrize('mode', ['castp_param', 'override'])
def test_non_protor_geometry_preserves_explicit_hydrogen(
    implementation, mode, protein_with_explicit_hydrogen
):
    options = (
        {'radii_model': mode}
        if mode != 'override'
        else {'atom_radii_override': np.full(5, 3.1)}
    )
    geometry = implementation.build_castp_geometry(
        protein_with_explicit_hydrogen, **options
    )
    assert geometry.atom_indices_map.tolist() == [0, 1, 2, 3, 4]


@pytest.mark.parametrize(
    'profile,terminal_retained', [('castp3_protor', False), ('protor', True)]
)
def test_only_server_profile_omits_an_observed_unlisted_terminal_atom(
    profile, terminal_retained, protein_with_explicit_hydrogen
):
    pdb = protein_with_explicit_hydrogen
    lines = pdb.read_text().splitlines()
    lines[4] = lines[4][:12] + ' OXT' + lines[4][16:76] + ' O' + lines[4][78:]
    pdb.write_text('\n'.join(lines) + '\n')
    geometry = castp3_geometry.build_castp_geometry(pdb, radii_model=profile)
    assert (4 in geometry.atom_indices_map) == terminal_retained
