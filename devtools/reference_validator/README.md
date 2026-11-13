# Exact reference-validator foundation

Developer tools under TopoMT #76, first consumer #181. This is a bounded P0
foundation with a scoped P1 analytic construction, not a supported public
detector or a general multi-ball region enumerator. The [implementation plan](../../devguide/DFND/physical_reference_validator_implementation.md)
retains the remaining scientific gates.

The model freezes rational nm values, source atom/frame IDs, input SHA-256,
probe and a box or tetrahedron. Captured floats retain their exact binary value.
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
enclosure, aperture inventory or morphological label. Exact geometry completion,
all six hulls, high-precision curved-volume integration and production
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
declared; this prototype admits only nonperiodic boxes/tetrahedra and must not
pretend to construct an arbitrary hull.

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
multi-ball regions and requested high-precision integration remain unresolved.
