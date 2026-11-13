# Exact reference-validator foundation: source checkpoint

Owner [#76](https://github.com/uibcdf/topomt/issues/76); first consumer #181.
Initial proof producer: `3b75f595eb6f52d9e6ff66a8f02bdcb0efb4633a`.
Operational continuation: `997f69b3d496333d7c89e2fc18dcd5a487ab38c1`.
These are bounded implemented P0 tranches of the
[implementation plan](physical_reference_validator_implementation.md), not a
complete connected-region validator or a supported public TopoMT detector.

## Direct inputs and checked resume — 2026-11-13 UTC

The three steric inputs are centers `(N,3)`, radii `(N,)` and the probe radius.
`Model.from_spheres(centers_nm, radii_nm, probe_nm, domain=...)` now receives
them directly and creates detached exact values, row IDs and a numerical source
digest. No bonds, chemical types or DFND results are needed. Units are explicit.
The extra domain is the finite observation context; the three sphere inputs
already define the globally excluded set. A hull and an exterior box ask
different volume/connectivity questions and cannot be silently interchanged.

Run/checkpoint contracts are implemented for the admitted box/tetrahedron
partition prototype. A run binds the model, fixed depth/leaf ceilings and exact
code/runtime identity; only per-step split budgets may change. Every unknown
cell remains in its frontier, including cells at a ceiling. Source changes
require a new run, while original mathematical certificates remain checkable.

Independent validation checks model/kernel/configuration identity, complete
coverage, counters, run summaries, parent links, preserved resolved cells and
nested volume bounds. It imports no producer or run-search module. Storage
uses exclusive new directories and a checksum manifest written last; incomplete
or altered bundles are rejected. This is not a universal power-loss durability
claim or atomic-directory-publication promise.

The [frozen resume protocol](../evidence/reference_validator_resume_v1/protocol.json)
reuses the original normalized 1.7 Å tetrahedron model. Its
[retained receipt](../evidence/reference_validator_resume_v1/receiving/receipt.json)
contains nine saved/read-back states plus an uninterrupted control:

| Step | Cumulative splits | Checked disposition |
| --- | --- | --- |
| 0 | 0 | Unresolved root; per-step budget reached. |
| 1–7 | 17, 34, 51, 68, 85, 102, 119 | Checked refinements with nested exact bounds; unresolved cells remain explicit. |
| 8 | 120 | 121 covered cells; complete finite-domain exclusion. |

The final mathematical certificate is identical to the uninterrupted control.
The capture uses one CPU and a 2 GiB address-space ceiling; 2.17 seconds elapsed,
peak RSS 21,508 KiB. It uses the saved exact model and standard-library checking,
without reloading quantities, DFND or an external geometric engine. These are
resource receipts for a small operational control, not competitive benchmarks.

## Implemented and checked

- Immutable exact nm models, explicit source atom/frame IDs, input SHA-256,
  strict probe contact, exact radius expansion and canonical rational JSON.
  Binary64 values retain their actual rational value, including conversion
  effects; no decimal approximation or hidden geometric epsilon is introduced.
- Admitted convex domains are boxes and nondegenerate tetrahedra. General
  atomic-center hulls are rejected by the first four-ball receiving route;
  it cannot substitute a box and change the validation question.
- Sufficient full-cell exclusion/availability predicates, exact convex-domain
  membership and whole-segment checks against every expanded atom. Nearest-center
  or four-local-atom checks cannot discard another blocker.
- A bounded Python partition pilot produces complete proof trees: box octants
  or tetrahedron longest-edge bisection. The independent checker reconstructs
  their coverage and recomputes all claims, without importing producer search,
  DFND, NumPy or the quantity codec. Shared trusted primitives are exact rational
  arithmetic and convexity, not an unchecked topology result.
- Exact total probe-center volume enclosures. Unknown cells remain in the upper
  bound; no requested volume precision is claimed. Only complete exclusion or
  an entirely free convex domain supplies an exhaustive zero/one component count.
- Standalone point/path and partition verification, schema/model/arithmetic
  binding, checker source fingerprints, finite work/input limits and saved CLI
  reading. Corrupt/missing/overlapping leaves, false covers/free claims and
  colliding paths are rejected.
- The four-ball reader uses the public PyUnitWizard quantity codec, propagating
  its RecordError on altered records. Received binary64 nm arrays are frozen
  exactly, without a claim of fresh equality to a newly executed DFND input.

The [developer usage guide](../../devtools/reference_validator/README.md) describes
the commands. The [frozen pilot protocol](../evidence/reference_validator_p0_v1/protocol.json)
precedes retained receiving. All ten proofs, exact models and original checker
receipts are in [the captured run](../evidence/reference_validator_p0_v1/receiving/receipt.json).
It records producer and dependency/source identities, checksums and resources.

## Actual frozen tetrahedron receiving

| Question | Checked result | Scope |
| --- | --- | --- |
| 1.2 Å, depth 6 | 38 leaves, 28 unknown; a valid broad volume enclosure with lower bound zero. | No component inventory or requested precision. |
| 1.4 Å, depth 6 | 38 leaves, 28 unknown; a valid broad volume enclosure with lower bound zero. | No enclosure/void or component-count proof. |
| 1.7 Å, depth 10 | 117 leaves, four unknown. | Small remaining volume does not prove exclusion. |
| 1.7 Å, depth ceiling 18 | 121 leaves, each covered by a specified expanded atomic ball; `[0,0]` volume. | Complete finite-tetrahedron exclusion; zero components. |
| Exact centroid, 1.2/1.4 Å | Two strict-free point certificates. | Positive point availability; no exhaustive component count. |
| Centroid to each of four face centroids, 1.2 Å | Four entire segments independently checked against all atoms and the tetrahedron. | Four access paths, not a boundary-patch inventory or global optimality proof. |

The positive points coexist with zero **lower** bounds from coarse cell
enclosures: those are conservative intervals, not zero-volume claims. No native
component label is used as reference truth. The 1.7 Å proof strengthens one
already studied finite negative control; it does not qualify #181's tubes.

The run takes 0.72 seconds internally (0.87 seconds for the bounded process),
peak RSS 51,844 KiB, one CPU and a 2 GiB address-space cap with a 60-second
external deadline. These measurements describe this tiny pilot, not performance
against DFND or another engine. Original case/notebook/download bytes remain
unchanged; retained proofs are new developer evidence.

Later source hardening in this delivery additionally rejects a decoded model
whose source binding differs from the frozen protocol, and rejects rational
inputs incorrectly labeled as received binary64 values. Dedicated failing tests
preceded both guards. The original receipt/source fingerprints remain historical
at `3b75f59`; saved models and mathematical proofs are independently replayed by
the final checker without overwriting the original verification records.

## Verification and remaining work

Test-first development began with absent-module failures. The first real-input
checks retained an insufficient depth-10 negative attempt and propagated the
owning codec's rejection type; tests now explicitly retain both unresolved and
proved outcomes. Coverage includes sub-float rational gaps, large translations,
exact contact, nonlocal radii, false endpoint-only paths, schema/model corruption,
budget ceilings, fresh-process checking without DFND/producer and saved replay.

For the initial tranche, repository Ruff/format and scoped mypy on all eight
source files pass, with Python 3.11 syntax and the actual 3.14 environment.
That bounded selection
passes **55 tests**: 38 new model/proof/receiving controls plus 17 existing
report/finding/original-artifact checks. It takes 4.45 seconds, peak RSS
90,624 KiB, one CPU and a 2 GiB address-space limit. The original 355 files
are checked unchanged. Report indexes, offline comparative metadata and 212
local file links pass. No full-suite or supported-platform matrix is inferred.
Linux-only capture/resource controls do not qualify a portable distribution.

The operational continuation passes **79 selected tests**, including 24 new
direct-input/run/storage/resume controls and all earlier selected checks.
It takes 14.30 seconds, peak RSS 91,336 KiB, one CPU and a 2 GiB address-space
limit. Repository Ruff/format and scoped mypy on thirteen source files pass;
report indexes and offline finding checks pass. The original 355 case files
remain unchanged. This is source evidence, not a full suite or public/platform
qualification.

The bounded P0 model/proof and operational run/checkpoint contracts above are
source-delivered; their initial absence is superseded by the continuation.
Complete general domain admission remains P1/P2 work. P1 still needs the
local/global geometry feasibility decision and an exhaustive free-region
construction. P4 needs volume precision targets and curved/high-order validated
integration; these broad enclosures do not meet the plan's k=24 target. Other
five-case hulls, all 19 profiles, complete apertures/attachments, biological
classification and public API/package qualification remain subsequent gates.

This standalone developer checker retains host/source/model provenance; it adds
no public scientific-client attribution boundary or original external kernel.
The planned P6 automatic attribution/API admission remains under #76. Do not
credit DFND, SBL or another detector as executed by the rational checker.
#180/#181/#184/#188 and the existing comparative findings keep their dispositions;
no native correction, original-provider run or protein phase is claimed.
