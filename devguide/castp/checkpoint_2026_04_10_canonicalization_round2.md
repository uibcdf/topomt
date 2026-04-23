# CASTp Checkpoint 2026-04-10 Canonicalization Round 2

## Purpose

This checkpoint records the second canonicalization pass performed after the
2026-04-10 audit documents were written.

The goal of this pass was not to optimize parity incrementally after each local
change. The goal was to eliminate a set of clearly non-canonical shortcuts and
then evaluate the resulting package as a whole.

## Canonical corrections applied

### 1. Mouth walks now start from outward-oriented simplex faces

The weighted mesh already preserved oriented tetrahedra. This pass made that
orientation usable by the CASTp mouth logic by adding explicit access to
outward-oriented face atom order.

This matters because MKALF mouth connectivity is defined over oriented
edge-facets, not over sorted atom triples.

Files:

- [topomt/weighted_delaunay_mesh.py](/home/diego/repos@uibcdf/topomt/topomt/weighted_delaunay_mesh.py)
- [topomt/third_party/castp/core/castp_core/mouths.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/mouths.py)

### 2. Mouth faces now carry both simplex index and face index

The native pocket boundary code now passes the owning simplex and owning face
index for each mouth triangle. This gives the mouth walk enough local context
to start from the correct oriented face rather than reconstructing orientation
from sorted face atoms.

Files:

- [topomt/third_party/castp/core/castp_core/components.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/components.py)
- [topomt/third_party/castp/core/castp_core/mouths.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/mouths.py)

### 3. Edge `mu1` / `mu2` ranks were added and are now used in mouth-edge openness

This was the most important correction in this round.

Before this pass, the native mouth logic treated edge openness as if edge
membership in the alpha complex depended only on `rho`.

That is not canonical.

In MKALF, attached edges (`rho = 0`) are still governed by `mu1`. Therefore an
attached edge is not automatically in the complex.

This pass reconstructs edge `mu1` and `mu2` ranks from the face rank tables
following the historical `spectrum.c` rules, and uses:

- `rho <= rank1` when `rho != 0`
- `mu1 <= rank1` when `rho == 0`

to decide whether an edge is in the complex during mouth walks.

Files:

- [topomt/third_party/castp/core/castp_core/geometry.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/geometry.py)
- [topomt/third_party/castp/core/castp_core/mouths.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/mouths.py)

### 4. `rank1 = base_rank` remains the canonical working choice for pocket assembly

This pass did not reintroduce `probe_rank` into component assembly. The code and
docstrings were kept aligned with the audited MKALF reading already established
earlier in the project notes.

## Immediate effect on the short diagnostic battery

The integrated 5-case battery after this canonicalization pass is:

- `1stp`
- `1rop`
- `1ubq`
- `2lyz`
- `2pk4`

### Exact green cases

The following cases reached exact feature parity by `feature_type` and
`atom_indices`:

- `1stp`
- `1rop`
- `2lyz`
- `2pk4`

This means exact parity for:

- `pocket`
- `channel`
- `branched_channel`
- `void`

on those systems.

### Residual case

`1ubq` is the only remaining residual in this short battery.

Observed status:

- oracle: `9 pocket`, `0 channel`, `0 branched_channel`, `3 void`
- native: `10 pocket`, `0 channel`, `0 branched_channel`, `3 void`
- exact: `8 pocket`, `0 channel`, `0 branched_channel`, `3 void`

Residual structure:

1. one oracle pocket is recovered almost exactly but misses a single lining atom
2. one extra very small native pocket of 4 atoms remains

This no longer looks like the earlier mouth-partition failure pattern.

It now looks more like one of:

- a residual atom-materialization difference
- a residual tiny-pocket reporting difference
- or a CASTp-3.0-specific post-filtering/reporting rule

## Immediate effect on medium diagnostic cases

The same canonicalization pass was probed on:

- `2cba`
- `3ks3`
- `1ake`

Results:

### `2cba`

- oracle: `17 pocket`, `3 channel`, `0 branched_channel`, `11 void`
- native: `18 pocket`, `2 channel`, `0 branched_channel`, `11 void`
- exact: `15 pocket`, `2 channel`, `0 branched_channel`, `11 void`

### `3ks3`

- oracle: `14 pocket`, `4 channel`, `0 branched_channel`, `10 void`
- native: `16 pocket`, `4 channel`, `0 branched_channel`, `10 void`
- exact: `12 pocket`, `3 channel`, `0 branched_channel`, `10 void`

### `1ake`

- oracle: `21 pocket`, `5 channel`, `2 branched_channel`, `19 void`
- native: `20 pocket`, `5 channel`, `2 branched_channel`, `19 void`
- exact: `19 pocket`, `5 channel`, `1 branched_channel`, `19 void`

Interpretation:

- the old systematic overproduction of `channel` and `branched_channel` has
  been dramatically reduced
- `void` parity remains strong
- the remaining medium-case residuals now look much smaller and much more local
  than the earlier pre-canonicalization failures

## Testing status

The focused native CASTp suite still passes:

- `tests/test_castp_core.py`
- `tests/test_castp.py`

Additional short-battery regression coverage was added for exact green-case
parity on:

- `1stp`
- `1rop`
- `2lyz`
- `2pk4`

## Current interpretation

This pass appears to have closed the main canonical mouth-partition gap that was
dominating the earlier battery.

The project is now in a better state:

- mouth logic is closer to the historical algorithm
- short-case parity is mostly closed
- medium-case residuals are smaller and less taxonomically pathological

The next step should focus on the remaining fine-grained residuals, starting
with `1ubq`, rather than reopening the broad mouth-partition diagnosis that
motivated this pass.

## What is still not proven faithful

This pass closed the largest known canonical gap, but it did not prove that the
native method is already fully faithful to CASTp.

The following points remain explicitly open and should orient the next
iteration.

### 1. Edge `mu1` / `mu2` are reconstructed, not literally ported

The new edge-rank behavior is now much closer to the historical algorithm and
clearly improves parity.

However, the current implementation still reconstructs edge `mu1` / `mu2` from
the native face-rank tables. It is not a literal port of the original
combinatorial pipeline.

So this part should be treated as:

- strongly improved
- probably directionally correct
- but not yet formally closed as a fidelity question

### 2. The `Fnext` walk is still an approximation of the historical data structure

The native method now uses oriented simplex faces and local face ownership,
which is a substantial improvement.

But the Python implementation still does not expose exactly the same
edge-facet-level combinatorial representation as MKALF.

This means:

- the current walk is much more canonical than before
- but it still cannot be claimed to be a literal port

### 3. Mouth-seed selection looks much better, but is not yet formally proven identical to `alf_scan_pocket_f1()`

The current results suggest that the selection of mouth triangles is now close
enough to recover the short green battery exactly.

Still, we have not yet completed a case-by-case audit demonstrating that the
native seed set is identical to the historical `alf_scan_pocket_f1()` output on
all relevant cases.

### 4. Feature atom materialization has not been audited as deeply as mouth topology

The remaining `1ubq` residual suggests that the next important diagnostic layer
may no longer be mouth topology itself.

It may instead involve:

- feature atom materialization
- boundary atom reporting
- tiny-pocket reporting
- or a CASTp-3.0-specific post-filtering convention

So the next iteration should explicitly inspect how `atom_indices` are produced,
not only how pockets are topologically assembled.

### 5. The boundary between "our residual bug" and "CASTp-3.0 evolution beyond MKALF 4.1" is still open

The new results put the project in a much better position:

- the dominant non-canonical mouth bias has been reduced sharply
- medium-case parity is now much closer

But that does not yet settle whether the last residual differences are:

- remaining implementation defects in TopoMT
- or genuine differences between CASTp 3.0 and the historical MKALF 4.1 logic

This distinction remains one of the main goals of the next phase.

## Recommended orientation for the next iteration

The next iteration should not reopen broad architectural changes.

It should proceed in this order:

1. inspect `1ubq` in detail as the leading fine-grained residual
2. audit feature-atom materialization and tiny-pocket reporting
3. use `2cba`, `3ks3`, and `1ake` as medium validation cases
4. only revisit deeper combinatorial changes if those residuals still demand it
