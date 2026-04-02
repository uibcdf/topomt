**AlphaSpace2 Continuity Notes**

Purpose: record what is already implemented for scoring/contact and what the next concrete actions are if we continue evolving TopoMT’s native AlphaSpace2 route.

1. **Completed in `0.3.0`**
   - Full alpha/beta pipeline with grid volumes, overlap matrices, and contact matrix; all stored in `AlphaSpace2State`.
   - Beta probe scores computed with `_compute_beta_scores` use the vendored tables and match the helper computation; CDK2 is the parity guard.
   - Documentation captures the Vina tables used and the descriptor guarantees (devguide/alphaspace2_contract.md).

2. **Next incremental work**
   - Expand tests to compare pocket/pocket contact (still optional).  
   - Consider packaging `_grid_volume`/`_overlap_matrices` as util functions in MolSysMT. (Proposal already noted.)  
   - Revisit `argdigest` rollout once we decide whether bare floats should stay as `nm` defaults for scoring arguments.

3. **Scheduled checks**
   - Run `python -m pytest tests/methods/alphaspace2/test_parity.py -k "beta_probe or cdk2"` after any scoring, table or contact change.
   - Review contract doc if new descriptors or tables are added.

With this log we can pick up the thread later without losing track of the parity goal we just met.
