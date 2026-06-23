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
