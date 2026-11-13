# Reference-validator center hulls and exact box clipping

Owner [#76](https://github.com/uibcdf/topomt/issues/76); first native consumer
#181. This domain-construction tranche follows the
[implementation plan](physical_reference_validator_implementation.md). It does
not select the complete multi-ball region construction or qualify free volumes.

## Scientific object and source boundary

For all received centers `X`, the declared domain is `H=conv(X)`. A bounding box
is a computational enclosure, not a replacement for H. Radii/probe do not define
this center hull; they remain essential inputs to the later steric free set.

`CenterSource` is an immutable numerical proof view with exact nm centers,
original row/frame IDs, input-file hash and numerical interpretation. It is not
another molecular-system representation. Duplicated/interior source centers
remain present; coincident geometric vertices use the smallest source ID.
The certificate's `source_sha256` binds the complete center-source record;
that record separately retains the original file's SHA-256.

`freeze_centers` uses PyUnitWizard's public QuantityRecord reader, verifies its
coordinate record and explicitly extracts nm binary64 values. Each captured
number becomes its exact rational value. A nondefault pm/fs application policy
does not change the received source or get overwritten. Decoder errors propagate.
Only the coordinate block is qualified here; radii/probe receiving and equality
to freshly executed DFND input remain separate work. Historical source bytes
and embedded case identifiers are preserved.

The geometry-only tranche initially left the steric Model unchanged. The
[subsequent hull/steric integration](reference_validator_hull_sterics_checkpoint.md)
now admits verified original center hulls for exact point/path/whole-domain
proofs, explicitly preserving every sphere and source context. Complete
sphere-cut partitions and public admission remain separate work.

## Exact proposal and independently checked equality

The producer incrementally builds an oriented triangular hull with exact
rational signs, merges coplanar facets and proposes primitive integer
halfspaces `n_i*x <= d_i`. It supplies source anchors and boundedness witnesses.
No Qhull, SciPy, CGAL or cddlib code executes in this route. Existing public
TopoMT convex-hull metrics retain their own behavior and attribution.

The checker does not import that incremental constructor. It proves:

1. **Full dimensionality and containment.** Four original centers have a
   nonzero affine determinant. Each supporting plane contains three
   noncollinear original centers; every source center satisfies its inequality.
   Thus `H` is full-dimensional and `H subset P`, where P is the intersection
   of the proposed closed halfspaces.
2. **Boundedness.** Strictly positive rational weights sum to one and give
   `sum(w_i*n_i)=0`. Three normals are linearly independent. A recession
   direction v would satisfy `n_i*v<=0` for every i; the positive weighted sum
   forces every product to zero, and full rank forces v=0. P is bounded.
   The producer derives weights from its oriented triangle area vectors; the
   checker only trusts the explicit algebraic equilibrium, not mesh closure.
3. **Exhaustive vertices.** Enumerate every independent plane triple. Integer
   Cramer arithmetic gives its rational intersection; test it against every
   halfspace. Every vertex of the full-dimensional bounded P occurs in this
   list, including vertices outside the source that an incomplete plane list
   might introduce. The producer instead proposes source vertices by the rank
   of active planes; it does not supply the checker's enumeration conclusion.
4. **Reverse containment.** Every enumerated P vertex must equal an original
   center, with a complete canonical source map. Since a bounded polytope is
   the convex hull of its vertices, `P subset H`. Together the containments
   prove **P=H**, not merely that a proposed enclosure contains the atoms.

The [polyhedral-computation reference](https://cddlib.github.io/polyhedral_faq/)
describes H/V representations and their equivalence; the
[CGAL hull manual](https://doc.cgal.org/latest/Convex_hull_3/index.html) gives
background on source extreme points and arithmetic requirements. These are
documentary references, not execution of those libraries or a qualification
of another implementation. The declared trusted base here is exact integer/
rational arithmetic, exhaustive plane intersections and the stated polyhedral
theorems, not a machine-checked proof of Python.

A decisive control removes one plane from an octahedron while retaining valid
containment and positive boundedness weights. The resulting larger polytope
has the non-source vertex `(1,1,1)`; exhaustive checking rejects it. Testing
source containment alone would miss that failure mechanism.

## Geometric volume and closed clipping

Facet polygons are recovered from the complete vertex list and sorted with
exact planar orientation predicates. Their cycles point outward relative to
the integer normals, which are not unit vectors. A fan from an interior point
to each convex facet triangulates the polytope. Exact determinant sums give
its **geometric** volume in nm**3; no spherical clearance is involved.

To intersect with a closed box, append its six exact halfspaces, canonicalize
duplicates and enumerate the resulting vertices. The original hull proof
already supplies boundedness. Empty intersections have dimension -1; nonempty
point/edge/face contacts have dimensions 0/1/2, with explicit retained vertices
and zero three-dimensional geometric volume. Full-dimensional intersections
receive exact positive volume. Zero-volume seams must not be discarded when
later assembling connectivity. A zero geometric clip volume is not a statement
that the probe's physical free set is empty.

The certificate includes the original hull proof, explicit nm clip box and
claimed vertices/dimension/volume. The checker recomputes them; nested input
records are detached. Corrupted source bindings, enlarged/missing facets,
false weights/rank/source maps, wrong units and invented clip outcomes are
rejected. Lower-dimensional source hulls are explicitly rejected as unsupported
3D domains, rather than receiving a fabricated 3D result.

## Frozen receiving and resource envelope

The [protocol](../evidence/reference_validator_hulls_v1/protocol.json) freezes
tetrahedron/cube/octahedron controls, six cube clips and the six original source
files with hashes. Clipping controls include half-volume, empty intersection,
face/edge/point contact and a positive `2^-80`-scale sliver. Other tests cover a
non-axis tetrahedral cut, exact translation/scaling, duplicate/coplanar centers,
corruption, units, saved engine-free reading and finite work rejection.

This pilot admits at most 128 centers, 192 halfspaces and 1,200,000 plane triples
per enumeration. Limits do not relax geometry. The capture schedules original
sources only when explicitly selected, sequentially with one CPU, 2 GiB address
space, 30 CPU seconds and a 40-second wall deadline per source. Failed/timed-out
workers remain unresolved and cannot acquire an empty-result interpretation.
Use an external bounded parent process too; free host resources are not reserved.

Original receiving records the actual quantity-decoder versions/source identity,
source/certificate/checker hashes and resources. Saved checking needs neither
the producer nor PyUnitWizard/NumPy/floating geometry. This is source/domain
evidence, not installed/public/platform qualification or any DFND correction.

For the present phase the maintainer selects sequential local execution,
without Slurm. One CPU, explicit time/address-space limits and host pressure
checks remain required for these pilots. The helper can retain allowlisted
scheduler identifiers if later run in an allocation; numerical certificates
do not depend on Slurm. Free resources observed now are not a reservation.

## Actual receiving and current resource disposition

Source/protocol `2b6985bfb8a3ee8a2b856060435a7c3b93fbab6b` produces the
[small retained receiving](../evidence/reference_validator_hulls_v1/receiving/receipt.json):
three analytic hull controls and six clips, 28 JSON files and 70,653 bytes.
All are saved and independently checked after reading. The bounded ordinary
control uses one CPU, 2 GiB, 0.25 seconds and peak RSS 23,512 KiB; the receipt
retains its distinct internal sample. It explicitly selects no original inputs.
No managed allocation or six-case qualification is inferred from this run.

The earlier [Slurm attempt](../evidence/reference_validator_hulls_v1/scheduler_attempt.json)
requested one CPU, 2 GiB and five minutes on `tests`, with five-second immediate
admission. Job 5 failed before execution; queue readback was empty. Node state
readback showed `tests=inval` and `normal=unk*`, despite a responding controller.
The allocation failed; its node/configuration cause is not diagnosed. That
attempt ran no calculation. Its managed-retry disposition is superseded by
the maintainer's subsequent local-execution decision and receiving below.
General infrastructure context
is [uibcdf-infrastructure#1](https://github.com/uibcdf/uibcdf-infrastructure/issues/1).

The failed-attempt record and first small receiving keep their original bytes.
Preliminary pre-commit probes only informed resource sizing, not source
qualification. The new batch uses a fresh additive directory.

## Actual local six-source receiving — 2026-11-13 UTC

Source `9a276cd9827f4d84fc048d94e06ee6d043779106` captures the unchanged protocol
in [local_receiving](../evidence/reference_validator_hulls_v1/local_receiving/receipt.json).
All six original sources are accepted after exact hull construction, saving,
reading and independent checking. Every original center remains in its source,
including centers that are not extreme vertices. Geometric facet counts below
refer to exact normalized binary64 input geometry, with coplanar planes merged.

| Original input | Centers | Hull vertices | Facets | Worker wall seconds |
| --- | ---: | ---: | ---: | ---: |
| `regular_tetrahedron` | 4 | 4 | 4 | 0.44 |
| `closed_shell` | 72 | 72 | 140 | 31.36 |
| `shell_with_opening` | 66 | 66 | 128 | 22.39 |
| `straight_tube_narrow_dense` | 81 | 25 | 46 | 1.57 |
| `straight_tube_wide_sparse` | 77 | 45 | 86 | 7.44 |
| `dumbbell` | 94 | 66 | 128 | 26.66 |

These are observed source-domain results, not independently predicted counts
or accessible-volume references. Each saved verification includes exact positive
rational geometric volume and a complete source-vertex map; all retain
`free_volume_status=not_computed` and `free_topology_status=not_computed`.
Radii/probe are not consumed, and no fresh DFND-input equality is claimed.

The new receiving contains 52 JSON files and 682,226 bytes, including repeated
small controls, raw SHA-256 bindings and producer/checker/dependency identities.
The [execution record](../evidence/reference_validator_hulls_v1/local_execution.json)
binds this receipt to the conservative local policy. The whole process takes
90.94 seconds with one CPU and peak child RSS 56,816 KiB; each worker has a
2 GiB address-space, 30 CPU-second and 40 wall-second cap. Samples before,
during and after show over 51 GiB available and no memory pressure/active swap.
No scheduler job or reserved machine resources are claimed.

The continuation selection passes 211 tests (previous 202 plus nine retained
receiving/replay controls), including original artifact integrity. Every saved
original was independently verified by the full capture; the routine regression
selection replays two representative originals to avoid repeating that cost.
The selected process uses one CPU/2 GiB, 18.27 seconds and peak RSS 95,692 KiB.
All 355 original case files remain unchanged. This is Linux source evidence,
not a full suite or public/platform qualification. No environment is changed.
Repository Ruff/format, report indexes, offline finding consistency and 274 local
file targets pass; scientific source is unchanged from `9a276cd`.

## Developer route

```bash
python -m devtools.reference_validator freeze-hull-source INPUT.json SOURCE.json
python -m devtools.reference_validator hull SOURCE.json HULL.json
python -m devtools.reference_validator verify-hull SOURCE.json HULL.json
python -m devtools.reference_validator clip-hull SOURCE.json HULL.json CLIP.json --lower-nm 0 -2 -2 --upper-nm 2 2 2
```

Run within external CPU/RAM/deadline limits. CLI bounds are explicit nm and can
be rational strings. New outputs never overwrite existing files. The separate
saved-hull checker makes no claim that a floating plane estimate or a source
file hash alone is a certified domain.

For receiving, `python -m devtools.reference_validator.capture_hulls PROTOCOL.json
NEW_DIRECTORY` captures only small controls. Explicit `--original-case NAME`
or `--all-originals` selects original inputs. Original inputs/artifacts are never
rewritten. A manifest records successful and unresolved observations separately.

## Remaining construction work

These geometric hulls and clips do not enumerate obstacle-free pieces, prove
sphere-boundary attachments or assign per-region volume. The analytic contained-
ball volume route has its own box admission and cannot consume H by substitution.
Continue the complete multi-ball construction and its checked hull-clipped
assembly under #76, with #181 as first consumer. Existing native boundary/
qualification findings keep their dispositions. Public receiving, attribution
and installed API/package admission remain P6; no original provider, protein
phase or comparative superiority claim follows.
