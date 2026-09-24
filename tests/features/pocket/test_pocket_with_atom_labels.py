""" """

import topomt as tmt

# 12 cases with atom_labels and not boundaries or points:
# 1. instant Pocket with feature_id and no topography
# 2. instant Pocket with no feature_id and no topography
# 3. instant Pocket with feature_id and topography
# 4. instant Pocket with no feature_id and topography
# 5. add existing Pocket with feature_id and no topography to topography
# 6. add existing Pocket with no feature_id and no topography to topography
# 7. add existing Pocket with feature_id and topography to topography
# 8. add existing Pocket with no feature_id and topography to topography
# 9. add new Pocket with feature_id and no topography to topography
# 10. add new Pocket with no feature_id and no topography to topography
# 11. add new Pocket with feature_id and topography to topography
# 12. add new Pocket with no feature_id and topography to topography


# 1. instant Pocket with feature_id and no topography
def test_pocket_with_atom_labels_1():

    # default: '{atom_name}-{atom_id}/{group_name}-{group_id}/{chain_name}-{chain_id}'
    atom_labels = [
        'N-26/PRO-7/A-A',
        'CA-34/ILE-8/A-A',
        'O-44/ALA-9/A-A',
    ]
    pocket = tmt.features.Pocket(feature_id='P1', atom_labels=atom_labels)

    assert pocket.boundaries == set()
    assert pocket.points == set()
    assert pocket.solvent_accessible_area is None
    assert pocket.solvent_accessible_volume is None
    assert pocket.molecular_surface_area is None
    assert pocket.molecular_surface_volume is None
    assert pocket.length is None
    assert pocket.corner_points_count is None
    assert pocket.feature_id == 'P1'
    assert pocket.feature_type == 'pocket'
    assert pocket.feature_label is None
    assert pocket.source == 'TopoMT'
    assert pocket.source_id == 'P1'
    assert pocket.atom_indices is None
    assert pocket.atom_labels == atom_labels
    assert pocket.atom_label_format == tmt.config.defaults.atom_label_format
    assert pocket.shape_type == 'concavity'
    assert pocket.dimensionality == 2
    assert pocket._topography is None


# 2. instant Pocket with no feature_id and no topography
def test_pocket_with_atom_labels_2():

    atom_label_format = '{atom_id}/{group_id}/{chain_id}'
    atom_labels = [
        '26/7/A',
        '34/8/A',
        '44/9/A',
    ]
    pocket = tmt.features.Pocket(
        feature_id=None, atom_labels=atom_labels, atom_label_format=atom_label_format
    )

    assert pocket.boundaries == set()
    assert pocket.points == set()
    assert pocket.solvent_accessible_area is None
    assert pocket.solvent_accessible_volume is None
    assert pocket.molecular_surface_area is None
    assert pocket.molecular_surface_volume is None
    assert pocket.length is None
    assert pocket.corner_points_count is None
    assert pocket.feature_id is None
    assert pocket.feature_type == 'pocket'
    assert pocket.feature_label is None
    assert pocket.source == 'TopoMT'
    assert pocket.source_id is None
    assert pocket.atom_indices is None
    assert pocket.atom_labels == atom_labels
    assert pocket.atom_label_format == atom_label_format
    assert pocket.shape_type == 'concavity'
    assert pocket.dimensionality == 2
    assert pocket._topography is None


# 3. instant Pocket with feature_id and topography
def test_pocket_with_atom_labels_3(topography_empty_1tcd):

    # default: '{atom_name}-{atom_id}/{group_name}-{group_id}/{chain_name}-{chain_id}'
    atom_labels = [
        'N-26/PRO-7/A-A',
        'CA-34/ILE-8/A-A',
        'O-44/ALA-9/A-A',
    ]
    topography = topography_empty_1tcd
    pocket = tmt.features.Pocket(
        feature_id='P1', atom_labels=atom_labels, topography=topography
    )

    assert pocket.boundaries == set()
    assert pocket.points == set()
    assert pocket.solvent_accessible_area is None
    assert pocket.solvent_accessible_volume is None
    assert pocket.molecular_surface_area is None
    assert pocket.molecular_surface_volume is None
    assert pocket.length is None
    assert pocket.corner_points_count is None
    assert pocket.feature_id == 'P1'
    assert pocket.feature_type == 'pocket'
    assert pocket.feature_label is None
    assert pocket.source == 'TopoMT'
    assert pocket.source_id == 'P1'
    assert pocket.atom_indices == [25, 33, 43]
    assert pocket.atom_labels == atom_labels
    assert pocket.atom_label_format == tmt.config.defaults.atom_label_format
    assert pocket.shape_type == 'concavity'
    assert pocket.dimensionality == 2
    assert id(pocket._topography) == id(topography)
    assert id(topography['P1']) == id(pocket)
    assert len(topography) == 1


# 4. instant Pocket with no feature_id and topography
def test_pocket_with_atom_labels_4(topography_empty_1tcd):

    atom_label_format = '{atom_id}/{group_id}/{chain_id}'
    atom_labels = [
        '26/7/A',
        '34/8/A',
        '44/9/A',
    ]
    topography = topography_empty_1tcd
    feature_id = topography._make_next_feature_id('pocket')
    pocket = tmt.features.Pocket(
        feature_id=None,
        atom_labels=atom_labels,
        atom_label_format=atom_label_format,
        topography=topography,
    )

    assert pocket.boundaries == set()
    assert pocket.points == set()
    assert pocket.solvent_accessible_area is None
    assert pocket.solvent_accessible_volume is None
    assert pocket.molecular_surface_area is None
    assert pocket.molecular_surface_volume is None
    assert pocket.length is None
    assert pocket.corner_points_count is None
    assert pocket.feature_id == feature_id
    assert pocket.feature_type == 'pocket'
    assert pocket.feature_label is None
    assert pocket.source == 'TopoMT'
    assert pocket.source_id == feature_id
    assert pocket.atom_indices == [25, 33, 43]
    assert pocket.atom_labels == atom_labels
    assert pocket.atom_label_format == atom_label_format
    assert pocket.shape_type == 'concavity'
    assert pocket.dimensionality == 2
    assert id(pocket._topography) == id(topography)
    assert id(topography[feature_id]) == id(pocket)
    assert len(topography) == 1


# 5. add existing Pocket with feature_id and no topography to topography
def test_pocket_with_atom_labels_5(topography_empty_1tcd):

    # default: '{atom_name}-{atom_id}/{group_name}-{group_id}/{chain_name}-{chain_id}'
    atom_labels = [
        'N-26/PRO-7/A-A',
        'CA-34/ILE-8/A-A',
        'O-44/ALA-9/A-A',
    ]
    topography = topography_empty_1tcd
    pocket = tmt.features.Pocket(
        feature_id='P1', atom_labels=atom_labels, topography=None
    )
    topography.add_feature(pocket)

    assert id(pocket._topography) == id(topography)
    assert id(topography['P1']) == id(pocket)
    assert len(topography) == 1
    assert pocket.atom_indices == [25, 33, 43]


# 6. add existing Pocket with no feature_id and no topography to topography
def test_pocket_with_atom_labels_6(topography_empty_1tcd):

    atom_label_format = '{atom_id}/{group_id}/{chain_id}'
    atom_labels = [
        '26/7/A',
        '34/8/A',
        '44/9/A',
    ]
    topography = topography_empty_1tcd
    feature_id = topography._make_next_feature_id('pocket')
    pocket = tmt.features.Pocket(
        feature_id=None,
        atom_labels=atom_labels,
        atom_label_format=atom_label_format,
        topography=None,
    )
    topography.add_feature(pocket)

    assert id(pocket._topography) == id(topography)
    assert id(topography[feature_id]) == id(pocket)
    assert len(topography) == 1
    assert pocket.atom_indices == [25, 33, 43]


# 7. add existing Pocket with feature_id and topography to topography
def test_pocket_with_atom_labels_7(topography_empty_1tcd):

    # default: '{atom_name}-{atom_id}/{group_name}-{group_id}/{chain_name}-{chain_id}'
    atom_labels = [
        'N-26/PRO-7/A-A',
        'CA-34/ILE-8/A-A',
        'O-44/ALA-9/A-A',
    ]
    topography = topography_empty_1tcd
    pocket = tmt.features.Pocket(
        feature_id='P1', atom_labels=atom_labels, topography=topography
    )
    topography.add_feature(pocket)

    assert id(pocket._topography) == id(topography)
    assert id(topography['P1']) == id(pocket)
    assert len(topography) == 1
    assert pocket.atom_indices == [25, 33, 43]


# 8. add existing Pocket with no feature_id and topography to topography
def test_pocket_with_atom_labels_8(topography_empty_1tcd):

    atom_label_format = '{atom_id}/{group_id}/{chain_id}'
    atom_labels = [
        '26/7/A',
        '34/8/A',
        '44/9/A',
    ]
    topography = topography_empty_1tcd
    feature_id = topography._make_next_feature_id('pocket')
    pocket = tmt.features.Pocket(
        feature_id=None,
        atom_labels=atom_labels,
        atom_label_format=atom_label_format,
        topography=topography,
    )
    topography.add_feature(pocket)

    assert id(pocket._topography) == id(topography)
    assert id(topography[feature_id]) == id(pocket)
    assert len(topography) == 1
    assert pocket.atom_indices == [25, 33, 43]


# 9. add new Pocket with feature_id and no topography to topography
def test_pocket_with_atom_indices_9(topography_empty_1tcd):

    # default: '{atom_name}-{atom_id}/{group_name}-{group_id}/{chain_name}-{chain_id}'
    atom_labels = [
        'N-26/PRO-7/A-A',
        'CA-34/ILE-8/A-A',
        'O-44/ALA-9/A-A',
    ]
    topography = topography_empty_1tcd
    topography.add_new_feature(
        feature_type='pocket', atom_labels=atom_labels, feature_id='P1'
    )

    assert isinstance(topography['P1'], tmt.features.Pocket)
    assert len(topography) == 1
    assert id(topography['P1']._topography) == id(topography)
    assert topography['P1'].atom_indices == [25, 33, 43]


# 10. add new Pocket with no feature_id and no topography to topography
def test_pocket_with_atom_indices_10(topography_empty_1tcd):

    atom_label_format = '{atom_id}/{group_id}/{chain_id}'
    atom_labels = [
        '26/7/A',
        '34/8/A',
        '44/9/A',
    ]
    topography = topography_empty_1tcd
    feature_id = topography._make_next_feature_id('pocket')
    topography.add_new_feature(
        feature_type='pocket',
        atom_labels=atom_labels,
        atom_label_format=atom_label_format,
    )

    assert isinstance(topography[feature_id], tmt.features.Pocket)
    assert len(topography) == 1
    assert id(topography[feature_id]._topography) == id(topography)
    assert topography[feature_id].atom_indices == [25, 33, 43]


## 11. add new Pocket with feature_id and topography to topography
## This test makes no sense because the Pocket is created inside the topography
## The method add_new_feature has no topography input argument
#
## 12. add new Pocket with no feature_id and topography to topography
## This test makes no sense because the Pocket is created inside the topography
## The method add_new_feature has no topography input argument
#
#
