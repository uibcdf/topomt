import warnings
import numpy as np
import molsysmt as msm
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial import ConvexHull

from topomt import Topography
from topomt.alpha_spheres import AlphaSpheres
from topomt._private.puw_utils import get_magnitude, get_magnitudes


_LINKAGE_MAP = {
    's': 'single',
    'm': 'complete',
    'a': 'average',
    'c': 'centroid',
}

_METRIC_MAP = {
    'e': 'euclidean',
    'b': 'cityblock',
    'c': 'correlation',
}


def fpocket4(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    min_radius: str = '3.4 angstroms',
    max_radius: str = '6.2 angstroms',
    clust_cut_dist: str = '2.4 angstroms',
    linkage_method: str = 's',
    distance_metric: str = 'e',
    min_pock_nb_asph: int = 15,
    apolar_min_ratio: float | None = None,
    min_density: float | None = 0.7,
    pbc: bool = False,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    Native FPocket4-like pipeline using HAC. logic in NM.
    """
    topo = Topography(molecular_system=molecular_system, structure_indices=structure_indices)
    molsys = topo._molsys

    # Safe normalization to NM
    min_radius_val = get_magnitude(min_radius, unit='nm')
    max_radius_val = get_magnitude(max_radius, unit='nm')
    cut_val = get_magnitude(clust_cut_dist, unit='nm')

    # Adimensional parameters
    apolar_min_ratio_val = get_magnitude(apolar_min_ratio) if apolar_min_ratio is not None else None
    min_density_val = get_magnitude(min_density) if min_density is not None else None

    # System Selection
    atom_indices = msm.select(molecular_system=molsys, selection=selection, syntax=syntax)
    remove_idx = msm.select(
        molecular_system=molsys,
        selection="group_type in ['water', 'ion', 'small molecule']",
        mask=atom_indices, syntax='MolSysMT',
    )
    if len(remove_idx) > 0:
        atom_indices = [idx for idx in atom_indices if idx not in remove_idx]

    atom_indices = msm.select(
        molecular_system=molsys,
        selection='atom_type not in ["H"]',
        mask=atom_indices, syntax='MolSysMT',
    )

    coords = msm.get(
        molecular_system=molsys,
        selection=atom_indices,
        structure_indices=structure_indices,
        coordinates=True,
    )[0]
    coords_nm = get_magnitudes(coords, unit='nm')

    # Alpha Spheres generation
    alpha = AlphaSpheres(points=coords_nm, radii=None)
    alpha.remove_small_alpha_spheres(min_radius_val)
    alpha.remove_big_alpha_spheres(max_radius_val)

    n_as = alpha.centers.shape[0]
    if n_as < 2:
        return topo

    # Clustering
    link = _LINKAGE_MAP.get(linkage_method.lower(), 'single')
    metric = _METRIC_MAP.get(distance_metric.lower(), 'euclidean')

    D = pdist(alpha.centers, metric=metric)
    Z = linkage(D, method=link)
    labels = fcluster(Z, t=cut_val, criterion='distance')

    pockets_dict: dict[int, list[int]] = {}
    for lab in np.unique(labels):
        comp = np.where(labels == lab)[0].tolist()
        pockets_dict.setdefault(int(lab), []).extend(comp)

    pockets_raw = [sorted(set(c)) for c in pockets_dict.values()]

    # Descriptors and Filtering
    descriptors = _compute_descriptors_for_pockets(alpha, pockets_raw, apolar_min_ratio_val)
    pockets_filtered, descriptors = _filter_pockets(
        pockets_raw,
        descriptors,
        min_pock_nb_asph=min_pock_nb_asph,
        min_density=min_density_val,
        apolar_min_ratio=apolar_min_ratio_val,
    )

    # Populate Topography
    from topomt.features.Pocket import Pocket
    for comp, desc in zip(pockets_filtered, descriptors):
        atom_indices_local = set()
        for as_idx in comp:
            atom_indices_local.update(alpha.points_of_alpha_sphere[as_idx])
        pocket_atom_indices = [atom_indices[idx] for idx in atom_indices_local]
            
        pocket_feature = Pocket(
            atom_indices=sorted(pocket_atom_indices),
            center=desc['center'],
            volume=desc.get('volume', 0.0),
            score=desc['score']
        )
        topo.add_feature(pocket_feature)

    return topo


def _compute_descriptors_for_pockets(alpha: AlphaSpheres, pockets: list[list[int]], apolar_min_ratio: float | None):
    descriptors: list[dict[str, float]] = []
    for comp in pockets:
        centers = alpha.centers[np.array(comp, int)]
        radii_vals = alpha.radii[np.array(comp, int)]
        n_as = len(comp)
        centroid = np.mean(centers, axis=0) if n_as > 0 else np.zeros(3)

        volume = 0.0
        density = 0.0
        if n_as >= 4:
            try:
                hull = ConvexHull(centers)
                volume = float(hull.volume)
                if volume > 0:
                    density = n_as / volume
            except Exception: pass

        mean_radius = float(np.mean(radii_vals))
        max_radius = float(np.max(radii_vals))
        score = n_as * (density if density > 0 else 1.0)

        descriptors.append(
            {
                'n_alpha_spheres': n_as,
                'center': centroid,
                'mean_radius': mean_radius,
                'max_radius': max_radius,
                'volume': volume,
                'density': density,
                'score': score,
                'apolar_ratio': None # Placeholder
            }
        )
    return descriptors


def _filter_pockets(pockets, descriptors, *, min_pock_nb_asph, min_density, apolar_min_ratio):
    filtered_pockets = []
    filtered_desc = []
    for comp, desc in zip(pockets, descriptors):
        if desc['n_alpha_spheres'] < min_pock_nb_asph: continue
        if min_density is not None and desc['density'] < min_density: continue
        filtered_pockets.append(comp)
        filtered_desc.append(desc)
    return filtered_pockets, filtered_desc
