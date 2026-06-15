"""Selectors for DFND component, tetrahedron, and face records."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


def _raw_from_source(source: Any) -> dict[str, Any]:
    dfnd_data = getattr(source, 'dfnd', None)
    if dfnd_data is not None:
        return _raw_from_source(dfnd_data)

    raw = getattr(source, 'raw', None)
    if raw is not None:
        return raw

    if isinstance(source, dict):
        candidate = source.get('raw', source)
        if isinstance(candidate, dict):
            return candidate

    raise ValueError('source must be a Topography, DFNDData, DFND result, or raw dict')


@dataclass(frozen=True)
class _ComponentSourceView:
    records: tuple[tuple[Any, str | None], ...]
    capabilities: frozenset[str]


def _component_source_view(source: Any) -> _ComponentSourceView:
    dfnd_data = getattr(source, 'dfnd', None)
    if dfnd_data is not None:
        return _component_source_view(dfnd_data)

    dfn = getattr(source, 'dfn', None)
    registry = getattr(dfn, 'components', None) if dfn is not None else None
    if registry is not None:
        records = tuple(
            (component, getattr(component, 'side', None))
            for component in registry.values()
        )
        capabilities = frozenset(
            side for _component, side in records if side in {'wet', 'dry'}
        )
        return _ComponentSourceView(records, capabilities)

    if isinstance(source, dict):
        records = []
        capabilities = set()
        raw = source.get('raw', source)
        if isinstance(raw, dict) and 'wet_components' in raw:
            capabilities.add('wet')
            records.extend((component, 'wet') for component in raw['wet_components'])
        dry = source.get('dry')
        if isinstance(dry, dict) and 'components' in dry:
            capabilities.add('dry')
            records.extend((component, 'dry') for component in dry['components'])
        if capabilities:
            return _ComponentSourceView(tuple(records), frozenset(capabilities))

    raise ValueError(
        'source must contain a DFND component registry or component result records'
    )


def _requests_side(side: Any, expected: str) -> bool:
    if side is None:
        return False
    if isinstance(side, str):
        return side == expected
    return expected in side


def _validate_component_capability(view: _ComponentSourceView, side: Any) -> None:
    for expected in ('wet', 'dry'):
        if _requests_side(side, expected) and expected not in view.capabilities:
            raise ValueError(f'source does not contain {expected} components')


def _iter_components(source: Any, side: Any = None):
    view = _component_source_view(source)
    _validate_component_capability(view, side)
    yield from view.records


def _component_raw_id(component: Any) -> Any:
    if isinstance(component, dict):
        return component.get('id')
    component_id = getattr(component, 'component_id', None)
    if isinstance(component_id, str) and '-' in component_id:
        suffix = component_id.rsplit('-', 1)[-1]
        try:
            return int(suffix)
        except ValueError:
            return suffix
    return component_id


def _component_family(component: Any, inferred_side: str | None = None) -> Any:
    if isinstance(component, dict):
        return component.get('family', 'dry_bank' if inferred_side == 'dry' else None)
    return getattr(component, 'family', None)


def _component_side(component: Any, inferred_side: str | None = None) -> Any:
    if inferred_side is not None:
        return inferred_side
    return getattr(component, 'side', None)


def _component_id(component: Any, inferred_side: str | None = None) -> str:
    component_id = getattr(component, 'component_id', None)
    if component_id is not None:
        return str(component_id)

    raw_id = _component_raw_id(component)
    prefix = 'DRY' if _component_side(component, inferred_side) == 'dry' else 'WET'
    return f'{prefix}-{raw_id}'


def _component_id_matches(
    component: Any,
    inferred_side: str | None,
    expected: str | int | Iterable[str | int] | None,
) -> bool:
    if expected is None:
        return True
    if isinstance(expected, (str, int)):
        expected_values = {expected}
    else:
        expected_values = set(expected)

    raw_id = _component_raw_id(component)
    values = {_component_id(component, inferred_side), raw_id, str(raw_id)}
    return bool(values & expected_values)


def _component_key(component: Any) -> Any:
    if isinstance(component, dict):
        return component.get('component_key')
    return getattr(component, 'component_key', None)


def _component_support_key(component: Any) -> Any:
    if isinstance(component, dict):
        return component.get('support_key')
    return getattr(component, 'support_key', None)


def _component_flags(component: Any) -> list[Any]:
    if isinstance(component, dict):
        return list(component.get('flags', []))
    return list(getattr(component, 'flags', []))


def _component_tetrahedron_ids(component: Any) -> list[int]:
    if isinstance(component, dict):
        ids = component.get(
            'tetrahedron_indices',
            component.get('tetrahedron_ids', []),
        )
    else:
        ids = getattr(component, 'node_indices', [])
    return [int(tetrahedron_id) for tetrahedron_id in ids]


def _component_atom_indices(component: Any) -> list[int]:
    if isinstance(component, dict):
        atom_indices = component.get('atom_indices', [])
    else:
        atom_indices = getattr(component, 'atom_indices', [])
    return [int(atom_index) for atom_index in atom_indices]


def _component_size(component: Any) -> int:
    if isinstance(component, dict) and 'size' in component:
        return int(component['size'])
    return len(_component_tetrahedron_ids(component))


def _matches_value(record_value: Any, expected: Any) -> bool:
    if expected is None:
        return True
    if isinstance(expected, str):
        return record_value == expected
    if isinstance(expected, Iterable):
        return record_value in expected
    return record_value == expected


def _matches_flags(
    record: dict[str, Any], flags_has: str | Iterable[str] | None
) -> bool:
    if flags_has is None:
        return True

    flags = record.get('flags', [])
    if isinstance(flags_has, str):
        expected_flags = {flags_has}
    else:
        expected_flags = set(flags_has)
    return expected_flags.issubset(set(flags))


def _face_dedupe_key(face: dict[str, Any], unique_by: str | None) -> Any:
    if unique_by is None:
        return None
    if unique_by in face:
        return face[unique_by]
    if unique_by == 'face_id':
        atoms = face.get('face_atoms_local')
        if atoms is not None:
            return tuple(sorted(atoms))
    return None


def select_components(
    source: Any,
    *,
    side: str | Iterable[str] | None = None,
    family: str | Iterable[str] | None = None,
    component_ids: str | int | Iterable[str | int] | None = None,
    component_keys: str | Iterable[str] | None = None,
    support_keys: str | Iterable[str] | None = None,
    min_size: int | None = None,
    flags_has: str | Iterable[str] | None = None,
) -> list[Any]:
    """Return DFND components matching graph-side and spatial-representation filters."""
    selected = []
    for component, inferred_side in _iter_components(source, side):
        if not _matches_value(_component_side(component, inferred_side), side):
            continue
        if not _matches_value(_component_family(component, inferred_side), family):
            continue
        if not _component_id_matches(component, inferred_side, component_ids):
            continue
        if not _matches_value(_component_key(component), component_keys):
            continue
        if not _matches_value(_component_support_key(component), support_keys):
            continue
        if min_size is not None and _component_size(component) < min_size:
            continue
        if not _matches_flags({'flags': _component_flags(component)}, flags_has):
            continue
        selected.append(component)
    return selected


def select_component_ids(
    source: Any,
    *,
    side: str | Iterable[str] | None = None,
    family: str | Iterable[str] | None = None,
    component_ids: str | int | Iterable[str | int] | None = None,
    component_keys: str | Iterable[str] | None = None,
    support_keys: str | Iterable[str] | None = None,
    min_size: int | None = None,
    flags_has: str | Iterable[str] | None = None,
) -> list[str]:
    """Return canonical DFND component ids such as ``WET-1`` or ``DRY-1``."""
    out = []
    for component, inferred_side in _iter_components(source, side):
        if not _matches_value(_component_side(component, inferred_side), side):
            continue
        if not _matches_value(_component_family(component, inferred_side), family):
            continue
        if not _component_id_matches(component, inferred_side, component_ids):
            continue
        if not _matches_value(_component_key(component), component_keys):
            continue
        if not _matches_value(_component_support_key(component), support_keys):
            continue
        if min_size is not None and _component_size(component) < min_size:
            continue
        if not _matches_flags({'flags': _component_flags(component)}, flags_has):
            continue
        out.append(_component_id(component, inferred_side))
    return out


def select_component_tetrahedron_ids(
    source: Any,
    *,
    side: str | Iterable[str] | None = None,
    family: str | Iterable[str] | None = None,
    component_ids: str | int | Iterable[str | int] | None = None,
    component_keys: str | Iterable[str] | None = None,
    support_keys: str | Iterable[str] | None = None,
    min_size: int | None = None,
    flags_has: str | Iterable[str] | None = None,
) -> list[int]:
    """Return tetrahedron ids from matching DFND components."""
    tetrahedron_ids = []
    for component in select_components(
        source,
        side=side,
        family=family,
        component_ids=component_ids,
        component_keys=component_keys,
        support_keys=support_keys,
        min_size=min_size,
        flags_has=flags_has,
    ):
        tetrahedron_ids.extend(_component_tetrahedron_ids(component))
    return tetrahedron_ids


def select_component_atom_indices(
    source: Any,
    *,
    side: str | Iterable[str] | None = None,
    family: str | Iterable[str] | None = None,
    component_ids: str | int | Iterable[str | int] | None = None,
    component_keys: str | Iterable[str] | None = None,
    support_keys: str | Iterable[str] | None = None,
    min_size: int | None = None,
    flags_has: str | Iterable[str] | None = None,
) -> list[int]:
    """Return component atom indices from matching DFND components."""
    atom_indices = []
    seen = set()
    for component in select_components(
        source,
        side=side,
        family=family,
        component_ids=component_ids,
        component_keys=component_keys,
        support_keys=support_keys,
        min_size=min_size,
        flags_has=flags_has,
    ):
        for atom_index in _component_atom_indices(component):
            if atom_index in seen:
                continue
            seen.add(atom_index)
            atom_indices.append(atom_index)
    return atom_indices


def select_tetrahedra(
    source: Any,
    *,
    tetrahedron_ids: int | Iterable[int] | None = None,
    residence_state: str | Iterable[str] | None = None,
    transit_role: str | Iterable[str] | None = None,
    flags_has: str | Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """Return DFND tetrahedron records matching the requested state filters."""
    raw = _raw_from_source(source)
    return [
        tetrahedron
        for tetrahedron in raw.get('tetrahedra', [])
        if _matches_value(tetrahedron.get('tetrahedron_id', None), tetrahedron_ids)
        and _matches_value(tetrahedron.get('residence_state'), residence_state)
        and _matches_value(tetrahedron.get('transit_role'), transit_role)
        and _matches_flags(tetrahedron, flags_has)
    ]


def select_tetrahedron_indices(
    source: Any,
    *,
    tetrahedron_ids: int | Iterable[int] | None = None,
    residence_state: str | Iterable[str] | None = None,
    transit_role: str | Iterable[str] | None = None,
    flags_has: str | Iterable[str] | None = None,
) -> list[int]:
    """Return positional indices of matching DFND tetrahedron records."""
    raw = _raw_from_source(source)
    return [
        index
        for index, tetrahedron in enumerate(raw.get('tetrahedra', []))
        if _matches_value(tetrahedron.get('tetrahedron_id', None), tetrahedron_ids)
        and _matches_value(tetrahedron.get('residence_state'), residence_state)
        and _matches_value(tetrahedron.get('transit_role'), transit_role)
        and _matches_flags(tetrahedron, flags_has)
    ]


def select_tetrahedron_ids(
    source: Any,
    *,
    tetrahedron_ids: int | Iterable[int] | None = None,
    residence_state: str | Iterable[str] | None = None,
    transit_role: str | Iterable[str] | None = None,
    flags_has: str | Iterable[str] | None = None,
) -> list[int]:
    """Return ``tetrahedron_id`` values for matching DFND tetrahedron records."""
    raw = _raw_from_source(source)
    return [
        int(tetrahedron.get('tetrahedron_id', index))
        for index, tetrahedron in enumerate(raw.get('tetrahedra', []))
        if _matches_value(tetrahedron.get('tetrahedron_id', None), tetrahedron_ids)
        and _matches_value(tetrahedron.get('residence_state'), residence_state)
        and _matches_value(tetrahedron.get('transit_role'), transit_role)
        and _matches_flags(tetrahedron, flags_has)
    ]


def select_tetrahedron_atom_indices(
    source: Any,
    *,
    tetrahedron_ids: int | Iterable[int] | None = None,
    residence_state: str | Iterable[str] | None = None,
    transit_role: str | Iterable[str] | None = None,
    flags_has: str | Iterable[str] | None = None,
) -> list[list[int]]:
    """Return local atom index quads for matching DFND tetrahedron records."""
    return [
        [int(atom) for atom in tetrahedron['local_atom_indices']]
        for tetrahedron in select_tetrahedra(
            source,
            tetrahedron_ids=tetrahedron_ids,
            residence_state=residence_state,
            transit_role=transit_role,
            flags_has=flags_has,
        )
        if len(tetrahedron.get('local_atom_indices', [])) == 4
    ]


def select_faces(
    source: Any,
    *,
    owner_tetrahedron_ids: int | Iterable[int] | None = None,
    neighbor_tetrahedron_ids: int | Iterable[int] | None = None,
    permeability_state: str | Iterable[str] | None = None,
    transit_edge: bool | Iterable[bool] | None = None,
    flags_has: str | Iterable[str] | None = None,
    unique_by: str | None = 'face_id',
) -> list[dict[str, Any]]:
    """Return DFND face records matching ownership and permeability filters."""
    raw = _raw_from_source(source)
    selected = []
    seen = set()

    for face in raw.get('faces', []):
        if not _matches_value(face.get('owner_tetrahedron_id'), owner_tetrahedron_ids):
            continue
        if not _matches_value(
            face.get('neighbor_tetrahedron_id'),
            neighbor_tetrahedron_ids,
        ):
            continue
        if not _matches_value(face.get('permeability_state'), permeability_state):
            continue
        if not _matches_value(face.get('transit_edge'), transit_edge):
            continue
        if not _matches_flags(face, flags_has):
            continue

        dedupe_key = _face_dedupe_key(face, unique_by)
        if dedupe_key is not None:
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
        selected.append(face)

    return selected


def select_face_indices(
    source: Any,
    *,
    owner_tetrahedron_ids: int | Iterable[int] | None = None,
    neighbor_tetrahedron_ids: int | Iterable[int] | None = None,
    permeability_state: str | Iterable[str] | None = None,
    transit_edge: bool | Iterable[bool] | None = None,
    flags_has: str | Iterable[str] | None = None,
    unique_by: str | None = 'face_id',
) -> list[int]:
    """Return positional indices of matching DFND face records."""
    raw = _raw_from_source(source)
    selected = []
    seen = set()

    for index, face in enumerate(raw.get('faces', [])):
        if not _matches_value(face.get('owner_tetrahedron_id'), owner_tetrahedron_ids):
            continue
        if not _matches_value(
            face.get('neighbor_tetrahedron_id'),
            neighbor_tetrahedron_ids,
        ):
            continue
        if not _matches_value(face.get('permeability_state'), permeability_state):
            continue
        if not _matches_value(face.get('transit_edge'), transit_edge):
            continue
        if not _matches_flags(face, flags_has):
            continue

        dedupe_key = _face_dedupe_key(face, unique_by)
        if dedupe_key is not None:
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
        selected.append(index)

    return selected


def select_face_ids(
    source: Any,
    *,
    owner_tetrahedron_ids: int | Iterable[int] | None = None,
    neighbor_tetrahedron_ids: int | Iterable[int] | None = None,
    permeability_state: str | Iterable[str] | None = None,
    transit_edge: bool | Iterable[bool] | None = None,
    flags_has: str | Iterable[str] | None = None,
    unique_by: str | None = 'face_id',
) -> list[int]:
    """Return ``face_id`` values for matching DFND face records."""
    raw = _raw_from_source(source)
    selected_face_ids = []
    selected_faces = select_faces(
        source,
        owner_tetrahedron_ids=owner_tetrahedron_ids,
        neighbor_tetrahedron_ids=neighbor_tetrahedron_ids,
        permeability_state=permeability_state,
        transit_edge=transit_edge,
        flags_has=flags_has,
        unique_by=unique_by,
    )
    raw_position_by_identity = {
        id(face): index for index, face in enumerate(raw.get('faces', []))
    }
    for face in selected_faces:
        fallback_id = raw_position_by_identity[id(face)]
        selected_face_ids.append(int(face.get('face_id', fallback_id)))
    return selected_face_ids


def select_face_atom_indices(
    source: Any,
    *,
    owner_tetrahedron_ids: int | Iterable[int] | None = None,
    neighbor_tetrahedron_ids: int | Iterable[int] | None = None,
    permeability_state: str | Iterable[str] | None = None,
    transit_edge: bool | Iterable[bool] | None = None,
    flags_has: str | Iterable[str] | None = None,
    unique_by: str | None = 'face_id',
) -> list[list[int]]:
    """Return local atom index triplets for matching DFND face records."""
    return [
        [int(atom) for atom in face['face_atoms_local']]
        for face in select_faces(
            source,
            owner_tetrahedron_ids=owner_tetrahedron_ids,
            neighbor_tetrahedron_ids=neighbor_tetrahedron_ids,
            permeability_state=permeability_state,
            transit_edge=transit_edge,
            flags_has=flags_has,
            unique_by=unique_by,
        )
        if len(face.get('face_atoms_local', [])) == 3
    ]


def select_edges(
    source: Any,
    *,
    tetrahedron_ids: int | Iterable[int] | None = None,
    atoms_subset: Iterable[int] | None = None,
    atoms_exact: Iterable[int] | None = None,
) -> list[dict[str, Any]]:
    """Return DFND edge records (id + two atoms + incident tetrahedra).

    Filters (all by global atom indices):
    - ``tetrahedron_ids``: edges incident to any of these tetrahedra.
    - ``atoms_subset``: edges whose *both* atoms lie in this set (used to collect
      all edges contained in an atom selection).
    - ``atoms_exact``: the edge whose two atoms are exactly this pair.
    """
    raw = _raw_from_source(source)
    tet_filter = tetrahedron_ids
    subset = set(int(a) for a in atoms_subset) if atoms_subset is not None else None
    exact = frozenset(int(a) for a in atoms_exact) if atoms_exact is not None else None

    selected = []
    for edge in raw.get('edges', []):
        atoms = [int(a) for a in edge.get('atom_indices', [])]
        if tet_filter is not None and not any(
            _matches_value(tid, tet_filter) for tid in edge.get('tetrahedron_ids', [])
        ):
            continue
        if subset is not None and not set(atoms).issubset(subset):
            continue
        if exact is not None and frozenset(atoms) != exact:
            continue
        selected.append(edge)

    return selected
