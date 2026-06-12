import pytest

from topomt.dfnd.components import Components, DryComponent, WetComponent


def _wet(component_id='WET-1', family='void', component_key=None):
    return WetComponent(
        component_id=component_id,
        component_key=component_key,
        family=family,
        node_indices=[1],
    )


def _dry(component_id='DRY-1'):
    return DryComponent(component_id=component_id, node_indices=[2])


def test_add_rejects_duplicate_id_without_mutating_registry():
    registry = Components()
    original = _wet()
    registry.add(original)
    before = registry.info()

    with pytest.raises(ValueError, match='already registered'):
        registry.add(_dry('WET-1'))

    assert registry['WET-1'] is original
    assert registry.info() == before
    assert registry.get_components(by='side', value='dry') == set()


def test_add_rejects_component_owned_by_another_registry_atomically():
    source = Components()
    destination = Components()
    component = _wet()
    source.add(component)

    with pytest.raises(ValueError, match='different Components registry'):
        destination.add(component)

    assert len(destination) == 0
    assert component._components is source


@pytest.mark.parametrize('component_id', [None, '', 3])
def test_add_rejects_invalid_component_id(component_id):
    registry = Components()

    with pytest.raises((TypeError, ValueError)):
        registry.add(_wet(component_id))

    assert len(registry) == 0


def test_registered_component_id_is_immutable_except_through_rename():
    registry = Components()
    component = _wet()
    registry.add(component)

    with pytest.raises(AttributeError, match='rename'):
        component.component_id = 'WET-2'

    registry.rename('WET-1', 'WET-2')
    assert component.component_id == 'WET-2'
    assert list(registry) == ['WET-2']


def test_connect_validates_both_ids_before_mutating_relations():
    registry = Components()
    registry.add(_wet())

    with pytest.raises(KeyError, match='DRY-1'):
        registry.connect('WET-1', 'DRY-1')

    assert registry.neighbors_of('WET-1') == set()
    assert 'DRY-1' not in registry._neighbors_of


def test_rename_updates_indexes_relations_and_component_references():
    registry = Components()
    wet = _wet()
    dry = _dry()
    wet.dry_lining = {'DRY-1': {'area': 1.0}}
    wet.lining_bodies = ['DRY-1']
    dry.wet_lining = {'WET-1': {'area': 1.0}}
    dry.neighbor_component_ids = ['WET-1']
    registry.add(wet)
    registry.add(dry)
    registry.connect('WET-1', 'DRY-1')
    registry.coast_faces = [{'wet_component_id': 'WET-1', 'dry_component_id': 'DRY-1'}]

    registry.rename('WET-1', 'WET-main')

    assert registry['WET-main'] is wet
    assert registry.get_components(by='side', value='wet') == {wet}
    assert registry.neighbors_of('DRY-1') == {wet}
    assert dry.wet_lining == {'WET-main': {'area': 1.0}}
    assert dry.neighbor_component_ids == ['WET-main']
    assert registry.coast_faces[0]['wet_component_id'] == 'WET-main'


def test_failed_rename_leaves_registry_unchanged():
    registry = Components()
    wet = _wet()
    dry = _dry()
    registry.add(wet)
    registry.add(dry)
    registry.connect('WET-1', 'DRY-1')

    with pytest.raises(ValueError, match='already registered'):
        registry.rename('WET-1', 'DRY-1')

    assert list(registry) == ['WET-1', 'DRY-1']
    assert wet.component_id == 'WET-1'
    assert registry.neighbors_of('WET-1') == {dry}


def test_replace_is_explicit_and_preserves_relations():
    registry = Components()
    original = _wet()
    neighbor = _dry()
    registry.add(original)
    registry.add(neighbor)
    registry.connect('WET-1', 'DRY-1')
    replacement = _wet(family='pocket')

    registry.replace('WET-1', replacement)

    assert registry['WET-1'] is replacement
    assert original._components is None
    assert replacement._components is registry
    assert registry.neighbors_of('WET-1') == {neighbor}
    assert registry.by_family('void') == []
    assert registry.by_family('pocket') == [replacement]


def test_failed_replace_leaves_registry_unchanged():
    registry = Components()
    original = _wet()
    registry.add(original)

    with pytest.raises(ValueError, match='must match'):
        registry.replace('WET-1', _wet('WET-2'))

    assert registry['WET-1'] is original
    assert original._components is registry
    assert registry.by_family('void') == [original]


def test_remove_cleans_indexes_relations_and_back_reference():
    registry = Components()
    wet = _wet()
    dry = _dry()
    registry.add(wet)
    registry.add(dry)
    registry.connect('WET-1', 'DRY-1')

    removed = registry.remove('WET-1')

    assert removed is wet
    assert wet._components is None
    assert 'WET-1' not in registry
    assert registry.neighbors_of('DRY-1') == set()
    assert registry.get_components(by='side', value='wet') == set()


def test_copy_preserves_registry_semantics_with_independent_components():
    registry = Components()
    wet = _wet()
    dry = _dry()
    registry.add(wet)
    registry.add(dry)
    registry.connect('WET-1', 'DRY-1')

    copied = registry.copy()

    assert copied is not registry
    assert copied['WET-1'] is not wet
    assert copied['WET-1']._components is copied
    assert copied.neighbors_of('WET-1') == {copied['DRY-1']}
    copied.remove('WET-1')
    assert 'WET-1' in registry


def test_registry_resolves_contextual_component_key():
    registry = Components()
    component = _wet(component_key='component-key-1')
    registry.add(component)

    assert registry.get_component_by_key('component-key-1') is component
    assert registry.get_components(by='key', value='component-key-1') == {component}

    registry.rename('WET-1', 'WET-main')
    assert registry.get_component_by_key('component-key-1') is component
