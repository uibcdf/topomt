# `fpocket4` Scalable Options

## Purpose

This document collects design ideas for a future `fpocket4` implementation mode
or family of modes oriented to large systems, provisionally named:

- `implementation='topomt-scalable'`

The purpose of this document is not to change the current behavior of:

- `implementation='wrapper'`
- `implementation='native'`
- `implementation='topomt'`

Instead, it records the options we currently see for making `fpocket4` faster
and more scalable on large systems, especially cases such as `2HGR.pdb`.

The intended target is not an approximate detector. The intended target is a
more scalable implementation path that preserves the same final parity contract
already established for `implementation='native'`.

## Scope and architectural rule

The current rule should remain explicit:

- `wrapper`
  means external binary integration
- `native`
  means parity-oriented reproduction of the audited upstream source behavior
- `topomt`
  means TopoMT-specific methodological corrections
- `topomt-scalable`
  would mean a strategy optimized for large systems and scalability while
  preserving the same final parity target as `native`

Performance-oriented heuristics or approximations should **not** be introduced
silently into `native`.

## Why this is needed

The current native path reaches final exact parity against the audited local
fpocket source build on the audited routine systems, but large systems remain
expensive.

`2HGR.pdb` is the clearest current motivation:

- retained heavy atoms: `55,628`
- much larger than the routine control systems (`~1,000-2,300` heavy atoms)
- both the audited local fpocket build and the current native path are slow
- current native geometry construction generates hundreds of thousands of raw
  alpha-spheres on this input

That makes `2HGR.pdb` a good deep-validation and performance benchmark, and it
justifies a future scalable path.

## Current performance reading

The main large-system cost currently appears to come from:

1. building the DelaunayMesh alpha-sphere-derived view for very large point
   sets;
2. handling very large raw alpha-sphere populations;
3. global clustering over many accepted alpha-spheres;
4. downstream descriptor work if the pocket candidate set remains large.

So the most promising scalable work is likely to happen:

- before or during alpha-sphere generation;
- in candidate reduction before global clustering;
- and in replacing global clustering with a more scalable strategy.

## CPU-first rule for the next stage

Before introducing:

- local CPU pools,
- distributed execution,
- or GPU acceleration,

TopoMT should first study how far a single-process CPU design can be improved
without changing the hardware model.

This is important because it forces the project to answer a stricter question:

- what work is intrinsically necessary,
- and what work is only expensive because the current implementation is too
  global, too object-heavy, or too eager.

For the next stage, `topomt-scalable` should therefore be explored first as a
**CPU-first, single-process redesign**.

## CPU-first design principles

The first scalable prototype should try to improve cost through:

- less global work;
- fewer raw alpha-sphere candidates surviving into late stages;
- fewer Python objects created before the final output layer;
- more array-oriented intermediate data;
- lazier descriptor evaluation;
- and clustering routes that scale with local connectivity rather than with a
  full global hierarchy.

These principles are more important than any one concrete optimization.

## More detailed CPU-only option families

### 1. Reduce object overhead aggressively

The current parity-oriented path benefits from clear intermediate structures,
but that clarity is expensive on very large systems.

For a future `topomt-scalable` path, a better strategy may be:

- keep intermediate alpha data in dense arrays as long as possible;
- delay creation of `AlphaSphere`, `Pocket`, or other Python objects until the
  final candidate set is already small;
- store per-alpha fields in columnar form instead of object-per-alpha form;
- postpone unit-wrapped or feature-wrapped objects until output materialization.

Potential gain:

- lower Python overhead
- better cache behavior
- lower memory pressure during the largest phases

### 2. Filter during generation, not only after generation

One of the current costs is that large systems first produce a very large raw
alpha population and only then reduce it.

For `topomt-scalable`, it may be better to reject candidates as early as
possible.

Ideas:

- apply clearly safe radius-window rejection immediately;
- compute cheap geometric rejection criteria before expensive per-alpha
  bookkeeping;
- attach a fast local-neighborhood test during generation to reject obviously
  redundant or low-value alpha-spheres;
- optionally maintain a region-local "best representative" policy for
  near-equivalent candidates.

The key idea is:

- if a candidate is obviously unpromising, it should die before entering the
  global candidate arrays.

### 3. Separate exact geometry from expensive semantics

Some work may be unavoidable if the geometry is global, but not every semantic
operation needs to happen immediately after geometry construction.

A scalable CPU path may therefore benefit from a staged pipeline:

1. geometric generation
2. cheap geometric rejection
3. connectivity clustering
4. only then descriptor-rich pocket materialization

This means descriptor work such as pocket-level summaries, ranking terms, or
surface-related quantities should be deferred until the cluster set is already
small enough.

### 4. Replace global hierarchical clustering with sparse connectivity

This is likely one of the strongest CPU-only candidates.

The parity path is valuable, but a scalable path should seriously consider
representing alpha connectivity through:

- sparse radius graphs;
- adjacency from local spatial hashing;
- union-find over neighbor edges;
- or connected-components style clustering with local thresholds.

This would avoid building or traversing a large global linkage structure for
systems where local geometric connectivity is the only thing that really
matters.

### 5. Introduce a progressive candidate budget

Very large systems may benefit from an explicit budget model.

This does not have to mean a hard cap. It can mean:

- each region or tile can only pass a bounded number of near-equivalent
  candidates forward;
- high-density regions must compress redundant alphas before the global stage;
- and late-stage descriptor work is only run on the survivors.

This would make worst-case growth much more predictable than the current
generate-first, reduce-later behavior.

### 6. Make descriptor evaluation lazy and selective

A scalable path should distinguish between:

- descriptors needed only for survival;
- descriptors needed only for ranking;
- descriptors needed only for final reporting.

Those three groups should not be computed at the same stage by default.

For example:

- a cluster may be dropped without ever computing the full expensive descriptor
  stack;
- only top-ranked or survivor pockets may need the full final descriptor set;
- and debugging or audit modes can opt back into richer intermediate output.

### 7. Explore local reconciliation instead of global certainty

If full global certainty is too expensive, a CPU-scalable path may get better
cost-quality tradeoffs by solving smaller local problems and then reconciling
them.

That reconciliation could happen at several levels:

- alpha representatives
- local pocket fragments
- overlapping region merges
- near-duplicate pocket suppression

This idea overlaps with spatial partitioning, but the key design point is that
the expensive part of the computation should happen on bounded local problems,
not on one monolithic global state whenever possible.

### 8. Create a "fast internals, faithful outputs" path where possible

Not every scalable change has to relax the final user-visible behavior.

Some CPU-only work could make `topomt-scalable` faster without changing the
scientific output much, for example:

- replacing object-heavy internals with arrays;
- avoiding repeated conversions;
- reusing spatial indices across stages;
- and postponing expensive output construction until the end.

This is a useful reminder: scalability is not always the same as approximation.

## Option families

### 1. Pure CPU algorithmic improvements

These are the first options that should be considered before GPU work.

#### 1.1 Spatial partitioning before global geometry

Partition the receptor into spatial tiles or regions, for example using:

- KD-tree based blocks
- voxel grids
- bounding-box partitioning
- overlapping subdomains

Potential benefit:

- avoid building one monolithic global geometry structure for the entire system

Main risk:

- pockets near subdomain boundaries may be split or distorted unless overlap
  and reconciliation are handled carefully

#### 1.2 Candidate reduction before expensive clustering

Keep the current geometric generation, but reduce the candidate set earlier.

Options:

- stronger but explicitly scalable-only radius/candidate filters
- local density pruning
- discard clearly buried or clearly redundant alpha-spheres
- deduplicate near-equivalent alpha-spheres more aggressively

Potential benefit:

- smaller clustering problem
- lower memory pressure

Main risk:

- may accidentally change fidelity unless carefully defined and benchmarked

#### 1.3 Replace global hierarchical clustering

The current parity-oriented path uses a global single-linkage hierarchical
clustering workflow. For very large systems, that may be one of the main
scaling bottlenecks.

Alternatives to explore in `topomt-scalable`:

- graph connected components on a radius-neighbor graph
- union-find / disjoint-set clustering
- grid-neighbor clustering
- approximate radius-graph clustering

Potential benefit:

- much better scaling than a full global linkage matrix

Main risk:

- may fail to reproduce the exact same semantics as the parity-oriented path

#### 1.4 Multi-stage pocket detection

Use a coarse-to-fine strategy:

1. coarse candidate detection
2. coarse clustering
3. local refinement only in promising regions

Potential benefit:

- avoid spending full cost on clearly irrelevant parts of the system

Main risk:

- requires a proof or strong empirical demonstration that the same final pocket
  contract is preserved

### 2. CPU parallelization and distribution

If algorithmic work alone is not enough, the next options are process-level
parallelism and distributed execution.

#### 2.1 Multi-process local partitioning

Run independent geometric work on spatial partitions in parallel across CPU
processes.

Good fit for:

- large systems
- workstation or server execution

Requirements:

- partitioning strategy
- reconciliation of overlapping subdomain results

#### 2.2 Distributed execution across nodes

Potential future direction for very large systems or batch workflows.

Possible models:

- job-array style partition processing
- scheduler-driven region jobs
- explicit task graph systems

Main value:

- large performance ceiling for very big systems or many systems

Main risk:

- complexity is much higher than local CPU parallelism

### 3. GPU-oriented acceleration

GPU work is likely valuable, but should come after the CPU-side design is
better understood.

#### 3.1 Good GPU candidates

Operations that look naturally GPU-friendly:

- large batched distance calculations
- overlap/contact checks
- neighborhood tests
- surface point sampling
- ASA/SASA-like calculations
- grid occupancy and voxel operations

#### 3.2 Harder GPU candidates

Operations that are less straightforward:

- exact global Delaunay/Voronoi construction
- direct reproduction of upstream embedded-Qhull semantics

That does not mean GPU is impossible there, but it is less likely to be the
first scalable win.

### 4. Hybrid strategies

The most realistic large-system path may be hybrid:

- CPU for geometry construction or partition management
- GPU for distance-heavy or surface-heavy phases
- local refinement only where needed

Any such hybrid path must still be validated against the same final native
parity target.

## Candidate design directions for `topomt-scalable`

### Direction A: Partition + local geometry + merge

Workflow:

1. partition the receptor into overlapping spatial regions
2. compute local alpha-spheres in each region
3. cluster locally
4. merge overlapping pockets across regions

Pros:

- natural route to multi-process scaling
- avoids one global geometry object

Cons:

- tricky reconciliation at region boundaries

### Direction B: Global geometry + scalable graph clustering

Workflow:

1. keep one global alpha-sphere generation step
2. reduce candidate set aggressively
3. replace global linkage clustering with a scalable graph/union-find method

Pros:

- easier to compare against the current native path
- likely simpler than full partitioning

Cons:

- still pays the global geometry construction cost

This direction is especially attractive for a first CPU-only prototype because
it isolates one likely hotspot without forcing an immediate redesign of the
geometry stage.

### Direction C: Coarse-to-fine detection

Workflow:

1. coarse spatial scan or coarse cavity proxy
2. identify promising regions
3. run detailed alpha-sphere logic only inside them

Pros:

- can save a lot of time on very large systems

Cons:

- hardest to benchmark for fidelity

## Recommended near-term exploration order

The most pragmatic order currently looks like:

1. profile native `fpocket4` on large systems by phase
2. quantify candidate explosion before clustering
3. prototype a sparse connectivity or union-find clustering replacement on CPU
4. prototype array-first internals that delay Python object creation
5. test early candidate-reduction rules on large systems
6. evaluate spatial partitioning for large systems
7. only then consider GPU acceleration for the most expensive remaining phases

## CPU-only brainstorming questions

The next design pass for `topomt-scalable` should explicitly study questions
like these:

- Can the geometry stage emit a cheaper intermediate representation than full
  object-rich alpha-sphere records?
- Can accepted candidates be compressed regionally before any global
  clustering?
- Can the clustering problem be reframed as sparse graph connectivity instead
  of global linkage?
- Can descriptor evaluation be split into survival, ranking, and reporting
  phases?
- Can local redundancy be removed deterministically without harming the final
  pocket contract too much?
- Can large systems be processed as a sequence of bounded local problems before
  any global merge?

## Idea triage rule

Every scalability idea should be classified into one of these buckets before
implementation work grows:

### Bucket A: likely exact-preserving

These are ideas that mainly change internals, data layout, or evaluation order
without obviously changing the mathematical result.

Examples:

- replacing Python objects with dense arrays in intermediate stages;
- delaying object construction until the final output layer;
- splitting descriptor computation into lazy stages;
- reusing spatial indices instead of rebuilding them;
- caching reusable geometry products when the exact same values are needed more
  than once.

These should be explored first.

### Bucket B: plausible but needs proof

These are ideas that might preserve the same final result, but only if their
equivalence is demonstrated carefully.

Examples:

- replacing hierarchical clustering with a sparse connectivity route that is
  intended to be mathematically equivalent;
- local compression of near-equivalent alpha-spheres under a rule that claims
  to keep the same survivors;
- partition-and-merge strategies that aim to reconstruct the same final
  pockets.

These are valid `topomt-scalable` candidates only if the parity claim survives
benchmarking.

### Bucket C: speed-oriented but parity-risky

These are ideas that may be useful for exploratory research, but they are not
acceptable for `topomt-scalable` if they change the final result.

Examples:

- aggressive coarse prefilters with no proof of equivalence;
- approximate clustering thresholds;
- approximate nearest-neighbor substitutions that change the accepted
  candidate set;
- hard candidate caps that can eliminate valid survivors.

These may still be interesting conceptually, but they should be rejected for
`topomt-scalable` if they drift from `native`.

## First-wave exactness-preserving candidates

The most promising first implementations are the ones most likely to stay in
Bucket A.

### 1. Array-first internal representation

Instead of moving quickly into object-rich intermediate structures, keep the
heavy stages in arrays:

- centers
- radii
- lining atom indices
- polarity markers
- cluster ids
- descriptor-ready scalar fields

Then build Python objects only after the survivor set is already small.

Why this looks safe:

- it changes representation, not semantics
- it should preserve the same accepted candidates if the same formulas are used

### 2. Lazy descriptor materialization

Separate descriptors into stages:

- acceptance-stage fields
- cluster survival fields
- ranking/final-report fields

Why this looks safe:

- if the same descriptor formulas are applied to the same surviving pockets,
  the final result should remain unchanged
- the gain comes from not evaluating expensive fields for clusters that die
  early

### 3. Reuse and caching of spatial products

Potential reusable products:

- atom neighbor lookups
- alpha neighbor lookups
- region-local candidate indices
- repeated atom-subset descriptors

Why this looks safe:

- caching avoids recomputation without changing the formulas

### 4. Minimize conversions and wrappers

A scalable path should audit every expensive stage for repeated:

- unit conversions
- object wrapping/unwrapping
- list-to-array or array-to-list transitions
- repeated atom-index remapping

Why this looks safe:

- these are implementation costs, not algorithmic semantics

### 5. Streaming instead of fully materialized stages

The current path tends to think in large complete stage outputs:

- build all raw candidates
- then filter them
- then cluster them

A more creative exact-preserving alternative is to stream candidates through
multiple exact filters before they ever become part of a large retained set.

Possible pattern:

1. generate a bounded batch of raw candidates
2. apply all exact cheap rejection rules immediately
3. emit only survivors into the retained structure
4. continue with the next batch

Why this looks safe:

- if the same exact rules are applied, batching changes memory behavior more
  than semantics

Potential gain:

- lower peak memory
- smaller live candidate populations
- better locality

### 6. Exact connected-component decomposition before pocket work

Before the expensive pocket stages, it may be possible to decompose the problem
into exact independent subproblems.

Examples of possible exact decompositions:

- disconnected receptor regions
- disconnected alpha-neighbor components
- spatial components separated by a guaranteed gap larger than the pocket
  connectivity threshold

Why this is interesting:

- it is more creative than generic partitioning because it only splits the
  system when exact independence can be certified
- independent components can then be solved with the same semantics and merged
  trivially

Why this looks safe:

- certified disconnected components should not affect each other in the final
  pocket result

### 7. Signature-based memoization of repeated local work

Large structures may contain repeated or near-repeated local configurations.

A future scalable path could test whether some exact local computations can be
memoized by a stable signature, for example:

- lining-atom identity sets
- local neighborhood graph signatures
- descriptor subproblems defined on the same atom subset

Why this is creative:

- it attacks repeated work through reuse rather than pruning

Why it might stay safe:

- memoization does not change formulas if the signature really identifies the
  same exact subproblem

Main caution:

- the signatures must be exact enough; approximate signatures would move this
  idea into a parity-risky bucket

## Second-wave candidates that need equivalence work

These are probably the most important for large wins, but they need a stronger
proof burden.

### 1. Equivalent connectivity clustering

Question:

- can the current pocket grouping be reformulated as sparse graph connectivity
  while producing the same final clusters as the current parity path?

Why it matters:

- if yes, this could remove one of the largest global bottlenecks

Required proof:

- identical cluster ids up to renumbering
- identical final pocket membership

### 2. Exact-preserving local compression

Question:

- are there near-equivalent alpha-sphere families where all but one member are
  provably redundant for the final pocket result?

Why it matters:

- large systems may contain local candidate explosions that are internally
  redundant

Required proof:

- removing the compressed members does not change final pocket membership or
  ranking

### 4. Event-driven active-region evaluation

Question:

- can the method avoid treating the whole system as equally active by driving
  late-stage work only from regions that actually contain surviving candidates?

Possible pattern:

- generate exact candidates globally or semi-globally
- maintain an active frontier of regions with survivors
- only run the expensive local follow-up work where surviving candidates still
  exist

Why this is creative:

- it changes the control flow rather than only the math

Required proof:

- inactive regions must be inactive by exact consequence, not by heuristic

### 5. Certified upper-bound rejection

Question:

- are there exact upper bounds that let the method reject some regions or
  clusters before computing the full expensive descriptor stack?

Examples:

- a region cannot reach the minimum alpha count anymore
- a partial cluster cannot possibly exceed the required density threshold
- a candidate family cannot produce a valid pocket after exact local tests

Why this is creative:

- it uses mathematical impossibility rather than approximation to save work

Required proof:

- the bound must be rigorous; approximate upper bounds are not acceptable for
  `topomt-scalable`

### 3. Partition-and-reconcile with exact reconstruction

Question:

- can overlapping spatial regions be solved locally and reconciled in a way
  that reconstructs the same final result as the global path?

Why it matters:

- this is one of the few routes with a chance of very large scaling gains

Required proof:

- same final pocket set as `native`
- no boundary-induced losses or artificial merges

## Explicit rejection rule

For `implementation='topomt-scalable'`, a candidate idea should be rejected if
any of the following becomes true in validation:

- final pocket count drifts from `native`
- pocket atom membership drifts from `native`
- ranking/order drifts in a way that changes the validated contract
- large-system drift appears only because the method prunes too aggressively

In other words:

- runtime wins are not enough
- peak-memory wins are not enough
- a strategy only qualifies for `topomt-scalable` if it stays faithful to the
  same final output contract

## Additional creative directions worth keeping in mind

These are not yet mature implementation proposals, but they are valuable
enough to keep on the design radar.

### 1. Exact sweep-line or region-activation scheduling

Instead of a monolithic "whole structure at once" mindset, the method could be
scheduled as a sequence of exact local activations driven by spatial order or
survivor emergence.

Potential value:

- better memory locality
- smaller live working sets

### 2. Hybrid exact geometry ownership

Some data structures may only be needed transiently for exact geometry, while
others are only needed for final pocket ownership.

A more creative internal split may be:

- one very compact geometry-focused representation for candidate generation
- one later feature-focused representation for survivors only

Potential value:

- exact same final output with much cheaper early-stage state

### 3. Exact witness-based retention

An internal candidate or cluster could be retained not because the whole rich
object is stored, but because a smaller witness proves it must survive into the
next stage.

Potential value:

- reduce the amount of state carried forward

Main caution:

- the witness has to be sufficient to reconstruct the exact same later outcome

### 4. Descriptor work sharing across pocket families

If several late-stage candidate pockets share substantial atom ownership or
lining structure, some descriptor work may be shareable instead of recomputed
from scratch each time.

Potential value:

- this could matter especially in large systems with many nearby candidate
  pockets

### 5. Exact pipeline reordering

The same exact mathematical result may be reachable with a cheaper execution
order.

Examples:

- delay expensive descriptor work until exact structural survival is known;
- move exact rejection criteria earlier if they do not depend on late-stage
  state;
- reorder pocket-finalization steps so that obviously dead structures never
  receive full materialization.

Potential value:

- large reduction in wasted late-stage work

Why this deserves attention:

- it may produce meaningful wins without changing the actual formulas

### 6. Ephemeral local structures

Some expensive intermediate structures may only be needed briefly within a
local computation window.

Possible pattern:

- build a local structure
- consume it fully
- discard it immediately
- keep only the exact survivor representation

Potential value:

- lower peak memory
- less global state pressure
- better locality

### 7. JIT-compiled exact kernels

Without moving to GPU or distribution, some exact inner loops may still be much
too Python-heavy.

Possible future route:

- identify pure numeric kernels in filtering, neighbor checks, local descriptor
  calculations, or candidate bookkeeping;
- compile them with an exact-preserving CPU route such as Numba or a similar
  approach.

Potential value:

- substantial speedups without changing the algorithmic contract

Main caution:

- only useful if profiling shows true Python-loop hotspots rather than SciPy/C
  dominated cost

### 8. Incremental closure of finished pocket regions

Some pocket regions may become exact "closed" survivors before the whole system
has been fully processed through all expensive late stages.

If such closure can be certified, the method may:

- finalize that region,
- remove it from active expensive bookkeeping,
- and continue only with unresolved regions.

Potential value:

- smaller active state over time

Main caution:

- closure must be exact; premature closure would break parity

## Additional risky ideas worth keeping for experiments

The following ideas are risky for parity, but still important enough to keep in
mind as explicit experiment candidates. They should only graduate into
`topomt-scalable` if they later demonstrate exact final parity against
`native`.

### 1. Region budgets with exact fallback

Idea:

- apply temporary candidate budgets or compression in very dense regions, but
  fall back automatically to the full exact path if the region cannot be shown
  safe

Why it might be worth testing:

- some regions may be obviously redundant in practice

Why it is risky:

- the fallback criteria may be hard to define correctly

### 2. Multi-resolution exactness guards

Idea:

- run a cheaper coarse structural pass, but require exact refinement wherever
  the coarse pass cannot certify equivalence

Why it might be worth testing:

- very large systems may contain vast inactive regions

Why it is risky:

- proving the guards are exact may be difficult

### 3. Stable representative selection in near-equivalent alpha families

Idea:

- if a family of alpha-spheres is near-equivalent under a provable rule, keep a
  stable representative and reconstruct the same final result from it

Why it might be worth testing:

- local candidate explosions may sometimes contain structural redundancy

Why it is risky:

- near-equivalence is not enough unless it is shown to preserve the final
  pocket contract exactly

### 4. Exact-by-construction region schedules

Idea:

- process the system in a nontrivial schedule chosen to minimize active state,
  while maintaining exact dependence ordering between regions

Why it might be worth testing:

- clever scheduling alone can sometimes reduce memory and repeated work

Why it is risky:

- exact dependence ordering may be difficult to certify in a complex geometry
  pipeline

## What should be measured

Any future `topomt-scalable` prototype should be evaluated on at least:

- final pocket count
- pocket atom membership
- ranking drift relative to `native`
- runtime
- peak memory use
- candidate counts after each major stage
- object counts or array sizes during the heaviest stages
- sensitivity to large systems such as `2HGR.pdb`

Suggested benchmark set:

- routine controls:
  - `1GG0.pdb`
  - `1N57.pdb`
  - `3LKF.pdb`
  - `E15ALA.pdb`
- large-system deep validation:
  - `2HGR.pdb`

## Non-goals

This document does **not** imply that:

- `native` should change its semantics;
- `topomt` should absorb scalability heuristics;
- or `topomt-scalable` may relax the final parity target already established by
  `native`.

For this document, the working rule is the opposite:

- `topomt-scalable` must aim to preserve the same final parity contract as
  `native`, while changing the internal strategy to improve runtime and memory
  use on large systems.

## Related documents

- [native_checkpoint.md](native_checkpoint.md)
- [parity_matrix.md](parity_matrix.md)
- [../pocket_algorithm_issues.md](../pocket_algorithm_issues.md)
- [../gpu_opportunities.md](../gpu_opportunities.md)
