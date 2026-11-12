---
summary: Develop explicit physicochemical observations on topographic feature supports, complementary to BindingMT.
issue: uibcdf/topomt#198
status: open
opened: 2026-11-12
closed:
verification: inspected
area: [science, architecture, characterization]
guard:
normative:
blocked_by: []
supersedes: []
---

# Physicochemical characterization of topographic features and regions

## What

The maintainer explicitly consolidates regional physicochemistry as part of
TopoMT's scientific remit. A pocket, channel, wall, protrusion or supported
interface can carry a chemical characterization independently of a chosen binding
partner. Geometry, topographic classification and physicochemical observations
are separate, composable axes.

This refines the [native binding-interface catalogue proposal](../binding_interface_native_catalogue_plan.md)
without withdrawing the contribution to BindingMT #112. BindingMT leads its
binding-domain catalogue; TopoMT owns observations conditioned on its topographic
supports. Shared agreements remain under MolSysSuite #195 and the earlier local
handoff remains #197. This issue owns the regional physicochemistry work.

## How

### Existing evidence and audit

Inspected source at TopoMT `7ecbb63babee21c232866ca4e2ee622d8e6d8dc7`:

- [Pocket physicochemistry helpers](../../topomt/tools/features/pockets/physicochemistry.py):
  supplied-mask apolar fractions, an element-rule SASA fraction and coarse residue
  hydrophobicity/polarity/charge summaries.
- [Existing helper tests](../../tests/test_tools_features_pockets_physicochemistry.py):
  narrow mask/subset and result-shape controls, not general chemical qualification.
- Addon `_components.py` / `_chemistry.py`: historical chemical/affinity display
  paths. Their glyph names do not establish native pharmacophore or binding models.
- [Earlier deferred analysis](../DFND/chemistry_overlay_analysis.md) and the
  [accepted conceptual contract](../topography_conceptual_contract.md#10-acceptance-scenarios-and-ecosystem-boundaries).

Audit element-only classifications, residue scales/charge approximations,
effective state/model handling, unknown defaults and denominator policy before
promoting these helpers to a general scientific layer. A coarse residue descriptor
can be legitimate when named; it does not establish atom-level recognition.
These are source observations, not fresh molecular execution or benchmark claims.

### Ownership

MolSysMT supplies chemical states, annotations/classification, molecular selections,
maps, radii and general numerical tools. Report a demonstrated reusable gap to its
owner rather than copying a chemical engine into TopoMT. TopoMT maps those facts
onto identified supports and owns feature-specific spatial reductions and
interpretation. BindingMT can consume these results to characterize an association
and add partner-specific contact, burial or interaction analyses. PharmacophoreMT
retains its native hypothesis/recognition semantics.

### Staged implementation

1. Inventory current code/resources and historical claims. Choose a first supported
   chemistry/state/model and support profile, definitions, public owner calls and
   exact missing-tool follow-ups. Do not require every future molecular profile.
2. Deliver mapped per-atom/group observations and declared aggregate descriptors
   through a public data route independent of the viewer. No `PolarPocket` class
   or primary topographic reclassification is required.
3. Add supported region-facing area contributions and spatial chemical patches.
   Distinguish lining atoms, accessible atoms, oriented wall patches and whole-atom
   SASA; unavailable spatial support is not an invented regional area.
4. Qualify public inspection, detached ownership, persistence, ordered source/local
   maps, historical/current-use checks, attribution and addon consumption.
5. Extend from the first pocket profile to another eligible feature and a spatial
   interface profile as their actual support contracts are qualified. Record
   deferred scope and owner issues rather than claiming universal feature coverage.

Candidate observations include polarity/apolarity, hydrophobicity under a named
scale, charge under a named model, eligible donor/acceptor/aromatic annotation,
surface contributions and the distribution/connectedness of chemical patches.
Keep atomic, unique-residue and area-weighted quantities distinct. Equal global
fractions do not imply equal spatial organization.

Changing annotation on fixed geometry does not change a feature's topological
family. A change of chemistry that alters atoms, radii or another geometric input
requires corresponding geometry/application reassessment. State, structure,
radius/probe/environment policy and classification weights remain explicit.

## Why

A molecular-topography toolkit should describe the chemical character actually
presented by its spatial regions, not leave every chemical question to a binding
consumer. A residue contributing one atom to a pocket does not expose all its
chemical groups toward the pocket. A support-conditioned data layer enables both
standalone TopoMT analyses and faithful reuse by BindingMT or other components.

## What was refuted

- Restricting TopoMT to bare geometry or making its regional chemistry require
  BindingMT/PISA.
- Treating every chemical descriptor as exclusively owned by a binding workflow.
- Reimplementing generic molecular chemistry, or generating native pharmacophores
  and affinity claims from renderer colors/thresholds.
- Equating a residue label, contact membership, regional wall area and whole-atom
  accessible area.
- Treating missing chemistry or undefined normalization as neutral/nonpolar zero.

## Scope and exclusions

The current delivery consolidates the proposal and staged plan; runtime work is
pending. Preserve the published BindingMT proposal, current DFND synthetic sequence
and all frozen inputs/results. No new protein phase, provider run, engine/model,
environment change or package/release is commissioned by this issue filing.

Provider-specific fpocket parity remains #19/#21/#24/#26. Topography context/support,
participants/interfaces and evaluations remain #60/#61/#62, closing only the rows
required by an admitted profile. Those whole programmes are not blanket blockers
for the source audit or a useful first molecular annotation slice.

## Acceptance criteria

- Record the selected profile, scientific definitions and qualified owner inputs.
- Produce actual public mapped observations and useful summaries independently of
  rendering; preserve context, coverage, methods, quantities and references.
- Validate independently authored maps/annotations, mixed chemical parts within a
  residue, equal global fractions with different distributions, weighted support
  populations, unknown/partial/empty data and zero-denominator distinctions.
- Keep valid DUM/synthetic geometry when chemical annotation is unavailable. Authored
  labels test mapping/reduction only; they are not real chemical recognition evidence.
- Use separately admitted small molecular controls for actual chemical receiving.
  Test state/model/source changes, relevant geometry dependencies and equivalent units.
- Exercise positive/empty/unknown public save/read, all contributors, aligned maps
  and original attribution without new scientific execution on reading.
- Extend beyond the first profile with explicit receiving. Before closure, reconcile
  scope and durable addressable guards, link any deferred family to its owner and
  record the disposition in the issue and local lifecycle.

## Proposal delivery

Issue #198 is filed with the scientific scope and staged acceptance above. The
maintained catalogue now has revision 2 clarifying this complementary ownership;
its published revision 1 and BindingMT response remain historical evidence.
Navigation, the earlier handoff and the June chemistry note link this owner.

Documentation checks: lifecycle indexes current, seven changed documents / 167
local path links valid, balanced code fences, no trailing whitespace and two
administrative reporting tests passed. The test selection used `--noconftest`,
one allowed logical CPU and bounded memory/thread settings; no molecular warmup
or scientific calculation ran. Runtime acceptance and scientific guards remain
future work and this issue stays open.
