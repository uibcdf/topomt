from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class FpocketPocket:
    pocket_id: int
    file_pocket_id: int
    atom_serials: list[int] = field(default_factory=list)
    center: np.ndarray | None = None
    score: float | None = None
    druggability_score: float | None = None
    n_alpha_spheres: int | None = None
    mean_alpha_sphere_radius: float | None = None
    mean_alpha_sphere_sasa: float | None = None
    mean_b_factor: float | None = None
    hydrophobicity_score: float | None = None
    polarity_score: float | None = None
    volume_score: float | None = None
    volume: float | None = None
    convex_hull_volume: float | None = None
    charge_score: float | None = None
    local_hydrophobic_density_score: float | None = None
    n_apolar_alpha_spheres: int | None = None
    apolar_alpha_sphere_ratio: float | None = None
    alpha_sphere_centers: np.ndarray | None = None
    alpha_sphere_radii: np.ndarray | None = None
    alpha_sphere_types: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class FpocketResult:
    source_pdb: Path
    output_dir: Path
    pockets: list[FpocketPocket] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:

        pockets = []
        for pocket in self.pockets:
            pockets.append(
                {
                    'pocket_id': pocket.pocket_id,
                    'file_pocket_id': pocket.file_pocket_id,
                    'atom_serials': pocket.atom_serials,
                    'center': None if pocket.center is None else pocket.center.tolist(),
                    'score': pocket.score,
                    'druggability_score': pocket.druggability_score,
                    'n_alpha_spheres': pocket.n_alpha_spheres,
                    'mean_alpha_sphere_radius': pocket.mean_alpha_sphere_radius,
                    'mean_alpha_sphere_sasa': pocket.mean_alpha_sphere_sasa,
                    'mean_b_factor': pocket.mean_b_factor,
                    'hydrophobicity_score': pocket.hydrophobicity_score,
                    'polarity_score': pocket.polarity_score,
                    'volume_score': pocket.volume_score,
                    'volume': pocket.volume,
                    'convex_hull_volume': pocket.convex_hull_volume,
                    'charge_score': pocket.charge_score,
                    'local_hydrophobic_density_score': pocket.local_hydrophobic_density_score,
                    'n_apolar_alpha_spheres': pocket.n_apolar_alpha_spheres,
                    'apolar_alpha_sphere_ratio': pocket.apolar_alpha_sphere_ratio,
                    'alpha_sphere_centers': None if pocket.alpha_sphere_centers is None else pocket.alpha_sphere_centers.tolist(),
                    'alpha_sphere_radii': None if pocket.alpha_sphere_radii is None else pocket.alpha_sphere_radii.tolist(),
                    'alpha_sphere_types': pocket.alpha_sphere_types,
                    'raw': pocket.raw,
                }
            )

        return {
            'source_pdb': str(self.source_pdb),
            'output_dir': str(self.output_dir),
            'pockets': pockets,
            'metadata': self.metadata,
        }
