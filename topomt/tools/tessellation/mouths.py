"""Mouth and boundary-face helpers over simplices."""

from collections.abc import Sequence

import numpy as np

from topomt.tools.geometry.primitives import triangle_area


def mouth_area_from_faces(
    faces: Sequence[tuple[int, int, int]],
    atom_coords: np.ndarray,
) -> float:
    """Compute the total area of triangular faces."""

    total_area = 0.0
    if not faces:
        return 0.0

    for face in faces:
        points = atom_coords[list(face)]
        total_area += triangle_area(points)

    return float(total_area)


def mouth_metrics_from_tetrahedra(
    pocket_indices: Sequence[int],
    simplices: np.ndarray,
    atom_coords: np.ndarray,
) -> dict:
    """Compute mouth descriptors from simplex boundary faces."""

    face_count = {}
    for idx in pocket_indices:
        atoms = simplices[idx]
        faces = [
            tuple(sorted((atoms[0], atoms[1], atoms[2]))),
            tuple(sorted((atoms[0], atoms[1], atoms[3]))),
            tuple(sorted((atoms[0], atoms[2], atoms[3]))),
            tuple(sorted((atoms[1], atoms[2], atoms[3]))),
        ]
        for face in faces:
            face_count[face] = face_count.get(face, 0) + 1

    boundary_faces = [face for face, count in face_count.items() if count == 1]
    total_area = mouth_area_from_faces(boundary_faces, atom_coords)

    total_perimeter = 0.0
    rim_atoms = set()
    centroids = []
    for face in boundary_faces:
        points = atom_coords[list(face)]
        centroids.append(points.mean(axis=0))
        edges = [(face[i], face[j]) for i, j in ((0, 1), (1, 2), (2, 0))]
        total_perimeter += sum(
            np.linalg.norm(atom_coords[source] - atom_coords[target])
            for source, target in edges
        )
        rim_atoms.update(face)

    mouth_center = np.mean(centroids, axis=0) if centroids else np.zeros(3)
    return {
        'mouth_area': float(total_area),
        'mouth_perimeter': float(total_perimeter),
        'rim_atoms': list(rim_atoms),
        'mouth_center': mouth_center,
    }
