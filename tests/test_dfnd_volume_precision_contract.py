"""Boundary-safe uncertainty and bounded quadrature diagnostics for #75."""

import math

import numpy as np
import pytest

from topomt.dfnd.core.solvent_volume import tetrahedron_empty_volume

TET = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
CENTER = np.array([[0.2, 0.2, 0.2]])


@pytest.mark.parametrize('radius', [0.001, 0.8])
def test_sampled_endpoint_without_geometric_proof_has_positive_uncertainty(radius):
    result = tetrahedron_empty_volume(TET, CENTER, np.array([radius]), n_samples=8)
    assert result.error > 0.0


def test_exact_binomial_coverage_includes_boundary_probabilities():
    from scipy.stats import binom

    from topomt.dfnd.core.volume_precision import binomial_interval

    for n in (8, 32):
        bounds = np.array([binomial_interval(k, n, 0.95) for k in range(n + 1)])
        for p in (0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999):
            covered = (bounds[:, 0] <= p) & (p <= bounds[:, 1])
            assert binom.pmf(np.arange(n + 1), n, p)[covered].sum() >= 0.95 - 1e-12


def test_converged_quadrature_is_an_estimate_with_retained_order_history():
    from topomt.dfnd.core.volume_precision import measure_region_volume

    result = measure_region_volume(
        TET[None],
        CENTER,
        np.array([0.1]),
        method='quadrature',
        n_quad=12,
        max_order=96,
        relative_tolerance=1e-4,
    )
    analytic = 1 / 6 - 4 * math.pi * 0.1**3 / 3
    assert result.status == 'converged'
    assert result.error_kind == 'successive_order_difference'
    assert len(result.history) >= 3
    assert result.error is not None and result.error > 0
    assert abs(result.volume - analytic) < 1e-4 / 6
    assert result.confidence_level is None and result.interval is None


def test_exhausted_quadrature_does_not_report_a_certified_error():
    from topomt.dfnd.core.volume_precision import measure_region_volume

    result = measure_region_volume(
        TET[None],
        CENTER,
        np.array([0.1]),
        method='quadrature',
        n_quad=6,
        max_order=12,
        relative_tolerance=1e-12,
    )
    assert result.status == 'unresolved'
    assert result.error is None
    assert len(result.history) == 2
    assert result.reason


def test_work_ceiling_can_stop_before_first_quadrature_evaluation():
    from topomt.dfnd.core.volume_precision import measure_region_volume

    result = measure_region_volume(
        TET[None], CENTER, np.array([0.1]), method='quadrature', n_quad=12, max_work=1
    )
    assert result.status == 'unresolved'
    assert result.volume is None and result.error is None
    assert not result.history


@pytest.mark.parametrize('samples', [0, -1, True, 2.5])
def test_invalid_sample_count_is_rejected(samples):
    from topomt.dfnd.core.volume_precision import measure_region_volume

    with pytest.raises(ValueError):
        measure_region_volume(TET[None], CENTER, np.array([0.1]), n_samples=samples)


def test_legacy_exact_keeps_numeric_result_with_explicit_unknown_error():
    from topomt.dfnd.core.solvent_volume import region_empty_volume_exact
    from topomt.dfnd.core.volume_precision import measure_region_volume

    result = measure_region_volume(
        TET[None], CENTER, np.array([0.1]), method='exact', n_quad=12
    )
    assert result.status == 'fixed_order_error_unknown'
    assert result.error_kind == 'unknown_quadrature_error'
    assert result.error is None
    assert result.volume == region_empty_volume_exact(
        TET[None], CENTER, np.array([0.1]), n_quad=12
    )


def test_batched_exclusion_matches_direct_all_atom_union():
    from topomt.dfnd.core.solvent_volume import _empty_fraction

    rng = np.random.default_rng(32)
    points, centers, radii = (
        rng.random((301, 3)),
        rng.random((57, 3)),
        np.full(57, 0.12),
    )
    direct = np.mean(
        np.all(np.sum((points[:, None] - centers) ** 2, axis=2) > radii**2, axis=1)
    )
    assert _empty_fraction(points, centers, radii, max_distance_pairs=127) == direct


def test_public_measurement_preserves_support_units_and_separate_observables():
    import pyunitwizard as puw

    from tests.test_benchlab_public_topography import public_result

    topo = public_result('regular_tetrahedron', 1.2)[0]
    cid = next(
        iter(topo.dfnd.dfn.components.get_components(by='side', value='wet'))
    ).component_id
    # Registry keys are the actual public component identity, not a case label.
    bare = topo.dfnd.solvent_volume_measurement(cid, n_samples=4096)
    probe = topo.dfnd.solvent_volume_measurement(
        cid, observable='probe_center', n_samples=4096
    )
    carrier = topo.dfnd.solvent_volume_measurement(cid, observable='carrier')
    assert bare['schema'] == 'dfnd.volume_measurement.v1'
    assert bare['error_kind'] == 'binomial_confidence_interval'
    assert bare['support']['source_id'] == topo.input_context.source_id
    assert bare['support']['tetrahedron_ids'] == probe['support']['tetrahedron_ids']
    values = [
        float(puw.get_value(item['volume'], to_unit='nm**3'))
        for item in (probe, bare, carrier)
    ]
    assert 0 <= values[0] <= values[1] <= values[2]
    assert carrier['status'] == 'analytic'
    assert puw.get_value(carrier['error'], to_unit='nm**3') == 0
    with pytest.raises(ValueError, match='observable'):
        topo.dfnd.solvent_volume_measurement(cid, observable='exterior_accessible')


def test_precision_method_credits_only_reached_interval_and_preserves_saved_reading():
    import ackredit

    from topomt.dfnd.core.volume_precision import measure_region_volume

    with ackredit.session('precision'):
        with ackredit.capture('mc') as captured:
            measure_region_volume(TET[None], CENTER, np.array([0.1]), n_samples=64)
        payload = captured.attribution.to_dict()
        assert 'doi:10.1093/biomet/26.4.404' in {
            item['id'] for item in payload['items']
        }
        with ackredit.capture('quadrature') as other:
            measure_region_volume(
                TET[None], CENTER, np.array([0.1]), method='exact', n_quad=6
            )
        assert 'doi:10.1093/biomet/26.4.404' not in {
            item['id'] for item in other.attribution.to_dict()['items']
        }
    with ackredit.session('saved'):
        restored = ackredit.Attribution.from_dict(payload)
        assert restored.report(format='bibtex')
        assert not ackredit.get_attribution().to_dict()['items']


def test_public_precision_reuses_references_and_survives_optional_recorder_failure(
    monkeypatch,
):
    import ackredit

    import topomt as tmt
    from tests.test_benchlab_public_topography import public_result
    from topomt import _ackredit

    topo = public_result('regular_tetrahedron', 1.2)[0]
    cid = next(
        c.component_id for c in topo.dfnd.dfn.components.values() if c.side == 'wet'
    )
    with ackredit.session('two measurements'):
        first = topo.dfnd.solvent_volume_measurement(cid, n_samples=64)
        second = topo.dfnd.solvent_volume_measurement(cid, n_samples=64)
        for item in (first, second):
            refs = tmt.get_attribution(item)
            assert refs['status'] == 'recorded'
            assert 'doi:10.1093/biomet/26.4.404' in {
                row['item']['id'] for row in refs['references']
            }
        tmt.get_attribution(first)['references'].clear()
        assert tmt.get_attribution(second)['references']
    monkeypatch.setattr(_ackredit, 'backend', lambda: None)
    absent = topo.dfnd.solvent_volume_measurement(cid, n_samples=64)
    assert tmt.get_attribution(absent)['status'] == 'unavailable'
    monkeypatch.undo()
    monkeypatch.setattr(ackredit, 'track_item', lambda *a, **k: 1 / 0)
    with ackredit.session('failed recording'), pytest.warns(Warning):
        failed = topo.dfnd.solvent_volume_measurement(cid, n_samples=64)
    assert tmt.get_attribution(failed)['status'] == 'failed'
    assert failed['volume'] == first['volume']
