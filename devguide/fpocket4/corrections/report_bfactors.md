# Report draft: B-factor statistics in fpocket vertex filtering

Suggested upstream title:

Global B-factor statistics in `rpdb.c` are computed over an inconsistent atom
population and affect `testVvertice()`

## Summary

During parity work on the native reimplementation of `fpocket4`, we found that
upstream `fpocket` appears to compute global B-factor statistics in a way that
is internally inconsistent:

- it accumulates B-factors over all atoms,
- but divides the average by the number of non-hydrogen atoms,
- and it initializes `min_bfactor` to `0.0`, which can keep the effective
  minimum fixed at zero when all atom B-factors are positive.

This affects the B-factor-based branch of `testVvertice()` and therefore the
acceptance or rejection of alpha spheres.

## Upstream locations

Relevant files:

- `src/rpdb.c`
- `src/voronoi.c`

Relevant code roles:

- global B-factor statistics are prepared while reading the receptor,
- vertex acceptance uses those statistics in `testVvertice()`.

Relevant snippets:

In `src/rpdb.c`:

```c
pdb->avg_bfactor = 0.0;
pdb->min_bfactor = 0.0;
pdb->max_bfactor = 0.0;
...
pdb->avg_bfactor += atom->bfactor;
...
if(atom->bfactor<pdb->min_bfactor){
    pdb->min_bfactor=atom->bfactor;
}
if(atom->bfactor>pdb->max_bfactor){
    pdb->max_bfactor=atom->bfactor;
}
...
pdb->natoms_h = num_h_atoms;
pdb->avg_bfactor /= (iatoms - num_h_atoms);
```

In `src/voronoi.c`:

```c
if (((sdbf>avg_bfactor) || (sdbf>((pdb->max_bfactor-pdb->min_bfactor)/4))) &&
    ((avg_bfactor > 0.0) && (barybf / avg_bfactor > 1.4)))
    return (-1.0);
```

## Why this matters

These statistics are not purely descriptive; they directly control whether a
candidate alpha sphere survives `testVvertice()`. Therefore, any inconsistency
in the global statistics changes geometry acceptance.

## Observed upstream semantics

### Global statistics

In the audited upstream code path, the effective behavior is:

1. `avg_bfactor` starts at `0.0`
2. `min_bfactor` starts at `0.0`
3. `max_bfactor` starts at `0.0`
4. B-factors from all atoms are accumulated into `avg_bfactor`
5. the final average is divided by the number of heavy atoms

Consequences:

- if all B-factors are positive, `min_bfactor` may remain `0.0`
- the reported average is not the true average over all atoms
- and it is not the true average over heavy atoms either

So the current `avg_bfactor` is effectively:

```text
sum(B over all atoms) / number_of_heavy_atoms
```

which does not correspond to a clearly defined physical population.

### Vertex filtering

`testVvertice()` uses these global statistics together with local per-tetrahedron
B-factor statistics such as:

- `barybf`
- `sdbf`

Therefore the global-statistics inconsistency propagates directly into vertex
acceptance decisions.

## Why this was detected

After fixing the raw-geometry diagnostic issue, the remaining mismatch between
upstream `fpocket` and the native TopoMT implementation was very small:

- `1N57`: accepted-vertex parity exact
- `E15ALA`: accepted-vertex parity exact
- `1GG0`: native missed `9` upstream-accepted alpha spheres
- `3LKF`: native missed `2` upstream-accepted alpha spheres

For `1GG0`, the missing `9` vertices were traced to a single cause:

- all passed equidistance checks,
- all passed barycenter checks,
- all were rejected only by the B-factor branch in the native code.

Recomputing the global B-factor statistics with the exact upstream-like
semantics removed that mismatch.

For `3LKF`, the remaining accepted-vertex mismatch was instead traced to the
radius tolerance branch, not to B-factors. That distinction was important
because it isolated the B-factor issue specifically to the `1GG0` residual case.

## Reproduction strategy

The issue can be reproduced by instrumenting or re-implementing the same
statistics outside `fpocket` and comparing two variants:

1. Upstream-like semantics:
   - initialize `avg = min = max = 0.0`
   - accumulate `avg` over all atoms
   - divide by heavy-atom count
   - update `min` from the initial zero
2. Internally consistent semantics:
   - select one atom population explicitly
   - compute average, min, and max over that same population

Then compare the resulting `testVvertice()` decisions on a system such as
`1GG0`.

Expected diagnostic result:

- with the upstream-like statistics, the 9 disputed vertices survive;
- with the internally consistent statistics, those same vertices are rejected
  by the B-factor branch.

## Observed behavior vs expected behavior

Observed:

- the average is accumulated over all atoms and normalized by heavy atoms only;
- the minimum can remain pinned at `0.0`;
- these values propagate into `testVvertice()` thresholds.

Expected:

- global statistics should be computed over a clearly defined and internally
  consistent atom population,
- and the minimum should be initialized from the first valid B-factor rather
  than from an arbitrary zero.

## Consequences

### Scientific/methodological consequence

The current upstream behavior is difficult to justify as a clean physical
observable because:

- the average is not computed over a consistent population,
- the minimum may be artificially pinned to zero,
- and the resulting thresholds may be looser or stricter for reasons unrelated
  to the actual local flexibility of the receptor.

### Reimplementation consequence

If TopoMT wants strict parity with upstream `fpocket`, the native mode must
reproduce this semantics, even if it is not methodologically ideal.

If TopoMT wants a scientifically cleaner method, that should live in a
different mode, not in the parity-preserving one.

## Recommended interpretation

This looks less like a deliberate modeling choice and more like an
implementation artifact that became part of the effective upstream behavior.

That does **not** mean TopoMT should normalize it silently. Instead:

- `implementation='native'` should reproduce it for parity,
- and a separate TopoMT-specific mode can use a corrected, internally coherent
  B-factor treatment.

## Suggested upstream action

Possible upstream corrections to discuss:

1. Define explicitly which atom population is used for global B-factor
   statistics.
2. Compute the average over that same population.
3. Initialize `min_bfactor` from the first valid value, not from `0.0`.
4. Add regression tests showing how `testVvertice()` should respond to the
   corrected statistics.

## Proposed code change

The likely minimal code correction in `rpdb.c` is:

1. decide the atom population explicitly,
2. initialize `min_bfactor` from the first atom in that population,
3. accumulate only over that same population,
4. divide by the size of that same population.

In pseudocode:

```c
int first = 1;
int count = 0;
pdb->avg_bfactor = 0.0;

for (i = 0; i < iatoms; i++) {
    atom = atoms + i;
    if (/* atom belongs to the chosen population */) {
        if (first) {
            pdb->min_bfactor = atom->bfactor;
            pdb->max_bfactor = atom->bfactor;
            first = 0;
        }
        if (atom->bfactor < pdb->min_bfactor) pdb->min_bfactor = atom->bfactor;
        if (atom->bfactor > pdb->max_bfactor) pdb->max_bfactor = atom->bfactor;
        pdb->avg_bfactor += atom->bfactor;
        count += 1;
    }
}

if (count > 0) pdb->avg_bfactor /= count;
```

If upstream prefers the heavy-atom population, then both numerator and
denominator should consistently use heavy atoms.

## Suggested regression test idea

An upstream regression test could:

1. load a receptor with positive B-factors and at least one hydrogen,
2. verify that `min_bfactor` is not artificially pinned to `0.0`,
3. verify that changing hydrogen count does not distort the average unless
   hydrogens are explicitly part of the selected population.

## Status

This note is a draft for:

- an upstream issue,
- a possible pull request,
- and internal TopoMT design decisions separating upstream fidelity from
  TopoMT-corrected behavior.
