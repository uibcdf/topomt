# two_blocks_interface

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `two_blocks_interface.pdb`
- **Atoms:** 250 · **Probe:** 1.4 Å
- **Expected by construction:** solvent-wide gap -> two dry banks + a wet interface lined by both
- **DFND families (significant):** 3x pocket, 2 dry bodies
<!-- /AUTO -->

- **Generator:** `two_blocks(gap=5.0, seed=0)`

## What to observe

Two blocks separated by a 5 Å gap (a solvent width). You should see, at once, both
**halves** of an interface (DFND's wet/dry symmetry):

- **Dry side — two banks.** Two `DryComponent`s (DRY-1, DRY-2), the probe-excluded
  interior of each block.
- **Wet side — the interface.** The gap component (WET-1, ~275 nodes) is flagged as
  an **interface**: `is_interface = True`,
  `interface_family = 'interface_pocket'`, `lining_bodies = ['DRY-1', 'DRY-2']`
  (lined by both banks). It appears in `components.wet_interfaces`.

Around it, a few small surface pockets (the texture of the blocks' outer faces),
which are not interfaces (single-body lining).

## Why

The interface is an **orthogonal axis** to the mouth-topology family (see
[`devguide/DFND/interfaces.md`](../../../devguide/DFND/interfaces.md) §2): the
family stays `pocket` (it counts mouths to OCEAN), but the interface descriptor
turns on because the lining receives a contribution from **≥2 distinct bodies**.
With a 5 Å gap (≈ probe diameter) a resident wet layer emerges between the blocks,
so the dry side splits into two banks (the native route, no chain labels). With a
gap ≤4 Å the banks would fuse (`two_blocks_fused`) and explicit labels would be
needed.

## DFND verdict

✅ **Correct.** It detects the two coupled halves: two dry banks + the wet gap
catalogued as an `interface_pocket` lined by both. The wet↔dry adjacency layer
(`WET-1.dry_lining` / `DRY-i.wet_lining` / `DRY-i.interface_walls`) closes the
symmetry.

> Honest caveat (not an inconsistency, a scope limit): WET-1 wraps **the whole
> exterior of both blocks in addition to the gap** (in a finite system with no sea
> level it is a hub with ~18 surface rafts hanging off it). The interface is
> *detected* but not *isolated* as its own region with a crisp boundary; the fine
> localization (`topomt/dfnd/experimental.py`) is only partial. See interfaces.md §8.
