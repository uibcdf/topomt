"""Regression tests for CASTp file loading."""

from pathlib import Path

import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.io.load_CASTp import load_CASTp


def _features_by_source_id(topography, feature_type):
    return {
        feature.source_id: feature
        for feature in topography.get_features(by='type', value=feature_type)
    }


def _castp_surface_features(topography):
    feature_types = ('pocket', 'void', 'channel', 'branched_channel')
    features = {}
    for feature_type in feature_types:
        features.update(_features_by_source_id(topography, feature_type))
    return features


def _value(quantity, unit=None):
    if unit is None:
        return float(puw.get_value(quantity))
    return float(puw.get_value(quantity, to_unit=unit))


def test_load_castp_tctim_imports_server_metrics():
    topography = load_CASTp(dir_path=tmt.demo['TcTIM']['CASTp_1tcd'])

    all_features = _castp_surface_features(topography)
    mouths = _features_by_source_id(topography, 'mouth')

    assert len(all_features) == 78
    assert len(mouths) == 42

    pocket_1 = all_features['Pocket 1']
    assert pocket_1.source == 'CASTp'
    assert len(pocket_1.atom_indices) == 68
    assert _value(pocket_1.solvent_accessible_area, 'angstroms**2') == pytest.approx(283.364)
    assert _value(pocket_1.molecular_surface_area, 'angstroms**2') == pytest.approx(456.907)
    assert _value(pocket_1.solvent_accessible_volume, 'angstroms**3') == pytest.approx(165.990)
    assert _value(pocket_1.molecular_surface_volume, 'angstroms**3') == pytest.approx(637.990)
    assert _value(pocket_1.length, 'angstroms') == pytest.approx(234.656)
    assert pocket_1.corner_points_count == 108

    pocket_2 = all_features['Pocket 2']
    assert len(pocket_2.atom_indices) == 36
    assert _value(pocket_2.solvent_accessible_volume, 'angstroms**3') == pytest.approx(54.058)

    mouth_1 = mouths['Mouth 1']
    assert mouth_1.source == 'CASTp'
    assert len(mouth_1.atom_indices) == 26
    assert _value(mouth_1.solvent_accessible_area, 'angstroms**2') == pytest.approx(57.751)
    assert _value(mouth_1.molecular_surface_area, 'angstroms**2') == pytest.approx(171.53)
    assert _value(mouth_1.solvent_accessible_length, 'angstroms') == pytest.approx(77.154)
    assert _value(mouth_1.molecular_surface_length, 'angstroms') == pytest.approx(85.95)
    assert mouth_1.n_triangles == 24

    mouth_2 = mouths['Mouth 2']
    assert len(mouth_2.atom_indices) == 14
    assert _value(mouth_2.solvent_accessible_area, 'angstroms**2') == pytest.approx(23.923)

    assert 'Mouth 25' not in mouths


def test_load_castp_hiv_imports_server_metrics():
    topography = load_CASTp(dir_path=tmt.demo['HIV-1 Protease']['CASTp_1hiv'])

    all_features = _castp_surface_features(topography)
    mouths = _features_by_source_id(topography, 'mouth')

    assert len(all_features) == 17
    assert len(mouths) == 14

    pocket_1 = all_features['Pocket 1']
    assert len(pocket_1.atom_indices) == 105
    assert _value(pocket_1.solvent_accessible_area, 'angstroms**2') == pytest.approx(521.316)
    assert _value(pocket_1.molecular_surface_area, 'angstroms**2') == pytest.approx(748.133)
    assert _value(pocket_1.solvent_accessible_volume, 'angstroms**3') == pytest.approx(460.905)
    assert _value(pocket_1.molecular_surface_volume, 'angstroms**3') == pytest.approx(1337.275)
    assert _value(pocket_1.length, 'angstroms') == pytest.approx(422.856)
    assert pocket_1.corner_points_count == 186

    pocket_2 = all_features['Pocket 2']
    assert len(pocket_2.atom_indices) == 16
    assert _value(pocket_2.solvent_accessible_volume, 'angstroms**3') == pytest.approx(9.850)

    mouth_1 = mouths['Mouth 1']
    assert len(mouth_1.atom_indices) == 36
    assert _value(mouth_1.solvent_accessible_area, 'angstroms**2') == pytest.approx(97.135)
    assert _value(mouth_1.molecular_surface_area, 'angstroms**2') == pytest.approx(237.38)
    assert _value(mouth_1.solvent_accessible_length, 'angstroms') == pytest.approx(94.456)
    assert _value(mouth_1.molecular_surface_length, 'angstroms') == pytest.approx(112.05)
    assert mouth_1.n_triangles == 32

    mouth_2 = mouths['Mouth 2']
    assert len(mouth_2.atom_indices) == 6
    assert _value(mouth_2.solvent_accessible_area, 'angstroms**2') == pytest.approx(5.715)


def test_load_castp_uses_only_mouths_present_in_mouth_file():
    topography = load_CASTp(dir_path=tmt.demo['TcTIM']['CASTp_1tcd'])
    mouths = _features_by_source_id(topography, 'mouth')

    assert 'Mouth 6' not in mouths
    assert 'Mouth 20' not in mouths
    assert 'Mouth 25' not in mouths


@pytest.mark.parametrize(
    ('zip_name', 'expected'),
    [
        (
            '1a4j.zip',
            {
                'n_pockets': 101,
                'n_mouths': 62,
                'pocket_1_atom_labels': 168,
                'pocket_1_sa_area': 940.137,
                'pocket_1_ms_area': 1228.571,
                'pocket_1_sa_volume': 1219.652,
                'pocket_1_ms_volume': 2712.339,
                'pocket_1_length': 681.759,
                'pocket_1_corner_points': 284,
                'mouth_1_atom_labels': 75,
                'mouth_1_sa_area': 317.427,
                'mouth_1_ms_area': 643.53,
                'mouth_1_sa_length': 221.867,
                'mouth_1_ms_length': 248.26,
                'mouth_1_triangles': 70,
            },
        ),
        (
            '1hiv.zip',
            {
                'n_pockets': 17,
                'n_mouths': 14,
                'pocket_1_atom_labels': 105,
                'pocket_1_sa_area': 521.316,
                'pocket_1_ms_area': 748.133,
                'pocket_1_sa_volume': 460.905,
                'pocket_1_ms_volume': 1337.275,
                'pocket_1_length': 422.856,
                'pocket_1_corner_points': 186,
                'mouth_1_atom_labels': 36,
                'mouth_1_sa_area': 97.135,
                'mouth_1_ms_area': 237.38,
                'mouth_1_sa_length': 94.456,
                'mouth_1_ms_length': 112.05,
                'mouth_1_triangles': 32,
            },
        ),
        (
            '1stp.zip',
            {
                'n_pockets': 9,
                'n_mouths': 6,
                'pocket_1_atom_labels': 43,
                'pocket_1_sa_area': 127.274,
                'pocket_1_ms_area': 231.759,
                'pocket_1_sa_volume': 74.087,
                'pocket_1_ms_volume': 319.870,
                'pocket_1_length': 125.176,
                'pocket_1_corner_points': 77,
                'mouth_1_atom_labels': 11,
                'mouth_1_sa_area': 13.424,
                'mouth_1_ms_area': 53.48,
                'mouth_1_sa_length': 24.755,
                'mouth_1_ms_length': 33.55,
                'mouth_1_triangles': 9,
            },
        ),
        (
            '1tcd.zip',
            {
                'n_pockets': 78,
                'n_mouths': 42,
                'pocket_1_atom_labels': 68,
                'pocket_1_sa_area': 283.364,
                'pocket_1_ms_area': 456.907,
                'pocket_1_sa_volume': 165.990,
                'pocket_1_ms_volume': 637.990,
                'pocket_1_length': 234.656,
                'pocket_1_corner_points': 108,
                'mouth_1_atom_labels': 26,
                'mouth_1_sa_area': 57.751,
                'mouth_1_ms_area': 171.53,
                'mouth_1_sa_length': 77.154,
                'mouth_1_ms_length': 85.95,
                'mouth_1_triangles': 24,
            },
        ),
        (
            '2pk4.zip',
            {
                'n_pockets': 7,
                'n_mouths': 3,
                'pocket_1_atom_labels': 14,
                'pocket_1_sa_area': 14.077,
                'pocket_1_ms_area': 52.441,
                'pocket_1_sa_volume': 4.252,
                'pocket_1_ms_volume': 48.078,
                'pocket_1_length': 23.608,
                'pocket_1_corner_points': 20,
                'mouth_1_atom_labels': 6,
                'mouth_1_sa_area': 3.809,
                'mouth_1_ms_area': 22.31,
                'mouth_1_sa_length': 8.817,
                'mouth_1_ms_length': 17.61,
                'mouth_1_triangles': 4,
            },
        ),
    ],
)
def test_load_castp_server_zip_imports_metrics(zip_name, expected):
    zip_path = Path('topomt/data/CASTp_3.0_server') / zip_name
    topography = load_CASTp(zip_file=zip_path)

    all_features = _castp_surface_features(topography)
    mouths = _features_by_source_id(topography, 'mouth')

    assert len(all_features) == expected['n_pockets']
    assert len(mouths) == expected['n_mouths']

    pocket_1 = all_features['Pocket 1']
    assert len(pocket_1.atom_labels) == expected['pocket_1_atom_labels']
    assert _value(pocket_1.solvent_accessible_area, 'angstroms**2') == pytest.approx(expected['pocket_1_sa_area'])
    assert _value(pocket_1.molecular_surface_area, 'angstroms**2') == pytest.approx(expected['pocket_1_ms_area'])
    assert _value(pocket_1.solvent_accessible_volume, 'angstroms**3') == pytest.approx(expected['pocket_1_sa_volume'])
    assert _value(pocket_1.molecular_surface_volume, 'angstroms**3') == pytest.approx(expected['pocket_1_ms_volume'])
    assert _value(pocket_1.length, 'angstroms') == pytest.approx(expected['pocket_1_length'])
    assert pocket_1.corner_points_count == expected['pocket_1_corner_points']

    mouth_1 = mouths['Mouth 1']
    assert len(mouth_1.atom_labels) == expected['mouth_1_atom_labels']
    assert _value(mouth_1.solvent_accessible_area, 'angstroms**2') == pytest.approx(expected['mouth_1_sa_area'])
    assert _value(mouth_1.molecular_surface_area, 'angstroms**2') == pytest.approx(expected['mouth_1_ms_area'])
    assert _value(mouth_1.solvent_accessible_length, 'angstroms') == pytest.approx(expected['mouth_1_sa_length'])
    assert _value(mouth_1.molecular_surface_length, 'angstroms') == pytest.approx(expected['mouth_1_ms_length'])
    assert mouth_1.n_triangles == expected['mouth_1_triangles']


def test_load_castp_classifies_surface_features_from_n_mouths():
    topography = load_CASTp(zip_file=Path('topomt/data/CASTp_3.0_server/1tcd.zip'))

    for feature_type in ('pocket', 'void', 'channel', 'branched_channel'):
        for feature in topography.get_features(by='type', value=feature_type):
            n_mouths = getattr(feature, 'n_mouths', None)
            if n_mouths is None:
                continue
            if feature_type == 'void':
                assert n_mouths == 0
            elif feature_type == 'pocket':
                assert n_mouths == 1
            elif feature_type == 'channel':
                assert n_mouths == 2
            elif feature_type == 'branched_channel':
                assert n_mouths >= 3
