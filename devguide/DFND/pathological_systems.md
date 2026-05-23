# DFND Pathological Systems (Known Failures)

Recorded on 2026-05-22. The synthetic battery in
[`synthetic_benchmarks.md`](synthetic_benchmarks.md) was, by construction, tuned
to shapes DFND *can* resolve — which biases it toward success and hides where the
method breaks. This document collects the opposite: synthetic systems with a
**known correct answer that DFND currently gets wrong**. They are the systems
that will let us improve.

Each failure is pinned by a test in `tests/test_dfnd_pathological.py` that asserts
the *current, wrong* behaviour. These are **regression markers**: when DFND is
improved, the test fails and must be updated to assert the corrected answer.
Generators are in `topomt/dfnd/synthetic.py`; PDBs are catalogued under
`topomt/data/synthetic/pathological_*.pdb`.

These ground the abstract limitations in [`known_limitations.md`](known_limitations.md)
with concrete, reproducible cases. F1–F8 below were the first set; a systematic
second sweep over untested mechanisms (numerical thresholds, anisotropy, topology,
input hygiene, packing density) follows further down, together with the
robustness checks that DFND passes.

## F1 — Deep narrow concavities fragment

`blind_well(well_radius=3, depth=14)` → **5 pockets** (should be **1**).

A deep, narrow blind well is segmented into a stack of pockets along its depth
instead of one pocket. The single-scale residence/transit decomposition cannot
keep a long narrow concavity whole: local residence maxima along the lumen become
separate domains. Real impact: deep grooves and narrow tunnels will be
over-counted and their volume split.

## F2 — Long thin channels lose through-connectivity

`slab_with_pore(pore_radius=3, thickness=14)` → **2 pockets, 0 channels** (should
be **1 channel** with 2 mouths).

A long thin pore is not recognised as a single through-channel. The resident
chain through the narrow lumen does not stay connected end to end, so instead of
one `multi_external_link_domain` joining both faces, DFND reports two separate
one-mouth pockets. Real impact: long pores/tunnels (ion channels, transport
pathways) may be missed as channels — the most worrying failure for the
"connectivity" story that is supposed to be DFND's strength.

## F3 — Flat convex surfaces emit spurious voids

`flat_slab(spacing=4.0)` → **8 false enclosed voids** + 2 pockets (should be
**0 cavities**).

A flat, purely convex slab — a negative control — produces false enclosed voids
between surface atoms at certain grid spacings. These are false positives: there
is no cavity. The effect is spacing-sensitive (it largely vanishes at 3.5 Å),
which is itself a warning: detection depends on packing density. Real impact:
flat or convex protein surface patches can generate phantom cavities; downstream
filtering (which does not yet exist) must remove them.

## F4 — Perfect lattices are degenerate and unstable

`hollow_cube(jitter=0.0)` vs `hollow_cube(jitter=0.1)` → **different family
counts** (should be **identical** under a 0.1 Å perturbation).

A perfect cubic lattice is massively coplanar/cospherical, the worst case for
Delaunay non-uniqueness (the WP4 limitation). The triangulation — and therefore
the topology DFND reports — changes when an infinitesimal jitter is applied. The
whole battery uses `jitter=0.1` precisely to dodge this; the unjittered cube
exposes it. Real impact: symmetric assemblies, idealised models, and
crystallographic lattices need explicit degeneracy handling (jitter, symbolic
perturbation, or weighted tie-breaking), not silent dependence on noise.

## F5 — Two bodies make a phantom inter-body pocket

`two_balls(ball_radius=6, gap=8)` → a **~485 Å³ pocket** in the gap (should be
**0 cavities**: two convex balls have none).

The concave saddle in the open space between two convex bodies is reported as a
large pocket. Running a single-structure pocket detector on a system with two (or
more) bodies invents pockets in the inter-body space. This is the false-positive
twin of the interface story ([`interfaces.md`](interfaces.md)): the same region
is a legitimate *interface* feature, but a naive per-structure pocket pass scores
it as a spurious binding pocket. Bodies must be identified first.

## F6 — The same cavity is classified differently by sampling density

`hollow_sphere(R=10)` at fixed probe 1.4, varying only `wall_spacing`:

| wall spacing | DFND family |
|---:|---|
| 3.0–4.0 Å | void |
| 4.3 Å | pocket |
| 4.6 Å | channel |

The **same geometric cavity** is called a void, a pocket, or a channel depending
only on how densely its wall is sampled — sparser walls leak the probe through
gaps that denser walls seal. This is arguably the most consequential failure:
real structures have non-uniform atomic density, so the void/pocket/channel call
can hinge on local sampling rather than on shape. Robustness here likely needs
the gate test to consider the *surface* a wall represents, not just its sampled
atoms.

## F7 — Thin gaps between bodies fragment into spurious voids

`parallel_plates(separation=3)` → **4 false enclosed voids** + 5 pockets (should
be one open slot / no enclosed void).

A thin gap between two facing surfaces fragments into a row of spurious voids and
pockets. Combined with F3, this says: thin slabs of solvent — common at contacts
and in clefts — are a reliable source of phantom enclosed cavities.

## F8 — Cavity volume is overestimated by ~40%

`hollow_sphere(R=10)` void: `volume_solvent_estimate` ≈ **3110 Å³** vs analytic
empty inner ball `4/3·π·(10−1.88)³` ≈ **2243 Å³** → **+39%**.

The solvent volume estimate significantly overshoots the analytic empty volume.
Any quantitative volume claim is currently unreliable at the tens-of-percent
level. (The estimate sums tetrahedral content that reaches past the
solvent-accessible inner ball; it needs calibration against analytic shapes.)

## F9 — Thin tubes are not recognised as channels

`cylinder_tube(tube_radius=2.5)` → 2 pockets, **0 channels** (should be **1
channel**); at `tube_radius=3.0` it even produces a spurious void. Distinct from
F2 (which is about *length*): here it is *thinness*. A lumen near the residence
threshold cannot hold a connected resident chain, so the channel collapses into
pockets. Worse, the `nonresident_passage_domain` family — defined precisely for a
passable-but-not-residable lumen — never appears, so there is no fallback class.
The radius family is catalogued as distinct PDBs (`pathological_thin_tube_r20`
→ nothing, `_r25` → pockets, `_r30` → a spurious void, `thin_tube_r35` →
recognised channel) so the failure-to-success progression is visible.

## F10 — Non-uniform sampling flips a closed cavity open

`hollow_sphere_patchy(sparse_fraction=0.6)` → **channel** (should be **void**).

The same geometrically closed sphere, but with one hemisphere's wall sparsely
sampled, leaks the probe through the sparse side and is reclassified as an open
channel. This is the **within-one-body** version of F6, and the most realistic:
protein surfaces are not uniformly sampled, so a genuinely enclosed cavity can be
called open wherever its wall is locally sparse. Robustness needs the gate to
reason about the surface a sparse patch represents, not just the present atoms.

## F11 — Classification depends on the radius model

On the **same coordinates**, different per-atom radius distributions reclassify
the cavity as void / pocket / channel (`R_gate` is exact only for equal radii;
the plane of centres stops being a mirror plane when radii differ). Real atoms
have fixed element radii, so this is not a daily failure — but it shows the gate
is sensitive to the radius model and that mixed-radius gates are not exact.

PDB has no radius field, but mixed radii are encoded by **element**: the
catalogued `pathological_mixed_radii_shell.pdb` uses noble gases of different vdW
radius (He 1.40, Ne 1.54, Ar 1.88, Kr 2.02, Xe 2.16) so a reader re-derives the
per-atom radius from the element symbol — the system survives a PDB round trip and
classifies differently from a uniform-argon wall on the same coordinates.

Genus blindness (a cavity wrapping an interior island reported as one simple
void) is pinned by `test_void_with_island_is_still_one_void` in the success
suite — it is a documented "does not capture", listed below.

## Second sweep — systematic mechanism coverage

A deliberate pass over mechanisms not yet probed. Most fragment or mis-classify;
a few are handled (see the next section). Pinned in `test_dfnd_pathological.py`.

**Numerical / threshold robustness**
- **Marginal residence flicker.** A tetrahedron sized so `R_residence ≈ probe`
  (edge 5.4 → 1.43) flips resident/non-resident under a 0.2 Å jitter (resident in
  6/10 seeds). The cavity exists or not depending on noise.
- **Marginal gate flicker.** A sphere whose wall gate sits at the probe threshold
  (spacing 4.2) is classified void / pocket / channel depending only on the seed.
- **Non-monotone probe response.** The dumbbell yields 2 significant domains at
  probe 1.4 but **5 at probe 2.0** — a *larger* probe finds *more* features
  (spurious over-fragmentation grows with probe).

**Anisotropy / segmentation (more of disease 1)**
- **Oblate slit void** → splits into 2 voids (ideal 1).
- **Tapering cone** → fragments into pockets, no channel (ideal 1).
- **Star/branched void** → lobes fragment; the core void is not even dominant.
- **Toroidal (genus-1) void** → splits into 2 voids (topology not preserved).
- **Pocket-in-pocket** → over-segments into many flat pockets, no hierarchy.
- **U-channel** (two mouths on one face) → not connected as a channel + a
  spurious void.
- **Edge cavity** (at the block corner) → fragments into several pockets (does not
  crash on the hull, at least).

**Robustness / input hygiene**
- **Isolated outlier atom.** Appending one atom 100 Å away spans huge Delaunay
  slivers and creates a phantom pocket — the result is not robust to outliers.

**False-positive rate at scale (the headline number)**
- **Loosely packed blob** (`min_separation = 3.8 Å`) → many phantom voids,
  **~70–115 spurious features per 1000 atoms**. The rate is a *steep* function of
  packing: at vdW contact (`3.0 Å`, atoms overlapping) it drops to **zero**. This
  both quantifies the noise risk and supports the hope that real structures
  (atoms in contact) mitigate it — but the margin is a knife-edge.
- **Coarse-grained shell** (few large beads) → a closed cavity leaks and reads as
  open: the low-resolution / CA-only realistic case of the sampling disease.

## Robustness checks that PASS (mechanisms DFND handles)

Pinned as passing tests, so a regression that breaks them is caught:

- **Epsilon-stable.** Classification is unchanged across `epsilon` 1e-9 … 1e-2.
- **Extreme probes degrade cleanly.** A too-large probe (8 Å) vanishes with no
  junk; a 5 Å probe still reports the void.
- **Thin septum holds.** A 1 Å internal wall keeps two chambers as two voids (no
  bleed-through) — the inverse of the fusion failures.
- **Dense packing is clean.** At vdW contact a solid blob yields zero spurious
  features.

## Watch list (not yet pinned as clean failures)

- **`surface_concavity_domain` unreachable.** Every shallow dent tried so far
  classifies as a `pocket` (a resident ball always fits); the provisional family
  has no synthetic ground-truth case yet.
- **`degenerate_subprobe_domain` unreachable.** Like `nonresident_passage`
  (see F9), this raw family has no end-to-end synthetic case that produces it.
- **A direct `R_gate` mixed-radius probe.** F11 shows radius sensitivity at the
  system level; a 3-atom gate with very unequal radii compared against a
  Monte-Carlo largest-passing-disk would quantify the approximation error in the
  primitive itself.

## Failure families (summary)

~25 pinned failures (plus 4 passing robustness checks) cluster into four
underlying diseases:

1. **Fragile single-scale segmentation** — deep well, long pore, thin gap, thin
   tube, oblate slit, tapering cone, star void, toroidal void, pocket-in-pocket,
   U-channel, edge cavity: long/thin/deep/branched/nested features fragment or
   collapse. *By far the most pervasive disease — almost every non-trivial cavity
   over-segments.* The likely fix is probe-sweep persistence + watershed merging.
2. **Dependence on sampling / packing, not geometry** — flat slab, perfect
   lattice, global wall density, local sparse patch, coarse-grained shell, and the
   loose-packing false-positive rate: the answer follows how the surface is
   sampled. *The biggest threat to real-system transfer* — but the packed-blob
   experiment shows it largely vanishes at vdW contact, which real structures have.
3. **Numerical / threshold instability** — marginal residence, marginal gate,
   non-monotone probe response: near a threshold the answer flips with noise or
   probe.
4. **Uncalibrated quantification, radius model, bodies & topology** — volume
   +40%, radius-dependent class, phantom inter-body pocket, outlier sensitivity,
   genus blindness.

## How to use these

When working on segmentation, degeneracy, or filtering: run
`pytest tests/test_dfnd_pathological.py`. A test that flips from passing to
failing means the corresponding failure mode has changed — update the assertion
to the new (hopefully correct) behaviour and note it here. Add new pathological
systems freely; failures are more informative than successes.
