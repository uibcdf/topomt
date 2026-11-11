# Local residence and gate capacities

DFND attaches a capacity to a cell and another to each face. Think of them as
the best local accommodation available on two different supports. The support
constrains the **probe center**, not the whole probe ball.

## Intended operators

For a closed tetrahedron $T$ with vertex atom set $I_T$, and a closed triangular
face $f$ with its three atom indices $I_f$, the intended clearance maxima are

$$R_T^*=\max_{x\in T}c_{I_T}(x),\qquad
R_f^*=\max_{x\in f}c_{I_f}(x).$$

They motivate `R_residence` and `R_gate`. The implementation searches admissible
active-set candidates and returns a nonnegative capacity, initialized to zero
when no positive candidate wins. A zero capacity does not encode a negative
signed maximum or prove a global free-space topology.

Requiring the center to lie in the closed support permits an optimum on a face
or edge. Requiring the entire probe sphere to lie within the artificial
tetrahedron would define a different operator.

## How candidates are calculated

The residence solver generates four-atom interior tangency candidates,
three-atom tangencies constrained to face planes, and two-atom tangencies
constrained to edge lines. The gate solver works in the face plane, generating
three-atom and edge-constrained two-atom candidates. Both retain admissible
centers and recompute their actual minimum clearance to the relevant atom list.

A large algebraic tangency root is insufficient: its center may lie outside
the support or another atom in the local list may limit it. `R_apollonius4`
is a diagnostic about four-atom tangency; it is not the residence definition.
See [the derivation](appendices/clearance_derivations.md) for the equations and
numerical qualifications. Candidate enumeration and scalar/batch agreement do
not by themselves supply a formal completeness proof for every degenerate input.

## From capacities to states

With numerical epsilon $\varepsilon$ and selected tolerances $\tau_r,\tau_g$,
the capacity tests are

$$\text{resident}(T)\iff R_T\ge p-\varepsilon-\tau_r,$$
$$\text{capacity-pass}(f)\iff R_f\ge p-\varepsilon-\tau_g.$$

Under `flag_only`, a capacity-passing face is admitted. Under `block_suspect`,
admission additionally requires no intrusion-suspect flag. Counts and local
classes below use that **post-policy** admission decision. A face may pass its
capacity threshold and still be blocked.

A margin is the capacity minus $p$. Decisions close to the corresponding band
are marked marginal: $|R_T-p|\le\varepsilon+\tau_r$ for residence and
$|R_f-p|\le\varepsilon+\tau_g$ for gate capacity. These flags retain the numerical
proximity even when intrusion policy blocks a face. Epsilon widens admission
below the nominal threshold; a larger tolerance widens the band further. That
policy is inspectable and affects the discrete result.
It is not a measured probability of passage or molecular flexibility.

| Local permeability class | Admitted faces of a tetrahedron |
| --- | --- |
| `open` | All four |
| `coast` | At least one, fewer than four |
| `sealed` | None |

Residence is independent of this local label. A cell can be resident and sealed
at the selected probe, as the tetrahedron demonstrates at 1.4 Å. Nonresident
states can still have locally admitted faces because the face/cell obstacle
lists differ and because numerical policies must be considered.

## Local success and physical meaning

For a fixed support, using fewer obstacle atoms can only increase the exact
maximum clearance. A successful three-atom gate calculation is therefore a
candidate for an all-atom crossing, not its certificate. Even two genuine free
face positions do not prove that a free path joins them inside the cell.

The intrusion diagnostic adds a separate decision about the cell's opposite
atom, explained below. Its absence is not collision certification.

The [straight-tube study](../benchlab/synthetic/straight_tube_narrow_dense/index.md) makes
this distinction concrete. At its initial source `b07a20e`, a 2.5 Å probe has
local wet components and public candidates although an independent all-atom
bound covers the entire finite hull. Diagnosis and public qualification remain
under [#181](https://github.com/uibcdf/topomt/issues/181); this observation alone
does not identify a capacity-solver error. Do not interpret those candidates
as certified physical free regions.

For an exact all-atom-valid path, any point of the path inside a closed cell
implies that cell's exact local residence maximum is at least $p$. This
{ref}`conditional implication <residence-and-paths>`
is important when interpreting nonresident connectors. The code's connector
rule remains a discrete construction whose physical reconciliation is open.

## The apex intrusion policy

For each incidence `(T, f)`, let $a$ be the vertex of $T$ opposite face $f$,
and $h$ its absolute distance to the face's supporting plane. The current
heuristic marks `intrusion_suspect` when $h\le r_a+\varepsilon$; a face normal
with norm at most epsilon is also marked suspect. This uses the **bare apex
radius**, not $r_a+p$. It does not check where the projected disk falls on the
triangle or search every nonlocal atom.

Under `flag_only`, the flag is retained without blocking. Under `block_suspect`,
that owner's incidence is blocked. The two cells sharing an internal face have
different opposite apices, so they can disagree after this policy even though
their `R_gate` is bit-identical. An internal transit edge needs both admissions.
See the [executed shell inspection](network_and_decomposition.md#advanced-inspection-one-face-two-owner-states).

This heuristic may add blocking beyond the local capacity test and omits
probe-expanded obstacles that do not intersect the plane at their bare radius.
It is a declared graph policy with limited scope, not a complete path test.

## Worked scale

For the equal-radius regular tetrahedron of edge 5.3 Å and atom radius 1.7 Å,

$$R_T=\frac{\sqrt6}{4}(5.3)-1.7=1.545573909\ \text{Å},$$
$$R_f=\frac{5.3}{\sqrt3}-1.7=1.359956427\ \text{Å}.$$

Thus the 1.4 Å probe is resident while every face is closed. These values have
an independent geometric derivation and are compared with the implementation in
the [worked example](worked_tetrahedron.md).
