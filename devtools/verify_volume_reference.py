"""Independent Cartesian volume sampling on frozen finite carrier domains.

No TopoMT module, numerical integrator, sample, estimate or interval is imported.
The statistical bound is conditional on IID sampling and the declared geometry;
floating membership tests are not interval-arithmetic proofs.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from devtools.verify_closed_shell_wall_cover import _values

HOEFFDING_REFERENCE = {
    'title': 'Probability Inequalities for Sums of Bounded Random Variables',
    'authors': ['Wassily Hoeffding'],
    'year': 1963,
    'journal': 'Journal of the American Statistical Association',
    'volume': '58',
    'issue': '301',
    'pages': '13-30',
    'doi': '10.1080/01621459.1963.10500830',
    'url': 'https://doi.org/10.1080/01621459.1963.10500830',
}


def inside_union(points: np.ndarray, cells: np.ndarray) -> np.ndarray:
    """Return direct barycentric membership in a finite tetrahedron union.

    Parameters
    ----------
    points, cells : numpy.ndarray
        Shapes (N,3) and (K,4,3), in the same explicit caller-declared unit.

    Returns
    -------
    numpy.ndarray
        Boolean union membership, without double-counting overlapping cells.

    Raises
    ------
    ValueError
        A cell is degenerate or too ill-conditioned for this reference.
    """
    included = np.zeros(len(points), dtype=bool)
    for cell in cells:
        basis = (cell[1:] - cell[0]).T
        if np.linalg.cond(basis) > 1e12:
            raise ValueError('Unqualified degenerate/ill-conditioned reference cell')
        eligible = (
            (~included)
            & np.all(points >= cell.min(axis=0), axis=1)
            & np.all(points <= cell.max(axis=0), axis=1)
        )
        ids = np.flatnonzero(eligible)
        if not len(ids):
            continue
        bary = (points[ids] - cell[0]) @ np.linalg.inv(basis).T
        included[ids] = np.all(bary >= 0.0, axis=1) & (bary.sum(axis=1) <= 1.0)
    return included


def free_at_probes(
    points: np.ndarray, centers: np.ndarray, radii: np.ndarray, probe: float
) -> tuple[np.ndarray, np.ndarray]:
    """Return all-atom bare and expanded-ball free masks in a common length unit.

    The caller bounds the point batch; all input atoms participate. No local
    vertex-ball proxy or independent sphere-volume subtraction is used.
    """
    if not len(centers):
        return np.ones(len(points), dtype=bool), np.ones(len(points), dtype=bool)
    squared = np.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2)
    return np.all(squared > radii**2, axis=1), np.all(
        squared > (radii + probe) ** 2, axis=1
    )


def hoeffding_interval(
    count: int,
    samples: int,
    box_volume: float,
    confidence: float,
    geometric_upper: float,
) -> tuple[float, float, float]:
    """Return a two-sided bounded-IID confidence interval scaled by box volume.

    Parameters
    ----------
    count, samples : int
        Indicator successes and positive sample count.
    box_volume, geometric_upper : float
        Bounding-box volume and an independently known geometric upper volume.
    confidence : float
        Per-observable confidence strictly between zero and one.

    Returns
    -------
    tuple of float
        Clipped lower/upper bounds and the unclipped statistical half-width.

    Raises
    ------
    ValueError
        Counts, confidence or volumes are invalid.
    """
    if (
        not 0 <= count <= samples
        or samples < 1
        or not 0 < confidence < 1
        or not np.isfinite([box_volume, geometric_upper]).all()
        or box_volume <= 0
        or geometric_upper < 0
    ):
        raise ValueError('Invalid Cartesian reference interval controls')
    half_width = box_volume * np.sqrt(np.log(2 / (1 - confidence)) / (2 * samples))
    estimate = box_volume * count / samples
    return (
        max(0.0, float(estimate - half_width)),
        min(geometric_upper, float(estimate + half_width)),
        float(half_width),
    )


def regular_vertex_sector_volume(
    vertices: np.ndarray, radii: np.ndarray
) -> dict[str, float]:
    """Evaluate bare regular-tetrahedron vertex sectors after checking hypotheses.

    Parameters
    ----------
    vertices, radii : numpy.ndarray
        Four centers and equal nonnegative radii, in a common length unit.

    Returns
    -------
    dict
        Edge, solid angle, carrier/empty volume and geometric validity margins.

    Raises
    ------
    ValueError
        The tetrahedron is irregular or the sectors overlap/are truncated.
    """
    from itertools import combinations

    edges = np.array(
        [
            np.linalg.norm(vertices[i] - vertices[j])
            for i, j in combinations(range(4), 2)
        ]
    )
    edge, radius = float(edges[0]), float(radii[0])
    if not np.allclose(edges, edge, rtol=0.0, atol=1e-11) or not np.all(
        radii == radius
    ):
        raise ValueError('The reference requires equal edges and vertex radii')
    if radius < 0 or edge - 2 * radius <= 1e-12:
        raise ValueError('Vertex ball sectors overlap or lack a strict margin')
    altitude = edge * np.sqrt(2 / 3)
    if altitude - radius <= 1e-12:
        raise ValueError('Vertex ball sectors reach an opposite face')
    omega = 3 * np.arccos(1 / 3) - np.pi
    carrier = edge**3 / (6 * np.sqrt(2))
    return {
        'edge': edge,
        'radius': radius,
        'solid_angle': float(omega),
        'carrier_volume': float(carrier),
        'empty_volume': float(carrier - 4 * omega * radius**3 / 3),
        'pair_nonoverlap_margin': edge - 2 * radius,
        'opposite_face_margin': float(altitude - radius),
    }


def integrate_domain(
    cells: np.ndarray,
    centers: np.ndarray,
    radii: np.ndarray,
    probe: float,
    *,
    n_samples: int,
    seed: int,
    confidence: float,
    batch_size: int,
) -> dict[str, Any]:
    """Independently sample Cartesian support/ball indicators in bounded batches.

    Parameters
    ----------
    cells, centers, radii : numpy.ndarray
        Frozen disjoint-interior cells and all atom balls in explicit nm units.
    probe : float
        Probe expansion in nm; zero gives the bare exclusion model.
    n_samples, seed, batch_size : int
        Frozen positive count, random seed and positive point-batch ceiling.
    confidence : float
        Per-observable Hoeffding confidence; no joint panel claim is implied.

    Returns
    -------
    dict
        Counts, volume intervals, sample digest and explicit numerical scope.

    Raises
    ------
    ValueError
        Geometry/budgets are invalid or membership is ill-conditioned.
    """
    if len(cells) == 0 or min(n_samples, batch_size) < 1 or probe < 0:
        raise ValueError(
            'A nonempty finite domain and valid sampling controls are required'
        )
    low, high = cells.reshape(-1, 3).min(axis=0), cells.reshape(-1, 3).max(axis=0)
    box_volume = float(np.prod(high - low))
    vectors = cells[:, 1:, :] - cells[:, 0:1, :]
    carrier = float(
        np.sum(
            np.abs(
                np.einsum(
                    'ij,ij->i', vectors[:, 0], np.cross(vectors[:, 1], vectors[:, 2])
                )
            )
        )
        / 6
    )
    counts = {'carrier': 0, 'bare_empty': 0, 'probe_center': 0}
    rng = np.random.default_rng(seed)
    digest = hashlib.sha256()
    # This also bounds point/atom temporaries independently of production code.
    batch_size = min(batch_size, max(1, 262144 // max(1, len(centers))))
    for start in range(0, n_samples, batch_size):
        points = rng.uniform(low, high, size=(min(batch_size, n_samples - start), 3))
        mask = inside_union(points, cells)
        bare, expanded = free_at_probes(points, centers, radii, probe)
        digest.update(np.ascontiguousarray(points, dtype='<f8').tobytes())
        for key, selected in [
            ('carrier', mask),
            ('bare_empty', mask & bare),
            ('probe_center', mask & expanded),
        ]:
            counts[key] += int(np.count_nonzero(selected))
            digest.update(np.packbits(selected).tobytes())
    result: dict[str, Any] = {
        'length_unit': 'nm',
        'volume_unit': 'nm**3',
        'carrier_volume': carrier,
        'box_volume': box_volume,
        'n_samples': n_samples,
        'seed': seed,
        'confidence_level': confidence,
        'confidence_scope': 'Per observable, conditional on IID sampling and the fixed geometry; floating membership is not a formal interval proof',
        'sample_and_membership_sha256': digest.hexdigest(),
        'criterion': HOEFFDING_REFERENCE,
    }
    for key, count in counts.items():
        lower, upper, half_width = hoeffding_interval(
            count, n_samples, box_volume, confidence, carrier
        )
        result[key] = {
            'count': count,
            'estimate': box_volume * count / n_samples,
            'interval': [lower, upper],
            'unclipped_half_width': half_width,
            'half_width_over_carrier': half_width / carrier,
        }
    return result


def load_domains(
    input_file: Path, protocol_file: Path
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    """Restore source-mapped frozen domains without executing TopoMT.

    Parameters
    ----------
    input_file, protocol_file : Path
        Original quantity-aware case input and frozen volume-domain protocol.

    Returns
    -------
    tuple
        All centers/radii and per-domain cells/probe metadata, numeric nm.

    Raises
    ------
    ValueError
        Input identity, source mapping or tetrahedron inventories differ.
    """
    fixture = json.loads(input_file.read_bytes())
    protocol = json.loads(protocol_file.read_bytes())
    if (
        protocol['schema'] != 'topomt.benchlab.volume-domain-protocol/1'
        or protocol['input_sha256']
        != hashlib.sha256(input_file.read_bytes()).hexdigest()
    ):
        raise ValueError('Volume reference input identity differs')
    centers = _values(fixture['coordinates'], 'coordinates', 'nm')
    radii = _values(fixture['atom_radii'], 'atom_radii', 'nm')
    expected = fixture.get('derivation', {}).get(
        'parent_atom_indices', list(range(len(centers)))
    )
    if expected != protocol['source_atom_indices']:
        raise ValueError('Frozen source correspondence differs')
    local = {atom: i for i, atom in enumerate(expected)}
    domains = []
    for domain in protocol['domains']:
        rows = domain['tetrahedra_source_atom_indices']
        if len({tuple(sorted(row)) for row in rows}) != len(rows):
            raise ValueError('Duplicate frozen domain tetrahedra')
        if any(len(set(row)) != 4 for row in rows):
            raise ValueError('Invalid frozen domain tetrahedron')
        cells = centers[np.array([[local[atom] for atom in row] for row in rows])]
        domains.append(
            {**domain, 'cells': cells, 'probe_nm': domain['probe_angstroms'] / 10}
        )
    return centers, radii, domains
