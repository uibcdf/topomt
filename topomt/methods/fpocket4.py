import warnings
import numpy as np
import molsysmt as msm
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial import ConvexHull

from topomt import Topography
from topomt.alpha_spheres import AlphaSpheres
from topomt import pyunitwizard as puw
from topomt._private.digestion import digest


_LINKAGE_MAP = {
    's': 'single',    # single-linkage
    'm': 'complete',  # maximum/complete-linkage
    'a': 'average',   # average-linkage (UPGMA)
    'c': 'centroid',  # centroid-linkage
}

_METRIC_MAP = {
    'e': 'euclidean',
    'b': 'cityblock',
    'c': 'correlation',
    # Otros códigos del help (a,u,x,s,k) no son apropiados para coords 3D de esferas;
    # si se pasan, caemos a 'euclidean' con aviso.
}


@digest()
def fpocket4(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    # Radios por defecto (FPocket4)
    min_radius: str = '3.4 angstroms',
    max_radius: str = '6.2 angstroms',
    # Corte del dendrograma (equivale al -D de FP4)
    clust_cut_dist: str = '2.4 angstroms',
    # Método de enlace (-C) y métrica (-e)
    linkage_method: str = 's',   # 's'|'m'|'a'|'c'
    distance_metric: str = 'e',  # 'e'|'b'|'c' (euclidean default)
    # Filtros finales
    min_pock_nb_asph: int = 15,      # -i 15
    apolar_min_ratio: float | None = None,  # FP4 por defecto desactiva filtro (0.0 en help => keep all)
    min_density: float | None = 0.7,  # ~M_MIN_AS_DENSITY
    # Varios
    pbc: bool = False,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    FPocket4-like pipeline usando HAC:
      1) Genera alfa-esferas y filtra por radios [min_radius, max_radius].
      2) Construye matriz de distancias entre centros de alfa-esferas (métrica -e).
      3) HAC con método de enlace -C; corta dendrograma a distancia clust_cut_dist (-D).
      4) Filtra bolsillos por tamaño mínimo (>= min_pock_nb_asph) y, opcionalmente, por fracción apolar.
    Devuelve: lista de listas de índices de alfa-esferas por pocket.
    """
    # --- Selección y limpieza básica (sin aguas/iones/small, sin H) ---
    topo = Topography(molecular_system=molecular_system, structure_indices=structure_indices)
    molsys = topo._molsys

    atom_indices = msm.select(molecular_system=molsys, selection=selection, syntax=syntax)
    remove_idx = msm.select(
        molecular_system=molsys,
        selection="group_type in ['water', 'ion', 'small molecule']",
        mask=atom_indices, syntax='MolSysMT',
    )
    if len(remove_idx) > 0:
        atom_indices = list(set(atom_indices) - set(remove_idx))

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

    # --- Alfa-esferas + filtros de radio ---
    alpha = AlphaSpheres(points=coords, radii=None)
    alpha.remove_small_alpha_spheres(min_radius)
    alpha.remove_big_alpha_spheres(max_radius)

    n_as = alpha.centers.shape[0]
    if n_as == 0:
        return []
    if n_as == 1:
        return [[]] if min_pock_nb_asph <= 1 else []

    # --- Métrica y método de enlace ---
    link = _LINKAGE_MAP.get(linkage_method.lower(), None)
    if link is None:
        warnings.warn(f"linkage_method '{linkage_method}' no reconocido; usando 'single'.")
        link = 'single'

    metric = _METRIC_MAP.get(distance_metric.lower(), None)
    if metric is None:
        warnings.warn(f"distance_metric '{distance_metric}' no apropiada para coords 3D; usando 'euclidean'.")
        metric = 'euclidean'

    # --- Distancias y corte en unidades coherentes ---
    centers_vals, centers_unit = puw.get_value_and_unit(alpha.centers)
    cut_val = puw.get_value(clust_cut_dist, to_unit=centers_unit)

    # pdist exige ndarray float (sin unidades)
    D = pdist(centers_vals, metric=metric)

    # SciPy: 'centroid' requiere euclidiana; avisamos si no cuadra
    if link == 'centroid' and metric != 'euclidean':
        warnings.warn("Centroid linkage requiere distancia euclídea; forzando 'euclidean'.")
        D = pdist(centers_vals, metric='euclidean')

    # --- Clustering jerárquico y corte por distancia ---
    Z = linkage(D, method=link)
    # criterion='distance' => umbral directo en la misma unidad que D (centers_unit)
    labels = fcluster(Z, t=cut_val, criterion='distance')

    # Agrupar índices por etiqueta
    pockets_dict: dict[int, list[int]] = {}
    for lab in np.unique(labels):
        comp = np.where(labels == lab)[0].tolist()
        # aplicar fusión estilo apply_clustering: si el mismo label aparece, se acumula
        pockets_dict.setdefault(int(lab), []).extend(comp)

    # fusionar duplicados y normalizar
    pockets = []
    for comp in pockets_dict.values():
        merged = sorted(set(comp))
        pockets.append(merged)

    # --- Calcular descriptores y aplicar filtros (tamaño, densidad, apolaridad) ---
    descriptors = _compute_descriptors_for_pockets(alpha, pockets, apolar_min_ratio)
    pockets, descriptors = _filter_pockets(
        pockets,
        descriptors,
        min_pock_nb_asph=min_pock_nb_asph,
        min_density=min_density,
        apolar_min_ratio=apolar_min_ratio,
    )

    # --- Reindexar/ordenar por score (aproxima el reIndex + sort de FPocket) ---
    pockets_with_scores = list(zip(pockets, descriptors))
    pockets_with_scores.sort(key=lambda x: x[1]['score'], reverse=True)
    pockets = [p for p, _ in pockets_with_scores]

    return pockets


def _compute_descriptors_for_pockets(alpha: AlphaSpheres, pockets: list[list[int]], apolar_min_ratio: float | None):
    """Compute simple geometric and apolar descriptors for each pocket."""
    descriptors: list[dict[str, float]] = []
    ap_mask = getattr(alpha, 'is_apolar', None)
    types = getattr(alpha, 'types', None) if ap_mask is None else None

    for comp in pockets:
        centers = puw.get_value(alpha.centers[np.array(comp, int)])
        radii_vals = puw.get_value(alpha.radii[np.array(comp, int)])
        n_as = len(comp)

        volume = None
        surface = None
        density = 0.0
        if n_as >= 4:
            try:
                hull = ConvexHull(centers)
                volume = float(hull.volume)
                surface = float(hull.area)
                if volume > 0:
                    density = n_as / volume
            except Exception:
                volume = None
                surface = None
                density = 0.0

        mean_radius = float(np.mean(radii_vals)) if n_as > 0 else 0.0
        max_radius = float(np.max(radii_vals)) if n_as > 0 else 0.0

        apolar_ratio = None
        if apolar_min_ratio is not None:
            if ap_mask is not None:
                apolar_ratio = float(np.sum(ap_mask[np.array(comp, int)])) / n_as
            elif types is not None:
                apolar_ratio = float(np.sum(types[np.array(comp, int)] == 1)) / n_as

        # Proxy de score: tamaño ponderado por densidad (similar a ordenar por tamaño y densidad)
        score = n_as * (density if density > 0 else 1.0)

        descriptors.append(
            {
                'n_alpha_spheres': n_as,
                'mean_radius': mean_radius,
                'max_radius': max_radius,
                'volume': volume,
                'surface': surface,
                'density': density,
                'apolar_ratio': apolar_ratio,
                'score': score,
            }
        )

    return descriptors


def _filter_pockets(
    pockets: list[list[int]],
    descriptors: list[dict[str, float]],
    *,
    min_pock_nb_asph: int,
    min_density: float | None,
    apolar_min_ratio: float | None,
):
    """Apply size, density, and apolar filters akin to FPocket refine step."""
    filtered_pockets: list[list[int]] = []
    filtered_desc: list[dict[str, float]] = []

    for comp, desc in zip(pockets, descriptors):
        if desc['n_alpha_spheres'] < min_pock_nb_asph:
            continue
        if min_density is not None and desc['density'] < min_density:
            continue
        if apolar_min_ratio is not None:
            if desc['apolar_ratio'] is None:
                warnings.warn('AlphaSpheres no expone tipado apolar; se omite filtro apolar.')
            else:
                if desc['apolar_ratio'] < apolar_min_ratio:
                    continue
        filtered_pockets.append(comp)
        filtered_desc.append(desc)

    return filtered_pockets, filtered_desc
