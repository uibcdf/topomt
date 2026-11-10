"""Conditional volume uncertainty and bounded quadrature convergence records."""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from topomt._ackredit import attributed, scientific_call


@dataclass(frozen=True)
class VolumeMeasurement:
    """Numeric core measurement in the caller's common length-cubed unit.

    ``error`` is a sampling envelope or convergence diagnostic as identified by
    ``error_kind``. Neither covers model/support error. A missing first estimate
    is ``None`` rather than zero; ``history`` retains (order, value) pairs.
    """

    volume: Optional[float]
    error: Optional[float]
    method: str
    status: str
    error_kind: str
    interval: Optional[tuple[float, float]] = None
    confidence_level: Optional[float] = None
    n_samples: int = 0
    n_empty: Optional[int] = None
    history: tuple[tuple[int, float], ...] = ()
    reason: Optional[str] = None


def _integer(value, name, minimum=1):
    if (
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, np.integer))
        or value < minimum
    ):
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return int(value)


@attributed('clopper_pearson', route='criterion', retain=False)
def binomial_interval(
    successes: int, samples: int, confidence_level: float = 0.95
) -> tuple[float, float]:
    """Return a two-sided Clopper–Pearson interval for an IID binomial count.

    Parameters
    ----------
    successes, samples : int
        Observed successes and positive total sample count.
    confidence_level : float
        Confidence strictly between zero and one.

    Returns
    -------
    tuple of float
        Lower and upper proportion bounds, including nonzero endpoint widths.

    Raises
    ------
    ValueError
        Counts or confidence are invalid.
    """
    samples = _integer(samples, 'samples')
    successes = _integer(successes, 'successes', 0)
    if (
        successes > samples
        or not np.isfinite(confidence_level)
        or not 0 < confidence_level < 1
    ):
        raise ValueError('Invalid binomial count or confidence level')
    from scipy.stats import beta

    alpha = (1 - confidence_level) / 2
    lower = (
        0.0
        if successes == 0
        else float(
            scientific_call(
                'scipy', beta.ppf, alpha, successes, samples - successes + 1
            )
        )
    )
    upper = (
        1.0
        if successes == samples
        else float(
            scientific_call(
                'scipy', beta.ppf, 1 - alpha, successes + 1, samples - successes
            )
        )
    )
    return lower, upper


def _geometry(tetrahedra, atom_positions, atom_radii):
    cells = np.asarray(tetrahedra, dtype=float).reshape(-1, 4, 3)
    centers = np.asarray(atom_positions, dtype=float).reshape(-1, 3)
    radii = np.asarray(atom_radii, dtype=float).reshape(-1)
    if (
        len(centers) != len(radii)
        or not np.isfinite(cells).all()
        or not np.isfinite(centers).all()
        or not np.isfinite(radii).all()
        or (radii < 0).any()
    ):
        raise ValueError(
            'Volume geometry must be finite with matching nonnegative radii'
        )
    return cells, centers, radii


def _analytic_volume(cells, centers, radii, total):
    if total == 0.0:
        return 0.0
    positive = radii > 0.0
    centers, radii = centers[positive], radii[positive]
    if not len(centers):
        return total
    low, high = cells.reshape(-1, 3).min(axis=0), cells.reshape(-1, 3).max(axis=0)
    nearest = np.clip(centers, low, high)
    if np.all(np.linalg.norm(nearest - centers, axis=1) >= radii):
        return total
    # Each tetrahedron is convex. One ball covering its four vertices covers
    # that whole cell; an observed all-hit sample is never this proof.
    for cell in cells:
        distances = np.linalg.norm(cell[:, None, :] - centers[None, :, :], axis=2)
        if not np.any(np.all(distances <= radii, axis=0)):
            return None
    return 0.0


@attributed('geometry', retain=False)
def measure_region_volume(
    tetrahedra: np.ndarray,
    atom_positions: np.ndarray,
    atom_radii: np.ndarray,
    *,
    method: str = 'mc',
    n_samples: int = 40000,
    seed: int = 0,
    confidence_level: float = 0.95,
    n_quad: int = 24,
    max_order: int = 96,
    relative_tolerance: float = 1e-4,
    absolute_tolerance: float = 0.0,
    max_work: int = 2000000,
) -> VolumeMeasurement:
    """Measure empty volume on disjoint-interior tetrahedral carrier cells.

    Parameters
    ----------
    tetrahedra, atom_positions, atom_radii : numpy.ndarray
        Shapes (K,4,3), (A,3), (A,), all in one caller-declared length unit.
        Callers supply every excluding ball and disjoint-interior carrier cells.
    method : {'mc', 'quadrature', 'exact'}
        IID simplex-mixture sampling, bounded order refinement, or legacy fixed
        order with explicitly unknown quadrature error.
    n_samples, seed : int
        Positive sample count and reproducible random seed.
    confidence_level : float
        Conditional binomial confidence for sampling only.
    n_quad, max_order : int
        Initial/legacy Gauss order and refinement ceiling.
    relative_tolerance, absolute_tolerance : float
        Convergence target relative to carrier volume plus absolute volume.
        Two successive differences must meet it; this is not a rigorous bound.
    max_work : int
        Ceiling on the declared sum K*order**2*max(1,A) proxy, not wall time.

    Returns
    -------
    VolumeMeasurement
        Estimate, availability, uncertainty type and supporting sample/history.
        Volume/error use the cube of the supplied common length unit.

    Raises
    ------
    ValueError
        Geometry, method or numerical controls are invalid.
    """
    from .solvent_volume import (
        _cell_volumes,
        _empty_fraction,
        _sample_simplex,
        region_empty_volume_exact,
    )

    if method not in {'mc', 'quadrature', 'exact'}:
        raise ValueError("method must be 'mc', 'quadrature' or 'exact'")
    cells, centers, radii = _geometry(tetrahedra, atom_positions, atom_radii)
    volumes = _cell_volumes(cells)
    total = float(volumes.sum())
    if method == 'mc':
        n_samples = _integer(n_samples, 'n_samples')
        if not np.isfinite(confidence_level) or not 0 < confidence_level < 1:
            raise ValueError('confidence_level must be strictly between zero and one')
        analytic = _analytic_volume(cells, centers, radii, total)
        if analytic is not None:
            return VolumeMeasurement(
                analytic,
                0.0,
                method,
                'analytic',
                'geometric_proof',
                interval=(analytic, analytic),
            )
        rng = np.random.default_rng(seed)
        counts = rng.multinomial(n_samples, volumes / total)
        points = np.concatenate(
            [
                _sample_simplex(rng, cells[k], int(counts[k]))
                for k in np.nonzero(counts)[0]
            ]
        )
        fraction = _empty_fraction(points, centers, radii)
        count = int(round(fraction * n_samples))
        low, high = binomial_interval(count, n_samples, confidence_level)
        volume = total * fraction
        interval = (total * low, total * high)
        error = max(volume - interval[0], interval[1] - volume)
        return VolumeMeasurement(
            volume,
            error,
            method,
            'estimated',
            'binomial_confidence_interval',
            interval,
            confidence_level,
            n_samples,
            count,
        )
    n_quad = _integer(n_quad, 'n_quad')
    if method == 'exact':
        volume = region_empty_volume_exact(cells, centers, radii, n_quad=n_quad)
        return VolumeMeasurement(
            volume,
            None,
            method,
            'fixed_order_error_unknown',
            'unknown_quadrature_error',
            history=((n_quad, volume),),
        )
    max_order, max_work = (
        _integer(max_order, 'max_order'),
        _integer(max_work, 'max_work'),
    )
    if (
        max_order < n_quad
        or not np.isfinite([relative_tolerance, absolute_tolerance]).all()
        or min(relative_tolerance, absolute_tolerance) < 0
    ):
        raise ValueError('Invalid quadrature ceiling or convergence tolerance')
    if total == 0.0:
        return VolumeMeasurement(0.0, 0.0, method, 'analytic', 'geometric_proof')
    history: list[tuple[int, float]] = []
    differences: list[float] = []
    work = 0
    order = n_quad
    target = absolute_tolerance + relative_tolerance * total
    while order <= max_order:
        cost = len(cells) * order**2 * max(1, len(centers))
        if work + cost > max_work:
            break
        work += cost
        volume = region_empty_volume_exact(cells, centers, radii, n_quad=order)
        if history:
            differences.append(abs(volume - history[-1][1]))
        history.append((order, volume))
        if len(differences) >= 2 and max(differences[-2:]) <= target:
            return VolumeMeasurement(
                volume,
                max(differences[-2:]),
                method,
                'converged',
                'successive_order_difference',
                history=tuple(history),
            )
        order *= 2
    return VolumeMeasurement(
        history[-1][1] if history else None,
        None,
        method,
        'unresolved',
        'unknown_quadrature_error',
        history=tuple(history),
        reason='Order or declared work-proxy budget exhausted before two convergence checks',
    )
