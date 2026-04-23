"""
"""

import topomt as tmt
import importlib
import warnings
from molsysmt.native.molsys import MolSys
from topomt.features import Mouth, Pocket
from topomt import pyunitwizard as puw
from topomt.get_topography import get_topography
from topomt.get_topography import _run_alphaspace2, _run_castp, _run_pocketeer, _run_pycasta
import pytest
import numpy as np

def test_empty_Topography():

    topography = tmt.Topography()

    assert type(topography) == tmt.Topography
    assert len(topography) == 0
    assert topography.features == {}
    assert topography.molecular_system is None
    assert topography._molsys is None
    assert topography.get_features(by='type', value='pocket')==set()
    assert topography.get_features(by='type', value='pocket', as_feature_ids=True)==set()
    assert topography.get_features(by='dimensionality', value=2)==set()
    assert topography.get_features(by='dimensionality', value=2, as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='concavity')==set()
    assert topography.get_features(by='shape', value='convexity')==set()
    assert topography.get_features(by='shape', value='mixed')==set()
    assert topography.get_features(by='shape', value='boundary')==set()
    assert topography.get_features(by='shape', value='point')==set()
    assert topography._make_next_feature_id('pocket')=='POC-1'


def test_empty_Topography_with_molecular_system(topography_empty_1tcd):

    topography = topography_empty_1tcd

    assert type(topography) == tmt.Topography
    assert len(topography) == 0
    assert topography.features == {}
    assert topography.molecular_system == tmt.demo['TcTIM']['1tcd.pdb']
    assert type(topography._molsys) == MolSys
    assert topography.get_features(by='type', value='pocket')==set()
    assert topography.get_features(by='type', value='pocket', as_feature_ids=True)==set()
    assert topography.get_features(by='dimensionality', value=2)==set()
    assert topography.get_features(by='dimensionality', value=2, as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='concavity')==set()
    assert topography.get_features(by='shape', value='convexity')==set()
    assert topography.get_features(by='shape', value='mixed')==set()
    assert topography.get_features(by='shape', value='boundary')==set()
    assert topography.get_features(by='shape', value='point')==set()
    assert topography._make_next_feature_id('pocket')=='POC-1'

def test_Topography_new_pocket(topography_empty_1tcd):

    pdb_file = tmt.demo['TcTIM']['1tcd.pdb']
    topography = topography_empty_1tcd

    feature_id = topography.add_new_feature(feature_type='pocket', atom_indices=[1,2,3])    
    new_feature = topography.features[feature_id]

    assert feature_id == 'POC-1'
    assert type(topography) == tmt.Topography
    assert len(topography) == 1
    assert list(topography.features.keys()) == ['POC-1']
    assert isinstance(list(topography.features.values())[0], Pocket)
    assert isinstance(topography['POC-1'], Pocket)
    assert topography.molecular_system == tmt.demo['TcTIM']['1tcd.pdb']
    assert type(topography._molsys) == MolSys
    assert topography.get_features(by='type', value='pocket')==set([new_feature])
    assert topography.get_features(by='type', value='pocket', as_feature_ids=True)==set(['POC-1'])
    assert topography.get_features(by='dimensionality', value=2)==set([new_feature])
    assert topography.get_features(by='dimensionality', value=2, as_feature_ids=True)==set(['POC-1'])
    assert topography.get_features(by='shape', value='concavity')==set([new_feature])
    assert topography.get_features(by='shape', value='concavity', as_feature_ids=True)==set(['POC-1'])
    assert topography.get_features(by='shape', value='convexity')==set()
    assert topography.get_features(by='shape', value='convexity', as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='mixed')==set()
    assert topography.get_features(by='shape', value='mixed', as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='boundary')==set()
    assert topography.get_features(by='shape', value='boundary', as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='point')==set()
    assert topography.get_features(by='shape', value='point', as_feature_ids=True)==set()
    assert topography._make_next_feature_id('pocket')=='POC-2'
    assert topography._make_next_feature_id('void')=='VOI-1'


def test_feature_info_uses_public_identifiers():

    feature = Pocket(feature_id='POC-7', atom_indices=[1, 2, 3], source='pocketeer', source_id='pocketeer:7')

    assert feature.info() == {
        'feature_id': 'POC-7',
        'feature_type': 'pocket',
        'shape_type': 'concavity',
    }


def test_connect_features_updates_relations(topography_empty_1tcd):

    topography = topography_empty_1tcd
    pocket_id = topography.add_new_feature(feature_type='pocket', atom_indices=[1, 2, 3, 4])
    mouth = Mouth(feature_id='MOU-1', atom_indices=[1, 2])

    topography.connect_features(mouth, pocket_id)

    assert topography.children_of(pocket_id, as_feature_ids=True) == {'MOU-1'}
    assert topography.parents_of('MOU-1', as_feature_ids=True) == {pocket_id}
    assert topography[pocket_id].boundaries == {'MOU-1'}
    assert topography['MOU-1'].surfaces == {pocket_id}


def test_demo_supports_uppercase_castp_keys():

    assert tmt.demo['TcTIM']['1TCD.pdb'] == tmt.demo['TcTIM']['1tcd.pdb']
    assert tmt.demo['HIV-1 Protease']['1HIV.pdb'] == tmt.demo['HIV-1 Protease']['1hiv.pdb']


def test_run_pocketeer_maps_local_indices_to_global(topography_empty_1tcd, monkeypatch):
    pocketeer_module = importlib.import_module('topomt.third_party.pocketeer._native_impl')
    PocketeerPocket = pocketeer_module.PocketeerPocket
    PocketeerSphere = pocketeer_module.PocketeerSphere

    def fake_pocketeer(*args, **kwargs):
        spheres = [
            PocketeerSphere(
                sphere_id=0,
                center=np.array([0.1, 0.2, 0.3]),
                radius=0.2,
                atom_indices=[0, 2, 3, 4],
            ),
        ]
        pockets = [
            PocketeerPocket(
                pocket_id=3,
                spheres=spheres,
                centroid=np.array([0.1, 0.2, 0.3]),
                volume=0.5,
                score=1.5,
            ),
        ]
        return pockets, spheres, [10, 20, 30, 40, 50]

    monkeypatch.setattr(pocketeer_module, 'pocketeer', fake_pocketeer)

    topo = _run_pocketeer(topography_empty_1tcd.copy(deep=True))

    pocket = next(iter(topo.get_features(by='type', value='pocket')))
    assert pocket.atom_indices == [10, 30, 40, 50]
    assert pocket.source == 'pocketeer'
    assert pocket.source_id == 'pocketeer:3'
    assert puw.is_quantity(pocket.center)
    assert puw.is_quantity(pocket.volume)
    assert np.allclose(puw.get_value(pocket.center, to_unit='nm'), [0.1, 0.2, 0.3])
    assert puw.get_value(pocket.volume, to_unit='nm**3') == pytest.approx(0.5)


def test_run_alphaspace2_uses_filtered_atom_index_mapping(topography_empty_1tcd, monkeypatch):
    alphaspace2_module = importlib.import_module('topomt.third_party.alphaspace2.native')
    get_topography_module = importlib.import_module('topomt.get_topography')

    class FakeKDTree:

        def __init__(self, data):
            self.data = data

        def query_ball_point(self, vertex, radius):
            return [0, 2]

    def fake_alphaspace2(*args, **kwargs):
        clusters = [[0, 1]]
        vertices = np.array([[0.1, 0.1, 0.1], [0.11, 0.1, 0.1]])
        radii = np.array([0.2, 0.2])
        return clusters, vertices, radii, None, [5, 8, 13, 21]

    monkeypatch.setattr(alphaspace2_module, 'alphaspace2', fake_alphaspace2)
    monkeypatch.setattr(get_topography_module, 'cKDTree', FakeKDTree)

    topo = _run_alphaspace2(topography_empty_1tcd.copy(deep=True), min_vertices=1)

    pocket = next(iter(topo.get_features(by='type', value='pocket')))
    assert pocket.atom_indices == [5, 13]
    assert pocket.source == 'alphaspace2'
    assert pocket.source_id == 'alphaspace2:0'


def test_run_alphaspace2_state_path_returns_quantities(topography_empty_1tcd, monkeypatch):
    alphaspace2_module = importlib.import_module('topomt.third_party.alphaspace2.native')

    def fake_alphaspace2(*args, **kwargs):
        state = object()
        return [], np.empty((0, 3)), np.empty((0,)), None, [5, 8, 13, 21], state

    def fake_state_to_pocket_records(state):
        return [
            {
                'pocket_index': 0,
                'atom_indices': [5, 13],
                'center': np.array([0.1, 0.2, 0.3]),
                'volume': 0.5,
                'score': 1.0,
                'alpha_sphere_centers': np.array([[0.1, 0.2, 0.3]]),
                'alpha_sphere_radii': np.array([0.2]),
                'beta_centers': np.array([[0.15, 0.25, 0.35]]),
                'beta_scores': [0.8],
                'nonpolar_volume': 0.2,
                'is_contact': False,
            }
        ]

    monkeypatch.setattr(alphaspace2_module, 'alphaspace2', fake_alphaspace2)
    monkeypatch.setattr(alphaspace2_module, '_state_to_pocket_records', fake_state_to_pocket_records)

    topo = _run_alphaspace2(topography_empty_1tcd.copy(deep=True), min_vertices=1)

    pocket = next(iter(topo.get_features(by='type', value='pocket')))
    assert puw.is_quantity(pocket.center)
    assert puw.is_quantity(pocket.volume)


def test_run_castp_emits_feature_types_and_mouth_relations(topography_empty_1tcd, monkeypatch):
    castp_module = importlib.import_module('topomt.third_party.castp._native_impl')

    def fake_castp(*args, **kwargs):
        return (
            [
                {
                    'feature_type': 'pocket',
                    'source_id': 'castp:pocket:1',
                    'atom_indices': [1, 2, 3, 4],
                    'center': np.array([1.0, 2.0, 3.0]),
                    'area': 16.0,
                    'volume': 10.0,
                    'score': 10.0,
                    'n_mouths': 1,
                    'mouth_area': 4.0,
                    'mouth_perimeter': 6.0,
                    'iT': [0, 1],
                    'tetrahedron_indices': [0, 1],
                    'mouths': [
                        {
                            'id': 1,
                            'atom_indices': [1, 2, 3],
                            'area': 4.0,
                        }
                    ],
                },
                {
                    'feature_type': 'channel',
                    'source_id': 'castp:channel:1',
                    'atom_indices': [5, 6, 7, 8],
                    'center': np.array([2.0, 3.0, 4.0]),
                    'volume': 12.0,
                    'score': 12.0,
                    'n_mouths': 2,
                    'mouth_area': 7.0,
                    'tetrahedron_indices': [2, 3],
                    'mouths': [
                        {'id': 1, 'atom_indices': [5, 6, 7], 'area': 3.0},
                        {'id': 2, 'atom_indices': [6, 7, 8], 'area': 4.0},
                    ],
                },
                {
                    'feature_type': 'void',
                    'source_id': 'castp:void:1',
                    'atom_indices': [9, 10, 11, 12],
                    'center': np.array([4.0, 5.0, 6.0]),
                    'volume': 8.0,
                    'score': 8.0,
                    'n_mouths': 0,
                    'mouth_area': 0.0,
                    'tetrahedron_indices': [4],
                    'mouths': [],
                },
            ],
            object(),
        )

    monkeypatch.setattr(castp_module, 'castp', fake_castp)

    topo = _run_castp(topography_empty_1tcd.copy(deep=True))

    pockets = topo.get_features(by='type', value='pocket')
    channels = topo.get_features(by='type', value='channel')
    voids = topo.get_features(by='type', value='void')
    mouths = topo.get_features(by='type', value='mouth')

    assert len(pockets) == 1
    assert len(channels) == 1
    assert len(voids) == 1
    assert len(mouths) == 3

    pocket = next(iter(pockets))
    assert puw.is_quantity(pocket.center)
    assert puw.is_quantity(pocket.area)
    assert puw.is_quantity(pocket.volume)
    assert puw.is_quantity(pocket.mouth_area)
    assert puw.is_quantity(pocket.mouth_perimeter)
    assert pocket.iT == [0, 1]
    assert pocket.n_mouths == 1
    assert topo.children_of(pocket.feature_id, as_feature_ids=True) == {'MOU-1'}

    channel = next(iter(channels))
    assert channel.n_mouths == 2
    assert topo.children_of(channel.feature_id, as_feature_ids=True) == {'MOU-2', 'MOU-3'}

    void = next(iter(voids))
    assert void.n_mouths == 0
    assert topo.children_of(void.feature_id, as_feature_ids=True) == set()


def test_run_pycasta_maps_local_indices_to_global(topography_empty_1tcd, monkeypatch):
    pycasta_module = importlib.import_module('topomt.third_party.pycasta._native_impl')

    def fake_pycasta(*args, **kwargs):
        pockets_tet = [[0]]
        volumes = [0.125]
        simplices = np.array([[0, 1, 2, 3]])
        return pockets_tet, volumes, simplices, [11, 12, 14, 18]

    monkeypatch.setattr(pycasta_module, 'pycasta', fake_pycasta)

    topo = _run_pycasta(topography_empty_1tcd.copy(deep=True))

    pocket = next(iter(topo.get_features(by='type', value='pocket')))
    assert pocket.atom_indices == [11, 12, 14, 18]
    assert pocket.source == 'pycasta'
    assert pocket.source_id == 'pycasta:0'


def test_get_topography_argdigest_standardizes_engine_and_structure_index(monkeypatch):
    get_topography_module = importlib.import_module('topomt.get_topography')

    called = {}

    def fake_run_pycasta(topo, **kwargs):
        called['method'] = 'pycasta'
        called['structure_indices'] = topo.structure_indices
        return topo

    monkeypatch.setattr(get_topography_module, '_run_pycasta', fake_run_pycasta)

    topo = get_topography(
        tmt.demo['TcTIM']['1tcd.pdb'],
        engine='pycasta',
        structure_index=0,
    )

    assert called['method'] == 'pycasta'


def test_run_pocketeer_wrapper_routes_to_wrapper_integration(topography_empty_1tcd, monkeypatch):
    provider_module = importlib.import_module('topomt.third_party.pocketeer.api')
    get_topography_module = importlib.import_module('topomt.get_topography')

    called = {}

    def fake_wrapper(molecular_system, **kwargs):
        called['molecular_system'] = molecular_system
        called['kwargs'] = kwargs
        return tmt.Topography(
            molecular_system=molecular_system,
            selection=kwargs['selection'],
            structure_indices=kwargs['structure_indices'],
        )

    monkeypatch.setattr(provider_module, 'get_topography', fake_wrapper)

    topo = get_topography_module._run_pocketeer(
        topography_empty_1tcd.copy(deep=True),
        implementation='wrapper',
        upstream_root='/tmp/pocketeer',
    )

    assert isinstance(topo, tmt.Topography)
    assert called['molecular_system'] == topography_empty_1tcd.molecular_system
    assert called['kwargs']['selection'] == topography_empty_1tcd.selection
    assert called['kwargs']['structure_indices'] == topography_empty_1tcd.structure_indices
    assert called['kwargs']['upstream_root'] == '/tmp/pocketeer'


def test_run_alphaspace2_wrapper_routes_to_wrapper_integration(topography_empty_1tcd, monkeypatch):
    integration_module = importlib.import_module('topomt.third_party.alphaspace2.library')
    get_topography_module = importlib.import_module('topomt.get_topography')

    called = {}

    def fake_wrapper(molecular_system, **kwargs):
        called['molecular_system'] = molecular_system
        called['kwargs'] = kwargs
        return tmt.Topography(
            molecular_system=molecular_system,
            selection=kwargs['selection'],
            structure_indices=kwargs['structure_indices'],
        )

    monkeypatch.setattr(integration_module, 'get_topography', fake_wrapper)

    topo = get_topography_module._run_alphaspace2(
        topography_empty_1tcd.copy(deep=True),
        implementation='wrapper',
        min_vertices=12,
        upstream_root='/tmp/alphaspace2',
    )

    assert isinstance(topo, tmt.Topography)
    assert called['molecular_system'] == topography_empty_1tcd.molecular_system
    assert called['kwargs']['selection'] == topography_empty_1tcd.selection
    assert called['kwargs']['structure_indices'] == topography_empty_1tcd.structure_indices
    assert called['kwargs']['min_vertices'] == 12
    assert called['kwargs']['upstream_root'] == '/tmp/alphaspace2'


def test_run_pycasta_wrapper_routes_to_wrapper_integration(topography_empty_1tcd, monkeypatch):
    provider_module = importlib.import_module('topomt.third_party.pycasta.api')
    get_topography_module = importlib.import_module('topomt.get_topography')

    called = {}

    def fake_wrapper(molecular_system, **kwargs):
        called['molecular_system'] = molecular_system
        called['kwargs'] = kwargs
        return tmt.Topography(
            molecular_system=molecular_system,
            selection=kwargs['selection'],
            structure_indices=kwargs['structure_indices'],
        )

    monkeypatch.setattr(provider_module, 'get_topography', fake_wrapper)

    topo = get_topography_module._run_pycasta(
        topography_empty_1tcd.copy(deep=True),
        implementation='wrapper',
        upstream_root='/tmp/pycasta',
    )

    assert isinstance(topo, tmt.Topography)
    assert called['molecular_system'] == topography_empty_1tcd.molecular_system
    assert called['kwargs']['selection'] == topography_empty_1tcd.selection
    assert called['kwargs']['structure_indices'] == topography_empty_1tcd.structure_indices
    assert called['kwargs']['upstream_root'] == '/tmp/pycasta'


def test_get_topography_wrapper_kwargs_do_not_emit_digest_not_digested_warning(monkeypatch):
    get_topography_module = importlib.import_module('topomt.get_topography')

    def fake_wrapper(molecular_system, **kwargs):
        return tmt.Topography(
            molecular_system=molecular_system,
            selection=kwargs['selection'],
            structure_indices=kwargs['structure_indices'],
        )

    monkeypatch.setattr(
        importlib.import_module('topomt.third_party.pocketeer.api'),
        'get_topography',
        fake_wrapper,
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        topo = get_topography(
            tmt.demo['TcTIM']['1tcd.pdb'],
            method='pocketeer',
            implementation='wrapper',
            upstream_root='/tmp/pocketeer',
            r_min=3.0,
            r_max=6.0,
            polar_probe_radius=1.4,
            sasa_threshold=20.0,
            merge_distance=1.75,
            min_spheres=35,
        )

    assert isinstance(topo, tmt.Topography)
    assert not any(type(item.message).__name__ == 'DigestNotDigestedWarning' for item in caught)


def test_pocketeer_sasa_warning_uses_topomt_catalog_warning():
    pocketeer_module = importlib.import_module('topomt.third_party.pocketeer._native_impl')
    smonitor_module = importlib.import_module('topomt._private.smonitor')
    coords_nm = np.zeros((3, 3), dtype=float)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        result = pocketeer_module._sasa_molsysmt(
            None,
            coords_nm=coords_nm,
            polar_probe_radius_nm=0.14,
        )

    assert result.shape == (3,)
    assert len(caught) == 1
    assert isinstance(caught[0].message, smonitor_module.PocketeerSasaBackendWarning)
