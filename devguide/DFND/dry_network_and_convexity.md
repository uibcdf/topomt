# DFND Dry Network and Convexity

This document defines the first DFND contract for the dry side of the method.

The wet side of DFND decomposes the probe-habitable space into
`concavity_domains`. The dry side characterizes the complementary
probe-excluded and probe-blocking structure. It is the starting point for future
convexity, boundary, and mixed features such as cores, protrusions, ridges,
rims, walls, separators, and lining regions.

This document is intentionally less mature than the wet-domain contract. The
canonical first step is the dry graph definition. Higher-order dry motifs remain
candidates until implemented and validated.

## 1. Interpretation

A dry tetrahedron is not literally an atom or a piece of molecular matter. It is
a finite Delaunay tetrahedron where the selected probe cannot reside.

A dry connection is not just geometric adjacency. It is adjacency through a face
that blocks the selected probe.

Therefore the dry side should be read as:

```text
dry graph = probe-excluded / probe-blocking network
```

This complements the residence/transit graph:

```text
residence = where the probe can reside
transit   = where the probe can pass through
dry graph = where the probe cannot reside and where faces block passage
```

A non-resident tetrahedron with at least two permeable contacts is a
`transit_connector`. It remains dry for residence metrics but participates in
probe movement.

## 2. Dry Nodes and Dry Edges

For a selected probe radius `R_probe`:

```text
dry_node(T) = finite tetrahedron T with R_residence(T) < R_probe
```

Dry connectivity uses non-permeable faces:

```text
dry_edge(T_i, T_j) =
    T_i and T_j are dry nodes
    and T_i, T_j share a finite face F
    and R_gate(F) < R_probe
```

Equivalently:

```text
dry connectivity = connectivity through non-permeable faces
```

This is the first canonical policy. It is preferred over simple dry-dry face
adjacency because it preserves the physical meaning of a probe-blocking barrier.

## 3. Dry Components

A `dry_component` is a connected component of dry nodes connected by dry edges.

```text
dry_component = connected component of dry_node graph through dry_edges
```

Dry components are graph objects. They are not yet final convexity features.
They provide the substrate for dry motifs and dry-interface analysis.

Many molecular systems may contain one dominant dry component associated with
the probe-excluded body of the molecule. This is not a failure of the
definition. The useful information is expected to come from dry interfaces,
dry depth, exposure, and motif analysis rather than from component counts alone.

## 4. Relation to Local Classes

The local class `open`, `coast`, or `sealed` is still defined by face
permeability pattern and is independent of wet/dry habitability.

Dry nodes may be:

```text
dry_open
dry_coast
dry_sealed
```

Interpretation:

- `dry_open`: probe cannot reside in the tetrahedron, but finite faces are
  permeable. If it has at least two permeable contacts, it is a
  `transit_connector` and can preserve movement connectivity while contributing
  no resident volume.
- `dry_coast`: probe cannot reside, but some faces are permeable and some are
  not. With exactly one permeable contact it is a `terminal_contact`; with two
  or more permeable contacts it can also be a `transit_connector`.
- `dry_sealed`: probe cannot reside and all finite faces are non-permeable.
  This is the strongest local dry barrier class.

Only faces with `R_gate < R_probe` create dry graph edges. Permeable faces belong to transit or terminal-contact logic, not dry-edge logic.

## 5. Dry Interface

The `dry_interface` is where dry graph objects meet residence regions, transit
domains, `ExternalLink` records, `OCEAN`, or the hull/exterior context.

Interface records should preserve:

- dry component id;
- dry tetrahedron ids;
- resident or transit tetrahedron ids when present;
- shared face ids;
- face permeability state;
- adjacent transit-domain or concavity-domain ids when present;
- adjacent `ExternalLink` ids when present;
- adjacent `OCEAN` or hull context when present;
- atom and residue ids supporting the interface.

The interface is expected to be important for:

- lining atoms of concavity domains;
- walls of pockets and channels;
- separators between wet domains;
- protrusions into accessible regions;
- rim candidates around exterior openings;
- future pharmacophore descriptors.

## 6. Dry Depth

Dry depth is the graph distance from the dry interface into each
`dry_component`.

Define dry boundary nodes as dry nodes incident to at least one dry-interface
record:

```text
dry_boundary_node(v) =
    dry_node(v)
    and v is adjacent to a wet node, ExternalLink, OCEAN, or hull/exterior
    context through a finite or hull face
```

The first dry-depth definition is unweighted graph distance inside the dry
graph:

```text
dry_depth(v) = shortest number of dry_edges from v
               to any dry_boundary_node in the same dry_component
```

This creates intuitive dry layers:

```text
dry_depth = 0  -> first dry shoreline
dry_depth = 1  -> second dry shoreline
dry_depth >= 2 -> deeper dry interior
```

Dry depth is a topographic descriptor. It should not be conflated with
Euclidean depth, solvent exposure, or elastic rigidity, although it may later be
correlated with those quantities.

## 7. Dry Interface Signatures

Each dry node, dry region, or dry motif can carry an interface signature:

```text
touched_concavity_domain_ids
touched_external_link_ids
touches_ocean
touches_hull
exposure_to_ocean
min/mean/max dry_depth
local dry class composition
```

These signatures are the main bridge from raw dry components to interpretable
topographic objects.

Examples:

```text
touches one concavity_domain mostly
    -> lining_region or wall_candidate

touches two or more concavity_domains
    -> separator_candidate or ridge_candidate

touches OCEAN strongly
    -> exposed protrusion_candidate or ridge_candidate

touches an ExternalLink boundary
    -> rim_candidate

has high dry_depth and weak OCEAN exposure
    -> dry_core_candidate
```

## 8. Candidate Dry Motifs

Candidate motifs derived from dry components and interfaces include:

- `dry_core_candidate`: large or deeply connected dry component;
- `dry_island_candidate`: smaller isolated dry component;
- `lining_region`: dry or dry-coast region adjacent to one concavity domain;
- `wall_candidate`: dry region forming a boundary of one concavity domain;
- `separator_candidate`: dry region adjacent to two or more wet domains whose
  removal or erosion could connect them;
- `ridge_candidate`: elongated dry/interface region separating wet regions or
  exterior-accessible regions;
- `rim_candidate`: dry/interface region around an `ExternalLink` or its derived
  mouth geometry;
- `protrusion_candidate`: dry component or dry-interface region exposed to
  `OCEAN` and projecting into wet/exterior space.

These are not canonical feature families yet. They should be reported as
candidate motifs or diagnostics until scoring, geometry, and stability rules are
validated.

`Rim` and `Mouth` should remain distinct:

```text
Mouth = geometric descriptor derived from an ExternalLink
Rim   = dry/interface motif around or bordering an opening
```

## 9. Dry Motif Discovery Strategy

The first `dry_motif` implementation should be conservative. It should compute
descriptors that support motif discovery without forcing fragile final labels.

Recommended first descriptors:

- dry component id;
- supporting dry node ids;
- supporting dry edge ids;
- supporting interface ids;
- adjacent concavity domain ids;
- adjacent external link ids;
- `touches_ocean`;
- `exposure_to_ocean`;
- minimum, mean, and maximum `dry_depth`;
- local class composition: `dry_open`, `dry_coast`, `dry_sealed`;
- compactness, elongation, or anisotropy when geometry is available;
- graph centrality or cut/corridor descriptors when graph analysis is enabled.

Possible dry-lumping signals:

- dry-depth layers;
- interface signature;
- OCEAN exposure;
- adjacency to one or more concavity domains;
- adjacency to one or more external links;
- graph bottlenecks or min-cut candidates;
- geometric shape descriptors.

The first implementation should expose these as raw/candidate descriptors. It
should not yet require a hard, public `Protrusion`, `Ridge`, or `Rim`
classification.

## 10. Possible Feature Destinations

Dry motifs may later feed several Topography feature families:

```text
ConvexityFeature:
    Protrusion
    Ridge
    Core

BoundaryFeature:
    Rim
    Neck
    derived mouth-related boundary descriptors

MixedFeature:
    Wall
    Separator
    LiningRegion
    Interface
```

Some dry motifs may remain annotations attached to a `ConcavityFeature` rather
than becoming public features.

## 11. Future Mechanical Coupling

Dry topology may provide a useful bridge to structural mechanics and dynamics.
Potential future descriptors include correlations between:

- `dry_depth`;
- dry-component centrality;
- dry-core membership;
- B-factors;
- RMSF from molecular dynamics;
- GNM/ANM fluctuation modes;
- hinge candidates;
- allosteric paths;
- mutation-sensitive buried regions.

This belongs to a future coupling layer with ElastNetMT or related elastic
network tools. It should not affect the first dry graph definition.

## 12. Possible Convexity Features

The future Topography layer may expose convexity features derived from dry
motifs:

```text
Core
Protrusion
Ridge
```

Boundary and mixed features may also be derived later:

```text
Rim
Wall
Separator
LiningRegion
Interface
```

These should not be implemented as final public features until the dry-motif
rules are validated on simple systems and real molecular examples.

## 13. Invariants

The first dry-network implementation should preserve these invariants:

- dry nodes are finite tetrahedra only;
- `OCEAN` is not part of the dry graph;
- dry edges require non-permeable shared faces;
- every dry node belongs to exactly one `dry_component` under the selected dry
  connectivity policy;
- dry components do not replace concavity domains;
- dry motifs are derived from dry components and dry interfaces;
- filtering tiny dry components is a reporting step, not a graph-construction
  rule;
- `dry_open` and marginal dry cases must be retained in raw diagnostics.

## 14. Implementation Status

Canonical now:

- `dry_node`;
- `dry_edge` through non-permeable faces;
- `dry_component`;
- `dry_interface` records;
- `dry_depth` as unweighted dry-graph distance from dry boundary nodes;
- dry interface signatures as raw descriptors.

Candidate or experimental:

- `dry_motif`;
- dry core detection;
- protrusion detection;
- ridge detection;
- rim detection;
- wall and separator detection;
- convexity, boundary, and mixed feature construction;
- coupling to B-factors, RMSF, GNM/ANM, hinges, and mutation sensitivity.

The wet-side DFND contract remains the implementation priority. The dry side is
now defined well enough to avoid conceptual drift when convexity work begins.
