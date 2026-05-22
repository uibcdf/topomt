# DFND Numerical Threshold Policy Checkpoint

This checkpoint records the first direct tests for DFND near-threshold behavior.

## Policy

For a quantity `x` compared with threshold `t` and length tolerance `epsilon`:

- `x > t + epsilon` is open;
- `x < t - epsilon` is closed;
- `abs(x - t) <= epsilon` is marginal.

Marginal states are classified deterministically on the conservative side:

- marginal residence is reported as non-resident;
- marginal face permeability is reported as non-permeable;
- raw records keep `marginal` flags so the decision remains auditable.

## Tests Added

`tests/test_dfnd_graph_contract.py` now checks:

- `_state_from_delta(...)` behavior above, below, and inside the tolerance band;
- exact-threshold `R_residence` records get a `marginal` flag and zero margin;
- exact-threshold `R_gate` face records get `marginal` flags and are reported
  as non-permeable;
- tetrahedra owning marginal faces also carry a `marginal` diagnostic flag.

These tests are numerical-policy tests, not cavity-quality validation.
