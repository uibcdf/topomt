"""Analytic and altered-proof challenges of the declared trusted construction."""

from copy import deepcopy
from fractions import Fraction as F
from itertools import product

import pytest

from devtools.reference_validator.model import Box, Model, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.verify import verify
from devtools.reference_validator.verify.power_cells import query_anchors


@pytest.mark.parametrize('radii', [[F(3, 2)], [F(3, 2), F(3, 2)], [F(3, 2), 1]])
def test_coincident_redundant_obstacles_preserve_eight_corner_regions(radii):
    # Every coordinate plane is covered since R**2>2. In each orthant,
    # moving coordinates away from zero increases distance to the center.
    model = Model.from_spheres(
        [(0, 0, 0)] * len(radii),
        radii,
        0,
        domain=Box(point((-1, -1, -1)), point((1, 1, 1))),
    )
    cert = topology_certificate(model)
    checked = verify(model, cert)
    assert (checked['n_components'], checked['n_boundary_patches']) == (8, 8)
    anchors = {
        f'corner_{i}': point(c) for i, c in enumerate(product((-1, 1), repeat=3))
    }
    result = query_anchors(model, cert, anchors=anchors, pairs=[])
    assert len({p['region_id'] for p in result['locations'].values()}) == 8
    assert all(p['boundary_patch_id'] for p in result['locations'].values())


def test_source_order_and_exact_boundary_contact_do_not_create_a_join():
    model = Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0)],
        [4, 4],
        1,
        domain=Box(point((-20, -3, -4)), point((20, 3, 4))),
    )
    reordered = Model(
        tuple(reversed(model.atoms)),
        model.probe,
        model.domain,
        model.source_sha256,
        frame_index=model.frame_index,
    )
    for received in [model, reordered]:
        cert = topology_certificate(received)
        checked = verify(received, cert)
        assert (checked['n_components'], checked['n_boundary_patches']) == (3, 3)
        query = query_anchors(
            received, cert, anchors={'contact': point((-8, 3, 4))}, pairs=[]
        )
        assert query['locations']['contact']['point_state'] == 'blocked'


@pytest.mark.parametrize('mutation', ['edge', 'free_vertex', 'region', 'boundary'])
def test_altered_geometric_claims_are_rejected_without_relying_on_a_file_hash(mutation):
    model = Model.from_spheres(
        [(0, 0, 0)], [F(3, 2)], 0, domain=Box(point((-1, -1, -1)), point((1, 1, 1)))
    )
    cert = deepcopy(topology_certificate(model))
    if mutation == 'edge':
        cert['cells'][0]['edges'].pop()
    elif mutation == 'free_vertex':
        cert['cells'][0]['free_vertices'].pop()
    else:
        key = 'components' if mutation == 'region' else 'boundary_components'
        cert[key] = [sorted(sum(cert[key], []))]
    with pytest.raises(ValueError):
        verify(model, cert)
