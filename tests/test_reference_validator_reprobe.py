"""Probe changes can reuse certified geometry only with identical inequalities."""

import copy
from dataclasses import replace
from fractions import Fraction

import pytest

from devtools.reference_validator.model import Atom, Box, Model, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.verify import verify


def _barriers():
    return Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0)],
        [4, 4],
        1,
        domain=Box(point((-20, -3, -4)), point((20, 3, 4))),
    )


@pytest.mark.parametrize(
    'probe,expected',
    [
        (Fraction(1) - Fraction(1, 2**80), 1),
        (Fraction(1), 3),
        (Fraction(1) + Fraction(1, 2**80), 3),
        (Fraction(100), 0),
    ],
)
def test_reprobe_reuses_exact_cells_but_recomputes_free_regions_and_patches(
    probe, expected
):
    from devtools.reference_validator.power_cells import reprobe_certificate

    source = _barriers()
    old = topology_certificate(source)
    unchanged = copy.deepcopy(old)
    target = replace(source, probe=probe)
    result = reprobe_certificate(source, old, target)
    assert old == unchanged
    assert result == topology_certificate(target)
    checked = verify(target, result)
    assert checked['n_components'] == expected
    assert checked['n_boundary_patches'] == expected
    assert result['model_sha256'] == target.digest
    for previous, current in zip(old['cells'], result['cells']):
        for key in ['atom_id', 'support', 'vertices', 'edges']:
            assert previous[key] == current[key]


def test_reprobe_rejects_changed_unequal_radius_power_planes():
    from devtools.reference_validator.power_cells import reprobe_certificate

    base = _barriers()
    source = replace(
        base, atoms=(base.atoms[0], Atom(1, base.atoms[1].center, Fraction(5)))
    )
    with pytest.raises(ValueError, match='power.*inequalities'):
        reprobe_certificate(
            source, topology_certificate(source), replace(source, probe=Fraction(2))
        )


@pytest.mark.parametrize('change', ['frame', 'source', 'domain', 'atom'])
def test_reprobe_rejects_any_nonprobe_model_change(change):
    from devtools.reference_validator.power_cells import reprobe_certificate

    source = _barriers()
    old = topology_certificate(source)
    if change == 'frame':
        target = replace(source, frame_index=1)
    elif change == 'source':
        target = replace(source, source_sha256='0' * 64)
    elif change == 'domain':
        target = replace(source, domain=Box(point((-21, -3, -4)), point((20, 3, 4))))
    else:
        target = replace(
            source,
            atoms=(Atom(0, source.atoms[0].center, Fraction(3)), source.atoms[1]),
        )
    with pytest.raises(ValueError, match='only.*probe'):
        reprobe_certificate(source, old, target)


def test_reprobe_rechecks_source_certificate_instead_of_trusting_its_geometry():
    from devtools.reference_validator.power_cells import reprobe_certificate

    source = _barriers()
    old = topology_certificate(source)
    old['cells'].pop()
    with pytest.raises(ValueError, match='inventory'):
        reprobe_certificate(source, old, replace(source, probe=Fraction(2)))


def test_reprobe_preserves_empty_and_coincident_source_cells():
    from devtools.reference_validator.power_cells import reprobe_certificate

    source = Model.from_spheres(
        [(0, 0, 0)] * 3, [1, 2, 2], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    target = replace(source, probe=Fraction(1))
    result = reprobe_certificate(source, topology_certificate(source), target)
    assert len(result['cells']) == 3
    assert verify(target, result)['n_components'] == 0
