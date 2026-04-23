# CASTp Native Parity Matrix 2026-04-10

## Purpose

This document compares the current native CASTp implementation against the
bundled CASTp 3.0 server oracle on the local fixture battery.

The goal is not yet to explain every individual mismatch. The goal here is to
measure them systematically and identify repeated failure patterns that can
guide the next algorithmic step.

## Comparison basis

- Oracle source: `topomt/data/CASTp_3.0_server/*.zip`
- Native path: `topomt.third_party.castp._native_impl.castp()`
- Features compared here:
  - `pocket`
  - `channel`
  - `branched_channel`
  - `void`
- `mouth` rows from the imported oracle are excluded from the main feature
  counts because the native path does not currently materialize mouths as
  top-level features in the same way.
- Exact parity means:
  - same `feature_type`
  - same `atom_indices` set

Important context:

- CASTp 3.0 and CASTpFold were previously compared on the same ZIP battery.
  Their `*.pocInfo` and `*.mouthInfo` tables were identical for every valid
  common system, so using either server as the oracle would make no practical
  difference here.

## Aggregate picture

Successful native-vs-oracle runs in this matrix:

- `21` systems completed
- `1` system failed before comparison: `1crn`

Aggregate exact matches on the completed set:

- `void`: `295 / 306`
- open features (`pocket + channel + branched_channel`): `124 / 405`

This is the main repeated pattern:

- `voids` are often exact or near-exact
- open features are consistently under-recovered as `pocket`
- and consistently overcalled as `channel` / `branched_channel`

Systems with exact `void` recovery but still poor open-feature parity:

- `1ake` (`11/28` open exact)
- `1hiv` (`4/14`)
- `1hsg` (`5/14`)
- `1lyz` (`1/5`)
- `1mbn` (`2/13`)
- `1pht` (`4/12`)
- `1rop` (`0/3`)
- `1stp` (`2/6`)
- `1tre` (`8/25`)
- `1ubq` (`5/9`)
- `2cba` (`8/20`)
- `2lyz` (`2/6`)
- `2pk4` (`1/3`)
- `3ks3` (`6/18`)
- `3ptb` (`2/13`)

This strongly suggests the dominant current failure is not the global weighted
geometry or the void construction. The dominant current failure is the handling
of open features:

- mouth partitioning
- channel / branched-channel taxonomic splitting
- and downstream conversion of what the oracle calls `pocket` into native
  `channel` or `branched_channel`

## Matrix

Legend:

- Oracle / Native / Exact are shown as `P/C/BC/V`
- `P` = `pocket`
- `C` = `channel`
- `BC` = `branched_channel`
- `V` = `void`

| PDB | Status | Oracle | Native | Exact | Notes |
|---|---|---:|---:|---:|---|
| 1a4j | ok | P55/C3/BC4/V39 | P21/C21/BC20/V39 | P21/C0/BC3/V38 | overcalls branched_channel; overcalls channel; undercalls pocket; exact 62/101 |
| 1ake | ok | P21/C5/BC2/V19 | P7/C11/BC9/V19 | P7/C3/BC1/V19 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 30/47 |
| 1crn | error | - | - | - | ValueError: Not enough atoms to build a CASTp weighted triangulation (min 4). |
| 1ea5 | ok | P32/C5/BC0/V42 | P14/C14/BC11/V41 | P11/C2/BC0/V40 | overcalls branched_channel; overcalls channel; undercalls pocket; exact 53/79 |
| 1f4v | ok | P27/C1/BC1/V23 | P6/C8/BC13/V18 | P5/C0/BC1/V18 | overcalls branched_channel; overcalls channel; undercalls pocket; exact 24/52 |
| 1hiv | ok | P13/C1/BC0/V3 | P4/C1/BC8/V3 | P4/C0/BC0/V3 | voids exact; overcalls branched_channel; undercalls pocket; exact 7/17 |
| 1hsg | ok | P12/C2/BC0/V4 | P4/C4/BC6/V4 | P4/C1/BC0/V4 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 9/18 |
| 1lyz | ok | P5/C0/BC0/V8 | P1/C1/BC2/V8 | P1/C0/BC0/V8 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 9/13 |
| 1mbn | ok | P13/C0/BC0/V10 | P2/C7/BC4/V10 | P2/C0/BC0/V10 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 12/23 |
| 1pht | ok | P12/C0/BC0/V1 | P4/C4/BC4/V1 | P4/C0/BC0/V1 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 5/13 |
| 1rop | ok | P3/C0/BC0/V0 | P0/C3/BC0/V0 | P0/C0/BC0/V0 | voids exact; overcalls channel; undercalls pocket; exact 0/3 |
| 1stp | ok | P5/C1/BC0/V3 | P2/C1/BC3/V3 | P2/C0/BC0/V3 | voids exact; overcalls branched_channel; undercalls pocket; exact 5/9 |
| 1tcd | ok | P34/C6/BC2/V36 | P7/C18/BC17/V36 | P6/C1/BC2/V35 | overcalls branched_channel; overcalls channel; undercalls pocket; exact 44/78 |
| 1tre | ok | P21/C4/BC0/V29 | P8/C7/BC10/V29 | P8/C0/BC0/V29 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 37/54 |
| 1ubq | ok | P9/C0/BC0/V3 | P6/C4/BC0/V3 | P5/C0/BC0/V3 | voids exact; overcalls channel; undercalls pocket; exact 8/12 |
| 2cba | ok | P17/C3/BC0/V11 | P6/C9/BC5/V11 | P6/C2/BC0/V11 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 19/31 |
| 2lyz | ok | P6/C0/BC0/V6 | P2/C1/BC3/V6 | P2/C0/BC0/V6 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 8/12 |
| 2pk4 | ok | P3/C0/BC0/V4 | P1/C0/BC2/V4 | P1/C0/BC0/V4 | voids exact; overcalls branched_channel; undercalls pocket; exact 5/7 |
| 2ptc | ok | P18/C0/BC0/V13 | P6/C7/BC5/V13 | P6/C0/BC0/V12 | overcalls branched_channel; overcalls channel; undercalls pocket; exact 18/31 |
| 3ks3 | ok | P14/C4/BC0/V10 | P5/C6/BC9/V10 | P4/C2/BC0/V10 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 16/28 |
| 3ptb | ok | P12/C1/BC0/V14 | P1/C6/BC5/V15 | P1/C1/BC0/V14 | voids exact; overcalls branched_channel; overcalls channel; undercalls pocket; exact 16/27 |
| 4cha | ok | P25/C1/BC2/V28 | P6/C3/BC15/V27 | P5/C0/BC0/V27 | overcalls branched_channel; overcalls channel; undercalls pocket; exact 32/56 |

## Immediate conclusions

### 1. `void` handling is substantially better than open-feature handling

The native path is already much closer to the oracle on `voids` than on
`pocket` / `channel` / `branched_channel`.

This means the most urgent remaining work is not a general rewrite of the whole
weighted geometry or the complement construction.

### 2. The native path systematically splits open features too aggressively

Across the battery, the native implementation repeatedly:

- undercalls `pocket`
- overcalls `channel`
- overcalls `branched_channel`

This is the clearest repeated signature in the matrix.

The working interpretation is:

- mouth grouping is still too fine;
- or CASTp 3.0 applies an additional post-rule beyond the current MKALF-like
  `Fnext` walk;
- or both.

### 3. The repeated failure is not confined to one fold class

The same broad pattern appears in:

- small compact proteins (`1ubq`, `1lyz`, `2lyz`)
- proteases (`1hsg`, `2ptc`, `3ptb`, `4cha`)
- TIM-barrel-like or enzyme-pocket cases (`1tre`, `1ake`, `1tcd`)
- heme or cavity-rich cases (`1mbn`)

So the issue is not obviously one special family or one single odd oracle case.

### 4. `1crn` exposes a practical coverage gap

`1crn` currently fails before comparison with:

- `ValueError: Not enough atoms to build a CASTp weighted triangulation (min 4).`

That should be treated separately from the parity problem:

- it is an input-handling or selection-path issue in the native implementation,
- not a mouth-classification mismatch.

### 5. `1a4j` confirms the same open-feature bias at larger scale

`1a4j` finished in a separate pass and fits the same general pattern:

- `void`: near exact (`38/39`)
- open features: strong overcalling of `channel` and `branched_channel`
- exact `pocket` matches exist (`21`), but the taxonomy of the remaining open
  features is still too fragmented

## Next recommended step

Do not jump from this matrix straight to random heuristics.

The matrix supports a narrower next question:

> What rule in CASTp 3.0 merges or suppresses mouth partitions so that many
> oracle `pocket` features are not promoted to `channel` / `branched_channel`
> the way the current native implementation does?

The best next audit targets are still:

- small red cases with exact `void` recovery but bad open-feature taxonomy,
  especially `1stp`, `1ubq`, `1lyz`, `2lyz`, `2pk4`, `1rop`;
- and selected medium red cases such as `1ake`, `2cba`, `3ks3`.
