"""EXPERIMENTAL DFND mechanisms -- exploratory, not stable API.

Nothing here is part of the interface *definition* (that lives in
``interfaces.py`` and ``devguide/DFND/interfaces.md``: a wet region is an
interface when its lining is contributed by >=2 dry banks). These routines are
layered on top of a finished decomposition and are meant for exploration only;
they are not called by ``get_topography`` and their output shape may change.

Current contents
----------------
``localize_interface_core`` and ``peel_surface_rafts`` -- two complementary,
*partial* localizers for *where* inside a wet component the inter-body slab sits,
as opposed to the shallow surface rafts that hang off it. Motivation: in finite
systems (no sea level) a single wet component can wrap the whole exterior of the
bodies *and* fill the gap between them; the interface slab is then the graph
**articulation core** of that component, and the surface puddles are pendant
rafts hanging off it through thin necks.

- ``localize_interface_core`` scores tetrahedra by **betweenness centrality** on
  the permeable-face graph; the high tail is the interface *spine* (high
  precision, low recall -- it finds the central channel, not the whole slab).
- ``peel_surface_rafts`` iteratively strips low-degree pendant tetrahedra; the
  removed pieces are clean surface rafts and the remainder covers the whole slab
  (recall 1.0) but bleeds into the exterior near the gap edges (~0.75 precision).

Measured on ``two_blocks_interface`` neither gives a crisp slab boundary: the
slab **grades into the exterior** at the gap rim, so there is no clean graph cut.
Treat these as exploratory signals, not a segmentation. Use ``interfaces.py`` to
decide whether a component is an interface at all.
"""

from typing import Any

import numpy as np


def _resident_permeable_graph(raw: dict[str, Any], resident_ids: set[int]):
    """Return an ``networkx.Graph`` over ``resident_ids`` with an edge per shared
    *permeable* face (the routes a probe can actually take inside the wet body)."""
    import networkx as nx

    graph = nx.Graph()
    graph.add_nodes_from(resident_ids)
    for face in raw['faces']:
        if not face.get('transit_edge', face.get('permeability_state') == 'permeable'):
            continue
        owner = face.get('owner_tetrahedron_id')
        neighbor = face.get('neighbor_tetrahedron_id')
        if owner in resident_ids and neighbor in resident_ids:
            graph.add_edge(owner, neighbor)
    return graph


def localize_interface_core(
    topography,
    component_id: int,
    *,
    quantile: float = 0.80,
    return_scores: bool = False,
) -> dict[str, Any]:
    """EXPERIMENTAL. Localize the inter-body slab inside wet ``component_id``.

    Scores every resident tetrahedron of the component by betweenness centrality
    on its permeable-face graph and returns the high-betweenness tail (>= the
    ``quantile`` of the score distribution) as the *core* -- the candidate
    interface slab. The complement, once the core is removed, falls apart into the
    pendant *rafts* (shallow surface puddles); we report those fragments so the
    separation can be judged.

    Parameters
    ----------
    topography : Topography
        A topography carrying a DFND substrate (``topography.dfnd``).
    component_id : int
        Wet component id (the integer ``id`` in ``raw['wet_components']``; the
        public ``Pocket`` feature ``WET-<id>`` maps to it).
    quantile : float
        Score threshold for the core (default 0.80 -> top 20% by betweenness).
    return_scores : bool
        If true, include the per-tetrahedron betweenness in the result.

    Returns
    -------
    dict with keys: ``component_id``, ``core_tetrahedron_ids``,
    ``raft_fragments`` (list of tetra-id lists), ``n_rafts``, ``threshold`` and,
    optionally, ``betweenness``.
    """
    import networkx as nx

    if not 0.0 <= quantile < 1.0:
        raise ValueError('quantile must be in [0, 1)')

    raw = topography.dfnd.raw
    component = next(
        (c for c in raw['wet_components'] if c['id'] == component_id), None
    )
    if component is None:
        raise ValueError(f'no wet component with id {component_id!r}')

    resident_ids = {int(t) for t in (component.get('resident_tetrahedron_ids') or [])}
    if len(resident_ids) < 3:
        return {
            'component_id': component_id,
            'core_tetrahedron_ids': sorted(resident_ids),
            'raft_fragments': [],
            'n_rafts': 0,
            'threshold': 0.0,
        }

    graph = _resident_permeable_graph(raw, resident_ids)
    betweenness = nx.betweenness_centrality(graph, normalized=True)
    scores = np.array([betweenness[t] for t in graph.nodes])
    threshold = float(np.quantile(scores, quantile))

    core = {t for t in graph.nodes if betweenness[t] >= threshold and threshold > 0.0}
    # Degenerate case: a flat score distribution (e.g. a path) gives threshold 0;
    # fall back to the single argmax so we always return a non-empty core.
    if not core:
        core = {max(graph.nodes, key=lambda t: betweenness[t])}

    rest = graph.subgraph(set(graph.nodes) - core)
    raft_fragments = [
        sorted(component_nodes) for component_nodes in nx.connected_components(rest)
    ]
    raft_fragments.sort(key=len, reverse=True)

    result = {
        'component_id': component_id,
        'core_tetrahedron_ids': sorted(core),
        'raft_fragments': raft_fragments,
        'n_rafts': len(raft_fragments),
        'threshold': threshold,
    }
    if return_scores:
        result['betweenness'] = {int(t): float(betweenness[t]) for t in graph.nodes}
    return result


def peel_surface_rafts(
    topography,
    component_id: int,
    *,
    max_pendant_degree: int = 1,
) -> dict[str, Any]:
    """EXPERIMENTAL. Strip pendant surface rafts from wet ``component_id``.

    Iteratively removes tetrahedra whose degree in the permeable-face graph is
    ``<= max_pendant_degree``; the removed nodes are the shallow surface puddles
    that hang off the slab through thin necks, and the surviving subgraph is the
    well-connected core (covers the whole inter-body slab, but also retains
    exterior tetrahedra near the gap rim -- the slab has no crisp graph boundary).

    Returns a dict with ``core_tetrahedron_ids`` (the survivors) and
    ``raft_tetrahedron_ids`` (the peeled pendants).
    """

    raw = topography.dfnd.raw
    component = next(
        (c for c in raw['wet_components'] if c['id'] == component_id), None
    )
    if component is None:
        raise ValueError(f'no wet component with id {component_id!r}')

    resident_ids = {int(t) for t in (component.get('resident_tetrahedron_ids') or [])}
    graph = _resident_permeable_graph(raw, resident_ids)

    peeled: set[int] = set()
    changed = True
    while changed:
        changed = False
        for node in list(graph.nodes):
            if graph.degree(node) <= max_pendant_degree:
                graph.remove_node(node)
                peeled.add(node)
                changed = True

    return {
        'component_id': component_id,
        'core_tetrahedron_ids': sorted(graph.nodes),
        'raft_tetrahedron_ids': sorted(peeled),
        'n_rafts_peeled': len(peeled),
    }
