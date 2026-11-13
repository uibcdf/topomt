# Exact reference-validator foundation

Developer tools under TopoMT #76, first consumer #181. This is the first P0
implementation tranche, not a supported public detector or a complete region
enumerator. The [implementation plan](../../devguide/DFND/physical_reference_validator_implementation.md)
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

Only complete exclusion and completely free convex domains receive proved
component counts (zero/one). A blocked point does not exclude its carrier.
Mixed partitions and positive paths do not acquire a general component count,
enclosure, aperture inventory or morphological label. Exact geometry completion,
all six hulls, high-precision curved-volume integration, general run/checkpoint
schemas, resume and production attribution/API admission remain pending. No
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
