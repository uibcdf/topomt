"""Focused audit of reporting semantics in the native CASTp path."""

# Reporting Audit 2026-04-17

## Purpose

This note audits the native CASTp implementation specifically at the reporting
layer.

The question here is not:

> do we roughly find similar pockets?

The question is:

> do we report the same classes of objects, and the same kinds of geometric and
> topological information, as canonical CAST / MKALF?

## Historical baseline

The reporting contract in MKALF is much richer than a plain list of pockets.

From `print_pocket.c`, MKALF explicitly distinguishes and prints:

- `iT`: tetrahedra in the pocket
- `rF`: regular (mouth) triangles
- `iF`: interior triangles
- `rE`: regular (mouth) edges
- `iE`: interior edges
- `rV`: regular (mouth) vertices
- `iV`: interior vertices

From `voids.c`, these categories are not arbitrary postprocessing labels. They
are derived from:

- pocket union-find state
- `rank1`
- `rank2`
- `alf_is_in_complex`
- `alf_is_interior`
- and the touched/in-pocket marking passes for edges and vertices

From the 1998 papers, the public contract also includes:

- atoms lining pockets
- atoms lining pocket openings
- pocket area/volume
- mouth area
- mouth circumference
- cavities and their analogous measures

So the canonical reporting layer is not secondary decoration. It is part of the
algorithmic product.

## What our native path already reports correctly enough

### 1. Main feature families

The native path already reports:

- `void`
- `pocket`
- `channel`
- `branched_channel`

This is broadly aligned with CAST's public output style.

### 2. Tetrahedron membership

Each native feature record keeps:

- `tetrahedron_indices`

This is a direct analogue of the `iT` support, even if not exposed in the same
historical textual format.

### 3. Pocket / void atom sets

Each native feature record keeps:

- `atom_indices`
- `component_atom_indices`

So we already report a usable atom-level representation of the component.

### 4. Mouth count and mouth geometry

The native path already reports:

- `n_mouths`
- `mouth_area`
- `mouth_perimeter`
- per-mouth atom indices
- per-mouth face sets
- per-mouth `triangle_indices`

This is a meaningful subset of the CAST reporting contract.

## What is still conceptually missing

### 1. The full historical `iF/rF/iE/rE/iV/rV` partition is now present, but not yet in a CAST-shaped public contract

This is the most important gap in the reporting layer.

Canonical MKALF explicitly separates:

- interior faces
- regular mouth faces
- interior edges
- regular mouth edges
- interior vertices
- regular mouth vertices

The raw native records now expose these sets explicitly, and `_native_impl.py`
preserves them.

What is still conceptually open is narrower:

- the public contract is still TopoMT-shaped rather than a literal CAST
  print/export contract
- downstream consumers have not yet been audited systematically against these
  new reporting fields

Conceptual implication:

- this is no longer a primary missing reporting layer

### 2. Mouth circumference is no longer missing

The CAST paper explicitly states that CAST reports:

- mouth area
- mouth circumference

Our native mouth records now keep:

- `area`
- `perimeter`
- `faces`
- `atom_indices`

So this item is now closed at the native reporting level.

### 3. Feature surface area is now present, but the full CAST-derived geometry layer is not yet audited closed

The papers emphasize:

- area and volume of pockets and cavities

Our current native records expose:

- `area`
- `volume`
- `mouth_area`

This closes the old gap where pockets and cavities had no explicit feature-area
field at all.

What remains open is whether every CAST-side derived geometric summary is now
covered, not whether feature area itself is absent.

### 4. `boundary_atom_indices` is only a partial analogue of canonical `rV`

The native `boundary_atom_indices` is much better than the old boundary-face
shortcut, but it is still only one projection of the historical reporting
partition.

What it captures:

- a notion close to regular pocket vertices (`rV`)

What it does **not** capture:

- explicit `iV`
- explicit edge partition
- explicit face partition

So `boundary_atom_indices` should not be confused with "we already have the
historical reporting layer".

### 5. `_native_impl.py` still compresses the reporting layer further

In `_native_impl.py`, `_component_to_record()` still reduces the raw feature
record to TopoMT-style output fields.

- `atom_indices`
- `boundary_atom_indices`
- `mouths`
- `properties`

But that compression is now weaker than before, because the wrapper already
preserves:

- `iF/rF/iE/rE/iV/rV`
- mouth `triangle_indices`
- mouth `perimeter`
- feature `area`

Conceptual implication:

- the public native API is still not a literal CAST print contract, but it no
  longer erases the main canonical reporting partitions

### 6. The output is still TopoMT-shaped, not CAST-shaped

This matters conceptually.

Right now the output is optimized for integration into the TopoMT ecosystem:

- normalized feature records
- source/source_id
- physicochemical properties
- feature-type normalization

That is reasonable for library design, but it is not the same thing as
reproducing CAST's own reporting contract.

So there are really two different questions:

1. can TopoMT represent CAST-like results?
2. does the native path currently reproduce the reporting semantics of CAST?

The answer to the second question is still: not fully.

## What is already conceptually strong

The native code is no longer weak at the level of:

- feature taxonomy
- mouth count
- atom-level component support
- per-mouth face clustering

So the reporting gap is **not** that we only have a vague summary.
The gap is that we still do not materialize the full canonical partition and
the full public geometry contract.

## Summary judgement

If we ask:

> Does the native reporting layer already match canonical CAST / MKALF?

the answer is:

- **no**

The main remaining reasons are:

1. the public surface is still TopoMT-shaped rather than CAST-shaped
2. some CAST-style derived summaries may still be absent or unaudited
3. `_native_impl.py` still normalizes output instead of mirroring the
   historical print contract

## Priority within the remaining conceptual gaps

Compared with the other major conceptual fronts:

- triangulation / SoS
- exact rank equivalence
- literal `mu1/mu2`

the reporting gap is probably **not** the first one to attack if the goal is
topological fidelity.

But if the goal is:

> a native implementation faithful to canonical CAST as an algorithmic product

then the reporting layer remains a first-class open front.

## Practical consequence

The native path can already be strong enough for many parity comparisons based
on feature atom sets.

But we still cannot honestly claim:

> we already reproduce the canonical CAST output semantics

until the reporting layer is extended beyond the current reduced
TopoMT-oriented projection.
