# DFND Input Policy

This document defines the first working input and radius policy for DFND.

The purpose is reproducibility. DFND should record exactly what molecular
material was used, what atoms were filtered, and what radii were assigned.

## 1. Default Atom Set

Initial default:

- use the selected molecular system as provided through MolSysMT;
- exclude hydrogens by default in the first implementation;
- use heavy atoms for the Delaunay substrate;
- keep the exact selected atom indices in raw records.

Open discussion:

- whether polar hydrogens should be included for some modes;
- whether a hydrogen-implicit radius model should become the preferred protein
  mode;
- whether waters, ions, cofactors, and ligands should be included by default or
  controlled through explicit selection presets.

## 2. Radius Model

Initial default:

- use MolSysMT van der Waals radii.

Reason:

- simple;
- broadly applicable;
- sufficient for the first DFND implementation and debugging phase.

Planned alternatives:

- CASTp3 or CASTpFold ProtOr-style protein radii;
- ligand-aware radii;
- element-only fallback radii;
- user-supplied radii.

Raw records must include:

- radius model name;
- per-atom radius values;
- per-atom element and atom identity where available;
- fallback flags for atoms whose radius was not assigned by the primary model.

## 3. Alternate Locations and Occupancy

DFND v1 does not implement an alternate-location policy. Alternate-location
resolution belongs upstream in MolSysMT.

Current policy:

- DFND assumes MolSysMT provides one resolved coordinate per selected atom;
- DFND does not expose `altloc_policy` in v1;
- DFND does not duplicate MolSysMT tests for alternate-location resolution;
- DFND validates only the final geometry it receives: finite coordinates,
  positive finite radii, consistent atom indices, and enough atoms for
  triangulation.

MolSysMT already provides and tests `solve_atoms_with_alternate_location(...)`,
including occupancy-based selection and the `A` conformer tie-break for 0.5
occupancy ties. Users who need explicit alternate-location control should apply
that preprocessing in MolSysMT before calling DFND.

Occupancy policy:

- atoms with occupancy less than one are still real coordinates unless they are
  alternative positions of the same atom;
- DFND does not drop partial-occupancy atoms blindly;
- if alternative positions exist, the molecular input should be resolved
  upstream before DFND receives it.

## 4. Waters, Ions, Ligands, and Cofactors

Default policy is still open.

Recommended first implementation:

- expose selection explicitly and do not hard-code a biochemical filter inside
  the geometry engine;
- provide convenience presets later, such as `protein_only`,
  `protein_and_cofactors`, or `include_waters`;
- record all excluded residue or molecule categories.

Reason:

- CASTp3, CASTpFold, fpocket, and other tools differ in preprocessing;
- DFND should not hide those choices;
- pocket topology can change significantly when waters, ions, or ligands are
  included.

## 5. B-Factors and Coordinate Uncertainty

B-factors may contain useful information about coordinate uncertainty or local
mobility, but they should not modify atom positions or radii in the first DFND
implementation.

First working policy:

- read and preserve B-factors when available;
- report B-factor summaries for features if useful;
- do not inflate radii or move coordinates based on B-factors by default.

Future experimental modes:

- uncertainty-aware tolerance scaling;
- B-factor-weighted marginal classification;
- ensemble generation from coordinate uncertainty;
- feature confidence scores using local B-factor statistics.

Any B-factor correction that affects geometry must be explicitly opt-in and
reported in raw records.

## 6. Coordinate Precision

Input coordinate precision can affect near-threshold decisions.

First working policy:

- preserve coordinates as float64 internally;
- report the input format when possible;
- do not round coordinates during DFND computation;
- allow the numerical policy to use input-aware tolerances later.

Open discussion:

- whether PDB-derived coordinates should imply a looser epsilon than mmCIF or
  high-precision arrays;
- whether repeated trajectory frames should use a trajectory-wide tolerance.

## 7. API Output Policy

Current v1 policy:

- `dfnd(...)` is the raw-first development and validation API;
- `get_topography(method='dfnd')` is the public TopoMT integration API;
- `get_topography(method='dfnd')` returns a normal `Topography` object;
- raw DFND records are attached as `topography.dfnd_records`;
- the complete raw-first result is attached as `topography.dfnd_result` while
  the method is being hardened.

Only stable compatibility domain families are converted to public `Topography`
features in v1: `void_domain`, `pocket_domain`, and
`multi_external_link_domain`. Provisional domain families remain available in
raw records until their public semantics are validated.

The detailed public contract is `api_contract_v1.md`.

## 8. Minimal Provenance

Every DFND result should store:

- input source or object description;
- selected atom indices;
- excluded atom indices, if any;
- atom radii;
- radius model;
- probe radius;
- tolerance policy;
- coordinate units;
- whether hydrogens were included;
- whether waters, ions, ligands, or cofactors were included;
- software version and DFND policy version.
