from pathlib import Path
import sys

import pytest

from topomt.methods.pycasta import pycasta


UPSTREAM_ROOT = Path('/home/diego/repos@others/pycasta/src/pycasta')
BOUND_DIR = UPSTREAM_ROOT / 'data' / 'bounded'


def _load_upstream_pycasta():
    if not UPSTREAM_ROOT.exists():
        pytest.skip('local pycasta upstream mirror is not available')

    if str(UPSTREAM_ROOT) not in sys.path:
        sys.path.insert(0, str(UPSTREAM_ROOT))

    import run_analysis  # noqa: PLC0415

    return run_analysis


def test_pycasta_matches_upstream_for_2pk4():
    run_analysis = _load_upstream_pycasta()
    pdb_path = BOUND_DIR / '2pk4.pdb'

    upstream = run_analysis.process_pdb(str(pdb_path))
    pockets, volumes, simplices, atom_indices = pycasta(
        str(pdb_path),
        return_atom_indices=True,
    )

    assert len(upstream['ranked_pockets']) == 1
    assert len(pockets) == 1

    upstream_top = upstream['ranked_pockets'][0]
    topomt_top = pockets[0]

    assert len(topomt_top) == len(upstream_top) == 62
    assert set(topomt_top) == set(upstream_top)
    assert volumes[0] == pytest.approx(upstream['pocket_volumes'][0] / 1000.0)


@pytest.mark.parametrize(
    ('pdb_name', 'expected_sizes'),
    [
        ('1a4j.pdb', None),
        ('1acj.pdb', None),
        ('1bid.pdb', None),
        ('1byb.pdb', None),
        ('1stp.pdb', [80, 55]),
        ('2ifb.pdb', [93, 38, 9]),
        ('1hew.pdb', [57, 61]),
        ('1a6w.pdb', None),
        ('1okm.pdb', None),
        ('1gca.pdb', None),
    ],
)
def test_pycasta_matches_upstream_counts_and_volumes_for_small_bounded_examples(
    pdb_name,
    expected_sizes,
):
    run_analysis = _load_upstream_pycasta()
    pdb_path = BOUND_DIR / pdb_name

    upstream = run_analysis.process_pdb(str(pdb_path))
    pockets, volumes, simplices, atom_indices = pycasta(
        str(pdb_path),
        return_atom_indices=True,
    )

    upstream_sizes = [len(pocket) for pocket in upstream['ranked_pockets']]
    if expected_sizes is None:
        expected_sizes = upstream_sizes

    assert len(pockets) == len(expected_sizes) == len(upstream['ranked_pockets'])
    assert [len(pocket) for pocket in pockets] == expected_sizes
    assert upstream_sizes == expected_sizes
    assert volumes == pytest.approx([value / 1000.0 for value in upstream['pocket_volumes']])
