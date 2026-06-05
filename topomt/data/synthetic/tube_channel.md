# tube_channel

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `tube_channel.pdb`
- **Atoms:** 77 · **Probe:** 1.4 Å
- **Expected by construction:** open tube -> channel (>=2 mouths). Wide/sparsely-walled: the lumen channel (channel, 2 mouths) is the dominant feature, alongside several shallow side-pockets at the wall windows.
- **DFND families (significant):** 1x channel, 2x pocket
<!-- /AUTO -->

- **Generator:** `cylinder_tube(length=20.0, tube_radius=6.0, wall_spacing=3.5, jitter=0.1, seed=0)`

## What to observe

The dominant feature is **one channel** running through the tube, family `channel`
with **`n_mouths = 2`** (WET-1, ~111 nodes). Around it there are **several shallow
side-pockets** (2 significant, up to 5 counting the tiny ones), sitting in the wall
windows.

## Why

A wide tube (radius 6 Å) with a porous wall: 7 rings of 11 atoms, axial spacing
3–4 Å. At that density the windows between wall atoms are comparable to or larger
than the probe, so some solvent settles in them forming shallow pockets in addition
to the lumen. The central lumen, by contrast, does connect both ends → a two-mouth
channel.

It is the same mechanism as `tube_channel_clean` but with a looser wall: here there
is **more lateral noise** (several pockets) because the windows are larger. The
clean version (`tube_channel_clean`) narrows the tube and densifies the wall to
leave only 1 pocket.

## DFND verdict

✅ **Correct.** The two-mouth channel is detected properly; the side-pockets are
real geometry (the probe genuinely fits in the windows of this loose wall), not
artifacts.

> Methodological note: during the initial study of this system it *looked* as if
> DFND "only saw pockets" and not the channel. That was the `_SIDE_BY_FAMILY`
> name-mismatch bug (see [`tube_channel_clean.md`](tube_channel_clean.md)): the
> channel was in the raw output but hidden from `components.wet`. Once fixed, the
> channel shows up as it should. A good reminder to distinguish "DFND gets it
> wrong" from "the typed view was hiding it".
