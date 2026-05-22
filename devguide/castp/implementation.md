# CASTp Native Implementation Plan

## Purpose

This document describes a from-scratch implementation plan for a faithful
native `castp` path in TopoMT.

Current closure / restart checkpoints:

- [../castp/checkpoint_2026_05_19_castp3_reproducibility_boundary.md](../castp/checkpoint_2026_05_19_castp3_reproducibility_boundary.md)
- [../castp/checkpoint_2026_04_28_castp3_oracle_parity_harness.md](../castp/checkpoint_2026_04_28_castp3_oracle_parity_harness.md)
- [../castp/checkpoint_2026_04_28_castp3_pycast_second_batch.md](../castp/checkpoint_2026_04_28_castp3_pycast_second_batch.md)
- [../castp/checkpoint_2026_04_28_castp3_pycast_small_batch.md](../castp/checkpoint_2026_04_28_castp3_pycast_small_batch.md)
- [../castp/checkpoint_2026_04_26_castp3_probe_limited_depth_audit.md](../castp/checkpoint_2026_04_26_castp3_probe_limited_depth_audit.md)
- [../castp/checkpoint_2026_04_23_castp1_functional_parity_closure.md](../castp/checkpoint_2026_04_23_castp1_functional_parity_closure.md)
- [../castp/castp1_original_build.md](../castp/castp1_original_build.md)

- [../castp/checkpoint_2026_04_20_castp1_redundant_vertices.md](../castp/checkpoint_2026_04_20_castp1_redundant_vertices.md)
- [../castp/checkpoint_2026_04_20_pre_parity_baseline.md](../castp/checkpoint_2026_04_20_pre_parity_baseline.md)
- [../castp/checkpoint_2026_04_10.md](../castp/checkpoint_2026_04_10.md)
- [../castp/checkpoint_2026_04_09.md](../castp/checkpoint_2026_04_09.md)
- [../castp/checkpoint_2026_04_07.md](../castp/checkpoint_2026_04_07.md)
- [../castp/checkpoint_2026_04_05.md](../castp/checkpoint_2026_04_05.md) (previous)

## CASTpFold Oracle Downloads

As of 2026-04-28, the server providers accept `output_zip_file`:

```python
topomt.third_party.castp.get_topography(
    pdb_path,
    backend='server',
    server='castpfold',
    probe_radius=1.4,
    wait=20,
    extra_wait=30,
    retries=3,
    output_zip_file='topomt/data/CASTpFold_server/1gcg.zip',
)
```

Use `CASTpFold` as the preferred oracle-download server while CASTp3 and
CASTpFold exports remain equivalent for the benchmark systems. The ZIP should
be persisted through `output_zip_file`; the older default path only loaded the
result from a temporary ZIP that was deleted at the end of the call.

Mouth parity must compare the same exported object. CASTpFold reports
`N_mth` as the number of topological mouths in `.pocInfo`, but `.mouth` records
are grouped by parent pocket/channel feature. The native `castp3` path therefore
keeps individual `topological_mouths` internally while exporting one aggregated
server-comparable mouth per parent feature in `mouths`.

Use `devtools/castp/compare_castp3_oracles.py` for native-vs-oracle CASTp3
parity checks. It compares stable PDB atom serials read from the oracle PDB
rather than raw Topography, MolSysMT-normalized, or geometry-local atom
indices. The CASTp3 native default selection is protein plus peptide molecules:
`molecule_type in ["protein", "peptide"]`.

## Current Code Split

As of 2026-04-24, the native CAST work is intentionally split into two code
paths:

- `topomt.third_party.castp`
- `topomt.third_party.castp3`

The purpose of this split is to protect the closed CASTp1 baseline while
allowing aggressive CASTp3/CASTpFold experimentation without contaminating the
stable path.

Current interpretation:

- `topomt.third_party.castp`
  - frozen reference implementation for the CASTp1-native line;
  - aligned with the CASTp1 closure documented in
    [../castp/checkpoint_2026_04_23_castp1_functional_parity_closure.md](../castp/checkpoint_2026_04_23_castp1_functional_parity_closure.md);
  - should not absorb speculative CASTp3 changes.

- `topomt.third_party.castp3`
  - isolated working copy created from `topomt.third_party.castp`;
  - dedicated to the CASTp3.0 / CASTpFold parity investigation;
  - safe place for experiments involving modern radii policy, input filtering,
    mouth/open-feature behavior, and any deeper geometry or flow changes that
    may diverge from CASTp1.

Implementation note:

- the `castp3` package is a real namespace copy with its internal imports
  rewritten to `topomt.third_party.castp3.*`;
- it is not a thin alias to `castp`;
- this separation is deliberate so that CASTp1 and CASTp3 can evolve
  independently from this point on.

It is intentionally separated from the current `topomt.third_party.castp._native_impl` prototype
and from the DFND line of work.

The goal is to implement the classical CAST/CASTp workflow, not a
DFND-style probe-flow reinterpretation.

This plan is based on three layers of evidence:

- the original CAST and CASTp papers;
- the CASTp 3.0 server outputs bundled as parity fixtures;
- and `pyCAST` as the clearest currently accessible open reexposition of the
  CAST algorithmic workflow.

Important caution:

- `pyCAST` is useful as a secondary methodological reference;
- it is **not** the TopoMT parity oracle for CASTp;
- and its public repository should not be treated as a fully authoritative
  executable reference for CASTp fidelity without qualification.

## Scope

The target is a native method that reproduces the classical CAST/CASTp output
semantics for:

- `pocket`
- `cavity`
- `channel`
- `mouth`

including:

- lining atoms;
- mouth/rim atoms;
- pocket/cavity/channel classification;
- number of mouths;
- mouth areas and lengths;
- pocket/cavity areas and volumes.

The canonical default probe radius remains:

- `1.4 Å`

## What this plan is not

This plan is **not**:

- a license to evolve the native path by local heuristics without checking the
  historical code and the CASTp 3.0 oracle;
- a DFND implementation under another name;
- or a proposal to base CASTp primarily on `R_insphere` / `R_gate` semantics.

Those quantities may still be useful elsewhere, but they are not the classical
CAST flow semantics that should define this method.

## Algorithmic reading of classical CAST/CASTp

The best current operational reading of the CAST workflow can be summarized as
follows.

1. Model the protein as a set of weighted points.
   - atoms contribute center coordinates and radii

2. Build the Delaunay / alpha-shape-related geometric structures.
   - the original CAST/CASTp papers clearly commit to alpha-shape and discrete
     flow foundations;
   - `pyCAST` makes the weighted-Delaunay reading explicit;
   - therefore weighted geometry should currently be treated as the leading
     implementation hypothesis, but still as something to verify carefully
     against parity outcomes

3. Represent the outside / exterior explicitly.
   - one practical way to do this is an infinity tetrahedron or equivalent
     dummy node;
   - this is a useful implementation device, but the papers do not expose it
     as a user-facing contract

4. Define the discrete-flow relation between neighboring tetrahedra.
   - this is the key topological step
   - it is not the same thing as DFND probe permeability

5. Compute the exterior-connected region under the discrete-flow relation.
   - the exact data structure may be phrased in terms of ancestors,
     descendants, sinks, or equivalent reachability machinery

6. Focus on tetrahedra that:
   - are outside the alpha complex;
   - and are not part of the exterior-connected region

7. Define connected components of that set.
   - these become the candidate topographic features

8. Delineate mouths and rim atoms.
   - mouths are the boundary openings of pockets with respect to the exterior

9. Distinguish pockets, cavities, and channels.
   - `pocket`: open feature with one mouth
   - `channel`: open feature with more than one mouth
   - `cavity` / `void`: buried feature with zero mouths

10. Compute the reported geometry.
   - pocket/cavity/channel area and volume
   - mouth area and length/circumference
   - lining atoms and mouth/rim atoms

## Architectural principles inside TopoMT

The native implementation should follow these internal rules.

### 1. Reuse `DelaunayMesh` as the substrate

`DelaunayMesh` should remain the shared geometric keystone.

However, CASTp should not be forced into the existing DFND network semantics.
The CAST implementation should instead build its own classical discrete-flow
layer on top of the mesh.

### 2. Keep CASTp semantics separate from DFND semantics

DFND:

- uses probe-dependent flow semantics based on local habitability and face
  permeability;
- is probe-physics-first.

CASTp:

- uses alpha-shape and classical discrete flow over tetrahedra;
- is topology/delineation-first.

Shared substrate is good.
Shared semantics by default is not.

### 3. Treat CASTp server exports as the parity oracle

The practical oracle for implementation is:

- `*.poc`
- `*.pocInfo`
- `*.mouth`
- `*.mouthInfo`

and the current downloaded CASTp 3.0 server fixtures.

The native implementation should be driven toward those outputs, not away from
them.

`pyCAST` may help interpret algorithmic steps, but parity decisions should be
resolved against:

- CAST/CASTp literature;
- and CASTp 3.0 server outputs.

## Proposed internal decomposition

The implementation should be split into small pieces.

### `topomt/third_party/castp/_native_impl.py`

Public method entry point.

Responsibilities:

- accept user-facing arguments;
- normalize probe radius and selection;
- invoke the internal CASTp engine;
- return structured pocket/cavity/channel dictionaries plus shared geometry if
  needed.

This file should stay thin.

### `topomt/third_party/castp/core/castp_core/geometry.py`

Responsibilities:

- construct or expose the Delaunay / alpha-complex-related geometry;
- isolate the geometry-specific details from the rest of the method.

Current status:

- this is now implemented on top of `WeightedDelaunayMesh`;
- the weighted mesh was recently corrected so that it preserves
  `oriented_simplices` instead of losing tetrahedron orientation by sorting;
- this matters because CAST/MKALF mouth connectivity depends on face/edge-facet
  orientation through `Fnext`.

The geometry choice must remain explicit and testable instead of being hidden.

### `topomt/third_party/castp/core/castp_core/discrete_flow.py`

Responsibilities:

- define tetrahedron-to-tetrahedron flow relations;
- represent the infinity tetrahedron `τ∞`;
- compute ancestors / descendants or equivalent reachability;
- separate exterior-connected tetrahedra from trapped components.

This is the heart of the classical CAST workflow.

### `topomt/third_party/castp/core/castp_core/components.py`

Responsibilities:

- build connected components of the trapped tetrahedra;
- classify components as pocket / cavity / channel;
- compute mouth counts.

### `topomt/third_party/castp/core/castp_core/mouths.py`

Responsibilities:

- delineate mouth boundary triangles;
- group mouth triangles by opening;
- identify rim atoms;
- compute mouth areas and lengths/circumferences.

Current status:

- the direct union of mouth faces across shared shape edges has been removed;
- the current code now restricts clustering to `Fnext`-style walks over open
  edges, matching the key MKALF rule;
- however, one red case remains (`1STP Pocket 7`), showing that faithful
  CASTp-3.0 mouth counting still needs additional work beyond that correction.

### `topomt/third_party/castp/core/castp_core/metrics.py`

Responsibilities:

- compute component volumes and areas;
- store the distinction between solvent-accessible and molecular-surface
  measures where possible;
- expose a structured dictionary ready for parity comparison.

## Recommended implementation slices

### Slice 1: Oracle-first validation

Before the native implementation is declared faithful:

- expand the CASTp loader parity battery on the downloaded server fixtures;
- keep `3ptb` tracked as a `molsysmt` parser blocker rather than hiding it;
- define test helpers that compare native output against CASTp exports by
  `source_id` and core metrics.

Status:

- already in progress

### Slice 2: Classical topology skeleton

Implement a first internal CASTp engine that:

- builds tetrahedral connectivity;
- defines the discrete-flow relation;
- identifies tetrahedra connected to infinity;
- identifies trapped connected components;
- classifies zero-mouth vs one-mouth vs multi-mouth components.

Success criterion:

- correct feature counts on the easiest audited systems

### Slice 3: Mouth delineation

Implement mouth grouping and rim-atom extraction faithfully.

Success criterion:

- correct mouth counts and basic mouth atom sets on audited systems

### Slice 4: Geometric metrics

Implement or reconcile:

- feature volumes;
- feature areas;
- mouth areas;
- mouth lengths/circumferences

Success criterion:

- parity on the metrics reported by `*.pocInfo` and `*.mouthInfo`

### Slice 5: Public `Topography` integration

Once the native engine is semantically stable:

- `_run_castp()` should emit `Pocket`, `Void`, `Channel`, and `Mouth`
  objects;
- mouth-to-pocket relations should be connected explicitly in `Topography`;
- the current heuristic “skip bulk solvent if atom count > 1000” should be
  removed.

## Immediate engineering decisions

These should be treated as fixed unless new evidence contradicts them.

1. Do not evolve the current `castp.py` prototype incrementally toward
   faithfulness.
   - rewrite it around the classical flow

2. Do not treat DFND's `R_insphere` / `R_gate` semantics as the classical CAST
   algorithm.
   - the methods are related only at the substrate level

3. Do not hide `molsysmt` PDB parser failures in CASTp loader work.
   - they must be reported upstream and tracked explicitly

4. Use CASTp exported files as the implementation oracle.

## Known blockers

### Geometry-substrate gap

The original CAST/CASTp papers clearly anchor the method in alpha shape and
discrete flow.

The strongest currently accessible open implementation reading (`pyCAST`)
further suggests weighted Delaunay geometry in the paper-level description.

However, the currently audited public `pyCAST` repository should not be treated
as confirming that weighted geometry operationally, because its public code path
does not currently provide a trustworthy weighted-Delaunay implementation.

TopoMT currently has:

- `DelaunayMesh`

but not yet a weighted Delaunay / regular triangulation substrate.

This means one early design choice must be made explicitly:

- either implement a weighted substrate now;
- or start with an approximation layer while keeping the weighted gap
  documented and tested against server parity.

That decision should not be hidden.

### MolSysMT parser blockers

Some CASTp-exported PDBs may still fail during `molsysmt` ingestion.

Current known case:

- `3ptb.pdb` from the CASTp 3.0 server zip battery

That must be tracked as an ecosystem issue, not normalized inside CASTp.

## Validation target systems

The current target server-export battery is:

- `1TCD`
- `1HIV`
- `1STP`
- `2PK4`
- `1A4J`
- `3PTB`

At the moment:

- five are usable as parity-import fixtures;
- `3PTB` is blocked by a `molsysmt` parser issue and should remain visible as
  such.

## End state

This work is finished only when all of the following are true:

- `castp` is no longer described as `CASTp-like`;
- the native method reproduces CASTp-style feature counts and classifications;
- mouths are explicit feature objects, not only scalar metadata;
- pockets, cavities, and channels are emitted distinctly;
- and the parity battery is based on real CASTp server outputs rather than on
  synthetic smoke tests.
