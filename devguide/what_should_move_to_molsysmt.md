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

- surrounding-atom queries around atom sets or point clouds;
- geometric neighborhood kernels;
- generic point-to-atom distance and overlap tests;
- sphere sampling utilities used by accessible-surface calculations;
- reusable Delaunay/Voronoi-facing helpers if they remain system-agnostic.

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

## Current candidates observed during native engine work

The current `fpocket4` and `alphaspace2` work suggests that the following are
strong candidates for `molsysmt` discussion:

- stable atom-type and element inference from PDB/mmCIF inputs;
- atomic radii lookup exposed through a public and robust API;
- generic ASA/SASA primitives;
- generic sphere-point sampling utilities;
- reusable atom-neighborhood queries around arbitrary point sets.

Some of these already exist partially in `molsysmt`, but the policy here is to
prefer strengthening and centralizing them there instead of growing parallel
helpers inside TopoMT.

## Review policy

Whenever a new helper is added to TopoMT during engine work, contributors
should ask:

- is this topography-specific?
- would another MolSysSuite package plausibly need it?
- would moving it to `molsysmt` reduce duplicated logic across the ecosystem?

If the answer to the last two questions is yes, the default action should be
to propose it to `molsysmt`.
