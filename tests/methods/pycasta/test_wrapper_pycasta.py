from pathlib import Path
import sys

import pytest

from topomt import pyunitwizard as puw
from topomt.get_topography import get_topography


UPSTREAM_ROOT = Path('/home/diego/repos@others/pycasta/src/pycasta')
BOUND_DIR = UPSTREAM_ROOT / 'data' / 'bounded'


def _load_upstream_pycasta():
    if not UPSTREAM_ROOT.exists():
        pytest.skip('local pycasta upstream mirror is not available')

    if str(UPSTREAM_ROOT) not in sys.path:
        sys.path.insert(0, str(UPSTREAM_ROOT))

    import run_analysis  # noqa: PLC0415

    return run_analysis


def _pocket_features(topography):
    return sorted(
        topography.get_features(by='type', value='pocket'),
        key=lambda pocket: pocket.score,
        reverse=True,
    )


def test_pycasta_wrapper_matches_upstream_reference_for_2pk4():
    run_analysis = _load_upstream_pycasta()
    pdb_path = BOUND_DIR / '2pk4.pdb'
    upstream = run_analysis.process_pdb(str(pdb_path))

    wrapper_topography = get_topography(
        str(pdb_path),
        method='pycasta',
        implementation='wrapper',
        upstream_root=str(UPSTREAM_ROOT),
    )
    wrapper_pockets = _pocket_features(wrapper_topography)

    assert len(wrapper_pockets) == len(upstream['ranked_pockets']) == 1
    assert puw.get_value(wrapper_pockets[0].volume, to_unit='nm**3') == pytest.approx(
        upstream['pocket_volumes'][0] / 1000.0
    )


@pytest.mark.parametrize(
    'pdb_name',
    ['1stp.pdb', '2ifb.pdb', '1hew.pdb'],
)
def test_pycasta_wrapper_matches_upstream_counts_for_small_examples(pdb_name):
    run_analysis = _load_upstream_pycasta()
    pdb_path = BOUND_DIR / pdb_name
    upstream = run_analysis.process_pdb(str(pdb_path))

    wrapper_topography = get_topography(
        str(pdb_path),
        method='pycasta',
        implementation='wrapper',
        upstream_root=str(UPSTREAM_ROOT),
    )
    wrapper_pockets = _pocket_features(wrapper_topography)

    assert len(wrapper_pockets) == len(upstream['ranked_pockets'])
