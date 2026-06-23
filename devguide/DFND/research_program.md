# DFND Research Program — characterization first

The north star is **not** "match other detectors". It is:

> **Give the user a rich, complete, useful characterization of a surface's
> topography — including things no other tool offers.**

Comparison with CASTp / fpocket / CAVER is a credibility lens (§3), never the
driver. A DFND result has value to the user whether or not another tool produces
something comparable. The operational counterpart — what "trustworthy" means and
how it is checked — is [`validation_plan.md`](validation_plan.md); maturity
labels live in `topomt/dfnd/output_status.py`.

## 1. What DFND offers the user (the spine)

This is the product: a complete topographic characterization, not a single
pocket-volume number.

- **A complete cavity inventory.** Pockets, voids, channels, percolating
  regions, and their mouths — every concavity of the surface, classified, not
  just the top-ranked druggable pocket.
- **Flow / transit characterization (the distinctive layer).** The model
  distinguishes where a probe can *reside* (`R_residence`) from where it can
  *pass* (`R_gate` at faces). That yields gates, constrictions, transit
  connectors, and a navigability picture that pocket-volume tools simply do not
  produce.
- **The solid (dry) side.** The dry network, interfaces/coasts, and *sealed
  voids* (no transit path = truly enclosed) — relevant to trapped waters/gases,
  packing defects, and protein–protein interfaces.
- **Rich per-feature shape.** Topological and solvent volume, mouth area, gate
  constriction, buriedness (`face_depth`), internal depth structure
  (`topological_depth` / `depth_regions`), and internal throats/chambers — a
  *shape*, not a scalar.
- **Dynamic characterization (the frontier value).** TopoMT ingests
  trajectories, and the lineage layer tracks a cavity with stable identity across
  frames: persistence, volume fluctuation, gate breathing (`R_gate(t)`),
  open/close behaviour, and cryptic pockets that appear only in motion. Static
  tools cannot do this by construction.
- **A topological fingerprint.** The whole cavity *network* — pockets + channels
  + voids + their connectivity via dry interfaces — as a comparable descriptor
  for structural comparison, clustering, or ML features. A volume cannot.

Each of these is something a user can inspect, act on, and learn from. None of
them needs an external baseline to be worth offering.

## 2. Where it goes (the ambitious directions)

Framed as characterization the user *gains*, not benchmarks to *win*:

- **Cavity dynamics.** Persistence, gate breathing, open/close kinetics over MD —
  new observables the transit/gate model yields for free.
- **Cryptic pockets.** Transient pockets that open/close, detected over MD +
  lineage — territory where static tools fail.
- **Ligand ingress/egress + tunnel tracking.** Channel + gate + (future)
  navigability = permeation pathways, tracked with stable identity along a
  trajectory.
- **Cavity-topology fingerprint.** From the lineage/identity/registry machinery
  to a comparable network descriptor.

Honest dependencies: the dynamic frontier needs lineage solid at scale and MD
infrastructure; any "a probe of radius *r* passes" statement needs
`validated_probe_path` / `widest_gate_path` (deferred). These gate *specific
claims*, not the value of the characterization itself.

## 3. Credibility and concordance (one lens, secondary)

When we *do* compare — to build user trust and to situate DFND — use the right
comparator per feature, and treat it as **concordance**, not a contest:

- **Pocket geometry (volume/area):** CASTp / CASTpFold (analytic).
- **Pocket detection:** ligand databases (sc-PDB, PDBbind, MOAD, COACH420/HOLO4K),
  fpocket, P2Rank — standard DCA / top-N metrics, for directly comparable
  numbers when a paper needs them.
- **Channels / tunnels:** CAVER, MOLE, **ChannelsDB** — *not* fpocket/CASTp.
- **The flow/transit/gate/dry layer:** *no external baseline* — validate on
  synthetic + known cases + expert review.

Peers use *different definitions*; report agreement **and explained divergence**.
Disagreement is where DFND's distinct ontology shows its value — mine the
disagreements, do not chase a match.

---

*Operational counterpart: [`validation_plan.md`](validation_plan.md). Output
maturity: `output_status.py`. Honest failure log:
[`known_limitations.md`](known_limitations.md).*
