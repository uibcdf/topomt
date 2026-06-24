import pytest

from topomt.dfnd.components import Components, DryComponent, WetComponent


# family is derived from the grounded signature (decision S5.2), so a test
# component must supply the grounded inputs that classify_topology names `family`:
# (n_mouths, n_resident_nodes, n_wall_faces).
_FAMILY_GROUNDED = {
    'void': (0, 1, 5),
    'pocket': (1, 1, 5),
    'channel': (2, 1, 5),
    'percolating': (1, 1, 0),
    'surface_concavity': (1, 0, 5),
    'degenerate_subprobe': (0, 0, 5),
}


def _wet(component_id='WET-1', family='void', component_key=None):
    n_mouths, n_resident, n_wall = _FAMILY_GROUNDED[family]
    component = WetComponent(
        component_id=component_id,
        component_key=component_key,
        node_indices=[1],
    )
    component.external_link_ids = list(range(n_mouths))
    component.n_mouths = n_mouths
    component.resident_node_indices = list(range(n_resident))
    component.has_residence = n_resident >= 1
    component.n_wall_faces = n_wall
    return component


def _dry(component_id='DRY-1'):
    return DryComponent(component_id=component_id, node_indices=[2])


def test_family_is_derived_from_the_grounded_signature_not_stored():
    # family is no longer a stored kernel fact: it is re-derived on read from
    # (n_mouths, n_resident_nodes, n_wall_faces) by classify_topology (decision S5.2)
    from topomt.dfnd import families as fam

    component = WetComponent(component_id='WET-1')
    component.n_mouths = 1
    component.external_link_ids = [0]
    component.resident_node_indices = [0]
    component.n_wall_faces = 5
    assert component.family == fam.POCKET
    # mutate the grounded inputs -> the name re-derives (there is no setter)
    component.n_mouths = 2
    component.external_link_ids = [0, 1]
    assert component.family == fam.CHANNEL
    # a dry bank keeps its structural side label; side is intrinsic to the subclass
    dry = _dry()
    assert dry.family == fam.DRY_BANK
    assert WetComponent(component_id='WET-2').side == 'wet' and dry.side == 'dry'


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
