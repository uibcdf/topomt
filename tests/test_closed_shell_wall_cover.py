"""A complete convex cover resolves the frozen shell's old 0.2 Å question."""

import copy
import json

import pytest

from devtools.verify_closed_shell_wall_cover import verify_certificate
from tests.test_benchlab_public_topography import ROOT, public_result, values
from topomt import pyunitwizard as puw

CASE = ROOT / 'closed_shell'
DATA = CASE / 'artifacts/wall_certificate_v1'


def certificate():
    return json.loads((DATA / 'certificate.json').read_text())


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_complete_convex_ball_cover_certifies_the_historical_probe(policy):
    with puw.context(standard_units=[*policy, 'radians']):
        verified = verify_certificate(
            CASE / 'artifacts/closed_shell_v1/input.json',
            DATA / 'protocol.json',
            certificate(),
        )
    assert verified['verification'] == 'passed'
    assert verified['conclusion'] == 'origin_free_and_enclosed'
    assert verified['hull_face_count'] == 140 and verified['leaf_count'] == 1037
    assert verified['maximum_depth'] == 5
    assert (
        float(
            values(
                verified['minimum_coverage_margin'],
                'minimum_coverage_margin',
                'angstroms',
            )
        )
        > 1e-6
    )
    assert (
        float(values(verified['origin_free_margin'], 'origin_free_margin', 'angstroms'))
        > 0
    )


def test_incomplete_partition_is_not_an_enclosure_certificate():
    broken = certificate()
    broken['leaves'].pop()
    with pytest.raises(ValueError, match='partition'):
        verify_certificate(
            CASE / 'artifacts/closed_shell_v1/input.json',
            DATA / 'protocol.json',
            broken,
        )


def test_wrong_covering_atom_is_not_an_enclosure_certificate():
    broken = copy.deepcopy(certificate())
    broken['leaves'][0]['covering_atom_index'] = (
        broken['leaves'][0]['covering_atom_index'] + 36
    ) % 72
    with pytest.raises(ValueError, match='covered'):
        verify_certificate(
            CASE / 'artifacts/closed_shell_v1/input.json',
            DATA / 'protocol.json',
            broken,
        )


def test_public_central_region_agrees_with_the_new_0p2_enclosure_reference():
    verified = verify_certificate(
        CASE / 'artifacts/closed_shell_v1/input.json',
        DATA / 'protocol.json',
        certificate(),
    )
    assert verified['conclusion'] == 'origin_free_and_enclosed'
    topo, _, _ = public_result('closed_shell', 0.2)
    assert topo.get_features(by='type', value='void')
    assert not topo.get_features(by='type', value='mouth')
    assert all(
        component['n_external_links'] == 0
        for component in topo.dfnd.raw['wet_components']
    )
