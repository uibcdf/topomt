"""Tests for pocket contact helpers in topomt.tools.features."""

import numpy as np

from topomt.tools.features.pockets import (
    ligand_contact_distances,
    ligand_contact_mask,
    probe_scoring,
    sasa_contact_validation,
)


def test_ligand_contact_distances_returns_summary():

    pocket_points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=float)
    ligand_coords = np.array([[0.0, 0.0, 2.0]], dtype=float)

    result = ligand_contact_distances(pocket_points, ligand_coords)

    assert result['min'] == 2.0
    assert result['max'] == np.sqrt(5.0)
    assert result['mean'] == np.mean([2.0, np.sqrt(5.0)])


def test_ligand_contact_mask_marks_close_vertices():

    vertices = np.array([[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]], dtype=float)
    ligand_coords = np.array([[0.5, 0.0, 0.0]], dtype=float)

    mask = ligand_contact_mask(vertices, ligand_coords, hit_dist=1.0)

    assert mask.dtype == bool
    assert mask.tolist() == [True, False]


def test_sasa_contact_validation_counts_contacts():

    pocket_coords = np.array([[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]], dtype=float)
    ligand_coords = np.array([[1.0, 0.0, 0.0]], dtype=float)

    result = sasa_contact_validation(
        pocket_coords,
        ligand_coords,
        atom_radii=0.5,
        probe_radius=1.4,
        contact_threshold=0.2,
    )

    assert result['n_contact'] == 1
    assert result['fraction'] == 0.5


def test_probe_scoring_returns_weighted_scores():

    vertices = np.array([[0.0, 0.0, 0.0]], dtype=float)
    ligand_coords = np.array([[1.0, 0.0, 0.0]], dtype=float)

    scores = probe_scoring(vertices, ligand_coords, probe_weights={'C': 1.0, 'N': 0.5}, cutoff=2.0)

    assert set(scores.keys()) == {'C', 'N'}
    assert scores['C'] > scores['N'] > 0.0
