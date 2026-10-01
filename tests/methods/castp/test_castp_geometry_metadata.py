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


@pytest.mark.parametrize('implementation', [castp_geometry, castp3_geometry])
def test_protor_connectivity_failure_is_preserved(implementation, monkeypatch):
    original_get = implementation.msm.get

    def get_with_unavailable_connectivity(*args, **kwargs):
        if kwargs.get('n_bonds'):
            raise RuntimeError('connectivity unavailable')
        return original_get(*args, **kwargs)

    monkeypatch.setattr(implementation.msm, 'get', get_with_unavailable_connectivity)

    with pytest.raises(RuntimeError, match='connectivity unavailable'):
        implementation.build_castp_geometry(
            INPUT_ROOT / 'regular_tetrahedron_v1/input_castp.pdb',
            radii_model='protor',
        )
