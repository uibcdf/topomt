import pytest

from topomt import Topography
from topomt.features import Mouth, Pocket, Void


def test_add_feature_rejects_duplicate_without_corrupting_indexes():
    topography = Topography()
    original = Pocket(feature_id='POC-1')
    topography.add_feature(original)
    before = topography.info()

    with pytest.raises(ValueError, match='already registered'):
        topography.add_feature(Void(feature_id='POC-1'))

    assert topography['POC-1'] is original
    assert topography.info() == before
    assert topography.get_features(by='type', value='void') == set()


def test_add_feature_owned_by_another_topography_is_atomic():
    source = Topography()
    destination = Topography()
    feature = Pocket(feature_id='POC-1')
    source.add_feature(feature)

    with pytest.raises(ValueError, match='different Topography'):
        destination.add_feature(feature)

    assert len(destination) == 0
    assert feature.topography is source


def test_automatic_feature_id_uses_next_free_suffix():
    topography = Topography(features=[Pocket(feature_id='POC-2')])

    assert topography.add_new_feature('pocket') == 'POC-1'
    assert topography.add_new_feature('pocket') == 'POC-3'


def test_registered_feature_id_is_immutable_except_through_rename():
    topography = Topography()
    feature = Pocket(feature_id='POC-1')
    topography.add_feature(feature)

    with pytest.raises(AttributeError, match='rename_feature'):
        feature.feature_id = 'POC-2'

    topography.rename_feature('POC-1', 'POC-main')
    assert feature.feature_id == 'POC-main'
    assert list(topography) == ['POC-main']


def test_failed_connect_does_not_auto_register_features():
    topography = Topography()
    invalid_child = Void(feature_id='VOI-1')
    parent = Pocket(feature_id='POC-1')

    with pytest.raises(ValueError, match='Child must be 0D or 1D'):
        topography.connect_features(invalid_child, parent)

    assert len(topography) == 0
    assert invalid_child.topography is None
    assert parent.topography is None


def test_rename_feature_updates_relations_and_feature_objects():
    topography = Topography()
    pocket = Pocket(feature_id='POC-1')
    mouth = Mouth(feature_id='MOU-1')
    topography.add_feature(pocket)
    topography.add_feature(mouth)
    topography.connect_features('MOU-1', 'POC-1')

    topography.rename_feature('POC-1', 'POC-main')

    assert topography.parents_of('MOU-1', as_feature_ids=True) == {'POC-main'}
    assert mouth.surfaces == {'POC-main'}
    assert topography['POC-main'].boundaries == {'MOU-1'}


def test_failed_rename_feature_leaves_registry_unchanged():
    topography = Topography()
    pocket = Pocket(feature_id='POC-1')
    void = Void(feature_id='VOI-1')
    topography.add_feature(pocket)
    topography.add_feature(void)

    with pytest.raises(ValueError, match='already registered'):
        topography.rename_feature('POC-1', 'VOI-1')

    assert list(topography) == ['POC-1', 'VOI-1']
    assert pocket.feature_id == 'POC-1'
    assert topography.get_features(by='type', value='pocket') == {pocket}


def test_replace_feature_is_explicit_and_preserves_compatible_relations():
    topography = Topography()
    original = Pocket(feature_id='POC-1')
    mouth = Mouth(feature_id='MOU-1')
    topography.add_feature(original)
    topography.add_feature(mouth)
    topography.connect_features('MOU-1', 'POC-1')
    replacement = Pocket(feature_id='POC-1')

    topography.replace_feature('POC-1', replacement)

    assert topography['POC-1'] is replacement
    assert original.topography is None
    assert replacement.topography is topography
    assert replacement.boundaries == {'MOU-1'}
    assert mouth.surfaces == {'POC-1'}


def test_failed_replace_feature_leaves_registry_unchanged():
    topography = Topography()
    original = Pocket(feature_id='POC-1')
    topography.add_feature(original)

    with pytest.raises(ValueError, match='must match'):
        topography.replace_feature('POC-1', Pocket(feature_id='POC-2'))

    assert topography['POC-1'] is original
    assert original.topography is topography
    assert topography.get_features(by='type', value='pocket') == {original}


def test_remove_feature_cleans_relations_and_back_reference():
    topography = Topography()
    pocket = Pocket(feature_id='POC-1')
    mouth = Mouth(feature_id='MOU-1')
    topography.add_feature(pocket)
    topography.add_feature(mouth)
    topography.connect_features('MOU-1', 'POC-1')

    removed = topography.remove_feature('POC-1')

    assert removed is pocket
    assert pocket.topography is None
    assert topography.parents_of('MOU-1', as_feature_ids=True) == set()
    assert mouth.surfaces == set()
    assert topography.get_features(by='type', value='pocket') == set()


@pytest.mark.parametrize('deep', [False, True])
def test_copy_preserves_semantic_state_and_rebinds_features(deep):
    topography = Topography(selection='protein', structure_indices=3)
    topography.dfnd = {'result': 1}
    topography.custom_analysis = {'value': [1]}
    topography.add_feature(Pocket(feature_id='POC-1'))

    copied = topography.copy(deep=deep)

    assert copied.selection == 'protein'
    assert copied.structure_indices == 3
    assert copied.dfnd == {'result': 1}
    assert copied.custom_analysis == {'value': [1]}
    assert copied['POC-1'] is not topography['POC-1']
    assert copied['POC-1'].topography is copied


@pytest.mark.parametrize('mutate_original', [False, True])
@pytest.mark.parametrize('operation', ['add', 'remove', 'rename', 'replace', 'connect'])
def test_shallow_copy_registry_mutations_are_independent(operation, mutate_original):
    original = Topography(
        features=[
            Pocket(feature_id='POC-1'),
            Pocket(feature_id='POC-2'),
            Mouth(feature_id='MOU-1'),
        ]
    )
    original.connect_features('MOU-1', 'POC-1')
    copied = original.copy(deep=False)
    changed, unchanged = (original, copied) if mutate_original else (copied, original)
    unchanged_features = dict(unchanged)

    if operation == 'add':
        changed.add_feature(Pocket(feature_id='POC-3'))
        assert 'POC-3' in changed
    elif operation == 'remove':
        removed = changed.remove_feature('POC-1')
        assert removed.topography is None
        assert 'POC-1' not in changed
        assert changed.parents_of('MOU-1', as_feature_ids=True) == set()
    elif operation == 'rename':
        changed.rename_feature('POC-1', 'POC-main')
        assert 'POC-1' not in changed
        assert changed.parents_of('MOU-1', as_feature_ids=True) == {'POC-main'}
    elif operation == 'replace':
        removed = changed.replace_feature('POC-1', Void(feature_id='POC-1'))
        assert removed.topography is None
        assert changed.get_features(by='type', value='void') == {changed['POC-1']}
        assert changed.children_of('POC-1', as_feature_ids=True) == {'MOU-1'}
    else:
        changed.connect_features('MOU-1', 'POC-2')
        assert changed.parents_of('MOU-1', as_feature_ids=True) == {'POC-1', 'POC-2'}

    assert dict(unchanged) == unchanged_features
    for by, value, expected in (
        ('type', 'pocket', {'POC-1', 'POC-2'}),
        ('type', 'void', set()),
        ('type', 'mouth', {'MOU-1'}),
        ('shape', 'concavity', {'POC-1', 'POC-2'}),
        ('shape', 'boundary', {'MOU-1'}),
        ('dimensionality', 2, {'POC-1', 'POC-2'}),
        ('dimensionality', 1, {'MOU-1'}),
    ):
        assert (
            unchanged.get_features(by=by, value=value, as_feature_ids=True) == expected
        )
        assert unchanged.get_features(by=by, value=value) == {
            unchanged[feature_id] for feature_id in expected
        }
    assert unchanged.children_of('POC-1', as_feature_ids=True) == {'MOU-1'}
    assert unchanged.children_of('POC-2', as_feature_ids=True) == set()
    assert unchanged.parents_of('MOU-1', as_feature_ids=True) == {'POC-1'}
    assert unchanged['POC-1'].boundaries == {'MOU-1'}
    assert unchanged['POC-2'].boundaries == set()
    assert unchanged['MOU-1'].surfaces == {'POC-1'}
    for registry in (original, copied):
        assert all(feature.topography is registry for feature in registry.values())


def test_shallow_copy_preserves_sharing_of_nested_analysis_payloads():
    original = Topography()
    original.dfnd = {'result': [1]}
    original.custom_analysis = {'value': [2]}

    copied = original.copy(deep=False)
    deep_copy = original.copy(deep=True)

    for name, key in (('dfnd', 'result'), ('custom_analysis', 'value')):
        original_payload = getattr(original, name)
        copied_payload = getattr(copied, name)
        assert copied_payload is not original_payload
        assert copied_payload[key] is original_payload[key]
        assert getattr(deep_copy, name)[key] is not original_payload[key]
