# CASTp3/CASTpFold Reproducibility Boundary

Date: 2026-05-19

This checkpoint closes the current CASTp3 parity investigation as a bounded
reproducibility audit. The objective was to decide whether strict CASTp3/
CASTpFold parity is still a realistic engineering target, or whether TopoMT
should keep CASTp1 as the canonical reproduced algorithm and move future pocket
detection work into an explicitly native TopoMT algorithm.

## Executive Decision

Strict CASTp3/CASTpFold parity should not remain the primary near-term target.

The recommended path is:

1. Keep the native CASTp1 implementation as the faithful, reproducible CASTp
   reference.
2. Keep the current CASTp3 path as an experimental CASTp3-like backend informed
   by CASTp1, ProtOr radii, CASTpFold server outputs, and oracle benchmarks.
3. Use CASTp3/CASTpFold oracles as external comparison data, not as a complete
   specification.
4. Start a native TopoMT pocket-detection algorithm whose rules are explicit,
   documented, testable, and under our control.

## Why Strict CASTp3 Parity Is Not Currently Reproducible

The CASTpFold ZIP files contain useful output files, but not enough internal
state to reconstruct the server algorithm:

- PDB input used by the server.
- `.poc` and `.pocInfo` feature atom sets and feature metrics.
- `.mouth` and `.mouthInfo` mouth atom sets and mouth metrics.
- `.contrib.csv` per-atom area/volume contributions.
- `.bulb.json` feature bulb centers/radii.

They do not include:

- weighted Delaunay/regular triangulation,
- alpha spectrum,
- simplex ranks,
- tetrahedron-to-feature assignments,
- face/edge/vertex rank tables,
- precise preprocessing policy beyond what can be inferred,
- server postprocessing rules for tiny mouths, tiny voids, and atom reporting.

Without those internal files or CASTp3 source code, several server decisions are
observable but not derivable from the public CASTp1 algorithm.

## Critical Evidence: `3ptb` and `1bmq`

Two minimal cases show a direct conflict between the CASTp1 mouth construction
and CASTpFold output.

| pdb | server feature | server type | server mouth | server mouth metrics | native classification |
|---|---:|---|---|---|---|
| `3ptb` | 27 | pocket | atoms 42, 50, 393; `Ntri=1` | `Area_sa=0.0`, `Area_ms=5.3`, bulb radius `0.3399` | one-tetrahedron void |
| `1bmq` | 34 | pocket | atoms 1034, 1048, 1376; `Ntri=1` | `Area_sa=0.0`, `Area_ms=4.82`, bulb radius `0.2312` | one-tetrahedron void |

In native TopoMT ranks, the server-reported mouth face is inside the alpha
complex at both the base/probe rank and the beta/depth rank:

| pdb | native base rank | native tetra rho | server mouth face rho/mu1/mu2 | native status |
|---|---:|---:|---:|---|
| `3ptb` | 21311 | 21343 | 21305 / 21343 / 22731 | face is in `Cpx_base` and `Cpx_beta` |
| `1bmq` | 25730 | 25732 | 25729 / 25732 / 26218 | face is in `Cpx_base` and `Cpx_beta` |

CASTp1 source code requires a mouth seed to be outside the alpha complex at
`rank1`. Therefore, given our current ranks, a CASTp1-faithful algorithm cannot
emit those faces as mouths.

This is the key reproducibility boundary: CASTpFold reports micro-mouths that
are not reachable through the CASTp1 mouth rule with the native rank tables.

## Hypotheses Tested and Rejected as Defaults

### Pocket-over-void priority

Rejected.

A post-hoc priority rule cannot be justified by CASTp1. In CASTp1, a pocket is
not produced by preferring a label over a void; it is produced by mouth-bearing
boundary components derived from the alpha complex and discrete-flow pocket
construction.

### Global alpha-boundary epsilon length

Rejected as default.

A small global epsilon can flip some near-threshold void cases, but it degrades
previously green controls and moves pockets, mouths, channels, and branched
channels together. It is useful diagnostically, not as a faithful CASTp3 rule.

### Face-rank epsilon

Rejected as default.

Opening faces within a few ranks of the base alpha rank explains part of `3ptb`
and `1bmq`, but it also degrades the 38-system benchmark and breaks green
controls. It is too broad.

### Treat singular faces as open for mouths

Rejected as default.

A temporary monkeypatch was tested where singular faces satisfying
`rho <= base < mu1` were treated as open for mouth/boundary reporting. This
matches the observation that the server-reported micro-mouth faces in `3ptb`
and `1bmq` are singular in the native ranks, but the rule is globally wrong.

Focused result:

| pdb | effect |
|---|---|
| `3ptb` | void count moved toward server, but pockets/channels became worse |
| `1bmq` | void count moved toward server, but channels and branched channels exploded |
| `1rop` | previously green pocket parity broke completely |
| `1hew` | previously green strict parity broke |
| `3phv` | previously green strict parity broke |
| `1ifb` | previously green strict parity broke |

Conclusion: singular-face opening is a useful diagnostic clue, but not a valid
CASTp3 default rule.

## Remaining CASTp3-Like Value

The current CASTp3 path is still valuable:

- It provides ProtOr radii and protein-only preprocessing compatible with the
  public CASTpFold parameter description.
- It gives a reproducible native implementation for many CASTp-like structures.
- It provides a benchmark harness and oracle comparison layer.
- It exposes concrete failure classes that can guide a TopoMT-native algorithm.

But it should be presented as CASTp3-like, not as a guaranteed reproduction of
the opaque server.

## Recommended TopoMT Direction

The next phase should be a native TopoMT pocket algorithm, explicitly designed
around these principles:

1. Use weighted Delaunay/alpha-shape geometry where it is robust and useful.
2. Keep probe accessibility, voidness, mouthness, and depth as separately
   inspectable concepts instead of compressing them into opaque server labels.
3. Define strict, documented rules for tiny mouths, tiny voids, and
   near-threshold features.
4. Treat atom reporting as a separate layer from tetrahedral topology.
5. Keep CASTp1 and CASTp3/CASTpFold as benchmarks, not as hidden specifications.
6. Report uncertainty/threshold status for features near the alpha boundary.

## Practical Next Steps

1. Freeze the current CASTp3 parity evidence and avoid adding more local
   compatibility switches unless they are clearly diagnostic and disabled by
   default.
2. Keep the 38-system oracle harness as regression data.
3. Define the TopoMT-native feature model: void, pocket, channel, branched
   channel, mouth, boundary atoms, wall atoms, and near-threshold flags.
4. Select a small design benchmark set:
   `1crn`, `2pk4`, `3ptb`, `1bmq`, `5dfr`, `1a6w`, `1stn`, `2ifb`, `1rop`,
   `1hew`.
5. Build the new algorithm in a separate module/path so CASTp1 and CASTp3-like
   behavior remain reproducible.
