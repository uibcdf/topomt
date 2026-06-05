"""Resolve an accumulated atom selection into DFND simplices (edge/face/tetra).

This powers the canvas right-click menu: molsysviewer pushes the active atom
selection to the add-on (``on_active_selection_changed``); we map it to the DFND
simplices it defines and return context-menu items. Clicking an item
(``on_context_action``) highlights the simplex and dumps its diagnostic info.

All matching is by **global** atom indices (the space molsysviewer reports):
- 2 atoms forming an edge  -> "Select edge id X"
- 3 atoms forming a face   -> "Select face id X"
- 4 atoms forming a tetra  -> "Select tetrahedron X"
- otherwise / larger sets  -> bulk "Select all N edges/faces/tetrahedra contained"
"""

from typing import Any

from topomt.dfnd.selectors import select_edges, select_faces, select_tetrahedra

ACTION_ID = 'dfnd-select-simplex'
SELECTION_GROUP = 'Selección actual'
HIGHLIGHT_TAG = 'dfn-highlight'


def simplex_selection_info(view) -> dict[str, Any] | None:
    """Inspect the last DFND simplex selected via the context menu.

    Returns a dict (``kind``, ``atom_indices``, ``tetrahedron_ids``, plus the
    simplex id/ids), or ``None`` if nothing has been selected. Parallels
    molsysviewer's ``view.active_selection.info()`` for the DFND simplex layer.
    """
    # Prefer the public namespace; fall back to the legacy private runtime.
    namespace = None
    addons = getattr(view, 'addons', None)
    if addons is not None:
        try:
            namespace = getattr(addons, 'topomt', None)
        except Exception:
            namespace = None
    if namespace is None:
        namespace = getattr(view, '_topomt_addon_runtime', None)
    info = getattr(namespace, 'active_simplex_selection', None) if namespace is not None else None
    return dict(info) if info else None


def _atom_set(atom_indices) -> list[int]:
    return sorted({int(a) for a in atom_indices})


def resolve_simplices(topography, atom_indices) -> list[dict[str, Any]]:
    """Return context-menu item dicts for the DFND simplices an atom set defines.

    Pure function (no view/IO) so it is unit-testable. Each item carries a
    ``payload`` echoed back to ``on_context_action``.
    """
    atoms = _atom_set(atom_indices)
    atom_set = set(atoms)
    n = len(atoms)
    if n < 2:
        return []

    # Simplices fully contained in the selection (all their atoms selected).
    edges = select_edges(topography, atoms_subset=atoms)
    faces = [
        face
        for face in select_faces(topography)
        if set(face.get('atom_indices', ())) and set(face['atom_indices']).issubset(atom_set)
    ]
    tetrahedra = [
        tet
        for tet in select_tetrahedra(topography)
        if set(tet.get('atom_indices', ())) and set(tet['atom_indices']).issubset(atom_set)
    ]

    items: list[dict[str, Any]] = []
    order = 0

    def add(item: dict[str, Any]) -> None:
        nonlocal order
        item.setdefault('group', SELECTION_GROUP)
        item.setdefault('order', order)
        order += 10
        items.append(item)

    # Exact single simplex: the whole selection IS one edge / face / tetra.
    exact_edge = next((e for e in edges if frozenset(e['atom_indices']) == atom_set), None)
    exact_face = next((f for f in faces if frozenset(f['atom_indices']) == atom_set), None)
    exact_tet = next((t for t in tetrahedra if frozenset(t['atom_indices']) == atom_set), None)

    if n == 2 and exact_edge is not None:
        add(_edge_item(exact_edge))
    elif n == 3 and exact_face is not None:
        add(_face_item(exact_face))
    elif n == 4 and exact_tet is not None:
        add(_tetra_item(exact_tet))

    # Bulk options for everything contained (skip a dimension already offered as
    # the single exact item).
    if not (n == 4 and exact_tet is not None) and tetrahedra:
        add(_bulk_item('tetrahedra', tetrahedra, 'tetrahedron_id', 'tetraedros'))
    if not (n == 3 and exact_face is not None) and faces:
        add(_bulk_item('faces', faces, 'face_id', 'caras'))
    if not (n == 2 and exact_edge is not None) and edges:
        add(_bulk_item('edges', edges, 'edge_id', 'aristas'))

    return items


def _edge_item(edge: dict[str, Any]) -> dict[str, Any]:
    a, b = edge['atom_indices']
    return {
        'id': ACTION_ID,
        'title': f"Seleccionar arista id {edge['edge_id']}: atoms {a}-{b}",
        'payload': {
            'kind': 'edge',
            'edge_id': edge['edge_id'],
            'atom_indices': list(edge['atom_indices']),
            'tetrahedron_ids': list(edge.get('tetrahedron_ids', [])),
        },
    }


def _face_item(face: dict[str, Any]) -> dict[str, Any]:
    neighbor = face.get('neighbor_tetrahedron_id', -1)
    neighbor_label = 'OCEAN' if neighbor == -1 else neighbor
    owner = face.get('owner_tetrahedron_id')
    perm = face.get('permeability_state', 'unknown')
    return {
        'id': ACTION_ID,
        'title': (
            f"Seleccionar cara id {face['face_id']}: "
            f"tetrahedra {owner}-{neighbor_label}; {perm}"
        ),
        'payload': {
            'kind': 'face',
            'face_id': face['face_id'],
            'atom_indices': list(face['atom_indices']),
            'tetrahedron_ids': [
                tid for tid in (owner, neighbor if neighbor != -1 else None) if tid is not None
            ],
        },
    }


def _tetra_item(tet: dict[str, Any]) -> dict[str, Any]:
    tid = tet.get('tetrahedron_id')
    return {
        'id': ACTION_ID,
        'title': f"Seleccionar tetraedro {tid}: {tet.get('combined_class', 'unknown')}",
        'payload': {
            'kind': 'tetrahedron',
            'tetrahedron_id': tid,
            'atom_indices': list(tet['atom_indices']),
            'tetrahedron_ids': [tid],
        },
    }


def _bulk_item(kind: str, records, id_key: str, label_es: str) -> dict[str, Any]:
    ids = [rec.get(id_key) for rec in records]
    tetra_ids = sorted(
        {
            int(tid)
            for rec in records
            for tid in (
                rec.get('tetrahedron_ids')
                or ([rec.get('tetrahedron_id')] if rec.get('tetrahedron_id') is not None else [])
            )
        }
    )
    atom_indices = sorted(
        {int(a) for rec in records for a in rec.get('atom_indices', [])}
    )
    return {
        'id': ACTION_ID,
        'title': f"Seleccionar todas las {label_es} contenidas ({len(records)})",
        'payload': {
            'kind': kind,
            'ids': ids,
            'atom_indices': atom_indices,
            'tetrahedron_ids': tetra_ids,
        },
    }
