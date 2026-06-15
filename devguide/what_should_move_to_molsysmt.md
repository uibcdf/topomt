# What Should Move to MolSysMT

## Purpose

TopoMT should not become a second molecular-systems library.

When a piece of functionality is a general observable, geometry primitive, or
system-level helper that is useful beyond topography, it should be proposed to
`molsysmt` and, when accepted, moved there.

This document records the rule and the current candidate areas.

## Design rule

Use this rule when deciding where new code belongs:

- keep in `topomt` anything that is specific to topography, features, or the
  semantics of a detection engine;
- propose to `molsysmt` anything that describes a molecular system in a
  general way and could be reused by other packages.

In practice:

- `Topography`, `Pocket`, `Channel`, `Mouth`, feature hierarchies, and
  engine-specific scoring stay in TopoMT;
- generic geometry kernels, molecular observables, and reusable system
  descriptors should tend to move to `molsysmt`.

## Expected workflow

When a reusable primitive is detected while developing TopoMT:

1. implement the smallest safe local version needed to keep progress moving;
2. document the candidate here;
3. open the proposal with the `molsysmt` team;
4. once accepted and stable, replace the local TopoMT implementation with the
   `molsysmt` version.

The local TopoMT copy should be treated as transitional unless there is a
clear reason to keep it here.

## Good candidates for `molsysmt`

### Atomic and element-level helpers

- atom-type inference from molecular records;
- element-aware atom radii lookup;
- electronegativity lookup;
- atom classification helpers such as heavy-atom masks, ion masks, and water
  masks.

These are not topography-specific. TopoMT needs them, but so can other
MolSysSuite packages.

### Generic molecular geometry

A sharp distinction decides whether geometry belongs in `molsysmt`:

- **Molecular geometry** — operates on a molecular system (atoms, coordinates,
  units, selections) — *does* belong in `molsysmt`. Examples: surrounding-atom
  queries around atom selections, neighbor kernels, point-to-atom distance and
  overlap tests. Most of these now exist there (`structure.get_neighbors`,
  `structure.get_distances`, `structure.get_contacts`).
- **Abstract computational geometry** — operates on bare NumPy arrays of points,
  centers, and radii with no molecular-system semantics — does *not* belong in
  `molsysmt`. Examples: Monte-Carlo union-of-spheres volume, voxel grid volume,
  triangle area, plane fitting, group overlap matrices. These stay in TopoMT (or
  a dedicated geometry utility), never in `molsysmt`.

The litmus test: if the function needs a molecular system to do its job, it can
move; if it only needs arrays, it cannot. This same decision is raised in the
MolSysMT proposal `topomt_requested_spatial_helpers_and_sasa.md` and is answered
the same way here.

These are building blocks, not feature semantics.

### Surface and accessibility observables

- SASA or ASA calculations for arbitrary atom selections;
- per-atom accessible surface estimates;
- generic exposed-area decompositions that do not depend on a specific pocket
  method.

TopoMT may consume these values, but they are molecular observables in their
own right.

### Reusable cavity-adjacent descriptors

- generic local packing density around atom sets;
- generic cavity-surrounding atom descriptors;
- generic buriedness or exposure observables that are not tied to one engine.

These should move only if they are formulated independently of `fpocket`,
`alphaspace2`, `pocketeer`, or another named method.

## Things that should stay in TopoMT

- the `Topography` object model;
- `Feature` subclasses and their hierarchy;
- `atom_indices` as topographic feature membership;
- alpha-sphere aggregation into pockets, mouths, channels, or other features;
- engine-specific clustering rules;
- engine-specific scores and druggability models;
- conversions from engine-native outputs into TopoMT features.

These are the core reason TopoMT exists.

## Status (2026-06-14)

A fresh audit of the native DFND/TopoMT boundary against the current `molsysmt`
surface shows that most historical candidates have **already been absorbed by
`molsysmt`**, and TopoMT already consumes them:

- element-aware atomic radii lookup -> `physchem.get_atomic_radius`
  (`definition='vdw'` / `'protor'`); used by DFND and `get_delaunay_mesh`;
- surrounding-atom / neighborhood queries -> `structure.get_neighbors`
  (threshold and fixed-count modes);
- point-to-atom distance and overlap -> `structure.get_distances`,
  `structure.get_contacts`;
- SASA / ASA, surface area, buriedness -> `physchem.get_sasa`,
  `get_surface_area`, `get_area_buried`, `get_buried_fraction`;
- heavy-atom / water / ion masks -> the `molsysmt` selection language.

The doc's earlier "good candidates" list is therefore largely **resolved**: it
predates these additions. TopoMT is not hoarding general molecular helpers — the
audit found none rolled locally beyond the items below.

Open items already filed as `molsysmt` proposals:

- `proposal_protor_atom_typing_and_radii.md` — implicit-hydrogen-aware ProtOr
  radii (relevant to DFND's hydrogen-excluded meshes; see
  `DFND/radius_convention_decision.md`);
- `topomt_requested_spatial_helpers_and_sasa.md` — configurable `probe_radius`
  in `physchem.get_sasa`, and the molecular-vs-abstract geometry decision.

The one genuinely **unfiled** candidate:

- **per-element electronegativity / polarity property** in `physchem`. It would
  subsume the hard-coded `probe_weights` element heuristic in
  `topomt/tools/features/pockets/contacts.py` (`{'C','N','O','X'}`). `molsysmt`
  currently has `physchem.get_polarity` only per residue group, not per element.
  See the `molsysmt` proposal `physchem_electronegativity_per_element.md`.

The local `probe_weights` heuristic stays in TopoMT until that property exists
upstream; it is then a candidate to source from `molsysmt`.

## Review policy

Whenever a new helper is added to TopoMT during engine work, contributors
should ask:

- is this topography-specific?
- would another MolSysSuite package plausibly need it?
- would moving it to `molsysmt` reduce duplicated logic across the ecosystem?

If the answer to the last two questions is yes, the default action should be
to propose it to `molsysmt`.
