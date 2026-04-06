"""Reusable discrete-flow helpers on tetrahedral tessellations."""

from collections import defaultdict, deque

import numpy as np


def build_open_neighbor_dict(
    mesh,
    open_mask: np.ndarray,
    face_radii: dict[tuple[int, int, int], float] | None = None,
    probe_radius: float | None = None,
) -> dict[int, list[int]]:
    """Return simplex adjacency restricted to open simplices and open faces."""

    simplex_indices = np.where(open_mask)[0]
    neighbor_dict = {int(index): [] for index in simplex_indices}
    for simplex_index in simplex_indices:
        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if neighbor == -1 or not open_mask[int(neighbor)]:
                continue
            if face_radii is not None and probe_radius is not None:
                face_key = mesh.get_face_atoms(simplex_index, face_index)
                face_radius = face_radii[face_key]
                if face_radius < probe_radius:
                    continue
            neighbor_dict[int(simplex_index)].append(int(neighbor))
    return neighbor_dict


def flow_targets_to_sinks(
    proxy_values: np.ndarray,
    neighbor_dict: dict[int, list[int]],
    tol_fraction: float = 0.01,
) -> dict[int, int]:
    """Map each simplex to the local sink reached by discrete descent."""

    flow_target = {}
    for simplex_index in neighbor_dict:
        current = int(simplex_index)
        current_proxy = float(proxy_values[current])
        visited = {current}

        while True:
            lower_neighbors = [
                neighbor
                for neighbor in neighbor_dict[current]
                if (current_proxy - float(proxy_values[neighbor])) > tol_fraction * max(current_proxy, 1e-12)
            ]
            if not lower_neighbors:
                break

            next_current = min(lower_neighbors, key=lambda neighbor: float(proxy_values[neighbor]))
            if next_current in visited:
                break

            current = int(next_current)
            current_proxy = float(proxy_values[current])
            visited.add(current)

        flow_target[int(simplex_index)] = current

    return flow_target


def group_by_flow_sink(
    flow_target: dict[int, int],
    neighbor_dict: dict[int, list[int]],
) -> dict[int, list[int]]:
    """Split simplices into connectivity-preserving sink groups."""

    sink_groups: dict[int, list[int]] = defaultdict(list)
    for simplex_index, sink in flow_target.items():
        sink_groups[int(sink)].append(int(simplex_index))

    final_components: dict[int, list[int]] = {}
    component_index = 0
    for grouped_simplices in sink_groups.values():
        grouped_set = set(grouped_simplices)
        visited = set()
        for seed in grouped_simplices:
            if seed in visited:
                continue
            stack = [seed]
            component = []
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                for neighbor in neighbor_dict[current]:
                    if neighbor in grouped_set and neighbor not in visited:
                        stack.append(neighbor)
            final_components[component_index] = sorted(component)
            component_index += 1

    return final_components


def flow_components(
    mesh,
    open_mask: np.ndarray,
    face_radii: dict[tuple[int, int, int], float],
    probe_radius: float,
    proxy_values: np.ndarray,
    tol_fraction: float = 0.01,
) -> dict[int, list[int]]:
    """Return components induced by discrete flow toward local sinks."""

    simplex_indices = np.where(open_mask)[0]
    if simplex_indices.size == 0:
        return {}

    neighbor_dict = build_open_neighbor_dict(
        mesh,
        open_mask,
        face_radii,
        probe_radius,
    )
    flow_target = flow_targets_to_sinks(
        proxy_values=np.asarray(proxy_values, dtype=float),
        neighbor_dict=neighbor_dict,
        tol_fraction=tol_fraction,
    )
    return group_by_flow_sink(flow_target, neighbor_dict)


def build_descending_flow_graph(
    proxy_values: np.ndarray,
    neighbor_dict: dict[int, list[int]],
    epsilon: float = 1e-12,
) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    """Build directed descending flow adjacency and its reverse graph."""

    forward_graph = {int(node): [] for node in neighbor_dict}
    reverse_graph = {int(node): [] for node in neighbor_dict}

    for source, neighbors in neighbor_dict.items():
        source_value = float(proxy_values[source])
        for target in neighbors:
            target_value = float(proxy_values[target])
            if source_value > target_value + epsilon:
                forward_graph[int(source)].append(int(target))
                reverse_graph[int(target)].append(int(source))

    return forward_graph, reverse_graph


def ancestors_of_exterior(
    reverse_graph: dict[int, list[int]],
    exterior_nodes: list[int] | set[int],
) -> set[int]:
    """Return all nodes that can flow to the exterior."""

    visited = set(int(node) for node in exterior_nodes)
    queue = deque(int(node) for node in exterior_nodes)

    while queue:
        current = queue.popleft()
        for ancestor in reverse_graph.get(current, []):
            if ancestor not in visited:
                visited.add(int(ancestor))
                queue.append(int(ancestor))

    return visited
