# DFND as the native core: theoretical reconstruction

Date: 2026-11-06, America/Mexico_City. Reviewed source:
`c117037fe2538c2185ad51a27600436d7c834356`.
Status: **conceptual review and proposed decision points**, not a replacement
for accepted contracts, an implementation change or fresh scientific validation.

This second reading follows the algorithm's reasoning from molecular geometry
to topographical entities. It complements the [repository audit](review_2026_11_06.md)
and qualifies the order in the [development proposal](development_plan_2026_11_06.md).
It includes the original proposals under `castp/ideas_paper_1998`, current DFND
definitions and the corresponding code. No new numerical experiment, notebook,
provider run, dependency installation or issue publication was performed.

## 1. Scientific objective and reference geometry

The objective is a rich characterization of molecular topography: empty-space
regions, outward relief, boundaries, interfaces, internal hierarchy and later
their evolution. Pocket detection is one use of this model. DFND is the native
semantic reference; Topography is the public scientific representation.

For reasoning, fix atom centres/radii and define the molecular ball union `U`.
Let `c_all(x) = min_i (distance(x, c_i) - r_i)`. For a spherical probe of radius
`p`, its collision-free centre set is `F_p = {x : c_all(x) >= p}`. This is a
reference construction for checking physical interpretations, not a new public
API or a claim that the current code computes this set exactly.

Distinguish `F_p`, the space occupied by a probe placed at those centres, bare
vdW-empty volume, and a union of tetrahedral carrier cells. Their connectivity,
volume and boundary measures are different objects. Molecular chemistry and
radius policy enter the chosen model; geometric accessibility alone supplies
neither solvent thermodynamics nor a biological transport rate.

## 2. Which algorithm the arguments support

The original [core proposal](../castp/ideas_paper_1998/topomt_core_algorithm_final.md)
uses weighted regular triangulation, an alpha complex, empty tetrahedra, directed
flow to sinks and attraction basins. Its title includes “final”, but it does not
define the current DFND implementation or establish a completed proof.

Current DFND deliberately uses ordinary Delaunay and local radius-aware
capacities, followed by undirected threshold-graph decomposition. The molecular
ball model, explicit supports, boundaries and semantic separation survive the
change. Alpha-complex/CAST flow guarantees do not transfer merely through that
shared motivation.

| Layer | Current mathematical/algorithmic role | Source correspondence |
| --- | --- | --- |
| Delaunay mesh | Partition of the atomic-centre convex hull into carrier cells and shared faces. Radii are applied afterwards. | `graph.py:288–336`; original weighted pipeline differs. |
| Residence | Maximum local clearance to four vertex balls, centre constrained to the closed cell. | `Mathematical_Definitions.md:81–125`; `clearance.py:332–414,461–629`. |
| Face capacity | Maximum local clearance to three face balls, centre in the closed triangle. | `Mathematical_Definitions.md:21–76`; `clearance.py:135–211,632–786`. |
| Transit policy | Resident cells plus optional nonresident cells having at least two admitted contacts. | `residence_transit_contract.md:85–150`; `graph.py:464–542`. |
| Components | Connected finite transit nodes; exterior connections are recorded separately. | `graph.py:820–897`; no sink-attraction map is computed here. |
| External links | Edge-connected clusters of permeable hull contacts to OCEAN. | `graph.py:891–965`; an opening can contain many triangles. |
| Interpretation | Residence, links and walls give topology names; morphology refines them. | `classify.py:22–47,119–174`; `feature_catalog.md`. |

Ordinary Delaunay is a legitimate geometric carrier without being a proof of
physical accessibility. A stronger physical method could still use it, provided
the relevant free subsets and connections were represented adequately. Choosing
an unweighted carrier and choosing local three-/four-atom obstacles are distinct
decisions.

## 3. A necessary clarification: residence and physical transit

The adopted residence definition is existential: a cell is resident if **some
probe-centre position in it** has sufficient clearance. It explicitly does not
require the whole probe sphere to lie inside the tetrahedron. See
[the residence audit](residence_radius_audit.md), lines 85–110 and 286–300.

Let `c_T(x)` use only the four vertex atoms of a cell `T`. Then:

```text
c_T(x) >= c_all(x)
R_residence(T) = max over x in T of c_T(x)

A physically valid path has c_all(gamma(t)) >= p.
If x = gamma(t) lies in T, then:

R_residence(T) >= c_T(x) >= c_all(x) >= p.
```

Thus, **under the stated exact maximum definition, a cell with
`R_residence(T) < p` cannot contain a centre position on a physically valid path
of that probe**. This also applies to its closed boundary. The probe extending
across artificial cell faces does not defeat the implication.

This is a logical consequence of the definitions, not a new measured molecular
failure or a claim that the implemented solver always attains the exact maximum.
Numerical error, generous thresholds and different residence/permeability
tolerances need their own interpretation.

The code's `transit_connector` remains a well-defined graph policy: it uses at
least two locally open three-atom faces and a nonresident four-atom cell. Those
contacts do not supply the missing physical witness. They can omit the opposite
apex/other atoms and do not establish that their admissible spots connect.
The intuitive sentence “the probe can pass through but cannot reside” therefore
needs reconciliation with the corrected existential definition before being
used as a physical justification of this policy.

The [known-limitations discussion](known_limitations.md), lines 90–145, already
flags continuous-space and connector ambiguity. However, a collision-free
**centre** subset cannot intersect a truly nonresident closed cell under this
definition. If “accessible space” instead means part of the probe's swept
physical volume, that is another set and should be named separately.

This review does not remove connectors or override their accepted policy. It
identifies a question for explicit resolution:

- Keep the graph as a declared local connectivity surrogate and evaluate its
  usefulness/errors with that meaning; or
- strengthen physical passage by validating all relevant obstacles and the
  connected free subsets/ports inside cells; or
- expose separate local descriptors and validated physical-path outputs.

A genuinely different residence meaning would require a documented scientific
decision; it cannot silently replace the current existential definition.

## 4. What local clearances prove, and what they leave open

Because the local obstacle lists are subsets of all atoms, their exact maximum
clearances are upper bounds on the corresponding all-atom maxima. A local
failure can exclude a physical centre/face crossing at that probe radius; a
local success is a candidate that still needs the omitted obstacles checked.
Do not apply this bound to an unqualified approximate numerical result.

Using one consistent all-atom clearance field, a face is a subset of either
incident closed tetrahedron. Consequently its maximum cannot exceed either
cell maximum. The documented absence of a universal ordering between current
`R_gate` and `R_residence` is compatible with their **different obstacle lists**;
it is not evidence for physical passage without an admissible centre.

Even an all-atom face witness and an all-atom cell maximum do not establish
which ports connect inside a cell. A scalar maximum records existence, not the
number or connectivity of the remaining free subsets. A graph-path certificate
needs compatible local connections and collision-free geometry, or an explicit
approximation/error policy. The current skeleton correctly disclaims collision
validation.

## 5. Exterior, concavities and internal hierarchy

OCEAN is a virtual exterior root. Once a globally collision-free centre exists
on a convex-hull face, the outward-normal ray increases its distance from every
atomic centre. Under the same fixed ball/probe model, that supplies a route to
infinity. This supports the exterior construction; current local face capacity
alone does not establish the globally clear starting point.

Removing the common root retains distinct finite components that would otherwise
all communicate through the exterior. Counting connected exterior contacts then
supports the model's void/one-opening/multiple-opening distinction. The result
also depends on the finite carrier and its boundary convention; it is not a
general theorem that every intuitive surface depression becomes a separate
component.

The current catalog additionally separates wall-less exposed regions and
refines one-opening regions by occlusion into Pocket/OpenConcavity and
provisional Groove/Cleft. Mouths, walls, chambers, constrictions and separators
have their own supports and relations. Nested topography needs the internal
capacity/depth hierarchy; adding more family names cannot supply segmentation.

Exterior links currently cluster whole admitted triangles by shared edges.
Existence of some free point on each triangle does not establish that their
free patches meet across the shared edge. Likewise, zero faces classified
closed does not mean every boundary point is unobstructed. Mouth multiplicity
and the exposed/percolating signature therefore retain their discrete meaning
until the corresponding physical-boundary interpretation is established.

With fixed geometry and policies, increasing probe radius removes admitted
resident nodes, locally permeable contacts and transit edges. The discrete
graphs are nested; their components can split, and counts need not decrease.
This motivates a multiscale hierarchy, but a motif merge tree from one query
still needs validation before its critical values are described as the exact
future history of the complete decomposition. In trajectories, the geometry and
Delaunay support can change, so correspondence is another problem.

## 6. Dry structure, convexities and interfaces are core work

Current raw bank construction uses `dry_mask = ~finite_transit`
(`graph.py:1200`), while local dry residence means `~resident`. Connectors explain
the difference. The two readings should retain their own names and supports.
They are not an exact physical partition into atomic solid and solvent.

The dry graph and its incidence with wet components/exterior provide a common
substrate for outward relief and mixed/boundary entities. They do not by
themselves segment every protrusion: one connected bank can carry many exposed
lobes, ridges, walls and rims.

| Target | Available grounding | Additional operator/decision needed |
| --- | --- | --- |
| Protrusion / convex patch | Exposed dry/interface support, atom geometry, face depth. | Connected relief patch, reference neighborhood/envelope, prominence and a reproducible base/boundary. |
| Ridge / apex | Elongation, neighboring concavities, exposure and depth fields. | Ridge/maximum criterion, local support and scale/stability policy. |
| Rim | Incidence around an exterior link. | Boundary extraction and ordering; distinguish aperture patch from surrounding dry rim. |
| Wall / solid separator | Wet–dry incidence; dry region facing one or several wet regions. | Localized patch/region and explicit side roles; distinguish solid septum from an empty-space throat. |
| Buried core | Deep dry support. | A core criterion; internal material is not automatically an outward convexity. |
| Molecular interface | Participant identities, facing supports and contact evidence. | Association criterion and localized realization, possibly without a wet region or mouth. |

Code currently emits dry boundary/exposed shells, resident-lining supports and
a maximum-depth core candidate (`graph.py:1481–1607`). These are useful seeds,
rather than general implemented protrusion/ridge detectors. The original
[fine taxonomy](../castp/ideas_paper_1998/topomt_topological_feature_types_fino.md),
lines 233–246, already requires an outward surface patch relative to a
neighborhood/reference and distinguishable prominence.

For interfaces, keep three meanings distinct: a mesh incidence record, a
multi-bank geometric descriptor, and a molecular association with a localized
support. One participant can span banks; a tight dimer can form one bank; atoms
can support several regions. Whole-component mixed lining does not by itself
localize an interface patch. The accepted
[public contract](../topography_conceptual_contract.md), lines 145–216, controls
this distinction and allows interfaces without a cavity or a mouth.

## 7. Consequence for the development proposal

Before interpreting an algorithmic change as improved physical topography,
select the intended object and reconcile residence/transit/obstacle scope.
Independent references should test each implication in that chain, rather than
only matching names or counts.

Add a dedicated convexity/boundary workstream: choose a dry relief support and
segmentation criterion, define a prominence/base policy, and freeze positive,
negative, multi-relief and scale controls. Couple it to, but distinguish it from,
the molecular-interface workstream. These are central parts of the intended
TopoMT core even though staged delivery can begin with smaller raw descriptors.

The small API fixes in the earlier plan remain independently useful. Rust and
performance still matter, but agreement with the current implementation cannot
resolve these theoretical questions. No algorithm/default change follows
automatically from this review. The existing #76 reference gate is related;
the new definitional reconciliation needs explicit issue-owner triage before
being treated as filed work or a settled replacement specification.

## Reading and reasoning record

The second reading covered the complete 687-line original core proposal and
the 608-/89-line detailed/condensed original taxonomies, current rationale and
catalog decisions, mathematical/residence/transit contracts, and relevant
primitive, graph, dry/interface, motif and public-model code. It deliberately
asks what each step implies rather than inferring validity from implementation
presence or previous passing test counts.

The residence/path implication, consistent-field face bound, conditional
exterior ray and fixed-policy graph nesting were independently checked in the
parallel conceptual reviews. They are transparent deductions under their stated
assumptions, not executed molecular evidence or newly adopted method policy.
The general protrusion/interface operators remain proposals to define and test.
