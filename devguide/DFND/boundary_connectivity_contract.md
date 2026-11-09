# Physical boundary connectivity: implementation proposal

Date: 2026-11-09. Owner: [#151](https://github.com/uibcdf/topomt/issues/151).
Status: **concrete acceptance proposal; no runtime adoption or scientific fix**.
The [public conceptual contract](../topography_conceptual_contract.md) and
[native object model](object_model.md) retain authority. The Python/dictionary
names below are candidate spellings for this bounded implementation, not an
announced public API or a new serialized schema. Broader support adoption is #60.

## Decision proposed for the next implementation

Keep three distinct observations:

1. **Native exterior link:** a cluster of admitted carrier triangles in the DFN.
   Its existing count, support keys and graph incidence retain their meaning.
2. **Physical boundary patch:** a connected component of strictly free
   probe-center space on an explicitly selected boundary surface. Its support
   includes excluded-ball constraints; a list of whole triangles is insufficient.
3. **Component contact and public Mouth:** attachment to a native component
   requires a compatible continuous path. Promotion to Mouth is a separate,
   versioned catalog decision with support and parent relation evidence.

Add the physical observation alongside native links, then qualify component
contacts. Preserve the current catalog/feature classes in the first bounded
increment. Expose qualified contacts through the public feature's boundary
description even when its current class is Percolating. Do not manufacture four
Mouth children or relabel the tetrahedron Channel just to match a patch count.
Whether all qualified hull contacts should become Mouth features, including
those of Percolating, is a subsequent explicit promotion decision under #151.
The acceptance tests here require inspectable contacts, not that decision.

This is a compatibility sequence, not acceptance of "fully free boundary" as
the meaning of the current Percolating class. Its current zero-wall predicate
means all carrier faces passed the native face predicate. Physical wall extent,
patch count and global accessibility require their own evidence.

## Defined geometric observable

For this panel let H be the closed convex hull of the selected atomic centers,
S its boundary, x_i an atomic center, r_i its adopted radius, and p the probe
radius. Define clearance c(x) = min_i (||x - x_i|| - r_i). The target set is

    P(S, p) = { x in S : c(x) > p }.

Its connected components are boundary patches. All selected atoms participate
in exclusion, including atoms outside a face's defining triple. This is a
probe-center observable on S, not a solvent-excluded molecular surface or a
surface independent of the chosen envelope. A future envelope is a different
surface context, even on identical input coordinates.

The mathematical inequality is strict. Numerical evidence carries an explicit
length tolerance and decision margin. The existing certificates use 1e-6 Å;
their stronger positive/negative margins justify the strict decisions. Do not
silently replace the target set by `c(x) > p + tolerance`, glue patches across a
covered edge, or resolve tangency/near-threshold uncertainty by rounding. The
current witnesses use floating arithmetic with margins, not formal interval
proofs. Unsupported/ambiguous cases remain unresolved.

Four disconnected patches on S can connect to the same free central region
and the same exterior. They are neither four volumetric components nor four
independent global transport channels. For the tetrahedron, the retained rays
connect the centroid through each patch to infinity; they do not prove every
native graph edge physically realizable.

## Candidate result and availability contract

The native raw result would gain `boundary_connectivity`; a typed native view
would belong under `topography.dfnd.dfn`, not a new `dfnd_*` root attribute.
The first acceptance test reads raw data received through the actual public
dispatcher, avoiding a new API dependency before the typed view is decided.

| Candidate field | Meaning and required evidence |
| --- | --- |
| `status` | `not_computed`, `unresolved`, or `resolved`; only the last permits a total count. |
| `surface` | `kind: atomic_center_convex_hull`, input snapshot, selected source atom map, recoverable hull geometry, surface identity and definition/version. |
| `query` | Probe/radius definition, all-atom exclusion scope, strictness, explicit units, numerical tolerance, algorithm/version and relevant margins. |
| `n_patches` | Integer for a resolved complete boundary decomposition; otherwise `None`. Computed zero requires a complete cover, not an empty candidate list. |
| `patches` | Complete resolved patches, each with `patch_id`, support and evidence. Partial candidates on unresolved results must be separately marked and cannot establish the total count. |
| `support` on a patch | `kind: hull_free_patch`, `carrier_faces_source_atom_indices`, face-local connected-region selectors and all excluded-ball constraints, with a recovery path. Whole-face carriers alone do not recover the patch. |
| `evidence` on a patch | `connectivity: resolved` requires verified within-face connectivity and seam decisions; include method, witnesses/bounds, completeness and decision margins. |
| `component_associations` | Separate status and path-supported associations to source component identity/support, including attachment point and exterior continuation. Proximity or a shared triangle alone is insufficient. |

Patch identifiers are contextual occurrences, independent of enumeration,
catalog family and reporting filters. Retain recoverable structural support
separately; no universal identifier across different probes or atom reindexings
is promised. Correspondence under rigid motion/permutation needs explicit maps.
Every record retains its exact query/input association and provenance.

`not_computed` means the analysis was not requested or its capability is absent.
`unresolved` means it was attempted without a complete justified decision;
include the reason and supported bounds/partial evidence. Do not report either
as zero. Empty resident DFND output does not suppress the global boundary
observable: the excluded tetrahedron has zero hull patches independently of its
lack of resident components. A missing/degenerate surface is an unresolved or
unsupported geometry, not proof of a covered surface.

The public feature would gain the method-neutral boundary entry
`physical_openings`, with `status`, `n_patches`, `patch_ids`, surface/support
references and `association_evidence`. The two positive controls require
`association_evidence.status: resolved`. The view refers to the same canonical
patch records, not a separately editable geometry. A provider that cannot
establish these contacts declares availability honestly.

Physical aperture area is an optional evaluation over a resolved support with
an accuracy contract. Existing `Mouth.area`/`area_geometric` are carrier-triangle
areas; retain their provenance and compatibility meaning until an explicit
migration. No aperture area, global bottleneck radius, or exact volume follows
from patch connectivity alone.

## Frozen acceptance panel

| Input / probe | Global physical patches | Central region evidence | Current native/public observation |
| --- | ---: | --- | --- |
| regular_tetrahedron / 1.2 Å | 4 | Four rays connect one free centroid to the four patches and infinity. | One native exterior cluster, zero wall faces, one Percolating, no Mouth children. |
| regular_tetrahedron / 1.4 Å | 0 | Covered hull and free centroid; enclosure. | Void, no Mouth children. |
| regular_tetrahedron / 1.7 Å | 0 | No free probe center anywhere in the finite hull. | No resident wet component. |
| closed_shell / 0.2 Å | 0 | Complete hull cover and free origin; enclosure. | Void output, no exterior links or Mouth children. |
| shell_with_opening / 1.4 Å | 1 | One free boundary patch and an origin-to-exterior ray. | One native/public pocket with one Mouth. |

References are the retained [tetrahedron certificate](../../docs/content/benchlab/synthetic/regular_tetrahedron/boundary_connectivity.md),
[complete shell cover](../../docs/content/benchlab/synthetic/closed_shell/closure_at_0p2.md)
and [opened-shell certificate](../../docs/content/benchlab/synthetic/shell_with_opening/opening_connectivity.md).
Their verifiers replay the original witnesses and validate input/protocol
hashes. The tests reconstruct full-precision inputs through MolSysMT and the
actual `get_topography(method='dfnd')` route; the opened shell retains its parent
selection map. The source projection is measured separately from the reference.
All frozen input, certificate and historical observation bytes stay unchanged.

`tests/test_dfnd_physical_boundary_contract.py` first produced seven failures
and two passes on the unchanged scientific source. All seven failures were
missing candidate views, not four-versus-one comparisons of different
observables. They are now **strict expected failures restricted to the custom
missing-view exception**. A present but incorrect/incomplete view or unrelated
error fails normally; a fully passing candidate unexpectedly passes and forces
review/removal of its marker. These markers are an executable proposal under
open #151, never correction/qualification evidence. Existing reference and
source-contract guards remain ordinary required passing tests.

## Bounded implementation and review gates

1. Record a reviewed decision on the observable and compatibility sequence in
   #151. If the proposed spelling/structure changes, update the acceptance tests
   and this proposal together before advertising any API.
2. Build the physical decomposition independently of reporting/catalog filters.
   Use all-atom clipped face regions with complete within-face component and
   seam decisions. Edge-blocking alone cannot solve multiple patches inside a
   face. Do not hard-code the number four or dispatch on case names/certificates.
   Production must not depend on BenchLab witnesses or `devtools` imports.
3. Establish bounded algorithms with explicit budget/unresolved fallback;
   propagate support, units, atom correspondence and evidence. For these inputs,
   recover the candidate supports and replay the known independent decisions.
4. Validate component-to-patch paths against component support, not just the
   global origin rays. Expose the method-neutral public contact view while
   preserving the recorded native/classification interpretation. Promotion
   changes need their own parent/support and compatibility tests under #151.
5. Remove expected-failure markers only as their behavior is delivered. Extend
   guards for unit-policy changes, rigid motion, mapped atom permutations,
   reporting suppression, cached-probe reuse, empty/ambiguous inputs, and
   actual raw/typed/public correspondence. The initial seven tests are a minimum
   receiving gate, not the full scientific/support acceptance suite.
6. Reconcile the current finding/card/hub, case summaries, issue and report
   before claiming correction. Keep source qualification distinct from installed
   artifacts/matrix (#16); retain the broader support (#60), independent-path
   (#76), and volume-precision (#75) gates.

All concrete next steps above belong to #151 within the stated boundaries;
this design slice does not close that issue or resolve its current finding.
