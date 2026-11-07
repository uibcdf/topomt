# DFND and MOLE: antecedents and contribution space

Date: 2026-11-07, America/Mexico_City. Scope: primary-source and
specification comparison; no scientific-kernel execution, molecular experiment,
installation or coordinate submission. This document records the review; it does
not change an accepted algorithm, runtime file or laboratory scheduling. This is
an assessment of defensible claims, not a conclusion that DFND is either original
or unoriginal as a whole.

The inspected TopoMT checkout was at `4b866396efc6dcf8ef0c84e5ba4ecac6f661b483`
when the source fingerprint was taken. The previously selected A1 API correction
remains pending while this comparison takes priority.
The MOLE reference was independently checked at
`e0df21c35a1116d712e5a09094aae62e130f698c`, with empty `git status --porcelain`.
Its README identifies MOLE 2.5. Numerical-core source, old author drafts, and the
2013/2018/2025 publications must retain distinct evidential roles.

A newer official tree was also inspected: clean `sb-ncbr/webchemistry` master
`fe0e84582a6bd42bc69224fd3a3022bf5c51cec3`, committed 2026-10-26. Its
`AppsAndServices/Tunnels` contains the same tetrahedron, edge, exterior/partition
and radius operations after ignoring headers/imports/whitespace. Profile geometry
also agrees; inspected changes include deferred chemistry/lining work and helper
APIs. `C25` below names the pinned MOLE source, not a claim that it is the newest
tree or the live web binary. Neither engine was compiled or executed.

The public [MOLE engine](https://github.com/sb-ncbr/MOLE),
[Webchemistry tree](https://github.com/sb-ncbr/webchemistry) and
[MOLEonline interface](https://github.com/sb-ncbr/moleonline-web) are distinct
repositories. Reference clones were created only in the task-owned ignored cache;
no pre-existing upstream checkout was updated. The bundled manual was located,
but text extraction was unavailable and no parser was installed.

This review qualifies the [current justification](Justification.md),
[theoretical reconstruction](core_theory_review_2026_11_06.md) and
[development proposal](development_plan_2026_11_06.md), without replacing their
accepted definitions or open scientific gates.

## Conclusion that is already justified

DFND cannot claim the invention of Delaunay/Voronoi molecular free-space graphs,
tetrahedron probe accommodation, interior/exterior scales, geometric cavity
components, graph depth, exits, channel bottlenecks, or structure-linked channel
descriptors. A more restricted contribution may exist in the exact pair of local
clearance functionals, the resulting transit policy and decomposition, and the
coupled wet/dry representation. Those possibilities require comparison and
validation; none is established by naming the objects differently or by the
absence of a matching public MOLE class name.

The reviewed justification treated explicit decoupling of habitability and
connectivity as the main contribution. That is too broad as an originality claim;
its descriptive statement that DFND implements the separation remains correct.
The [maintained justification](Justification.md) now acknowledges the antecedents
and MOLE's volumetric cavity preprocessing before path extraction.

## Primary evidence and its limits

**P07/P12: earlier antecedents.** The [2007 primary abstract](https://doi.org/10.1016/j.str.2007.10.007)
already describes Voronoi/Dijkstra channels and many-snapshot MD use; full text
was inaccessible, so detailed 1.x internals remain unverified. The
[2012 calculation section](https://pmc.ncbi.nlm.nih.gov/articles/PMC3394309/)
describes interior pruning by probe passage through tetrahedral faces, whereas
P13 describes existential accommodation inside a cell. Face passage is therefore
an explicit antecedent too, without demonstrating DFND's exact closed-face
maximum. Preserve P12/P13/C25 formulation differences rather than merging them.

**P13: published algorithm.** The 2013 article already defines sphere
accommodation inside a tetrahedron using its four atomic vdW spheres, within a
Delaunay-graph pipeline of exterior peeling, interior filtering, cavity
components, depth and paths. Its fit predicate precedes DFND's residence problem;
the numerical solver is not fully specified. [MOLE 2.0, sections Implementation / Steps
i–vii / Lining / Merging channels](https://pmc.ncbi.nlm.nih.gov/articles/PMC3765717/).

**P18: published update.** The 2018 description retains the preceding pipeline,
names Probe Radius and Interior Threshold as separate cavity controls, adds path
weight choices, and provides alternative radius profiles. It distinguishes
postprocessed flexibility from analysis of structural ensembles. This is prior
for richer settings and descriptors, not proof that MOLE implements DFND's exact
functionals. [MOLEonline 2018, Calculation of channels / Visualization /
Limitations](https://pmc.ncbi.nlm.nih.gov/articles/PMC6030847/).

**P25: current publication.** The 2025 article explicitly bases detection on the
2018 approach; its advances include visualization, shared structural results and
saved settings. It does not establish a newly specified numerical kernel.
[MOLEonline 2025, Description of the tool / Availability](https://pmc.ncbi.nlm.nih.gov/articles/PMC12448857/).

**C25: inspected numerical source.** Here C25 means the MOLE **2.5 core**, not a
2025 release or a source-to-deployed-service match. At the pinned MOLE revision,
the ordinary
`MaxClearance` construction uses pair gaps and opposite-plane distances;
`IsInterior` compares it with twice the interior threshold, while
`IsSolventAccessible` also considers the geometric-center/circumcenter offset.
A separate strict branch uses incident edge clearance. These are not DFND's
closed-tetrahedron optimization. [Tetrahedron.cs,
L141–223](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/Primitives/Tetrahedron.cs#L141-L223),
[L261–264](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/Primitives/Tetrahedron.cs#L261-L264).

The implemented MOLE edge clearance uses the three shared atoms and distance to
the line through the two circumcenters. It is not a maximum over the closed
triangular face. The framework distance implementation is for an infinite line,
so calling this a finite-segment clearance would also be inaccurate.
[Edge.cs, L60–94](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/Primitives/Edge.cs#L60-L94),
[Line3D.cs, L13–22](https://github.com/sb-ncbr/webchemistry/blob/fe0e84582a6bd42bc69224fd3a3022bf5c51cec3/Framework/Net/WebChemistry.Framework.Core/Math/Line3D.cs#L13-L22),
[MathEx.cs, L72–75](https://github.com/sb-ncbr/webchemistry/blob/fe0e84582a6bd42bc69224fd3a3022bf5c51cec3/Framework/Net/WebChemistry.Framework.Core/Math/MathEx.cs#L72-L75).

Current MOLE preprocessing removes hull nodes, propagates exterior removal,
removes interior nodes, computes depth, prunes shallow vertices and partitions
the remainder into boundary-touching cavities and voids. These are actual source
operations, not just names in the paper.
[ComplexComputation.cs, L71–142](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/ComplexComputation.cs#L71-L142),
[L201–210](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/ComplexComputation.cs#L201-L210),
[L349–385](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/ComplexComputation.cs#L349-L385).

**D13: author draft, secondary evidential status.** The same repository retains
`Publication/methods_v2.tex`: lines 113–117 already use an infinite exterior
vertex; lines 135–138 give peeling, filtering and components; line 150 gives
path depth. The draft contains unresolved placeholders. It strengthens the
historical antecedent but is not a substitute for the published algorithm or a
specification of the running service.
[Pinned author draft](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/Publication/methods_v2.tex#L113-L150).

The mismatch between P13's sphere-fit description and C25's formulas must stay
visible. A source difference cannot erase the published antecedent; a published
description cannot be used to assert that the current executable solves the
same optimization as DFND. No source comparison here establishes the exact
deployed MOLEonline binary.

## Claim-by-claim assessment

MOLE's retained object model deserves particular attention before comparing
outputs. Its [Cavity class](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/Cavity.cs#L20-L122)
stores tetrahedra, boundary facets, residues, approximate volume, depth, graph,
openings and pore exits. The inspected pipeline reports sealed positive-volume
components as voids only when they contain more than 20 tetrahedra. Hull cells
are initially removed unconditionally, before propagated exterior peeling.

Its [opening construction](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/CavityOpening.cs#L38-L126)
connects boundary tetrahedra sharing at least two atom vertices, partitions them,
then selects spatially separated pivots and one largest-volume pore-exit pivot
per component. Thus connectivity-based opening grouping also has an antecedent;
DFND's exact face support/counting convention is the narrower comparison target.

| DFND feature / tempting claim | What cannot be claimed as new | Narrow candidate and present qualification | Evidence / next discriminating comparison |
|---|---|---|---|
| Standard Delaunay of atomic centers with radii applied afterward | The substrate and atomic-radius-aware free-space analysis; P13 and D13 are direct antecedents. | Selection, radii policy and retained source maps are explicit DFND contracts, useful independently of geometric novelty. | Mathematical_Definitions L7–11; graph L318–338. Use identical atoms, coordinates and radii before attributing an output difference to an algorithm. |
| `R_residence(T) = max` of four-atom clearance on closed `T` | The question whether a spherical probe fits inside a tetrahedron: P13 already states that existential question. | Explicit scalar capacity, closed-domain handling, boundary active sets and diagnostics may provide a different solver/contract from C25. This is a candidate numerical-method contribution only after completeness, stability and antecedent review. | Mathematical_Definitions L72–114; clearance L332–413; actual graph uses batch implementation L333–344. Compare unequal radii, obtuse/sliver cells, face/edge optima, overlapping atoms, degeneracy and rescaling. |
| `R_gate(F) = max` of three-atom clearance on closed `F` | Edge passage capacity, clearance-dependent connectivity and bottlenecks in general; P13/C25 already distinguish graph passage costs from cavity preprocessing. | The domain and optimization differ concretely from C25's circumcenter-line clearance. This may be a meaningful alternative operator, not evidence of better physical reachability. | Mathematical_Definitions L17–68; clearance L135–211. Compare local gate values, witnesses and induced adjacency, especially nonacute faces and unequal radii. |
| Explicit residence versus permeability | Separating accommodation and passage broadly, or using more than one scale. | A specific pair of node/face functionals with independently inspectable margins may distinguish DFND's formal model. MOLE's Probe Radius/Interior Threshold are not automatically the same pair of local capacities. | Justification L34–46; graph L472–495; P13/P18/C25. Write operator-level correspondence rather than a parameter-name comparison. |
| Nonresident transit connectors, terminal contacts and `resident_only` alternative | A generic claim that a graph can pass through a node which is not a chamber. | DFND's exact rule `not resident` plus at least two permeable contacts is a concrete semantic choice. It remains to establish its realizable domain and useful consequences under the adopted exact local models. | graph L486–495, L514–542; Mathematical_Definitions L127–144, L192–197. Compare truth tables and valid geometric witnesses, then paths. Two open face witnesses alone do not prove that a continuous probe-center trajectory joins them. |
| Virtual `OCEAN` | Introducing an exterior graph vertex; D13 already does so. | DFND deliberately keeps finite transit cells and computes their components without the virtual root, rather than adopting C25's finite-cell peeling surface. This can change the reported object, not automatically improve it. | Mathematical_Definitions L199–234; graph L847–859. Compare region support before/after exterior processing, including exposed rafts, multiple fragments and broad open slabs. |
| Root removal followed by connected components | Connected-component graph decomposition, exterior separation or cavity diagrams as general ideas. | The complete DFND policy is an alternative definition of a component. The implementation never inserts a concrete ocean node: its finite adjacency is already the root-removed graph. | graph L847–859, L891–924 versus C25 preprocessing. An equivalence/counterexample must specify both policies and geometry, not merely observe different cavity counts. |
| `ExternalLink` as an edge-connected cluster of permeable hull faces | Exits, mouths, pore openings or access descriptors broadly; P13 already uses exits and multi-exit paths. | Exact face-cluster support, clustering convention and links separate from derived mouth geometry may be a useful representation and a distinct counting rule. | Mathematical_Definitions L223–231; graph L891–965. Compare one broad opening versus multiple disconnected contact patches with the same cavity and probe. |
| Family classification by external links, residence and walls | Pockets, voids, channels, pores and classification by access broadly. | DFND supplies a closed rule over its own grounded signature; `percolating` is a wall-count override. This is an explicit taxonomy for this graph, not proof of biological type or a new geometry detector. | classify L22–47; graph L968–983. Compare classifications only after aligning region and opening definitions. |
| Wet/dry complementary views of one mesh | Complementation, dual views or graph connectivity as mathematics. | Retaining a separate bank graph, its incidences and wet-side associations is a stronger specific DFND candidate for comparison with MOLE's exposed model. No matching MOLE layer was established by this bounded inspection; that is not proof of worldwide novelty. | graph L1200–1230, L1620–1752; dry_network_and_convexity L126–150. Compare what both tools retain and can reconstruct, not only their GUI defaults. |
| Dry bank / local dry distinction | Calling all nonresident cells a probe-excluded material body without checking the transit policy. | DFND's bank mask is the complement of **finite transit**, so connectors may be locally nonresident yet absent from banks. Bank edges also depend on `dry_adjacency`. Any novelty or topology statement must name those choices. | graph L487–495, L1200–1203, L1636–1672. Compare with the local wet/dry truth table in Mathematical_Definitions L151–197. |
| Dry interfaces, shells and face depth | Graph-distance depth or layer extraction broadly; P13 and C25 already implement depth. | Applying boundary-seeded distance to explicit dry banks, with role-specific contact records, is a possible model/descriptor contribution. Current depth is an unweighted graph count, not burial distance, SASA or a material property. | graph L1356–1433, L1435–1480; dry_network_and_convexity L152–185. Evaluate discretization, adjacency policy, contact seeding and localization before scientific interpretation. |
| Ridges, protrusions, rims, separators and dry cores | A current general detector for these motifs, or already validated convex topography. | Four dry descriptors are emitted: boundary shell, ocean-exposed shell, resident lining and maximum-depth core candidate. A bank-to-local-region/curve/patch segmentation operator, scale/support policy and geometric validation are still needed for the broader feature program. Unbuilt features cannot establish a present algorithmic advance. | graph L1482–1606; dry_network_and_convexity L223–242; classify L73–92. First define the target local object and its support independently of its proposed name. |
| Molecular interfaces | Equating a wet/dry face with a molecular interface, or a bank with a chemically defined participant. | Orthogonal multi-body lining labels can enrich a component. Current automatic promotion derives bank labels; tight bodies can fuse. Molecular labels and a localized interface region are additional contracts. | interfaces.py L8–14, L31–87; interfaces.md L79–106, L143–158, L181–190. Compare participant definitions and localization; distinguish relation, bank wall and realized spatial patch. |
| Hierarchy, chamber/throat candidates and persistence | Merge trees, union-find, bottlenecks, prominence or multiscale hierarchy as generic techniques. | The exact filtration uses internal transit faces ordered by `R_gate`, peaks from `R_residence`, and peak-minus-join persistence while retaining the original component. This combination merits comparison but is presently provisional and toy-qualified. It is not simply a full recomputation of DFND at every probe. | components L1021–1045, L1056–1167; output_status L130–160. Compare merge events, supports and limiting policies, including node births, connectors and changing exterior topology. |
| Stable identities, query reuse, lineage | Hashing, provenance, overlap matching, caching or event tracking in general. | DFND exposes atom-defined supports and contextual keys, separates a cached mesh from probe queries, and offers exact-support/Jaccard lineage under stable atom indexing. This is an assessable representation/API contribution without claiming a new geometric algorithm. | identity L38–114; graph L318–328, L810–825; lineage L1–14, L40–108, L111–157. Test identity and source semantics separately from correspondence quality. |
| Rich inspection, chemistry, persistence, visualization | Adding structural labels, profiles, saved results/settings or interactive viewers as a new category; P13/P18/P25 already supply precedents. | TopoMT-specific composability, source-bound recovery, copy/mutation protections and cross-provider consistency can be valuable software work. Each must be qualified through its actual public contract; it does not settle DFND originality. | Existing public API audit and current source context work. Separate engine execution, native DFND data, public feature projection and persistence claims. |

## Important mathematical limits on the candidate distinctions

A local algebraic illustration makes the implemented residence difference
concrete. For the previously adopted regular-tetrahedron reference with edge
`a=5.3 Å` and four equal atomic radii `r=1.7 Å`:

| Local quantity | Formula | Value |
| --- | --- | ---: |
| DFND residence target | `a*sqrt(6)/4-r` | 1.545574 Å |
| DFND gate target | `a/sqrt(3)-r` | 1.359956 Å |
| MOLE non-strict interior threshold capacity | `max(a-2*r, a*sqrt(2/3)-r)/2` | 1.313716 Å |

At a hypothetical common threshold of 1.4 Å the local residence predicates
therefore disagree. This is substitution into formulas, checked with Python's
standard `math` module, not a scientific-kernel run, a default-setting comparison
or an accuracy ranking. MOLE's hull removal and minimum void-size filter make a
one-cell application-level benchmark unsuitable. The plane term above is an
absolute apex-to-plane distance, not just a pair-gap estimate.

The source's [Voronoi path weight](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/Primitives/Edge.cs#L25-L38)
uses the sum of **squared** circumcentre/centroid displacements, whereas the 2018
prose/current methods describe distances. Its [profile construction](https://github.com/sb-ncbr/MOLE/blob/e0df21c35a1116d712e5a09094aae62e130f698c/WebChemistry.Tunnels/WebChemistry.Tunnels.Core/Tunnel.cs#L326-L383)
samples 100 spline knots, checks five nearest atomic centres at each, clamps
radii to at least 0.01 Å and builds radius splines. This is not a demonstrated
global vdW-distance minimum for unequal radii or a continuous collision-free
certificate. These details define the comparison target; they establish no
comparative accuracy result.

1. **The residence objective itself has a direct published antecedent.** For
   four vertex atoms, existence of a point satisfying all probe-clearance
   inequalities is equivalent to a max-min clearance threshold, if the same
   admissible domain is used. Closing the tetrahedron explicitly clarifies
   boundary cases; it does not by itself create a new accommodation problem.

2. **The gate difference is concrete but changes the modeled question.** DFND
   optimizes where a probe center could cross a face in its three-atom local
   model. C25 measures distance relative to a particular circumcenter line.
   Different values are expected for some geometries. Demonstrating this is a
   model distinction; demonstrating that one better measures the intended
   molecular phenomenon requires an independent target and error criterion.
   DFND's own specification excludes a guarantee of all-atom continuous-space
   reachability. A face optimum can be obstructed by a fourth or nonlocal atom.
   [Mathematical_Definitions.md](Mathematical_Definitions.md)

3. **The connector rule deserves proof before being used as a selling point.**
   Its software predicate is unambiguous, but existence and physical transit are
   separate questions. In particular, independently feasible faces do not, by
   logic alone, establish a connected free-center subset inside the intervening
   tetrahedron. The current diagnostic status of nonresident passages is a
   warning against using the classification table as evidence of a validated new
   phenomenon. [output_status.py](../../topomt/dfnd/output_status.py)
   More strongly, under the exact residence definition a physically valid
   probe-centre path cannot intersect a truly nonresident closed cell: its local
   four-atom clearance is at least its all-atom clearance. The
   [theoretical reconstruction](core_theory_review_2026_11_06.md) gives the
   implication and proposed interpretation choices. No connector policy changes
   automatically follow from this review.

4. **A two-field merge construction is not automatically a standard radius
   filtration.** DFND keeps current transit edges, then orders their capacities;
   its nodes are not reactivated at all possible probe radii in that routine.
   Any equivalence to persistent components of the whole probe-dependent graph
   needs to account for node residence, connector activation, gate intrusion,
   exterior relations and policy changes. The code accurately calls the result
   an internal descriptor, retaining one original component.
   [components.py](../../topomt/dfnd/components.py)

5. **The dry layer is a program of work, not finished convexity extraction.**
   A connected dry bank may span a whole molecular body. Getting individual
   protrusions/ridges requires an explicit localization/segmentation operator
   over bank or interface supports, then a geometric descriptor and a stability
   policy. Multiple-bank incidence can suggest a separator but cannot substitute
   for identifying its local support. The experimental interface routines use
   betweenness or pendant peeling; these standard graph operations do not yet
   define a universally bounded molecular interface patch.
   [experimental.py](../../topomt/dfnd/experimental.py)
   [interfaces.md](interfaces.md)

## How to decide what kind of contribution remains

| Claim level | Evidence needed before using the claim |
|---|---|
| New algorithm or geometric operator | An exact mathematical problem and operator, the closest existing definitions and implementation, a demonstrated non-equivalence or new solution, a correctness argument, and consequences on controlled inputs. An unimplemented aspiration or renamed graph object does not qualify. |
| Different useful model | Explicit assumptions and domains; examples where the alternative intentionally returns a different object; validation that this object answers a scientific question. This can be useful even when the primitives are known. |
| Representation / public API | A precise result and ownership contract, inspectable source maps, reproducible parameterization, round-trip and mutation guarantees, and examples that materially simplify composition. Do not relabel these as new molecular geometry. |
| Integration | A working, qualified boundary with MolSysMT, units, feature consumers and saved outputs. Integration novelty is specific to that ecosystem and cannot imply that competing tools lack the underlying analysis. |
| Performance engineering | Matched inputs, radii, outputs, correctness tolerances, hardware and versions, with timings and memory. Source architecture, vectorization or cached re-query design alone proves no comparative speed or accuracy claim. |

## Bounded next comparisons; no experiments performed here

1. Freeze a minimal operator specification for both P13's stated fit predicate
   and the exact inspected C25 implementation. Record where a service binary is
   unknown. Do not silently choose whichever reference makes DFND look better.
2. Compare residence and gate operators independently on analytic cells, with
   identical radii and unit conventions; include active boundary strata,
   unequal radii, near degeneracy and scale transformations. The earlier
   numerical audit's unresolved guards remain relevant; this review does not
   claim they passed.
3. Compare complete graph definitions and finite supports, including exterior
   processing, connector witnesses, edge acceptance and opening clustering.
   Separate different object definitions from detector failures.
4. Evaluate wet/dry bank and interface information against what MOLE exposes or
   permits reconstruction, then extend the literature search beyond MOLE before
   making a first-of-kind claim. Validate localized dry objects only after their
   segmentation/support contract exists.
5. Compare hierarchy outputs to the actual full query sweep, not only to another
   throat profile. Qualify lineage on atom-correspondent trajectories separately.

Until those gates are met, defensible wording is: **DFND is a TopoMT-native
geometric model that explicitly represents local residence, face permeability,
finite transit components and coupled dry-bank descriptors, with exact structural
supports and inspectable policies. Its relationship to prior MOLE accommodation,
cavity preprocessing and path analysis is being characterized.** This describes
implemented choices without declaring priority, superiority or universal
biophysical validity.

The recommendation is to continue the native DFND program, while grounding a
research claim in precise solver/decomposition differences and scientifically
useful coupled topography. Its undirected threshold graph does not compute a
physical flow field or transport rate. General relief/interface operators remain
work to define and qualify; they cannot count as delivered advances today.

No issue was published or closed. Existing numerical/reference work (#75/#76)
and the proposed theoretical reconciliation remain separate gates. Documentation
rendering, local-link validation and reporting-protocol checks apply to this
increment; remote CI, the full scientific suite, support matrix and installed
qualification remain deferred under [component qualification #16](https://github.com/uibcdf/topomt/issues/16).

## Files read for this pass

- `devguide/DFND/Mathematical_Definitions.md`: definitions through component
  families; `Justification.md`: complete current originality framing.
- `devguide/DFND/dry_network_and_convexity.md` and `interfaces.md`: reread from
  the preceding conceptual pass; focal sections cross-checked for this table.
- `abstract_contract.md`, `object_model.md`: exterior/root, support and hierarchy
  contracts cross-checked against the preceding full conceptual reading.
- `topomt/dfnd/core/clearance.py`: scalar operators and graph-facing batch entry
  points; `graph.py`: cached capacities, query states, finite components,
  external links, dry mask, interfaces, depth, motifs and dry adjacency.
- `components.py`: internal capacity hierarchy; `classify.py`, `identity.py`,
  `lineage.py`, `output_status.py`, `interfaces.py`, `experimental.py`: focal
  contribution and maturity contracts. Earlier full API audit remains at
  `.cache/dfnd-review/public_api_audit.md`; numerical audit is separate.
- Pinned MOLE `README.md`, `Primitives/Tetrahedron.cs`, `Primitives/Edge.cs`,
  `ComplexComputation.cs` and author `Publication/methods_v2.tex`; primary papers
  P13/P18/P25 inspected directly, P12 calculation sections and P07 abstract with
  the access limits above. Framework line-distance verification supplied
  by the independent numerical-code reviewer with pinned source citations.

No inference of absence from this bounded file set is a worldwide originality
search. No molecular-comparison tests were executed, and no scientific accuracy,
performance or deployed-service equivalence was qualified.

Documentation checks: report indexes are current; both reporting-protocol tests
passed in the shared Python 3.14 environment. Strict isolated Sphinx/MyST HTML
rendering of the seven changed guides passed, with 314 local link paths checked
separately. This checks local path existence, not remote HTTP responses or anchor
validity; it is not a full public-docs or scientific-suite qualification.
