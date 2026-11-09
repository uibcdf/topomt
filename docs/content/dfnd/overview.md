# What DFND asks and why it is constructed this way

Imagine moving a spherical probe among atoms represented by balls. At one
location it fits in a chamber; at another it fits locally but cannot enter from
outside; elsewhere a narrow opening controls access. The surrounding structure
also matters: a solid divider, an exposed ridge and an interface between two
molecular participants answer different topographic questions.

DFND organizes those observations on one geometric substrate. It produces
regions and supporting records that can be inspected, measured, named and related
through TopoMT. A pocket is one possible interpretation of those records.

## The construction in seven steps

1. Capture selected atom coordinates, effective radii and their source mapping.
2. Partition their finite convex hull into ordinary Delaunay tetrahedra.
3. Compute a local residence capacity for each cell and a local gate capacity
   for each face.
4. At a chosen probe radius, determine resident cells, admitted faces and the
   selected transit policy.
5. Decompose the finite transit graph, retaining contacts with a virtual exterior
   root separately. Build a complementary bank graph.
6. Derive boundaries, depth, morphology, interface descriptors and internal motifs.
7. Apply catalog rules and promote supported results into `Topography` features.

The name *flow network* refers to geometric connectivity in this construction.
The current DFN is undirected. It does not solve fluid flow, solvent diffusion,
binding kinetics or a directed attraction-to-sink process.

## Why ordinary Delaunay?

The triangulation supplies cells with recoverable atom-defined support and
shared faces with explicit adjacency. Geometry can be retained while many probe
queries reuse it. Atomic radii enter the local capacities rather than tessellation
weights. This separates the carrier from the exclusion and probe model.

That separation is a design choice, not a theorem that an unweighted mesh
recovers physical solvent topology. A local atom list can omit an obstacle even
when the carrier is perfectly valid. Changing the carrier and strengthening the
obstacle model are distinct decisions.

## Why two capacities?

Accommodation somewhere in a cell and accommodation somewhere on a particular
face are different constrained questions. Their maxima provide interpretable
local observations. A graph can then expose which cell contacts are admitted
for a chosen probe.

Three- and four-atom calculations are tractable local operators. Their locality
also loses information: omitted atoms can obstruct a candidate position, and
one maximum cannot describe all connected free subsets of a cell. DFND retains
diagnostics and policies for those issues; stronger physical statements require
additional evidence.

## Why remove an exterior root?

Accessible surface regions can communicate through the surrounding exterior.
Keeping that common root in a component search would join them through it.
Removing OCEAN makes a finite decomposition possible while preserving each
component's exterior contacts as separate records.

The finite support and its boundary convention therefore participate in the
definition of the reported regions. Global free-space connectivity alone does
not uniquely segment every intuitive surface depression.

## Why analyze wet and dry views together?

Free-region structure and surrounding barriers are complementary descriptions.
The same mesh supports incidence between them: which bank lines a wet region,
which faces form walls, and where a solid separator or exposed bank may support
further analysis. Recoverable incidence is useful before a general protrusion
or ridge segmentation method exists.

## Why separate identity, measurements and names?

One supported region can receive a different name when the probe or catalog
policy changes. A display rank is not a persistent identity, and a family label
does not define its geometry. Keeping support, observations and interpretation
distinct makes these changes inspectable instead of silently redefining the
object under study.

## Scientific position

Delaunay/Voronoi geometry, probe-based accessibility, cavity components and
channel paths have established antecedents. Alpha-complex pocket construction
and MOLE's accommodation/cavity/path pipeline are particularly relevant
{cite:p}`DFNDCAST1998,DFNDMOLE2013`. DFND's contribution must be evaluated through
its precise operators, resulting decomposition and coupled representations.
Different names or a shared geometric substrate do not establish novelty,
equivalence or superiority. [References](references.md) explain that context.

**Reading check:** can a region admit a probe position without providing an
entry path from outside? The next chapter defines both questions precisely.
