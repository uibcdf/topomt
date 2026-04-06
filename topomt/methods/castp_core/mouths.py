"""Mouth detection helpers for the native CASTp implementation."""

from collections import defaultdict


def cluster_mouth_faces(faces: list[tuple[int, int, int]]) -> list[list[tuple[int, int, int]]]:
    """Group face triples into mouth clusters by shared edges."""

    if not faces:
        return []

    edge_to_face_indices: dict[tuple[int, int], list[int]] = defaultdict(list)
    for face_index, face in enumerate(faces):
        edges = (
            tuple(sorted((face[0], face[1]))),
            tuple(sorted((face[0], face[2]))),
            tuple(sorted((face[1], face[2]))),
        )
        for edge in edges:
            edge_to_face_indices[edge].append(face_index)

    face_adjacency = [[] for _ in range(len(faces))]
    for face_indices in edge_to_face_indices.values():
        for index, source in enumerate(face_indices):
            for target in face_indices[index + 1 :]:
                face_adjacency[source].append(target)
                face_adjacency[target].append(source)

    visited = [False] * len(faces)
    clusters = []
    for seed in range(len(faces)):
        if visited[seed]:
            continue
        stack = [seed]
        visited[seed] = True
        cluster = []
        while stack:
            current = stack.pop()
            cluster.append(faces[current])
            for neighbor in face_adjacency[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
        clusters.append(cluster)

    return clusters
