# Exact reference-validator foundation

Developer tools under TopoMT #76, first consumer #181. This is a bounded P0
foundation with scoped P1 region, precision and hull-proof routes, not a supported public
detector or a general multi-ball region enumerator. The [implementation plan](../../devguide/DFND/physical_reference_validator_implementation.md)
retains the remaining scientific gates.

The model freezes rational nm values, source atom/frame IDs, input SHA-256,
probe and a box, tetrahedron or independently checked center hull. Captured
floats retain their exact binary value.
The original tetrahedron reader uses the public PyUnitWizard quantity codec,
including its integrity checks; it does not infer radii or substitute a box for
a general atomic-center hull. That route does not claim a fresh match with a
newly executed DFND input.

The verifier imports no producer, DFND, NumPy or quantity library. It checks
model identity, exact whole-cell predicates and partition coverage, or entire
path segments/point claims against every expanded ball. Its receipt fingerprints
the actual checker source and Python version. Fraction arithmetic, exact
determinants/convexity and the defined subdivision are the trusted base; this is
not a machine-checked proof of the Python runtime.

Boxes split eight ways; tetrahedra bisect their longest edge with exact midpoints.
Leaves form a complete prefix-free tree. One expanded ball covering all cell
vertices proves the whole convex cell blocked. A bounding-box distance lower
bound proves a whole cell free; failing that sufficient test means unknown.
The verifier reconstructs the tree independently of producer search and computes
exact lower/upper probe-center volume bounds. Unknown cells contribute only to
the upper bound. Those bounds do not imply requested numerical precision.

In the subdivision route, only complete exclusion and completely free convex
domains receive proved component counts (zero/one). A blocked point does not exclude its carrier.
Mixed partitions and positive paths do not acquire a general component count,
enclosure, aperture inventory or morphological label. General steric geometry
completion, clipped/per-region high precision and production
attribution/API admission remain pending. Run/checkpoint records and same-kernel
resumption are now implemented within the admitted partition envelope. No
original external scientific kernel is used by this rational developer route.

From the checkout, under external CPU/memory/time limits:

```bash
python -m devtools.reference_validator freeze-tetrahedron INPUT.json MODEL.json --probe-angstroms 1.7
python -m devtools.reference_validator produce MODEL.json CERTIFICATE.json --max-depth 18 --max-leaves 1024
python -m devtools.reference_validator verify MODEL.json CERTIFICATE.json
```

Outputs must be new files. The checker rejects incorrect/unknown claims instead
of trusting a producer's count or precision metadata. Input JSON is size-bounded
and duplicate fields are rejected by the saved-proof CLI. Pilot work limits are
explicit: at most 512 atoms, 4096 leaves and depth 24. These operational limits
do not widen the physical free set. The checker can use an explicit `Limits`
configuration; the initial producer keeps its bounded admission envelope.

The [frozen tetrahedron pilot](../../devguide/evidence/reference_validator_p0_v1/protocol.json)
specifies four partitions (including an intentionally unresolved budget), two
free-center claims and four continuous face-access paths. Run
`python -m devtools.reference_validator.capture PROTOCOL.json NEW_DIRECTORY`
with one CPU affinity and an external memory/deadline envelope. It writes exact
models, certificates, verifier receipts and a checksum-bearing run receipt.
Saved verification needs only the model/certificate files and this source;
original quantities, DFND and the producer are not required.

## Scientific inputs

The steric model needs atomic centers `(N,3)`, atomic radii `(N,)` and one probe
radius. At a center position `x`, every condition
`||x-center_i|| > radius_i + probe_radius` must hold. Bonds, chemical types,
energies and DFND results are not inputs to that geometric test.

The finite domain is an observation context, not another obstacle. The three
sphere inputs define the nonperiodic excluded set globally; a hull or box
specifies which finite volume and connectivity question is being asked. The
global exterior volume is unbounded. Units and boundary conditions must be
declared; the steric prototype admits nonperiodic boxes, tetrahedra and verified
center hulls. Hull point/path/whole-domain proofs are described below; general
mixed hull partitions and region enumeration remain pending.

For direct numerical inputs, the developer factory generates row IDs and a
canonical sphere-source digest automatically:

```python
from devtools.reference_validator.model import Box, Model, point

model = Model.from_spheres(
    centers_nm=[[0, 0, 0]],
    radii_nm=[0.17],
    probe_nm=0.14,
    domain=Box(point((-2, -2, -2)), point((2, 2, 2))),
)
```

These explicitly named nm arguments do not perform unit conversion. Use the
owning quantity tools before entering this numerical contract. Captured floats
retain their binary values; use Fraction inputs for exact intended rationals.
The resulting source digest identifies encoded sphere data, not a PDB file.

## Bounded execution and resume

```bash
python -m devtools.reference_validator start MODEL.json STEP_0 --max-depth 18 --max-leaves 1024 --split-budget 17
python -m devtools.reference_validator resume MODEL.json STEP_0 STEP_1 --split-budget 17
python -m devtools.reference_validator verify-run MODEL.json STEP_1 --parent STEP_0
```

The fixed request, model and source/runtime fingerprint define a reproducible
logical run ID, not a unique process/session ID. Each step has its own checkpoint
digest and parent link. Only its split budget may change: model, domain, depth,
leaf ceiling or kernel changes require a new run. A split classifies at most
eight children; root classification and independent checking are additional
bounded work. Run all commands within external CPU/RAM/deadline limits.

The frontier retains every unknown cell, including those at a ceiling. Stops
distinguish a step budget, depth ceiling, leaf ceiling and no remaining unknown
cells. None invents a general component count or a precision guarantee. Every
resume checks the original partition and the entire frontier. Independent
transition checking also proves retained resolved cells and nested volume bounds.

New directories contain `checkpoint.json`, a derived `run.json` and a raw-byte
checksum manifest written last. Existing directories are never overwritten.
Incomplete/changed bundles are rejected. This is a commit-marker protocol;
it does not claim atomic directory publication or universal power-loss durability.
The bytes interpreted by the reader are exactly those whose digests it checked.

Standalone `verify-run` without a parent explicitly leaves lineage not checked.
With a parent it verifies that immediate transition. The checker imports neither
run search nor DFND. Resuming executable work requires the exact recorded
kernel/runtime; after code changes, the saved mathematical certificate can still
be checked through the independent `verify` command. Keep historical records.

The [resume pilot protocol](../../devguide/evidence/reference_validator_resume_v1/protocol.json)
reuses the original frozen 1.7 Å model and compares a nine-step chain with an
uninterrupted control. Use
`python -m devtools.reference_validator.capture_resume PROTOCOL.json NEW_DIRECTORY`
with one CPU affinity and the external memory/deadline envelope.

## Scoped exact connected-region construction

```bash
python -m devtools.reference_validator box-topology MODEL.json CERTIFICATE.json
python -m devtools.reference_validator verify MODEL.json CERTIFICATE.json
```

The new route admits exactly one expanded ball and an axis-aligned box. It
rejects additional atoms and other domains; it never drops them or substitutes
a box. A complete monotone-sector cover with every pair intersection proves
exhaustive regions, including eight tiny corner components and exact throat
closure. No subdivision resolution or floating epsilon decides this result.

Accepted regions list IDs of their supported free pieces and a representative.
Each piece means `sector intersect strict free set`; `free_set_state=nonempty`
does not mean the entire sector is free. The retained certificate/model recover
the physical regions. Counts and IDs do not imply volume, boundary incidence,
enclosure or morphology. See the
[proof and remaining P1 gates](../../devguide/DFND/reference_validator_p1_feasibility.md).

The [frozen topology protocol](../../devguide/evidence/reference_validator_box_topology_v1/protocol.json)
contains thirteen analytic controls. Capture within one CPU affinity and an
external memory/deadline envelope:

```bash
python -m devtools.reference_validator.capture_box_topology PROTOCOL.json NEW_DIRECTORY
```

The standalone saved checker needs no topology producer, DFND or NumPy. General
multi-ball regions and clipped per-region high precision remain unresolved.

## Scoped certified volume integration

```bash
python -m devtools.reference_validator volume MODEL.json CERTIFICATE.json --absolute-nm3 1/16777216 --relative 1/16777216
python -m devtools.reference_validator verify MODEL.json CERTIFICATE.json
```

Every expanded ball must lie strictly inside an axis box. After exact containment
reduction, each positive-overlap cluster must have one/two maximal balls, with
distinct cluster interiors disjoint. Every source atom remains mapped. Larger
clusters and domain clipping are rejected. Sphere/cap formulas, exact rational
intervals, a bounded pi series and dyadic square-root enclosures provide rigorous
total free-volume bounds. This route computes no region inventory or boundary
incidence. See the [proof and scope](../../devguide/DFND/reference_validator_precision_feasibility.md).

Every enabled tolerance must pass. Zero error stays literal;
`--max-atan-terms 0 --max-distance-bits 0` may retain valid coarse bounds with
unresolved precision. The reader checks units and actual/maximum refinement.

The [volume protocol](../../devguide/evidence/reference_validator_analytic_volume_v1/protocol.json)
contains 23 profiles. Capture under one CPU affinity and external resource limits:

```bash
python -m devtools.reference_validator.capture_volume PROTOCOL.json NEW_DIRECTORY --crosscheck-mpfr
```

Omit `--crosscheck-mpfr` to run without gmpy2/MPFR. That flag adds a secondary
directed-rounding constant audit; the producer and saved checker do not need it.
General clipped/multi-region precision qualification remains pending.

The exact scalar codec admits at most 20,000 decimal digits per numerator or
denominator and keeps Python's global conversion guard unchanged. This supports
the tested maximal-refinement certificate; larger records are explicitly rejected.

## Exact source hulls and geometric clipping

```bash
python -m devtools.reference_validator freeze-hull-source INPUT.json SOURCE.json
python -m devtools.reference_validator hull SOURCE.json HULL.json
python -m devtools.reference_validator verify-hull SOURCE.json HULL.json
python -m devtools.reference_validator clip-hull SOURCE.json HULL.json CLIP.json --lower-nm 0 -2 -2 --upper-nm 2 2 2
```

The immutable center-only source retains units, original row/frame/file identity
and exact coordinates. Its hull is independent of probe/radii. Incremental exact
construction proposes supporting planes; the saved checker independently proves
boundedness and exhaustive vertex/source equality. Exact box clipping retains
empty, point, edge, face and full-dimensional outcomes. Returned geometric
volume is not probe-accessible volume; physical free topology is not computed.

See the [proof, receiving and scope](../../devguide/DFND/reference_validator_hull_checkpoint.md).
The center-only route consumes coordinates. The separate steric integration
below retains all atoms/radii/probe while using that independently checked hull.
The complete subdivision engine still admits only boxes/tetrahedra.

Capture the [frozen hull protocol](../../devguide/evidence/reference_validator_hulls_v1/protocol.json)
under one CPU affinity and external parent limits with
`python -m devtools.reference_validator.capture_hulls PROTOCOL.json NEW_DIRECTORY`.
The default schedules only small controls. `--original-case NAME` or
`--all-originals` selects original inputs, always sequentially. Each worker has
30 CPU seconds, a 40-second wall deadline and a 2 GiB address cap. A stop remains
unresolved; no geometric empty result is inferred. The pilot limits source count
to 128, facets to 192 and plane triples to 1,200,000 per enumeration. General
many-atom free regions and region-assigned precision remain pending.

The [retained local batch](../../devguide/evidence/reference_validator_hulls_v1/local_receiving/receipt.json)
at source `9a276cd` accepts all six original center hulls with independent
saved-file checking. The maintainer selected sequential local execution without
Slurm for this phase. It takes 90.94 seconds, peak child RSS 56,816 KiB, within
the limits above. This qualifies source hull geometry only; radii/probe, free
volumes and connected-region inventories remain separate work. See the
[execution record](../../devguide/evidence/reference_validator_hulls_v1/local_execution.json).

## Steric checks inside the certified hull

```bash
python -m devtools.reference_validator freeze-hull-model INPUT.json MODEL.json --probe-angstroms 1.4 --hull-certificate HULL.json
python -m devtools.reference_validator domain-proof MODEL.json CERTIFICATE.json
python -m devtools.reference_validator verify MODEL.json CERTIFICATE.json
```

Omit `--hull-certificate` to construct a bounded exact hull proof. The reader
consumes coordinates and atomic radii through their public quantity records,
explicitly converts both and the probe to nm, then verifies hull equality.
Every atom remains present, including interior atoms. Domain membership checks
exact halfspaces; continuous paths check every segment against all atoms.

For numerical input, explicitly replace the observation domain:

```python
hull_model = model.with_center_hull()
```

This returns a new source-bound Model and digest; it preserves the original.
Saved reading rechecks hull geometry and needs neither producer nor DFND nor
quantity libraries. Point/path certificates retain their existing schema.
Partition/run/resume explicitly reject hull domains until their clipped
subdivision is qualified; no bounding-box substitution occurs.

`domain-proof` proves whole-domain exclusion by one covering expanded ball,
or full convex availability by a sufficient distance bound. Otherwise it
retains `unknown`, `[0,V_hull]` and no component count. It does not prove general
union coverage, enumerate mixed regions or meet requested volume precision.

The [hull/steric checkpoint](../../devguide/DFND/reference_validator_hull_sterics_checkpoint.md)
explains guarantees, strict contact, old-record compatibility and remaining
work. Capture the [frozen protocol](../../devguide/evidence/reference_validator_hull_sterics_v1/protocol.json)
within external one-CPU/2 GiB/50 CPU-second/60 wall-second limits:

```bash
python -m devtools.reference_validator.capture_hull_sterics PROTOCOL.json NEW_DIRECTORY --originals
```

Default capture runs only four small analytic fixtures; `--originals` explicitly
adds six tetrahedron/narrow-tube profiles. An invalid path candidate is retained
as such, never as proof of physical disconnection. Original-profile receiving
remains to be executed at this source checkpoint.
