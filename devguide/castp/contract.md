# `castp` Contract

## Purpose

This document defines what TopoMT should mean by a faithful `castp`
implementation and which external artifacts should be treated as the parity
oracle.

## Canonical external basis

The external semantic reference for `castp` is CASTp 3.0 and its historical
CAST geometric basis:

- CAST original paper:
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC2144175/>
- CASTp 3.0 paper:
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC6031066/>

From those sources, the important points are:

- CAST/CASTp is based on `alpha shape` and `discrete flow` ideas;
- the method delineates `surface pockets`, `interior cavities`, and `cross
  channels`;
- it reports `mouth openings` explicitly;
- it reports `lining atoms`;
- and it measures volumes and areas analytically.

This means a faithful TopoMT `castp` path is not merely a connected-components
clusterer over filtered alpha spheres or filtered tetrahedra.

## Canonical default

Unless a test or fixture explicitly states otherwise, the canonical CASTp probe
radius must be treated as:

- `probe_radius = 1.4 Å`

That default should be used in:

- method documentation;
- parity fixtures from the CASTp server;
- and future native `castp` parity tests.

## What TopoMT must reproduce

For a native `castp` implementation to be considered faithful, it should
reproduce the following classes of output from CASTp exported results:

1. feature classification
- `pocket`
- `cavity`
- `channel`

2. feature delineation
- atoms lining each feature;
- atoms lining each mouth;
- stable mapping from exported CASTp identifiers to TopoMT features

3. analytical geometry
- solvent-accessible area;
- molecular-surface area;
- solvent-accessible volume;
- molecular-surface volume;
- mouth areas;
- mouth lengths/circumferences where available

4. topology
- number of mouths per pocket;
- distinction between open pockets and buried cavities;
- explicit treatment of exterior/bulk solvent

## Current practical oracle

Today the most reliable external oracle available inside the repository is the
set of CASTp exported files, not a local CASTp package or binary:

- `.poc`
- `.pocInfo`
- `.mouth`
- `.mouthInfo`

TopoMT already ships two CASTp-derived demo directories:

- `topomt/data/TcTIM/CASTp_1tcd`
- `topomt/data/HIV-1-Protease/CASTp_1hiv`

These fixtures should be treated as the first real parity-import battery.

Important import semantics:

- `.pocInfo` lists pocket-level analytical metrics;
- `.mouthInfo` lists mouth-level analytical metrics, including entries with
  zero mouths or zero triangles;
- `.poc` determines which pocket features are actually instantiated as
  TopoMT `Pocket` objects;
- `.mouth` determines which mouth features are actually instantiated as
  TopoMT `Mouth` objects.

In particular, `mouthInfo` may contain rows with `N_mth = 0`, but only mouths
present in `.mouth` should materialize as `Mouth` features in `Topography`.

## Current status of `topomt.methods.castp`

The current [topomt/methods/castp.py](/home/diego/repos@uibcdf/topomt/topomt/methods/castp.py)
implementation should be treated as a preliminary `CASTp-like` prototype, not
as a faithful CASTp implementation.

What it currently does:

- builds a `DelaunayMesh`;
- filters alpha-sphere/tetrahedral void proxies by a probe threshold;
- clusters connected components;
- estimates mouths from unshared local faces;
- computes a partial geometric summary

What it does **not** yet reproduce faithfully:

- explicit exterior/bulk-solvent classification;
- robust pocket vs cavity vs channel separation;
- CAST-style mouth delineation;
- direct parity against CASTp exported files;
- analytical solvent-accessible vs molecular-surface contracts aligned with
  CASTp server outputs

## Implementation target for the native path

The future native `castp` path should be rebuilt around:

- `DelaunayMesh` as the geometric substrate;
- an explicit CAST-style outside/exterior classification step;
- topological delineation of pocket, cavity, and channel regions;
- explicit mouth detection;
- and output dictionaries or features that can be matched directly against
  CASTp exported files.

## Validation target

Validation should proceed in two layers.

### 1. Loader parity

`load_CASTp()` must faithfully import CASTp exported files into `Topography`,
preserving:

- feature counts;
- source IDs;
- atom membership;
- analytical metrics from `*.pocInfo` and `*.mouthInfo`

This is already a real, testable target.

### 2. Native-method parity

`topomt.methods.castp.castp()` should eventually be validated against CASTp
server exports for a curated battery of PDB systems.

The first requested expansion set is:

- `1TCD`
- `1HIV`
- `1STP`
- `2PK4`
- `1A4J`
- `3PTB`

## Near-term engineering steps

1. keep the loader parity battery green and expand it;
2. treat bundled CASTp exports as the oracle;
3. rewrite the native method against that oracle instead of evolving the
   current clustering prototype ad hoc;
4. only then promote `castp` from `CASTp-like` to faithful native method
   status.
