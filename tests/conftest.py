import pytest

import topomt as tmt


def pytest_configure(config):
    """Pre-warm MolSysMT's numba cache once, in the xdist *controller*, before any
    worker is forked.

    MolSysMT compiles many kernels with ``@njit(cache=True)`` (on-disk cache).
    Under ``-n 12`` the workers otherwise hit a cold cache simultaneously and race
    to compile/write it, which surfaces as intermittent failures in the heavy
    real-system tests (see ``devguide/test_parallel_flakiness_2026_06_14.md``).
    The controller runs ``pytest_configure`` to completion *before* spawning
    workers, so warming here populates the disk cache race-free; workers then load
    the compiled functions instead of recompiling. Best-effort: never fail
    collection if warmup is unavailable.
    """
    if hasattr(config, "workerinput"):
        return  # xdist worker: only the controller pre-warms
    try:
        import molsysmt as msm

        msm.warmup()
    except Exception:
        pass

@pytest.fixture(scope="session")
def seed_topography_empty_1tcd():
    pdb_file = tmt.demo['TcTIM']['1tcd.pdb']
    topography = tmt.Topography(molecular_system=pdb_file)
    assert topography is not None
    return topography

@pytest.fixture(scope="function")
def topography_empty_1tcd(seed_topography_empty_1tcd):
    topography = seed_topography_empty_1tcd.copy(deep=True)
    assert topography is not None
    return topography
