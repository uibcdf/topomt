# DFND Strategic Assessment

Point-in-time external assessment originally recorded on 2026-05-20, after three rounds of conceptual review and the residence/transit refactor. Updated on 2026-05-21 after the first implementation-hardening sprint.

This document is an honest, calibrated judgment of the DFND project on three
strategic questions. It is not a benchmark and not a promise; it is a snapshot of
how defensible the project looks given the current design corpus and code state.
Scores are deliberately not inflated. Each score includes the evidence behind it
and the concrete event that would raise it.

## Scores at a Glance

| Question | Score | One-line reason |
|---|:---:|---|
| Worth continuing, not abandoning | **8 / 10** | Mature, internally coherent concept; risk is execution/validation, not the idea. |
| Good base to fight for popularization | **6.5 / 10** | Saturated, validated field; now has an executable substrate and early real-system checks, but no benchmark-quality result yet. |
| Opens doors to utilities absent in popular tools | **8 / 10** | Wet/dry symmetry, residence≠transit, MD identity — real and underserved, but still potential. |

## 1. Is It Worth Continuing? — 8 / 10

**Why this high.**

- The conceptual core is sound: decoupling local volume (`R_residence`) from
  connectivity (`R_gate`), and now from movement (the residence/transit
  separation), is a legitimate and well-articulated idea, not a reskin of an
  existing method.
- After the residence/transit refactor the corpus is internally coherent. The
  remaining open questions are scoped and named, not structural.
- There is already a code base under `topomt/dfnd/` and a clear v1 boundary in
  [`data_model_v1.md`](data_model_v1.md).
- The project metabolizes hard criticism well and converges quickly to correct
  design. That is a strong predictor of a project that will not stall on its own
  conceptual debt.

**Why not 9-10.**

- There is not yet a benchmark-quality result demonstrating that the conceptual elegance translates into better biological or methodological performance.
- The implementation is not production-ready: it passes engineering-contract tests and small real-system sweeps, but cavity-quality validation and reporting policy are still pending.

**What raises it:** executing the next validation layers in [`validation_plan.md`](validation_plan.md): stable reporting filters, qualitative cavity inspection, and a small comparison battery against external methods.

## 2. Good Base to Fight for Popularization? — 6 / 10

**Why cautious.**

- The field is crowded and well validated: CASTp-style alpha-shape tools,
  fpocket-style clustering, ML rankers such as P2Rank, and tunnel tools such as
  MOLE/Caver. Each has historical validation and an established user base.
- Popularization still requires what does not exist yet: a quantitative benchmark, cases where DFND clearly wins, a production-ready implementation, and ease of use. The first engineering validation layers are now active, but community-facing validation is not done.

**What helps.**

- Native integration in the MolSysSuite / MolSysMT ecosystem gives an adoption
  channel inside that ecosystem without fighting from zero (see
  [`Pertinence_Analysis.md`](Pertinence_Analysis.md)).
- The honesty discipline already in [`Justification.md`](Justification.md) and
  [`validation_plan.md`](validation_plan.md) (explicit "claims to avoid")
  protects credibility, which matters for adoption by a skeptical community.

**What raises it (to 7-8):** a small benchmark with at least one result that the
popular tools do not produce equally well — ideally on DFND's differentiating
ground (see Section 3), not on static pocket volume where the incumbents are
strongest.

## 3. Opens Doors to Utilities Absent in Popular Tools? — 8 / 10

**Why this is the strongest dimension.** DFND's genuinely distinctive surface
area is exactly where mainstream static pocket tools are weak:

- **Wet/dry symmetry:** dry topology (cores, protrusions, ridges, separators)
  computed with the same engine — almost no popular tool does this (see
  [`dry_network_and_convexity.md`](dry_network_and_convexity.md)).
- **Residence ≠ transit ≠ contact:** detection of non-resident passages
  (narrow pores / selectivity-filter-like constrictions), gating, and cryptic
  throats that are invisible to volume-only static detectors (see
  [`residence_transit_contract.md`](residence_transit_contract.md)).
- **Per-frame atom/tetrahedron/face identity:** a natural basis for trajectory
  tracking, cryptic-site detection, and breathing analysis — an underserved
  niche for CASTp/fpocket (see [`dynamic_topology.md`](dynamic_topology.md)).
- **Future bridge from dry topology to mechanics** (B-factors, RMSF, GNM/ANM,
  hinges) via ElastNetMT-style coupling.

**Why not 9-10.** These doors are still *potential*: documented and plausible,
not demonstrated. They depend on machinery (dynamics, dry motifs) that is
candidate/experimental in v1.

**What raises it (to 9):** one MD case where DFND captures a cryptic or
transient feature (e.g., a non-resident gating throat) that static incumbents
miss.

## 4. Combined Reading and Strategic Recommendation

The project is clearly worth continuing (8), and its greatest asset is
**functional originality** (8), not immediate competitiveness in the saturated
static-detection arena (6).

The strategy that maximizes return is to **play to the Section 3 strengths**
— dynamics, wet/dry symmetry, non-resident transit — rather than competing head
on with CASTp on static pocket volume, which is precisely where the incumbent is
most validated and where DFND is least differentiated.

Concretely:

- Treat static pocket detection as a correctness/sanity baseline, not as the
  headline claim.
- Aim the first publication-facing result at a differentiating capability
  (MD tracking, cryptic site, non-resident passage, or wet/dry complementarity).
- Keep the credibility discipline already adopted: no superiority claims, no
  physical-volume claims, no biological channel/pore claims from topology alone,
  until quantitative validation exists.

## 5. Provenance and Caveats

- This assessment reflects the corpus and code state on 2026-05-20. Scores are
  expected to move as [`validation_plan.md`](validation_plan.md) is executed.
- It is a subjective strategic judgment, not a measured benchmark. The
  validation plan, not this document, is the authority on actual performance.
- The scores are coupled to specific raising conditions stated above; treat
  those conditions as the roadmap, not the numbers.
