# Reference-validator P1: exact box controls and the remaining construction

Owner [#76](https://github.com/uibcdf/topomt/issues/76); first native consumer
#181. This is a bounded feasibility result under the
[implementation plan](physical_reference_validator_implementation.md), not the
selection or qualification of a general multi-ball topology engine. Its new
fixtures are validator controls, not additional BenchLab geometry families.

## Question and achieved scope

Can a standalone checker prove a nontrivial exhaustive component inventory,
including small regions and strict-contact separation, without a voxel
resolution cutoff or the native detector's labels?

For **exactly one expanded atomic ball in a full-dimensional axis-aligned box**,
the answer is yes. The implemented construction accepts arbitrary rational
centers, including centers on or outside the box, nonnegative atomic/probe
radii, and strict obstacle contact. It produces recoverable regions, their
representatives and complete inter-piece incidence evidence. Its at most eight
pieces are curved free subsets of sectors, not wholly free grid cells.

Multiple atoms and tetrahedral/general hulls are rejected by this route. The
existing partition route remains available at its separate, sufficient scope.
No per-region volume, boundary-patch inventory, enclosure/exterior label or
requested numerical precision follows from the new component result.

## Completeness argument checked by this construction

Let `B = product([lo_i, hi_i])`, ball center `c`, expanded radius `R`, and
`F = {x in B : sum((x_i-c_i)^2) > R^2}`. All comparisons use exact rational
arithmetic on the admitted numerical model.

1. **Cover the actual domain.** Split each box coordinate interval at `c_i`
   when it is strictly interior. Otherwise keep the single interval on its
   applicable side. Their Cartesian products form at most eight closed sectors
   `C_s`, with pairwise shared seams and union exactly `B`. Zero-width sectors
   at an outer face are omitted; the face remains in its full-dimensional
   neighboring sector. The checker reconstructs this cover from the model.
2. **Describe every local free piece.** In each sector choose the box corner
   `v_s` farthest from `c` coordinate by coordinate. Moving on the segment from
   any point of `C_s` to `v_s` never decreases any absolute coordinate distance
   from `c`. Squared distance therefore cannot decrease. Consequently
   `F_s = C_s intersect F` is empty exactly when `v_s` is blocked; otherwise it
   is star-shaped at `v_s` and hence path-connected. A nonempty piece is still
   defined by the strict sphere inequality; it does not fill its sector.
3. **Check every pair intersection.** `C_s intersect C_t` is a possibly lower
   dimensional rectangular product. Its maximum squared distance from `c` is
   attained at its coordinatewise farthest corner. The strict sign there is
   equivalent to `F_s intersect F_t` being nonempty. Every pair is present in
   the certificate, including blocked pairs and edge/point intersections;
   the checker recomputes each maximum. For a nonempty intersection it also
   verifies the entire two-segment path from both sector roots to the witness.
4. **Prove global completeness, not just positive connectivity.** Each `F_s`
   is relatively closed in `F`, since `C_s` is closed. The cover is finite.
   A connected intersection-graph cluster gives a path-connected union via
   its witnesses. Unions belonging to distinct graph clusters are disjoint
   and relatively closed; each also has a relatively closed complement, the
   finite union of the other clusters. They separate `F`. Thus graph clusters
   are exactly its connected/path-connected regions. No extra region can be
   hidden in an unlisted sector or seam.

The finite relatively closed cover is essential to the separation argument;
positive paths or an arbitrary collection of samples would not prove it.
There is no nerve/homotopy theorem or all-Betti-number claim here. This
elementary proof, rational arithmetic, model parsing and exact segment
predicates are the declared trusted base, not a machine-checked theorem about
the Python runtime. The checker does not import the producer or DFND.

## Certificate and reader meaning

`single_ball_box_topology` is an additive certificate kind in the developer
certificate schema. `pieces` records sector bounds, farthest roots and
`free_set_state = nonempty | empty`. `joins` records every pair's farthest
witness and free-set state. `components` proposes a partition of precisely
the nonempty piece IDs. The checker validates all of these, independently
assembles equivalence classes and rejects false merges or separations.

The accepted receipt sets `topology_complete = true` with scope
`single-ball-axis-box/1`. Each returned region lists its piece IDs and a free
representative. Together with the retained sector supports and original model,
this recovers the entire physical subset, not only its count. Piece IDs and
region IDs belong to that model/certificate; ordinal IDs are not asserted to
survive transformed models or changed probes. A shared sector boundary does
not merge regions unless its strict free intersection is proved nonempty.

Volume and boundary incidence explicitly remain `not_computed`. Do not add
sector box volumes to obtain free-region volumes: the sphere cuts them.
Changes to checker code change the pinned executable run identity. Original
partition certificates remain mathematically replayable, while old executable
checkpoints cannot silently resume under a different kernel.

## Frozen analytic controls

The [protocol](../evidence/reference_validator_box_topology_v1/protocol.json)
was written before the first prototype execution. Its expected counts are
independent analytic checks; they are not inputs to the topology algorithm or
its checker. The capture saves and rereads every model and certificate.

| Control | Independently justified result |
| --- | --- |
| Empty box | One region; the existing partition checker also proves exact box volume. |
| One ball covering the box | Zero regions by full coverage. |
| Unit ball inside `[-2,2]^3` | One region, by outward motion to the free connected box boundary. |
| Radius `3/2` or `173205/100000` in `[-1,1]^3` | Eight regions: coordinate planes are covered, each orthant has a free corner and an outward path to it. |
| Radius 4, probes `1-2^-80`, `1`, `1+2^-80`, box `[-10,10] x [-3,3] x [-4,4]` | Respectively one, two and two regions. Below total radius 5 the corner line joins the ends; at/above 5 the entire middle section is blocked, and each half joins its free end section. |
| Ball strictly outside box | One region; the box is wholly free. |
| Center on a box face | One region for the frozen radius, by outward motion to its wholly free opposite face. |
| Zero-radius obstacle | One region, even though the obstacle point remains excluded. |
| Center at a corner, farthest distance exactly 7 | Radius 7 covers the box; radius `7-2^-80` retains one nonempty region, without a size threshold. |

The `2^-80` differences and translated/scaled tests never pass through float.
They demonstrate exact decisions for these particular rational models, not
accuracy of the source's physical atomic radii or uncertain experimental data.

## General candidate review and disposition

The planning leads were reread on 2026-11-13. This is documentary review of
the linked manuals, not an installed/source-build qualification or a claim
that an undocumented capability is absent.

- [SBL's boundary manual](https://sbl.inria.fr/doc/Union_of_balls_boundary_3-user-manual.html)
  describes exact combinatorial ball-union boundaries, algebraic/interval
  vertex construction, and exterior/cavity boundary components. That is useful
  global geometry evidence, but does not by itself qualify our finite-domain
  clipping and clipped-free-region certificates.
- [SBL's volume manual](https://sbl.inria.fr/doc/Union_of_balls_surface_volume_3-user-manual.html)
  describes bounded integration from boundary restrictions, including interval
  transcendental calculations. A concrete arithmetic/build configuration and
  attainable target precision still need receiving evidence; a method label
  or a pair of doubles alone does not pass our requested-precision gate.
- [CGAL's spherical-kernel manual](https://doc.cgal.org/latest/Circular_kernel_3/index.html)
  supplies algebraic sphere/circle primitives. A primitive kernel does not
  automatically provide our exhaustive clipped free regions and attachments.

The new native analytic control demonstrates a small local-decomposition proof
contract, with actual nontrivial counts and contact handling. Its outward
monotonicity depends on having **one** obstacle; adding other atoms can destroy
it. It therefore cannot select local arrangements as the complete multi-ball
architecture, reject the global candidate, or replace the outstanding clipping
construction. No external geometric kernel was compiled or executed.

**P1 remains partial.** The next owning work under #76 is the explicit
multi-ball construction/coverage and clipping feasibility decision, plus the
validated curved-integration precision prototype. Qualify actual source,
license, arithmetic and checker obligations before selecting an external
backend. Broader P2/P3/P4 admission remains subsequent work; #181 and all
native comparative-finding dispositions are unchanged.

This developer route retains TopoMT source/model/checker provenance. It imports
no optional scientific provider, claims no execution of SBL/CGAL/DFND and adds
no public Ackredit boundary; production attribution/API admission remains P6.
