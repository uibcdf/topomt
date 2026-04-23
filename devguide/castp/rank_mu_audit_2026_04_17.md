"""Focused audit of rank and mu semantics in the native CASTp path."""

# Rank and `mu1/mu2` Audit 2026-04-17

## Purpose

This note audits the current native CASTp implementation specifically at the
level of:

- rank semantics
- `alf_is_in_complex`
- `alf_is_interior`
- `mu1` / `mu2` propagation

The goal is to separate three categories clearly:

1. things that are already semantically aligned with MKALF
2. things that are still reconstructions but look conceptually correct
3. things that remain open canonical gaps

## Historical baseline

The operational baseline in MKALF is explicit.

From `lookup.c`:

- `alf_is_in_complex(ALF_VERTEX/EDGE/TRIANGLE, rank, i)` is:
  - `rho <= rank` if `rho != 0`
  - `mu1 <= rank` if `rho == 0`
- `alf_is_in_complex(ALF_TETRA, rank, i)` is:
  - `rho <= rank`
- `alf_is_interior(ALF_VERTEX/EDGE/TRIANGLE, rank, i)` is:
  - `mu2 <= rank`
- `alf_is_interior(ALF_TETRA, rank, i)` is:
  - `rho <= rank`

From `spectrum.c`:

- the spectrum is built from `rho` events only
- `triangle_mus()` propagates tetrahedron rho ranks to triangle `mu1/mu2`
- `edge_mus()` propagates triangle ranks to edge `mu1/mu2`
- `vertex_mus()` propagates edge ranks to vertex `mu1/mu2`
- hull faces / edges / vertices get `mu2 = 0` after propagation

So the conceptual shape is very clear even when the exact low-level data
structure differs.

## What is already semantically aligned

### 1. `alf_is_in_complex` semantics

The native helpers:

- `_rank_table_is_in_complex`
- `_face_is_in_complex_at`
- `_edge_is_in_complex_at`
- `_vertex_is_in_complex_at`

now implement the correct branch logic:

- `rho != 0 -> rho <= rank`
- `rho == 0 -> mu1 <= rank`

This matches the historical lookup contract.

Assessment:

- semantically aligned
- no longer a leading canonical concern

### 2. `alf_is_interior` semantics

The native helpers:

- `_rank_table_is_interior`
- `_vertex_is_interior_at`

follow the correct historical rule:

- `mu2 == 0 -> not interior`
- otherwise `mu2 <= rank`

Assessment:

- semantically aligned

### 3. Spectrum support is conceptually built from `rho` only

The operational geometry path now assigns ranks from exact `rho` events only.

This is aligned with the historical contract:

- no `mu1`
- no `mu2`

inside spectrum construction.

Assessment:

- semantically aligned

### 4. Face `mu1/mu2` propagation follows the historical rule conceptually

The native code derives face `mu1` / `mu2` from incident tetrahedron rho ranks:

- `mu1 = min(incident tetra rho ranks)`
- `mu2 = max(incident tetra rho ranks)`
- hull faces get `mu2 = 0`

That is conceptually the same rule as `triangle_mus()`.

Assessment:

- semantically close enough to MKALF
- still generated through native data structures, not literally through `TrIndex`

### 5. Edge `mu1/mu2` propagation now follows the right historical branch logic

The native `_edge_mu_rank_maps()` now matches the historical `edge_mus()` rule:

- if triangle `rho != 0`, candidate `mu1` comes from triangle `rho`
- if triangle `rho == 0`, candidate `mu1` comes from triangle `mu1`
- `mu2` is the max propagated `face_mu2`
- hull edges get `mu2 = 0` after propagation

Assessment:

- semantically aligned
- implementation is still a reconstruction, but the rule is the right one

### 6. Vertex `mu1/mu2` propagation follows the right historical branch logic

The native `_vertex_mu_rank_arrays()` follows the same conceptual rule as
`vertex_mus()`:

- if edge `rho != 0`, candidate `mu1` comes from edge `rho`
- if edge `rho == 0`, candidate `mu1` comes from edge `mu1`
- `mu2` is propagated from incident edge `mu2`
- hull exposure resets `mu2 = 0`

Assessment:

- semantically aligned in branch structure

## What is still reconstruction, not literal identity

### 1. Rank lookup from threshold values still uses float support

The native helpers:

- `_rank_of_value(...)`
- `_probe_rank(...)`

still recover ranks from `spectrum_values` as float thresholds via
`np.searchsorted(...)`.

This is conceptually plausible, but it is not literally the same as querying a
historical exact-rank structure.

Why it matters:

- `base_rank = rank(0.0)`
- `rank2 = rank(probe^2)`

are central thresholds for the whole algorithm.

Assessment:

- still a real canonical gap
- probably the single most important open issue in the rank layer

### 2. `mu1/mu2` are still generated over our own mesh and indexing layer

Even when the branch logic is right, the implementation still depends on:

- our triangulation
- our face ownership
- our edge keys
- our vertex indexing

That means the native path still computes the historical semantics through a
different substrate.

Assessment:

- conceptually close
- not yet a literal MKALF port

### 3. Face attachedness still depends on our own face-level reconstruction

The attached/unattached split for triangles is decided by native evaluation of
the weighted predicates over the current triangulation.

The branch structure is consistent with MKALF, but this still sits on top of:

- our triangulation
- our neighbor relation
- our face ownership

Assessment:

- still reconstruction, not identity

## What remains a primary open gap

### 1. Exact rank equivalence is still not demonstrated

Even after the exact-ratio machinery, the full question is still open:

> do our assigned ranks coincide with MKALF's relevant operational ranks on the
> cases that matter?

This is not yet proved.

Why it remains primary:

- every `is_in_complex`
- every `is_interior`
- every pocket threshold
- every mouth openness decision

depends on the rank scale.

### 2. Rank thresholds still sit on a non-canonical triangulation substrate

Even if the rank branch logic is correct, the underlying simplices are still
those of the native triangulation, not DELCX/SoS.

So the rank layer cannot yet be declared literally canonical independently of
the triangulation substrate.

### 3. Reporting still does not expose the full historical rank-driven partition

Even if membership semantics are correct, the current public reporting layer
still does not fully materialize:

- interior faces / edges / vertices
- regular faces / edges / vertices

in the way MKALF internally does.

So the rank layer is semantically stronger than the public reporting layer.

## Summary judgement

### What is strong now

The **semantics** of rank-table lookup are now in good shape:

- `is_in_complex`
- `is_interior`
- face/edge/vertex `mu1/mu2` branch logic

These should no longer be treated as the most suspicious part of the native
path.

### What is still open

The remaining problems are not mostly in the branch logic anymore.
They are in:

1. exact equivalence of the assigned rank scale
2. dependence on the native triangulation substrate
3. the fact that `mu1/mu2` are still reconstructed over our own mesh/indexing
4. incomplete public reporting of the historical rank-driven partition

### Practical consequence

If we ask:

> Are we already using the right `rho/mu1/mu2` semantics?

the answer is:

- **mostly yes**, at the semantic branch level

If we ask:

> Are we already proving literal identity with MKALF in the whole rank layer?

the answer is still:

- **no**

And the main reason is no longer the local branch logic, but the combination of:

- exact rank-scale equivalence
- native triangulation substrate
- and reconstruction through our own mesh layer
