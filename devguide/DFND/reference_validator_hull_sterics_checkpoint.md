# Reference-validator sterics on a certified center hull

Owner [#76](https://github.com/uibcdf/topomt/issues/76); first native consumer
[#181](https://github.com/uibcdf/topomt/issues/181). This extends the
[exact hull checkpoint](reference_validator_hull_checkpoint.md) into the
physical Model. It does not enumerate general connected free regions.

## Admitted model and immutable proof

`HullDomain` admits the independently verified, full-dimensional hull of every
source atom center. A strict `center_hull` domain record embeds its complete
center-source record and original equality certificate. Reading independently
checks the proof, then reconstructs immutable halfspaces, vertices and exact
geometric volume. Serialized derived geometry is not trusted. Source/proof
objects and returned records are detached.

Model admission checks the complete ordered centers/IDs, original input hash,
frame and numerical interpretation against the hull source. Every atom/radius
remains in the steric Model, including interior and duplicate centers. The
probe and radii affect exclusion, not the hull geometry. A hull proof can be
reused only with matching center-source provenance; an unchanged shape alone
does not permit attachment to a different source/frame.

`Model.with_center_hull(certificate=...)` explicitly changes the observation
domain and model digest while preserving atoms, radii, probe and provenance.
Without a supplied proof it invokes the bounded exact constructor. A saved
reader instead imports the independent checker and needs no producer, DFND,
NumPy or quantity library. Supplying a clipped hull as the original center hull
is rejected. General clipped-domain subdivision remains subsequent work.

This adds a domain kind to the developer model schema. Earlier box/tetrahedron
records and digests retain their representation and saved mathematical proofs
remain readable. Older readers reject the new kind. Executable resume requires
the exact source/runtime fingerprint; changed code requires a new run.

## Physical facts and their scope

For the exact received nm values, a point x is free iff x belongs to the closed
hull and, for **every** atom, `squared_distance(x,c_i) > (r_i+p)^2`. Hull contact
is allowed; expanded-ball contact is excluded. Rational tests retain the exact
contact decision and gaps of `2^-80` without a floating epsilon.

A segment's endpoints must lie in H. Convexity then puts the entire segment
in H. The checker independently minimizes squared distance along that complete
segment against each expanded ball, including endpoint and interior minima.
Free endpoints alone are insufficient. A polyline proof checks every segment;
its acceptance proves connectivity of its endpoints in this declared finite
free set, not exhaustive regions, exterior reachability or native-carrier
qualification. Every actually reached hull-checker source is fingerprinted.

The `convex_domain` certificate has three dispositions:

| Claim | Independently checked justification | Volume and topology |
| --- | --- | --- |
| `blocked` | One identified expanded ball covers every convex-domain vertex. | Exact `[0,0]` free volume, complete zero components. |
| `free` | The exact sufficient bounding-box distance bound clears every atom. | Exact `[V,V]`, one component of the full convex domain. |
| `unknown` | Only domain containment is used. | Valid broad `[0,V]`, component count `None`. |

The first condition uses convexity of the ball. The second is sufficient and
can fail even when some free space exists. In particular, a zero lower bound
does not prove emptiness. General coverage by a union of balls, component
enumeration and requested volume precision are not supplied by this route.
It does not inherit a stronger exclusion proof from a historical record merely
because the physical conclusion is already known there.

The existing partition producer/checker, split, run and checkpoint entry points
explicitly reject hull domains before applying their box/tetrahedron rules.
The one-ball box topology and contained-ball analytic volume keep their original
admission. A bounding box never substitutes for the declared physical hull.

## Full sphere receiving and frozen pilot

`freeze_hull_model` reads both coordinates and radii through the public
PyUnitWizard QuantityRecord codec, verifies their records and explicitly
converts to nm. It receives every row, converts the explicitly specified probe
from angstroms, and freezes the resulting binary64 values as exact rationals.
A supplied original hull proof is checked against that same file/frame/source.
No atom radius is inferred. The older tetrahedron reader shares this sphere
receiving boundary and preserves its original numerical records. Tests cover
corrupted radii/coordinates and a nondefault pm/fs application unit policy.

The [frozen pilot protocol](../evidence/reference_validator_hull_sterics_v1/protocol.json)
specifies four analytic fixtures: a permeable cube, an interior obstacle with
free endpoints/colliding straight path/valid bent path, complete one-ball cube
coverage, and a tetrahedron point inside the bounding box but outside H.
They include strict contact and sub-binary64-scale rational margin controls.

Six original-source profiles select the unchanged tetrahedron at probes
1.2/1.4/1.7 Å and narrow tube at 1.2/1.4/2.5 Å, reusing the retained source hull
proofs. The old tube reference path carries exterior tails. The protocol keeps
the full candidate for explicit rejection as a finite-hull path, and selects
only its 15 inner waypoints for positive interior-path checking at small probes.
That slice makes no hull-boundary attachment or full exterior-path claim.
Path conversion uses explicit PyUnitWizard angstrom-to-nm conversion, frozen
before query execution; source/reference/proof files are hash-bound.

The default capture selects only small analytic fixtures. Explicit `--originals`
adds the six source profiles sequentially. One CPU, one numerical thread, a
2 GiB address ceiling, 50 CPU seconds and a 60-second external wall deadline
bound this pilot; Slurm is not used in the maintainer-selected present phase.
Rejected candidates are recorded separately from positive proofs and never
become disconnection/empty-region results. New directories preserve old evidence.

At this source checkpoint 229 selected tests pass (211 earlier plus 18 new
model/geometry/source/path/CLI/capture controls), in 17.04 seconds with peak RSS
96,324 KiB, one CPU and 2 GiB. Ruff/format and mypy on 27 source modules pass
with Python 3.11 syntax and the actual 3.14 dependency target. All 355 original
case files remain unchanged. Original-profile receiving is the next execution;
the protocol alone does not qualify it.

## Developer commands and remaining work

```bash
python -m devtools.reference_validator freeze-hull-model INPUT.json MODEL.json --probe-angstroms 1.4 --hull-certificate HULL.json
python -m devtools.reference_validator domain-proof MODEL.json CERTIFICATE.json
python -m devtools.reference_validator verify MODEL.json CERTIFICATE.json
python -m devtools.reference_validator.capture_hull_sterics PROTOCOL.json NEW_DIRECTORY --originals
```

Use external resource limits. Outputs are new files/directories. Point and
path certificates use the existing separately checked certificate schema.

Complete mixed free-region construction, a certified clipped partition/resume,
boundary patches/attachments, per-region precision and all 19-profile receiving
remain under #76. A path in H does not qualify a path confined to a particular
native carrier; #181/#180/#184/#188 keep their dispositions. This is developer
source evidence, not public/package/platform admission. Optional attribution
remains P6; no original external engine is executed or credited. No comparative
superiority, protein phase or native kernel change follows.

The DFND chapters `geometry_and_probe.md` and `exterior_and_boundaries.md` were
reviewed: their strict-clearance/finite-hull/path-versus-boundary distinction
is preserved. No public operator or biological interpretation changes.
