"""Pocket-ligand contact helpers."""

import numpy as np
from scipy.spatial.distance import cdist


def ligand_contact_distances(
    pocket_points: np.ndarray,
    ligand_coords: np.ndarray,
) -> dict[str, float | None]:
    """Return min/mean/max distances between pocket points and ligand coordinates."""

    if pocket_points.size == 0 or ligand_coords.size == 0:
        return {'min': None, 'mean': None, 'max': None}

    distances = cdist(pocket_points, ligand_coords)
    return {
        'min': float(distances.min()),
        'mean': float(distances.mean()),
        'max': float(distances.max()),
    }


def ligand_contact_mask(vertices: np.ndarray, ligand_coords: np.ndarray, hit_dist: float) -> np.ndarray:
    """Return a boolean mask selecting vertices within ``hit_dist`` of a ligand atom."""

    if len(vertices) == 0 or len(ligand_coords) == 0:
        return np.zeros(len(vertices), dtype=bool)

    distances = cdist(vertices, ligand_coords)
    return np.min(distances, axis=1) < hit_dist


def sasa_contact_validation(
    pocket_coords: np.ndarray,
    ligand_coords: np.ndarray,
    atom_radii: np.ndarray | float | None = None,
    probe_radius: float = 1.4,
    contact_threshold: float = 1.0,
) -> dict[str, float]:
    """Return a distance-based proxy for ligand contact under a SASA-style rule."""

    if pocket_coords.size == 0 or ligand_coords.size == 0:
        return {'n_contact': 0, 'fraction': 0.0}

    pocket_coords = np.asarray(pocket_coords, dtype=float)
    ligand_coords = np.asarray(ligand_coords, dtype=float)
    n_atoms = pocket_coords.shape[0]

    if atom_radii is None:
        radii = np.zeros(n_atoms, dtype=float)
    elif np.isscalar(atom_radii):
        radii = np.full(n_atoms, float(atom_radii))
    else:
        radii = np.asarray(atom_radii, dtype=float)
        if radii.shape[0] != n_atoms:
            raise ValueError('atom_radii length must match pocket_coords')

    distances = cdist(pocket_coords, ligand_coords)
    min_distance = distances.min(axis=1)
    contact_mask = min_distance < (radii + probe_radius + contact_threshold)
    n_contact = int(contact_mask.sum())
    fraction = float(n_contact / n_atoms) if n_atoms else 0.0
    return {'n_contact': n_contact, 'fraction': fraction}


def probe_scoring(
    vertices: np.ndarray,
    ligand_coords: np.ndarray,
    probe_weights: dict[str, float] | None = None,
    cutoff: float = 6.0,
    power: float = 2.0,
) -> dict[str, float]:
    """Return a simple distance-decay probe score against ligand coordinates."""

    if probe_weights is None:
        probe_weights = {'C': 1.0, 'N': 0.8, 'O': 0.7, 'X': 1.0}

    if vertices.size == 0 or ligand_coords.size == 0:
        return {key: 0.0 for key in probe_weights}

    distances = cdist(vertices, ligand_coords)
    eps = 1e-6
    inv = (cutoff / np.maximum(distances, eps)) ** power
    inv[distances > cutoff] = 0.0
    base_score = inv.sum()
    return {key: float(weight * base_score) for key, weight in probe_weights.items()}
