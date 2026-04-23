# CASTp Checkpoint 2026-04-05

## Purpose

This checkpoint records the exact conceptual and implementation state of the
native `castp` work before restarting the session.

It is meant to be sufficient to resume the CASTp parity effort without having
to reconstruct the reasoning from the chat history.

## Current goal

The immediate goal is **full parity for voids first**, before continuing with
mouths, channels, and pockets.

The target oracle is:

- `CASTp 3.0` zipped exports under `topomt/data/CASTp_3.0_server/`
- `CASTpFold` outputs only as confirmation that they match `CASTp 3.0` for the
  audited systems

The current audited systems are:

- `1TCD`
- `1HIV`

## Oracle semantics already clarified

The loader side is in a much better state now.

### `CASTp 3.0` and `CASTpFold`

For the audited systems, `CASTpFold` matches `CASTp 3.0` exactly in practice.

This means we can safely use:

- CASTp 3.0 zip fixtures as oracle
- CASTpFold documentation as a source of parameter semantics

### Feature typing in the oracle

`load_CASTp()` was corrected so that `.poc` entries are not all interpreted as
`pocket`.

The correct rule is:

- `0` mouths -> `void`
- `1` mouth -> `pocket`
- `2` mouths -> `channel`
- `>= 3` mouths -> `branched_channel`

This now matches the `.pocInfo` files for `1TCD` and `1HIV`.

## Parameterization currently understood

The only user-facing free parameter exposed by the CASTp servers is:

- `probe radius`

The geometric parameterization also depends on atom radii.

Two radii models were implemented and compared:

- `castp_param`
- `protor`

### Important current conclusion on radii

For the current CASTp 3.0 / CASTpFold oracle, `protor` is the better working
model.

Key observations:

- `castp_param` improved some cases, but stayed clearly worse
- `protor` gave near-parity voids for `1TCD`
- `protor` gave exact void parity for `1HIV` before the latest refactor

This does **not** yet prove that `protor` is the final canonical default, but
it is currently the strongest candidate for reproducing the current oracle.

## Most important conceptual correction

The biggest conceptual mistake discovered in the previous implementation phase
was this:

- we were treating `voids` and `pockets` as if both should be built from the
  same `discrete flow` pipeline

That is **not** faithful to the original CAST code.

### What the original code actually does

From `../Alphashape/castp/alpha-4.1-src/mkalf/voids.c`:

- `voids` are built by `alf_find_voids(input_rank)`
- `pockets` are built by `alf_init_pockets(rank1, rank2, do_wrap)`

These are different constructions.

### Correct interpretation

#### Voids

`voids` are built as **connected components of the complement**.

Operationally, `alf_find_voids(input_rank)`:

- scans the master list from `max_rank` down to `input_rank + 1`
- adds tetrahedra
- unions tetrahedra across complement triangles
- unions hull-adjacent tetrahedra with the outside component `0`

There is:

- no `depth`
- no sink logic
- no `hidden_triangle`

in the actual construction of voids.

#### Pockets

`pockets` do use:

- `discrete flow`
- `depth`
- sinks
- `rank1`
- `rank2`
- delayed stacks

This logic is implemented in `alf_compute_pocket_depths()` and
`alf_init_pockets()`.

### Consequence

For faithful CAST reproduction:

- `voids` must be computed by complement connectivity
- `pockets/channels` must be computed by the `discrete flow` machinery

This separation is coherent with the 1998 papers:

- the formal paper defines voids as bounded complement components
- the pocket construction is introduced later via the acyclic flow relation

## What was wrong with our previous `open_mask` reasoning

We had started using `open_mask` as if it were equivalent to:

- all empty tetrahedra relevant to the final void/pocket structure

That was too strong and conceptually unsafe.

The discussion around `Pocket 69` in `1TCD` exposed this confusion.

### `Pocket 69` residual

Oracle `Pocket 69` atoms:

- `488, 695, 696, 790, 851`

Best native match at the time:

- `488, 695, 696, 790`

Missing atom:

- `851`

The matching native void was mono-tetrahedral:

- tetrahedron `3813`
- atoms `[488, 695, 696, 790]`

Two neighboring tetrahedra containing `851` were identified:

- `7169 = [488, 695, 790, 851]`
- `7174 = [695, 696, 790, 851]`

And we established:

- both have `depth = 3813`
- both had `open = False`
- both had `retained = False`

This initially suggested that our `open_mask` might be excluding tetrahedra
that should belong to the void.

### Refined conclusion after reviewing original code

That conclusion was too quick.

From the original code, `depth -> sink` is **not** sufficient by itself for
void membership.

For voids, the original route is `alf_find_voids()`, not the pocket depth
route.

So the correct lesson from `Pocket 69` is:

- the current implementation still has a mismatch in how the complement
  tetrahedra are represented or retained
- but the argument cannot be “it flows to the sink, therefore it must be in the
  void”, because that belongs to the pocket logic, not the void logic

## Current code state

### Checkpoint commit

There is a git checkpoint commit already created before the latest refactor:

- `363b119 feat(castp): checkpoint native workflow and oracle fixtures`

This was made so the work could be restarted from a known point.

### New refactor already applied after that checkpoint

After the conceptual correction above, the code was changed again in:

- `topomt/third_party/castp/core/castp_core/components.py`

The current local state now separates:

- `void` construction through `_build_void_components()`
- `pocket/channel` construction through `_build_rank_driven_components()`

Specifically:

- `_build_void_components()` was added to mimic `alf_find_voids()`
- `build_castp_feature_records()` now:
  - builds `void` records from complement components
  - builds `pocket/channel` records from the rank-driven depth route
  - skips `n_mouths == 0` features in the pocket route, because those are no
    longer the source of `voids`

### Tests updated

`tests/test_castp_core.py` was adjusted so the old test that asserted the
rank-driven path returned a `void` no longer assumes that.

The focused test battery passed again after the refactor:

- `python -m pytest -q tests/test_castp_core.py tests/test_castp.py`

This was observed in the interactive session before the environment issue
blocked the next oracle comparison.

## What is still unresolved

The key unresolved question is:

- does the new `void` path now reproduce `1TCD` and `1HIV` oracle voids
  exactly?

This was the next measurement to run, but it was interrupted by environment
and runner issues before we could record the result cleanly.

## Environment and runner problems encountered

Two infrastructure problems were active during the last session.

### 1. Broken sandbox

Commands often failed inside the sandbox with:

- `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`

Because of this, many code-reading commands had to be rerun outside the
sandbox.

### 2. Session bookkeeping issue

The runner repeatedly reported:

- `The maximum number of unified exec processes you can keep open is 60`

even when `ps` did not show corresponding orphaned Python or Bash processes.

This appears to be runner/session bookkeeping, not an actual process leak that
could be fixed from inside the repo.

### 3. Python environment mismatch

A persistent shell was finally opened successfully outside the sandbox.

However, two candidate conda environments were tested and both failed to import
`pyunitwizard`:

- `topomt@uibcdf_3.12`
- `molsyssuite@uibcdf_3.13`

So the last session ended with a stable shell but an unresolved environment
selection problem.

## Next step to take in the next session

The immediate next step is **not** more conceptual reading.

The conceptual blocker has already been resolved:

- `voids` and `pockets` must follow different algorithms

The immediate next work item is:

1. activate the correct Python environment that can import:
   - `topomt`
   - `pyunitwizard`
   - `molsysmt`
2. run a short parity check for `voids` only on:
   - `1HIV`
   - `1TCD`
3. determine whether the new `_build_void_components()` route gives:
   - exact parity
   - near parity
   - or a new residual mismatch

Only after that:

4. inspect any remaining void residuals against the original
   `alf_find_voids()` semantics
5. once voids are fully closed, return to pockets/channels through
   `depth`/`mouths`

## Minimal commands to resume

After activating the correct environment, the first useful commands should be
small and targeted.

### 1. Focused tests

```bash
python -m pytest -q tests/test_castp_core.py tests/test_castp.py
```

### 2. Void parity probe

```bash
python -c "
from topomt.third_party.castp._native_impl import castp
from topomt.io.load_CASTp import load_CASTp

for name, pdb_path, zip_path in [
    ('1TCD', 'topomt/data/TcTIM/CASTp_1tcd/1tcd.pdb', 'topomt/data/CASTp_3.0_server/1tcd.zip'),
    ('1HIV', 'topomt/data/HIV-1-Protease/CASTp_1hiv/1hiv.pdb', 'topomt/data/CASTp_3.0_server/1hiv.zip'),
]:
    native, _ = castp(pdb_path)
    oracle = load_CASTp(zip_file=zip_path)
    native_voids = sorted(tuple(sorted(f['atom_indices'])) for f in native if f['feature_type'] == 'void')
    oracle_voids = sorted(tuple(sorted(f.atom_indices)) for f in oracle.features.values() if f.feature_type == 'void')
    exact = sum(1 for atoms in oracle_voids if atoms in set(native_voids))
    print(name, 'native_voids', len(native_voids), 'oracle_voids', len(oracle_voids), 'exact', exact)
"
```

## Files most relevant to resume

- `topomt/third_party/castp/core/castp_core/components.py`
- `topomt/third_party/castp/core/castp_core/geometry.py`
- `tests/test_castp_core.py`
- `tests/test_castp.py`
- `devguide/castp/contract.md`
- `../Alphashape/castp/alpha-4.1-src/mkalf/voids.c`
- `../Alphashape/castp/alpha-4.1-src/mkalf/lookup.c`
- `../Alphashape/castp/alpha-4.1-src/mkalf/spectrum.c`

## Files modified in this phase

The following project files were modified during the last implementation step
and should be reviewed first when resuming:

- `topomt/third_party/castp/core/castp_core/components.py`
- `tests/test_castp_core.py`
- `devguide/CASTp/implementation.md`
- `devguide/castp/checkpoint_2026_04_05.md`

## Hypotheses now discarded

The following interpretations were explicitly tested or reviewed and should not
be reintroduced without new evidence:

- `voids` should be built by `discrete flow`
- `depth -> sink` is sufficient for void membership
- our previous `open_mask` can be treated as identical to the final set of
  empty tetrahedra relevant to all CAST feature construction
- the remaining `void` residuals should be solved first by touching mouths or
  channel logic

## What not to do first in the next session

To keep the restart disciplined:

- do **not** start with mouths
- do **not** start with channels
- do **not** try to patch lining atoms by hand
- do **not** tune thresholds ad hoc

The first task after environment recovery must remain:

- measure `void` parity on `1TCD` and `1HIV` with the now-separated
  complement-components implementation

## Final note

The main conceptual uncertainty is no longer:

- “what does CAST do for voids?”

That part is now clear enough:

- `voids` are complement components
- `pockets` come from discrete flow

The next session should therefore be implementation-focused and measurement-led.
