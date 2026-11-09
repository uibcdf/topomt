# Depth, internal hierarchy and paths

A connected region can contain several chambers and narrow internal contacts.
DFND can describe that structure without replacing the component's primary
support or assigning each subregion a new family.

## Topological depth

For a component with exterior links, boundary nodes are its nodes incident to
those contacts. The initial depth is the smallest number of internal graph
edges from a node to that boundary set. Connected subsets of a depth layer
form depth regions.

This distance is dimensionless. Refining or changing the mesh can change its
value without changing a physical length proportionally. For a sealed component
with no exterior boundary, the current flat-depth convention does not mean its
interior is physically shallow; the chosen exterior-distance construction has
no starting boundary there. All of its stored node depths are zero. For an
accessible component, propagation uses the admitted transit graph, including
enabled connectors; a stored depth is not a count restricted to resident nodes.

## Access profiles and the funnel descriptor

At each represented depth $d$, the current descriptor selects the largest
resident-node capacity at that depth:

$$q_d=\max_{T\text{ resident},\ \operatorname{depth}(T)=d}R_T.$$

Levels without eligible nodes are omitted. With at least four levels, fit
$\hat q_d=a+bd$ by unweighted least squares and calculate

$$g=\frac{b(d_{\max}-d_{\min})}{\max_d q_d},\qquad
s=1-\frac{\sum_d(q_d-\hat q_d)^2}{\sum_d(q_d-\bar q)^2}.$$

`gradient` is $g$, negative for narrowing inward; `steadiness` is the fit score
$s$, stored rounded to four decimals. The implementation uses $s=0$ for a
constant profile and $g=0$ if the maximum capacity is nonpositive. With fewer
than four levels, `funnel` is `None`, not a negative detection. As elsewhere in
the morphology diagnostics, the fallback for an empty resident list is the
full component node list.

The provisional `is_funnel` rule requires $g\le-0.4$ and the **unrounded**
$s\ge0.8$. A constant-radius profile fails the narrowing test even if it looks
like a well-defined tube. Multiple branches at one depth are collapsed to their
maximum, so this profile is not a clearance measurement along one chosen path.
It does not measure a physical transport gradient or free energy, and does not
automatically promote a public Funnel feature. The single-cell tetrahedron has
neither enough levels for this fit nor enough centers for PCA elongation.

## Capacity merge hierarchy

Inside each current component, the implementation processes its admitted
internal transit edges in descending gate capacity. Basins carry their largest
node residence capacity. When two basins join at capacity $g$, a prominence-like
quantity is

$$\pi=R_{\rm peak,lower}-g.$$

Joins above the selected persistence floor produce throat candidates and
associated chamber candidates. Supports, parent-component keys and navigable
motif relations retain the basins and joining faces. Symmetric lobes can be
siblings under the same throat rather than an arbitrary nested parent/child pair.

These are provisional descriptors of the present component graph. The reported
`separation_radius` is the joining gate's capacity, not a universal physical
transition radius. Residence changes, excluded-atom checks, exterior-contact
regrouping and the selected query policy can affect the full decomposition at
another probe.

In particular, `flag_only` leaves suspect faces admitted: using `transit_edge`
does not universally eliminate intrusion flags. The graph policy remains part
of the hierarchy's context.

## Three uses of a narrow region

An internal admitted throat joins parts of one component. A nonpermeable wet/wet
boundary is a constriction between components at that query. A bank separating
regions is solid-side support. Their geometric roles and evidence differ even
when a renderer depicts each as a narrowing.

The compatibility `bottleneck` motif is a selected/ranked hierarchy descriptor.
It is not necessarily the minimum clearance of a globally optimal physical path.

## What the current channel skeleton computes

The skeleton helper uses the permeable **resident** subgraph. It ranks native
mouths by carrier area, selects the two widest usable contacts and chooses a
shortest route by center-to-center distance. Gate summaries are conditional on
that selected route.

This differs from maximizing the minimum capacity over all paths, from finding
every branch of a channel, and from validating an all-atom collision-free center
trajectory. Straight segments between cell centers can encounter obstacles.
A resident-only skeleton may also omit connectivity that the full component
obtained through nonresident connectors.

```{figure} figures/persistence_axes.svg
:alt: Capacity hierarchy within one query, probe changes on fixed coordinates and temporal changes on different coordinates form three distinct analysis axes.

Internal capacity hierarchy, probe-scale correspondence and temporal tracking
are separate analyses, even when they share support identifiers.
```

## Public interpretation

Native motifs are inspectable under the DFND result. Passing motif dictionaries
onto a public feature does not establish general spatial subregion promotion or
arbitrary parent/child relations. A chamber support, a measured path and a
public child feature each require their declared invariants.

Historical hierarchy toys provide engineering evidence for these descriptors.
They are not automatically new qualified BenchLab cases or a guarantee of
biological transport through every detected narrowing.
