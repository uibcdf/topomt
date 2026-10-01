# DFND Synthetic Benchmarks

Design note recorded on 2026-05-22 (updated the same day with the implemented
battery). It specifies a battery of synthetic structures (dummy atoms in simple
geometries) used to validate and explore DFND before real molecular systems, and
to compare against other detectors on controlled inputs.

**Status: implemented.** Generators live in `topomt/dfnd/synthetic.py`; the
parametric catalog (PDBs + an auto-labelled README) is built by
`python devtools/dfnd/build_synthetic_catalog.py` and written to
`topomt/data/synthetic/`. Assertions live in
`tests/test_dfnd_synthetic_benchmarks.py` (26 tests, all green). The battery is
designed to grow: parametric variants of a shape (a neck width, a mouth angle, a
probe) are first-class catalog entries.

## Purpose

Current reference policy (2026-10-01): see the
[notebook laboratory checkpoint](notebook_laboratory_checkpoint.md). These
generators provide controlled geometry; their shape names do not establish
ground truth for the discrete union-of-balls model. A sampled spherical shell
may leak through interatomic gaps and need not have the continuum sphere's
volume. Freeze and justify independent observables for each adopted case before
turning construction expectations into assertions. The tables below retain
historical intended shapes and observations, rather than certify every label.

This layer sits between two existing layers:
- [`toy_systems_v1.md`](toy_systems_v1.md): micro contract fixtures (4–13 atoms,
  hand-crafted to hit specific families/edge cases — unit-test level).
- [`validation_plan.md`](validation_plan.md) §1.3+: real small systems and
  benchmarks.

These synthetic shapes are the **meso-scale controlled-input** middle layer.

## Design Principles

- **Dummy atoms = argon** (single van der Waals radius, ≈ 1.88 Å). A single radius
  is the symmetric case where `R_gate` is exact, and keeps the geometry clean and
  controllable. Mixed radii can come later.
- **Parametric generator**: each shape produced from parameters (size, wall
  spacing, atom radius, optional jitter), not hand-written PDBs — reproducible and
  sweepable. Write PDBs (or arrays via `DelaunayFlowNetwork.from_coordinates_and_radii`).
- **Probe-tight walls** (critical, see below): a hollow shape only encloses a
  cavity if its wall is impermeable to the probe.
- **Two variants per shape**: a perfectly regular version (degeneracy stress test)
  and a slightly jittered version (stable, realistic).

## The Shape Battery (implemented)

Organized in tiers by difficulty. Parametric variants (a neck width, a mouth
angle, a probe radius) are separate catalog entries; the list is meant to grow.

**Tier A — simple**
| Shape | Expected | Notes |
|---|---|---|
| `tetrahedron` | minimal cell | sanity baseline |
| `hollow_sphere` | void (0 links) | best analytic volume benchmark |
| `hollow_sphere_with_opening` | pocket (1 mouth) | one polar cap removed |
| `cylinder_tube` | channel (≥2 mouths) | open tube |
| `solid_ball` | none | **negative control** |
| `blind_well` | pocket | bored well; depth variants |
| `slab_with_pore` | channel | through-pore |
| `two_voids` | 2 voids | counting / separation |
| `surface_bowl` | pocket + surface texture | dent + studied grid texture |

**Tier B — average**
| Shape | Expected | Notes |
|---|---|---|
| `branched_tube` | channel (3 mouths) | Y/T junction (lumen-cleared) |
| `nested_spheres` | 2 voids | cavity inside a cavity |
| `curved_tube` | channel (2 mouths) | curvature-independent detection |
| `flask` | void↔pocket as neck varies | throat gating |
| `hollow_sphere_two_openings` | pocket↔channel | **marginal mouth** threshold |

**Tier C — sophisticated / anomalous**
| Shape | Expected | Notes |
|---|---|---|
| `asymmetric_dumbbell` | 1→2 voids vs probe | offset throat |
| `swiss_cheese` | one mega-cluster | **percolation** |
| `void_with_island` | 1 void | genus not tracked (documented) |
| `helical_tube` | channel (2 mouths) | complex 3D path |
| `onion_shells` | 3 voids | nested counting |

**Tier D — adversarial (where other detectors can fail)**
| Shape | Expected | Why adversarial |
|---|---|---|
| `sliver_sheet` | no void/channel | alpha-shape sliver false-tunnel trap |
| `dumbbell` @ sep 12.5 | 1 void @1.5 → 2 @1.6 | **fusion/separation** in a 0.1 Å window |
| `pocket_with_mouth_intruder` | pocket→void w/ 1 atom | **4th-atom intrusion** over a 3-atom gate |
| (rotated `hollow_sphere`) | identical void | **orientation invariance** (vs grid/voxel) |
| `flask` @ neck 3.0 | void @1.4 → pocket @1.0 | **cryptic/gated** site (probe-dependent) |
| `rough_surface` | tiny spurious spray | sub-probe **over-reporting** study |

**Tier E — interfaces (dry banks + wet gap)** — model in [`interfaces.md`](interfaces.md)
| Shape | Expected | Notes |
|---|---|---|
| `two_blocks` | 2 dry banks + shared wet interface | fuses to 1 body below ~5 Å gap |
| `three_blocks` | 3 dry banks, 2 interfaces | multi-interface counting |
| `interface_pocket` | buried pocket lined by both bodies | **protein-protein interface cavity** (biological case) |

## Probe-Tight Wall Spacing (make-or-break)

A shell only seals a cavity if the probe cannot leak through the gaps between wall
atoms. The limiting leak is the 3-atom gate of a wall triangle. For equal radii
`r_a` and wall spacing `d` (nearest-neighbor centers), the equilateral 3-atom gate
is approximately:

```text
R_gate ≈ d / sqrt(3) - r_a
```

Impermeability to a probe of radius `R_probe` requires `R_gate < R_probe`:

```text
d < sqrt(3) * (r_a + R_probe)
```

For argon (`r_a ≈ 1.88`) and the water probe (`R_probe = 1.4`): `d < ≈ 5.7 Å`. Use
a comfortable margin — **wall spacing ≈ 3.5–4.5 Å** gives a clearly sealed wall;
≈ 3.76 Å is argon-touching (fully sealed). Document the chosen spacing per shape so
the void/channel result is reproducible.

(For fixed coordinates and radii, increasing `R_probe` above the gate threshold
seals that gate; decreasing it below the threshold opens it. Residence may also
be lost at a separate, larger threshold. Marginal epsilon cases require separate
numerical-policy checks.)

## Delaunay Degeneracy of Regular Lattices

Perfect cubic / spherical lattices are near-cospherical → the worst case for
Delaunay non-uniqueness and slivers (the WP4 limitation in
[`known_limitations.md`](known_limitations.md)). Run each shape **both ways**:
- **Perfect lattice**: a deliberate degeneracy stress test (does DFND stay sane?).
- **Small jitter** (e.g. ±0.1–0.3 Å): breaks exact degeneracies → stable, the
  default for ground-truth assertions.

## Metrics and Assertions

For each independently reviewed shape, establish which observables are justified:
- expected **family** and **number of external links**;
- **solvent volume estimate** vs an independent reference for the same ball model
  and volume definition, with a justified tolerance; an ideal continuum cavity
  is not automatically that reference;
- **probe sweeps**: vary `R_probe` and check justified family transitions (e.g.
  leaky→sealed as the probe exceeds the wall threshold). The
  sweep is a strong demonstration of DFND's volume/connectivity decoupling.

## Cross-Algorithm Comparison

The repository already carries oracle data and harnesses for CASTp, fpocket,
AlphaSpace2, and CASTpFold (`topomt/data/...`). Emitting these shapes as PDBs lets
those tools run on **controlled, known-answer geometry**, which is far more
diagnostic than comparing on a real protein with a fuzzy ground truth.

## Generator (implemented)

`topomt/dfnd/synthetic.py` exposes one function per shape returning a
`SyntheticSystem` with `.coords`, `.radii`, optional `.elements`, explicit
`.to_molsysmt()` / `.to_pdb(path)` conversion methods, and optional jitter.
Helpers such as `_tube_surface`, `_grid_box`, and `rotate` remain plain numerical
helpers. `devtools/dfnd/build_synthetic_catalog.py` defines the
`CATALOG` (shape + parameters + probe + expected note), writes one PDB per entry
to `topomt/data/synthetic/`, and regenerates that directory's `README.md` with
the DFND family summary actually produced — so the documented answer can never
drift from the code. Add entries and re-run to grow the battery.

## Relationship to Existing Docs

- Extends [`validation_plan.md`](validation_plan.md) §1.1–§1.2 with meso-scale,
  known-ground-truth shapes.
- Distinct from [`toy_systems_v1.md`](toy_systems_v1.md) (micro contract fixtures).
- Exercises the degeneracy limitation in [`known_limitations.md`](known_limitations.md).
