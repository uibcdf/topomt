# Bounded physical-boundary implementation decision

Date: **2026-11-10**. Owner: [#151](https://github.com/uibcdf/topomt/issues/151).
Status: **bounded source implementation received at `4fc235335446d97125ea5315600c463c5e41f4e9`; source-only scope**.
The design below was recorded before scientific changes. The later receiving
section separates implemented behavior from the original decision.
The [boundary contract](boundary_connectivity_contract.md) retains the observable
and compatibility decision. Preserve native links, catalog names and Mouth
promotion. Compute the physical view alongside them and associate a patch only
with an independently checked continuous path inside that component's carrier.

## Algorithm selected

Project each hull triangle into an orthonormal plane. Intersect every selected
probe-expanded ball with that plane. Inventory circle extrema, circle/circle
intersections, triangle vertices and circle/edge intersections. Between adjacent
critical x coordinates, the complete ordered circle/line arrangement is invariant.
Subtract the closed disk intervals from each triangle section. Retain analytic
endpoint selectors for every resulting strip. Join strips across event sections
only through positive free intervals; do not infer connectivity from images or
sample counts. This includes several free components inside one carrier face.

Inventory every hull edge independently, subtracting all expanded-ball intervals.
A positive-clearance interval on that edge connects its two incident face
regions. Retain those seam intervals and face-region selectors as recoverable
support. Circle centers, radii and triangle frames retain units, exact source IDs
and the query/input identity. Complete covered faces justify a zero count even
when a free interior remains. Unsupported hulls, near tangencies, ambiguous event
ordering and exhausted work budgets return `unresolved`, with no total count.
Floating decisions carry explicit margins; they are not formal interval proofs.

For association, try bounded candidate interior points from resident cell
centers and the component's convex carrier center. A successful straight segment
must pass all-atom closest-distance checks and a complete tetrahedron-interval
cover inside the claimed support. Continue from the hull point along its outward
normal; convex-hull halfspaces and all-atom distances validate the exterior ray.
Failure to find a segment is unresolved, not exclusion of curved paths. Retain
path endpoints, margins, carrier intervals and component/support identities.

## Frozen first acceptance and resource budgets

Before new execution: the five frozen rows are tetrahedron 1.2/1.4/1.7 Å,
closed shell 0.2 Å and opened shell 1.4 Å. Expected counts are 4/0/0/0/1,
from the independent retained references, never production inputs. Positive
associations must reach actual public features. The seven pending acceptance
targets become required tests only when delivered. Extend to the fixed shell
0.05 Å after that panel; do not assume ten physical openings.

Default work ceilings: 512 hull faces; 100,000 arrangement events in total;
4,096 attempted component-to-patch segments; one CPU, sequential face analysis.
The public query carries these limits and a separate 1e-7 nm numerical length
margin (1e-6 Å), independent of mesh epsilon and physical tolerance widening.
Explicit noncomputation is available. No budget exhaustion becomes zero.
The initial pilot must stay below 6 GiB address space and 120 s CPU; measure
actual wall time/RSS before extending the selected receiving panel.

New analytic planar controls precede implementation: one disk cuts a triangle
into two free regions, an interior disk leaves one region, an off-plane intruder
covers the face, and tangent/degenerate/budget cases remain unresolved. Segment
checks include an interior obstruction despite free endpoints. These controls
are developer regressions with explicit geometry, not new BenchLab catalog
entries or fresh held-out scientific benchmarks. Later mapped-motion/scale,
seam, tampering, suppression/reuse and association controls retain #151/#76.

This decision does not claim implementation or qualification. Final evidence and
any narrower supported scope must be appended rather than inferred from this text.

## Review refinements before the source checkpoint

Work accounting includes tested circle pairs, critical-section evaluation, cells,
joins and subdivision nodes, rather than accepting only the final event count
as the computational budget. Selected atoms are capped at 512; association-pair
records are independently capped at 4,096 to prevent an unbounded component ×
patch allocation. Path attempts retain their separate 4,096 ceiling.

A computed zero additionally requires a complete positive-margin ball cover,
with recoverable subdivision paths, not merely an empty arrangement inventory.
This cover also resolves a numerically marginal arrangement when it proves the
whole face covered; it never supplies a guessed positive count. The maximum
subdivision depth is 12. Near-threshold closure tests first exposed an
unjustified zero and now require an unresolved outcome. All accepted region
witnesses are rechecked on their carrier against all selected expanded balls.
Exterior continuation also retains a direct all-atom infinite-ray margin.

**Promotion decision:** retain the existing catalog and native-link Mouth
contract for this compatibility increment. Physical contacts are reported through
`feature.boundary['physical_openings']` and the canonical native record. Four
physical contacts therefore coexist with the tetrahedron's Percolating and zero
Mouth children. Neither a Channel relabeling nor replacement of Mouth carrier
areas is performed. A future incompatible Mouth/catalog migration needs its own
review under #60/#76; no such migration is required to read physical contacts.

The 0.05 Å shell pilot reports 13 patches with compatible paths, versus ten
native links. This is a **candidate runtime observation**, not an independent
13-patch reference, a completed #76 study or a comparative claim. The frozen
four/zero/zero/zero/one reference remains the first qualified receiving panel.

## Executed bounded receiving

The selected 14-module panel gives **207 passed**, 44.25 s pytest time /
46.063 s process wall time, peak RSS 445,552 KiB. One existing NumPy 2.5
shape-assignment deprecation comes from an unchanged snapshot test. All seven
#151 acceptance targets pass without expected-failure markers. The independent
reference verifiers retain their original implementation and frozen evidence.

Additional regressions cover an interior face obstruction creating two patches,
a nonlocal ball, event degeneracy, near closure, finite cover support, blocked
segment interiors, incomplete seams/inventories, false witnesses and work/path
budgets. Actual public/typed/raw counts, unit-policy changes, mapped motion/atom
permutation/similarity scaling, reporting suppression, mesh reuse and deep versus
shallow copies are exercised. The real Ackredit panel passes; NumPy/TopoMT credit
is retained without inventing a DFND publication or execution of another engine.

The core/config/graph and new test selector passes scoped mypy. The broader
legacy registry/data invocation still has 55 diagnostics, reproduced exactly by
shadowing the unchanged `7031181` files; this is not a clean legacy-module typing
claim. Its separate typing evidence was recorded with #77; following the bounded
public-registry correction on 2026-11-11, the native internal follow-up is
[#189](https://github.com/uibcdf/topomt/issues/189). Full CI, Python/OS
matrix and installed/release qualification remain #16/#58.

Execution used one CPU and numerical thread, 6 GiB address-space and 120 s CPU
limits. About 56 GiB remained available before execution with zero memory PSI and
no active sampled swap traffic. Slurm socket discovery failed; no allocation was
claimed. Input/protocol hashes and frozen certificate/notebook bytes remain intact.

After modular separation of planar arrangements from hull/path assembly, the
focused physical panel gives **41 passed**, including two capture guards. A new
red/green regression prevents hull-face enumeration from changing patch
occurrence IDs: identity uses the query and atom-defined region representatives,
while recovery retains complete clipped selectors. The six-file core/config/graph
and new tests pass mypy. This does not promise IDs across arbitrary remeshing.
The strict complete Sphinx build passes; 83 pages and 7,038 local targets validate
at the local candidate (not a newly served artifact).

Formal per-case capture at the committed fixing revision matches all five
independent counts, in 2.097 / 0.960 / 0.639 s respectively, peak RSS below
289,000 KiB. The protocols preceded capture in that same source commit. Complete
records are retained under each case's `physical_refinement_v1/observations.json`.
Historical package-version metadata reflects the preserved human version-file
change; the explicit source revision, not that mutable string, identifies this fix.

## Live lifecycle receiving

After source/evidence publication, the maintained finding card, hub and DFND/lab
opening summaries were updated and independently read back. #151 is closed for
its bounded source correction; #75/#76 and other wider owners remain open.
The [complete five-card live snapshot](../evidence/physical_boundary_live_readback_2026_11_10.json)
passes `comparative_findings.py --check --snapshot ...`: the sole remaining
current DFND limitation in this register is volume precision. The historical
boundary card is retained as source-resolved history, with explicit fixing
revision and no installed-package/biological claim. This evidence is distinct
from an updated hosted website or a new package publication.
