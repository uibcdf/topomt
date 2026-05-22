# DFND Known Conceptual Limitations and Open Risks

Point-in-time risk register recorded on 2026-05-20, before the first
implementation sprint. It consolidates the conceptual weak points identified
during the external geometric review and the project's own pre-implementation
audit.

This is a contract, not a list of fears. Every entry is tagged with a v1 policy
(`mitigate`, `flag`, or `defer`) and a validation hook so the team knows what is
attacked now and what is documented and consciously postponed.

Most of these risks are shared with CASTp / alpha-shape methods. DFND is more
exposed than a pure volume calculator because it makes claims about probe
*movement*, so its discretization assumptions are more load-bearing.

## Umbrella Framing

Almost everything below hangs from a single root:

```text
The Delaunay cell complex is an approximate topological skeleton of the
continuous probe-accessible space S, and S does not respect cell boundaries.

S = { p : min_i (dist(p, atom_i)) >= R_probe }   (where the probe center can be)
```

Residence, transit through connectors, the per-face gate, volume, and link
clustering are all manifestations of that one discretization. Read the register
with that in mind: these are several faces of one fundamental approximation, not
ten unrelated problems.

## Policy Legend

- `mitigate`: addressed in v1 by a concrete computation or rule.
- `flag`: kept in v1 as a raw/diagnostic marker; not silently trusted.
- `defer`: documented now, implemented later, kept off the v1 critical path.

## Origin Legend

- `WP1`-`WP4`: from the external geometric review (discretization, gate
  locality, access-axis fragility, Delaunay non-uniqueness).
- `new`: from the project pre-implementation audit (classification, metrics,
  scope).

## Summary

| ID | Risk | Layer | Origin | v1 policy |
|---|---|---|---|---|
| L0.1 | Input chemistry / radii / preprocessing controls the geometry | Input policy | new | mitigate |
| L1.0 | Cell complex is a skeleton of `S`, not `S` | Discretization | WP1 | flag |
| L1.1 | `nonresident_passage_domain` physically ambiguous | Discretization | WP1 | flag |
| L1.2 | Gate connectivity over-connects via slivers | Discretization | WP1 + WP2 | flag + mitigate |
| L1.3 | Nested concavities / single-scale `OCEAN` | Discretization | WP3 | defer |
| L2.1 | `R_gate` locality, active-set branches, and external-atom intrusion | Primitive geometry | WP2 + new | mitigate + flag |
| L2.1b | `R_residence` active-set completeness and degeneracy | Primitive geometry | new | mitigate |
| L2.2 | Delaunay non-uniqueness / stability | Primitive geometry | WP4 | flag |
| L3.1 | `surface_concavity_domain` is a negation-defined catch-all | Classification | new | flag / provisional |
| L3.2 | `has_residence` may be too lax | Classification | new | mitigate (report filters) |
| L4.1 | `external_link` clustering policy is decisive | Access / links | WP3 | mitigate (tests) |
| L5.1 | Physical solvent volume is a critical debt | Metrics | new | mitigate (v1) |
| L6.1 | Public taxonomy ahead of validation | Scope | new | defer |

---

## 0. Input Policy Layer

### L0.1 — Input chemistry / radii / preprocessing controls the geometry

- **Statement.** DFND decisions depend directly on atom coordinates, selected
  atoms, radii, protonation state, alternate-location policy, waters, ions,
  ligands, and other preprocessing choices. These inputs control `R_residence`,
  `R_gate`, residence, transit, external links, and all downstream families.
- **Why it matters.** Two equally valid preprocessing policies can produce
  different topographies. Without an explicit input contract, differences in
  results can be mistaken for algorithmic failures. This risk was already seen
  in CASTp1/CASTp3 comparisons.
- **v1 policy.** `mitigate`. Store the input policy in `DFNDParameters` and raw
  records: atom selection, radii model, alternate-location handling, hydrogen
  policy, water/ion/ligand policy, coordinate units, and any preprocessing
  performed before triangulation.
- **Validation hook.** Run the same toy or small molecular system under at least
  two explicit radii/selection policies and assert that raw records identify the
  policy difference.
- **Origin.** new.

---

## 1. Discretization Layer

### L1.0 — The cell complex is a skeleton of `S`, not `S` itself

- **Statement.** DFND approximates the connectivity of the continuous accessible
  space `S` with a discrete complex of cells (resident yes/no) and faces
  (permeable yes/no). `S` can intersect a non-resident cell near a wide face, and
  a resident cell's accessible sub-region is not its full tetrahedron. The
  complex cannot represent partial-cell accessibility.
- **Why it matters.** Graph connectivity is not exact probe reachability, and
  topological volume is not accessible volume. Treating the graph as ground
  truth would overstate precision.
- **v1 policy.** `flag`. State explicitly in the contract that the graph is a
  topological skeleton of `S`. Do not claim exact reachability.
- **Validation hook.** Toys with an analytically known `S` to measure
  discretization error in connectivity and volume.
- **Origin.** WP1 (umbrella).

### L1.1 — `nonresident_passage_domain` is physically ambiguous

- **Statement.** A domain of non-resident transit connectors (>= 2 links, no
  residence) describes a region the probe center may thread through gates but
  cannot reside in. If no cell can host the center with clearance, this may be a
  geometric contact rather than a stable physical passage. The real question is
  whether the accessible sub-region inside each connector continuously joins its
  permeable faces, or whether they are two disjoint contacts.
- **Why it matters.** A passage that is only a marginal contact is not a feature;
  promoting it would manufacture spurious channels/pores.
- **v1 policy.** `flag`. Keep it raw/provisional and do not promote it to a
  public `Channel` or biological pore feature in v1. It must carry a path
  capacity / bottleneck metric so the ambiguity is quantified, not merely
  declared.
- **Validation hook.** `toy_nonresident_pore_2links`, plus an adversarial toy
  where the two permeable faces have disjoint accessible spots inside the cell.
- **Origin.** WP1.

### L1.2 — Gate connectivity can over-connect via slivers

- **Statement.** Accepting non-resident transit connectors as bridges avoids
  artificially cutting pockets, but can create the opposite problem: domains
  joined by extremely thin or numerically unstable passages. This is a
  precision/recall trade-off, not a bug in either model. (Historical note: the
  wet-only graph under-connects; it was a conservative choice, not an error.)
- **Why it matters.** Spurious merges change domain identity and family counts
  as much as spurious splits do.
- **v1 policy.** `flag` + `mitigate`. Mark transit-connector edges as heuristic.
  Compute and report a minimum path capacity / bottleneck per domain so thin
  bridges are visible and can be filtered downstream. Coupled with L2.1: the
  slivers that over-connect here are exactly where the gate is least reliable.
- **Validation hook.** Adversarial sliver-bridge toy; bottleneck metric on the
  merged vs. unmerged domains.
- **Origin.** WP1 + WP2.

### L1.3 — Nested concavities and single-scale `OCEAN`

- **Statement.** With `sea_level = R_probe`, a pocket at the bottom of a wide
  bowl that also admits the probe merges with the bowl into one domain. The
  topographic hierarchy (sub-pocket inside a larger concavity) is not
  represented in v1. This is the dual of over-segmentation: large concave
  regions can be under-segmented.
- **Why it matters.** Real surfaces are hierarchical; flattening them can hide
  functionally distinct sub-sites.
- **v1 policy.** `defer`. Separating nested features needs depth/motif analysis
  ([`domain_motifs.md`](domain_motifs.md)) or a macro-surface mode. State
  explicitly that v1 does not hierarchize.
- **Validation hook.** Toy with a small pocket inside a shallow bowl; document
  that v1 reports one domain.
- **Origin.** WP3 (scale/nesting half).

---

## 2. Primitive Geometry Layer

### L2.1 — `R_gate` locality / external-atom intrusion

- **Statement.** `R_gate(F)` uses only the three face atoms. The opposite tetra
  vertex, or a bulky neighbor atom, can hang over the gate and block the real
  passage without `R_gate` seeing it, so a face can be falsely permeable. This is
  worst for flat/sliver cells, which are exactly the cells that become transit
  connectors (see L1.2).
- **Why it matters.** Falsely permeable gates systematically over-connect the
  transit graph at its least reliable nodes.
- **v1 policy.** `flag` (cheap guard). When computing `R_gate(F)`, check whether
  the opposite vertex (and/or neighbor apexes) intrudes into the gate disk: if
  the apex-to-face-plane distance is below `R_probe + r_apex`, mark the gate
  `intrusion_suspect`. The default v1 policy is diagnostic-only: do not make the
  gate non-permeable solely because of this flag. A stricter optional mode may
  later treat suspect gates as blocked, but that must be explicit because it can
  reintroduce under-segmentation.
- **Validation hook.** `toy_two_atom_gate` extended with an intruding fourth
  atom; assert the gate is flagged.
- **Origin.** WP2 + new.
- **Reference.** Detailed gate-radius audit and correction path: [`gate_radius_audit.md`](gate_radius_audit.md).

### L2.1b — `R_residence` active-set completeness and degeneracy

- **Statement.** The current DFND implementation treats four-atom tangency as an interior candidate and also evaluates face- and edge-limited active-set candidates. This is the correct direction, but near-degenerate tetrahedra can still stress candidate enumeration, validation, and numerical tolerance choices.
- **Why it matters.** Residence is part of the primary access x residence classifier. Underestimating residence can demote pockets, voids, or multi-link domains into non-resident families; overestimating residence can promote sliver contacts into resident features.
- **v1 policy.** `mitigate`. Use active-set `R_residence` as the residence primitive, retain `R_apollonius4` only as a diagnostic field, and keep the detailed rationale in [`residence_radius_audit.md`](residence_radius_audit.md).
- **Validation hook.** Maintain residence active-set toys covering interior4, face-limited, edge-limited, invalid four-atom candidate, and comparison with CASTp tetrahedron `rho`.
- **Origin.** new.

### L2.2 — Delaunay non-uniqueness and stability

- **Statement.** Under cosphericity (common in regular protein arrangements) the
  Delaunay triangulation is not unique. A tiny coordinate perturbation can flip
  tetrahedra and change domains and link counts. The method is built on the
  specific triangulation, and atom-quadruplet identities assume it is stable.
- **Why it matters.** Output reproducibility and dynamic identity across frames
  depend on triangulation stability.
- **v1 policy.** `flag`. Record the triangulation backend/options; surface
  near-degenerate simplices in raw diagnostics.
- **Validation hook.** Stability toy: a symmetric arrangement, perturbed, with an
  assertion on family/domain stability (or a documented sensitivity bound).
- **Origin.** WP4.

---

## 3. Classification Layer

### L3.1 — `surface_concavity_domain` is a negation-defined catch-all

- **Statement.** It is the only family defined by negation (accessible, no
  residence). Negation classes are inherently heterogeneous: surface noise,
  slivers, marginal contacts, and real shallow dents all land here. Its
  topographic/biological utility is not demonstrated.
- **Why it matters.** A heterogeneous residue class is hard to interpret and easy
  to misuse as if it were one thing.
- **v1 policy.** `flag` / provisional. Realizability is no longer in doubt; the
  open question is utility. Treat it as a diagnostic family by default, not as a
  public biological feature. Do not validate "the family" — validate whether
  evidence-based sub-types (n_nodes, area, depth, marginal fraction) separate
  real dents from noise.
- **Validation hook.** `toy_surface_dent_1link` plus small real systems; inspect
  the heterogeneity of what lands in the family.
- **Origin.** new.

### L3.2 — `has_residence` may be too lax

- **Statement.** A single marginally resident tetrahedron can turn a whole domain
  into a pocket/channel. Conceptually fine for primary topological
  classification, but weak for public reporting.
- **Why it matters.** Trivial one-cell "pockets" would flood the output and
  weaken credibility.
- **Mitigating context.** The conservative marginal policy already treats a tetra
  exactly at threshold (`|R_residence - R_probe| <= eps`) as non-resident, so the
  knife-edge case is covered. What remains uncovered is the clearly-resident but
  tiny (single-node) case.
- **v1 policy.** `mitigate`. Keep classification topological/binary; add
  secondary report filters (minimum resident volume, margin over probe radius,
  minimum resident-node count, epsilon stability). Principle: classification is
  topological; reporting is filtered/graded. Do not mix the two.
- **Validation hook.** Toy with one tiny resident node + filter thresholds;
  assert classification vs. reported feature differ as intended.
- **Origin.** new.

---

## 4. Access / Links Layer

### L4.1 — `external_link` clustering policy is decisive

- **Statement.** Grouping boundary faces by face-edge connectivity sets the link
  count, which in turn sets pocket vs. multi-external-link. The rule is
  reasonable but very consequential. The nastiest case is nearly coplanar
  adjacent boundary faces (geometrically one opening) whose edge-connectivity
  depends on the triangulation, linking back to L2.2.
- **Why it matters.** A pinched mouth split into two clusters flips a pocket into
  a channel.
- **v1 policy.** `mitigate`. Lock the policy and test it explicitly.
- **Validation hook.** Toys with openings that touch vertex-only, edge-only, and
  via near-coplanar faces; assert the resulting link counts.
- **Origin.** WP3 (clustering half).

---

## 5. Metrics Layer

### L5.1 — Physical solvent volume is a critical debt

- **Statement.** `volume_topological` includes atom-occupied portions and is not
  a physical pocket volume. To compare with the community, it is insufficient.
- **Why it matters.** Without a physical volume, DFND can classify domains but
  its headline metric is weak against CASTp/fpocket from day one.
- **Feasibility.** `volume_solvent_estimate` per tetra = tetra volume minus the
  sum of (atom sphere intersected with the tetra). Sphere-tetrahedron
  intersection has known analytical solutions (vertex/edge/face cases), but a
  robust implementation with unequal radii, tolerances, and slivers is
  geometrically delicate. Bounded effort, but not a throwaway helper.
- **v1 policy.** `mitigate`. Implement `volume_solvent_estimate` in v1; keep
  `volume_topological` only as an internal/debug proxy.
- **Validation hook.** Compare `volume_solvent_estimate` against a reference on a
  small known cavity.
- **Origin.** new.

---

## 6. Scope Layer

### L6.1 — Public taxonomy ahead of validation

- **Statement.** `ConcavityFeature`, `ConvexityFeature`, `BoundaryFeature`,
  `MixedFeature`, dry motifs, rim, ridge, etc. are useful as a conceptual map but
  must not contaminate the initial implementation.
- **Why it matters.** Building unvalidated public features first invites an
  ontology rewrite and dilutes the v1 critical path.
- **v1 policy.** `defer`. Implement raw records + primary classification +
  minimal metrics first. Keep the rest as documented conceptual map only.
- **Validation hook.** None for v1; promotion follows the criteria in
  [`open_design_questions.md`](open_design_questions.md) (documented definition,
  tests, toys, real cases, stability).
- **Origin.** new.

---

## Cross-References

- Residence/transit substrate: [`residence_transit_contract.md`](residence_transit_contract.md)
- Gate and asymmetry definitions: [`Mathematical_Definitions.md`](Mathematical_Definitions.md)
- Toy systems: [`toy_systems_v1.md`](toy_systems_v1.md)
- Validation path: [`validation_plan.md`](validation_plan.md)
- Data model and raw records: [`data_model_v1.md`](data_model_v1.md)
