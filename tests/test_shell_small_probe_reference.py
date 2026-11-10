"""Independent convex-nerve reference, including free face edges."""

import copy

import numpy as np
import pytest

from devtools.verify_small_probe_boundary import (
    build_face_certificate,
    verify_face_certificate,
)

TRIANGLE = np.array([[0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [0.0, 4.0, 0.0]])


@pytest.mark.parametrize('radius,count', [(0.2, 1), (1.2, 2), (5.0, 0)])
def test_augmented_reference_counts_free_face_components_without_covered_edges(
    radius, count
):
    centers = np.array([[1.0, 1.0, 0.0]])
    cert = build_face_certificate(TRIANGLE, centers, radius)
    result = verify_face_certificate(TRIANGLE, centers, radius, cert)
    assert result['free_components'] == count
    assert result['complete_two_skeleton']


@pytest.mark.parametrize('damage', ['missing', 'false_positive', 'false_negative'])
def test_reference_rejects_incomplete_or_false_convex_witnesses(damage):
    centers = np.array([[1.0, 1.0, 0.0]])
    cert = build_face_certificate(TRIANGLE, centers, 1.2)
    broken = copy.deepcopy(cert)
    if damage == 'missing':
        broken['decisions'].pop()
    elif damage == 'false_positive':
        row = next(row for row in broken['decisions'] if row.get('barycentric_weights'))
        row['barycentric_weights'] = [1.0, 0.0, 0.0]
    else:
        row = next(row for row in broken['decisions'] if row.get('dual_weights'))
        row['direction'] = [0.0, 0.0, 0.0]
    with pytest.raises(ValueError):
        verify_face_certificate(TRIANGLE, centers, 1.2, broken)
