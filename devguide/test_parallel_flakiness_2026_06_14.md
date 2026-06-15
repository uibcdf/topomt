# Parallel test flakiness under `-n 12` (finding, 2026-06-14)

**Status:** open. Root cause identified by evidence; fix not yet applied.

## Symptom

The full suite under `pytest -q -n 12` fails intermittently. Across three runs
of the *same* working tree:

- run A: 1 failure — `test_molsysviewer_topomt_addon.py::test_empty_render_result_replaces_previous_graph_tetrahedra_and_components`;
- run B: 4 failures — `test_dfnd_real_system_stability.py::...[1rop]`, `[2pk4]`,
  `test_molsysviewer_topomt_addon.py::test_subset_topography_preserves_real_dfnd_analysis`,
  `test_dfnd_pockets.py::test_get_topography_dfnd_smoke_with_real_small_pdb`;
- run C: 0 failures (clean).

Every failing test **passes in isolation**, the whole
`test_molsysviewer_topomt_addon.py` file **passes sequentially (`-n0`)**, and —
decisively — the **entire suite passes under `-n0`** (single process, every test
in a fixed order).

## It is parallel-only, not deterministic state pollution, and not a code change

- The full suite under `-n0` is **clean**. Single-process sequential execution is
  the worst case for deterministic global-state pollution; if a test were
  poisoning a Python global that another test reads, `-n0` would reproduce it. It
  does not. So this is **not** intra-process state pollution — it only appears
  with concurrent worker processes.
- It is not a recent code change: the failing set is **non-overlapping across
  runs**, the same code runs clean on a later `-n 12` run, and a control run with
  the 2026-06-14 unit/`radii_model` changes reverted failed *more* tests in a
  different cluster. Those corrections pass in isolation and on clean parallel
  runs.

## Likely causes (parallel-only)

Two distinct clusters, two different mechanisms:

- **Real-system cluster** (`test_dfnd_real_system_stability`, real-PDB smoke,
  subset-topography): the heavy path goes through MolSysMT, which compiles ~38
  kernels with `@njit(cache=True)` (on-disk cache). Under `-n 12` the workers hit
  a cold cache simultaneously and race to compile/write it — a classic numba
  concurrent-cache race that only manifests in parallel, exactly matching the
  `-n0`-clean / `-n 12`-flaky pattern. (An earlier note dismissed numba; the
  `-n0`-clean result revives it for *this* cluster specifically.)
- **Render cluster** (`test_empty_render_result_...`): an `AssertionError` about
  render state (a 4-node `RenderResult` where empty was expected). It is pure
  Python with no numba and passes in every sequential mode; the parallel-only
  mechanism here is **not yet pinned** (rare, and the obvious coupling points —
  `_resolve_topography` prefers the explicit arg, the test builds fresh mock
  nodes — are clean).

## Mitigation applied

`tests/conftest.py` now pre-warms the MolSysMT numba cache in the **xdist
controller** (`pytest_configure`, guarded by `hasattr(config, "workerinput")`),
which completes before workers are forked. The disk cache is then populated
race-free and workers load compiled kernels instead of recompiling. This targets
the real-system cluster.

## Remaining / recommended

1. Confirm the mitigation reduces the real-system cluster over repeated `-n 12`
   runs (a single green run does not prove a flaky fix).
2. The render cluster is still unexplained; if it recurs, a pragmatic safety net
   is `pytest-rerunfailures` (auto-retry) or `--dist loadfile`, rather than
   chasing a rare parallel-only race.

## Note on scope

This is independent of the 2026-06-14 unit-convention and `radii_model`
corrections: those pass in isolation and on a clean parallel run, and the
flakiness reproduces with them reverted.
