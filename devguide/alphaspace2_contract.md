**Topology Contract**

This note records the active contract for the native `alphaspace2` path so we
don't lose track of what already replicates upstream and what still requires
attention before the `0.3.0` milestone.

**Parity Coverage**

- `tests/test_alphaspace2.py` already asserts native state ≃ upstream `Snapshot`
  for alpha counts, pocket memberships, pocket volumes, beta groups, beta
  centers, beta spaces, and beta/pocket scores on reference systems
  (`1GG0`, `3LKF`, protease examples, CDK2)【tests/test_alphaspace2.py:122】.
- The same file also checks binder/contact propagation and Vina-aware scoring
  residuals through `_native_pocket_scores_from_state` and the `CDK2` parity
  regression, ensuring the scoring tables and filtered beta probe handling
  remain aligned with the upstream `genBScore`/`annotateVinaAtomTypes`
  semantics【tests/test_alphaspace2.py:274】.

**Mechanics We Guarantee**

- `AlphaSpace2State` reproduces `_build_state`’s equivalent of `Snapshot.run`:
  alpha generation (`_compute_alpha_layer`), pocket clustering
  (`_cluster_pockets`), beta clustering (`_cluster_betas`), beta scoring
  (`_compute_beta_scores`), and binder/contact propagation
  (`_compute_contact_masks`).
- Vina typing uses the same `.data/hp_types_dict.dat`,
  `.data/typing_from_pdb.dat`, and `.data/autodock_atom_type_info.dat`
  tables that the upstream package ships; `_prepare_vina_typing` and
  `_get_probe_scores` replicate `VinaScoring._gen_vina_type` and
  `_get_probe_score` with consistent interpolation and autodock term weighting.
- Binder/contact logic follows `Snapshot.calculateContact`: `alpha_contact`,
  `beta_contact`, and `pocket_contact` become `True` if any child alpha touches
  a binder within the 0.16 nm cutoff.
- We also emit pocket grid volumes, pocket overlap counts (intersection and
  union of lining atoms), and the binder contact matrix so downstream consumers
  have access to the same cavity characterization data that `Snapshot` would
  expose, even though we keep our TopoMT-native records.
- We guard that the nine-element beta probe score vector matches the `_get_probe_scores`
  computation for the same receptor/adv_atom_types inputs, so the per-beta scoring
  distribution stays faithful to upstream Vina scoring regardless of downstream
  formatting.
- The scoring tables inside `topomt/data/alphaspace2` are the data sources we
  mimic: `hp_types_dict.dat` and `typing_from_pdb.dat` map residues/atoms to
  autodock types, `autodock_atom_type_info.dat` lists probe radii + flags, and
  `vina_params.dat` exposes the five Vina weights used in `_get_probe_scores`. We
  copy their column semantics (radius in Å/2, four boolean indicators) when
  building `prot_types`, `hp_type`, `don_type`, and `acc_type` before calling
  `_get_probe_scores`.
- Pocket connectivity is visible through the `pocket_connection_matrix`
  (an adjacency graph derived from the overlap counts) and through derived
  `beta_overlap_*` matrices, giving the same connectivity statistics that the
  upstream `Snapshot` also exposes in its overlap-based features.
- The scoring tables are the ones bundled inside `topomt/data/alphaspace2`:
  `hp_types_dict.dat`, `typing_from_pdb.dat`, `autodock_atom_type_info.dat`,
  and `vina_params.dat`. `_prepare_vina_typing` uses these files to map every heavy
  atom to an autodock type and decide hp/don/acc roles, and `_get_probe_scores`
  weights the resulting distance terms with the same five Vina coefficients recorded
  in VinaScoring so the scoring math is self-contained in TopoMT.

**Contact propagation**

- We compute the binder contact matrix with `_contact_matrix` and propagate the
  resulting `alpha_contact` flags through `_compute_contact_masks` so that
  `beta_contact` and `pocket_contact` mirror the upstream `Snapshot.calculateContact`
  logic (i.e., any pocket/beta is in contact if one of its child alfas is).
  These flags also feed into `_state_to_pocket_records` so downstream consumers can
  read the contact truth for each pocket/beta without re-running the binder search.

**Expected Inputs**

- `alphaspace2.s` accepts `adv_atom_types` or a `pdbqt_file` to mirror the
  upstream `annotateVinaAtomTypes` usage.
- All distance parameters (`min_radius`, `max_radius`, `cluster_cutoff`,
  `beta_cluster_cutoff`, binder points) are normalized to `nm` using
  TopoMT’s `pyunitwizard`; bare floats therefore behave like the native upstream
  defaults, not the older `angstrom` interpretations.

**Residual Gaps**

- The only measured drift is the `CDK2` beta-outlier (≈3.8×10⁻³) when comparing
  our `molsysmt`-based ingest (float64) against the upstream `mdtraj`
  pipeline (float32). We treat that as a precision difference, not a logic bug,
  so there is no planned code change unless the tolerance fails in future
  data.
- The heavy-atom selection still retains some manual steps, but they are
  deliberate within `alphaspace2`; we do not yet wrap every public argument
  with `argdigest` because the semantics of bare floats are still explicitly
  defined as `nm`.

**Verification Steps**

1. Run `python -m pytest tests/test_alphaspace2.py -k cdk2` to keep the Vina
   scoring parity guard green.
2. Re-run `tests/test_topography.py` subsets that mutate `alphaspace2` inputs
   when you change binder/contact flags or state-to-pocket conversions.
3. Document any future change that would move `min_radius`, `max_radius`, or
   binder units off of `nm` so we can re-evaluate `argdigest` rollout.

With these assertions in place, `alphaspace2` already mirrors the upstream
behavior for the cover systems. The remaining work for `0.3.0` is to finish the
descriptor/scoring layer, but that effort can now build on this documented
baseline.
