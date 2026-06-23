# DFND Validation Plan

This document defines the validation path required before DFND is presented as a
competitive pocket, channel, or topography detector.

The goal is to separate three questions:

1. Does the raw graph implementation obey the DFND contract?
2. Does DFND identify chemically and structurally relevant sites?
3. Where does DFND intentionally differ from CASTp, fpocket, MOLE/Caver, or
   other tools?

## 1. Validation Layers

### 1.1. Contract Validation

Use the synthetic systems in [`toy_systems_v1.md`](toy_systems_v1.md).

Required checks:

- primitive wet/dry and permeable/non-permeable states;
- marginal-state policy;
- external-link clustering;
- transit-component extraction;
- residence-region extraction;
- concavity-component classification;
- transit-connector and terminal-contact policies;
- dry-component extraction;
- dry-interface extraction;
- face-depth calculation;
- raw-record provenance.

### 1.2. Geometric Feasibility Validation

Before relying on `surface_concavity`, `wet_coast`, or `wet_sealed`, run
explicit feasibility checks:

- construct or search for tetrahedra with `wet_coast`;
- validate the analytic `wet_sealed` regular-tetrahedron fixture;
- construct or search for additional tetrahedra with `wet_sealed`;
- estimate how common these states are under realistic C/N/O/S radii;
- document whether they are normal states, rare states, or numerical edge cases.

Before making exactness claims for `R_gate`, audit unequal-radius face gates:

- compare the current face-plane gate candidate with alternative 3D
  bottleneck models if available;
- measure expected bias for mixed radii;
- document the adopted v1 model explicitly.

### 1.3. Small Real-System Validation

Use a small curated panel before broad benchmarks.

Candidate systems can come from the CASTp/CASTpFold oracle set and known small
protein examples already used in this repository. The first panel should be
small enough to inspect manually.

Suggested first target size:

```text
5-10 proteins
known ligand or known pocket when possible
small to medium atom count
minimal alternate-location ambiguity
```

### 1.4. Quantitative Benchmark Validation

For publication-level claims, compare against recognized detectors and known
binding sites using explicit metrics.

Candidate metrics:

- distance from predicted site center to ligand center;
- top-N success rate for known binding sites;
- atom/residue overlap with known ligand-contact residues;
- overlap between predicted component atoms and reference pockets;
- external-link count and mouth/rim descriptors as diagnostic, not primary
  success metrics;
- volume comparisons may use `volume_solvent_estimate` for early engineering checks, while publication-level comparisons still require a higher-precision `volume_solvent` metric.

Possible benchmark sources:

- curated small CASTp/CASTpFold systems already downloaded in `topomt/data`;
- ligand-bound structures with known pockets;
- future scPDB/PocketMiner-style panels if the project moves toward a paper.


### 1.5. Monte Carlo Reference Fixtures For Radius Primitives

The current validation strategy for the radius primitives uses Monte Carlo
checks, where applicable, as an independent reference for `R_gate` and
`R_residence`. This is useful during
algorithm design because it tests the physical question directly: maximize
clearance over the admissible face or tetrahedron component without trusting the
same active-set solver being validated.

However, Monte Carlo reference calculations are expensive if repeated in every
test run. A future faster testing strategy should build a fixed reference
fixture database:

- generate a large battery of triangular faces and tetrahedra with random but
  controlled coordinates and atomic radii;
- compute high-sampling Monte Carlo estimates for `R_gate` and `R_residence`;
- store the generated coordinates, radii, reference radii, tolerances, and
  random seeds in a versioned test-data fixture;
- use those stored values as a regression oracle in normal unit tests;
- regenerate the fixture only when the reference policy, admissible component, or
  tolerance contract intentionally changes.

This keeps the Monte Carlo calculation as an external sanity check while making
routine tests deterministic and cheap.

## 2. What Not to Claim Before Validation

Do not claim yet that DFND:

- outperforms CASTp, fpocket, MOLE, Caver, AlphaSpace2, or P2Rank;
- gives exact physical pocket volumes;
- identifies biological channels solely from `n_external_links >= 2`;
- validates dry motifs as public convexity, boundary, or mixed features;
- contains other algorithms as formal limiting cases.

## 3. Minimal Success Criteria for v1

The first implementation can be considered internally successful when:

- all toy systems pass;
- raw records are reproducible and inspectable;
- `wet_coast`/`wet_sealed` feasibility is resolved or explicitly bounded;
- `R_gate` two-atom and three-atom active restrictions are tested;
- transit-connector and terminal-contact behavior is tested;
- 5-10 small real systems can be processed without crashes;
- reported components are visually and atomically traceable;
- topological volume is clearly separated from physical solvent volume.

## 4. What "validated" means here (re-anchored)

Sections 1–3 cover contract correctness and "what not to claim". This section
states what *validated* means — and re-anchors it on purpose:

> **TopoMT exists to give the user a rich, complete, useful characterization of a
> surface's topography. Validation exists to give the user confidence that this
> characterization is correct, complete, and honestly labelled — not to prove
> that DFND resembles CASTp, fpocket, or CAVER.**

External comparison is **one descriptive lens**, never the driver and never a
pass/fail bar. A DFND output (a sealed void, a transit channel, a gate
constriction, a cryptic pocket over a trajectory) has value to the user whether
or not another tool produces something comparable. The acceptance gates below
exist so "correct and trustworthy" can actually *conclude*, not so DFND can be
ranked against other detectors. For the distinctive characterization this
serves, see [`research_program.md`](research_program.md).

### 4.1. Claims (primary → secondary)

- **P0 — Trustworthy, complete characterization (primary).** DFND's outputs obey
  the contract (Sections 1–3), are deterministic, are *exact* on synthetic
  ground truth, carry honest error bounds, are labelled by maturity
  (`output_status.py`), and cover the surface's topography completely
  (pockets / voids / channels / percolating regions / mouths / dry network /
  interfaces). This is what lets a user rely on and act on the results.
- **C-topology — Known-case correspondence.** DFND channels and voids correspond
  to known channels/tunnels and classic buried cavities in topology and
  geometry.
- **C-robustness — Determinism / scale.** DFND runs, terminates, and is
  byte-identical run-to-run on a representative real-system panel.
- **C-navigability (deferred).** "A probe of radius *r* can pass" requires
  `validated_probe_path` / `widest_gate_path`; the current channel *skeleton*
  does not support this claim by construction.
- **Concordance (descriptive lens, NOT a goal).** Where semantics overlap, report
  how DFND agrees with — and explainably diverges from — CASTp/fpocket/CAVER on
  geometry and site recovery. Divergence is information, not failure.

### 4.2. Ground-truth tiers (strong → weak)

1. **Synthetic (exact answer)** — `toy_systems_v1.md` / `synthetic.py`: known
   void volumes, known channel bottlenecks. Assertable exactly.
2. **Annotated (real answer)** — curated PDBs with a known ligand/site; known
   channel proteins; classic buried cavities (T4 lysozyme L99A, myoglobin Xe).
3. **Peer concordance (descriptive, NOT pass/fail)** — DFND vs the per-feature
   baselines below, same probe. Peers use *different definitions*; report
   agreement **and explained divergence**, never "match-or-fail".

### 4.3. Baseline by feature type (use the right comparator)

| DFND feature | Correct baseline / ground-truth |
| --- | --- |
| Pockets (detection) | ligand DBs (sc-PDB, PDBbind, Binding MOAD, COACH420/HOLO4K), fpocket, P2Rank |
| Pockets/voids (geometry: volume, area) | CASTp / CASTpFold (analytic) |
| Channels / tunnels | **CAVER, MOLE, ChannelsDB** — *not* fpocket/CASTp |
| Buried / sealed voids | classic cavity cases (T4-L99A, Xe sites), ChannelsDB pores |
| Flow / transit / gate / dry network | **no external baseline** — synthetic + known-case + expert review |

The last row is DFND's distinctive layer (residence vs transit, gates, dry
network, interfaces). It cannot be tool-benchmarked; validate it on synthetic
and known cases.

### 4.4. Acceptance gates (fill the numbers)

| Axis | Metric | Gate (to set) |
| --- | --- | --- |
| C1 | relative volume/area error vs CASTp/analytic; R²/slope over the panel | e.g. <5–10% on synthetics; R²>0.9 vs CASTp |
| C2 | DCA ≤4 Å; top-N recovery; atomic Jaccard with the site | ≥ fpocket/CASTp baseline |
| C3a | feature↔reference match (greedy/Hungarian by overlap): precision/recall/F1 | report + characterize |
| C4 | completion rate; run-to-run raw hash; probe-sweep stability | 100%; byte-identical; no spurious jumps |

**The numeric gates and the exact PDB panel are the two open decisions.** They
belong here once fixed — until then, validation cannot conclude.

### 4.5. Sequencing

Robustness on real systems (C4) → automated synthetic correctness (C1) →
distinctive / known-case (C3a) → peer concordance (C2 + matching). Run
concordance **last** and as *disagreement mining*: over the panel, surface the
maximal DFND↔peer disagreements and explain each (definition difference vs real
bug). The explained divergences are the most informative output.

### 4.6. Frozen benchmark

The panels are a *fixed, versioned* set with a scripted harness logging metrics
to file — re-runnable after every change to catch regressions (e.g. the WP-15
orchestration refactor). Extend [`known_limitations.md`](known_limitations.md)
with every documented divergence.

### 4.7. External dependencies / caveats

- Native CASTp is blocked on parity — use the **reference** CASTp for
  C1/concordance until unblocked.
- C3b (navigability) waits on `validated_probe_path` / `widest_gate_path`.
