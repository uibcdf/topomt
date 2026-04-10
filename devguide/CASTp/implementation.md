# CASTp Native Implementation Plan

## Purpose

This document describes a from-scratch implementation plan for a faithful
native `castp` path in TopoMT.

Latest restart checkpoint:

- [../castp/checkpoint_2026_04_07.md](../castp/checkpoint_2026_04_07.md)
- [../castp/checkpoint_2026_04_05.md](../castp/checkpoint_2026_04_05.md) (previous)

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

- a continuation of the current connected-components prototype in
  [topomt/third_party/castp/_native_impl.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/_native_impl.py);
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

Important note:

- current `DelaunayMesh` is not weighted;
- `pyCAST` strongly suggests weighted Delaunay as the faithful interpretation;
- therefore this part may initially need either:
  - a temporary approximation layer;
  - or a proper weighted substrate;
- but the geometry choice must stay explicit and testable instead of being
  hidden.

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
