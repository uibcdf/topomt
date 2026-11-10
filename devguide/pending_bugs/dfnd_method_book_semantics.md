---
summary: Correct shared-face admission and complete the DFND method book's operator definitions.
issue: uibcdf/topomt#173
status: open
opened: 2026-11-09
closed:
severity: medium
verification: reproduced
area: [docs, dfnd]
guard:
normative:
blocked_by: []
supersedes: []
---

# DFND method-book semantics

## What

The public network chapter equates shared-face capacity with a shared
permeability decision. At source `9c8fbc4`, capacity is unique per face but
intrusion/admission can differ between its incident tetrahedra under
`block_suspect`. The wet edge requires both admissions; dry face adjacency
requires both nonpermeable incidences. The single-decision account is incomplete.

## How

The [cross-source audit](../DFND/approach_and_presentation_audit_2026_11_09.md)
retains the source map, exact frozen input hashes and a replay using the existing
public receiving helper. At `closed_shell`, probe 0.2 Å, internal face 6 has
identical `R_gate=0.1198879391121351` nm on owners 1/7 but differing post-policy
states. Both `transit_edge` records are false. There are 75 such unequal state
pairs on that input and 27 on `shell_with_opening` at 1.4 Å.

## Why

A reader cannot reconstruct non-default graph/bank policies from the current
explanation. The audit also identifies omitted fixed descriptor choices and
center definitions, a notation collision and an undiscoverable existing branch
helper. These belong to a bounded source-faithfulness correction of the book.

## What was refuted

The two gate capacities do not differ. The kernel already checks both incident
admissions. This replay establishes neither a physical crossing error nor a new
comparative limitation; default `flag_only` examples and prior #170/#172 checks
can pass while this explanation remains wrong.

## Scope and exclusions

Correct the public chapters/pseudocode and reconcile affected developer
guidance. State existing fixed/default values and distinguish them from public
parameters. Preserve scientific policies, historical artifacts and current
findings. #75/#76/#151 and #60/#61 retain their scientific/runtime scopes.

## Acceptance criteria

Explain the owner-specific bare-apex plane test, two-sided wet/dry predicates,
hierarchy floor/control availability, sampling/interface defaults, carrier
centroids and existing secondary skeletons. Resolve the overloaded `g` notation.
Add a concise status/reading map and link the existing many-cell public example.
Exercise the non-default policy on frozen inputs alongside reader examples;
validate rendered links and report lifecycle. This issue remains open: the audit
records the findings and does not implement those corrections.

## Audit-quality refinement — 2026-11-09

The reviewed audit now states its mathematical checks and assumption boundaries,
distinguishes runtime replays from source inspection, and gives an observable
completion criterion for each F1–F7 recommendation. Its reproduction checks all
three frozen-case summary rows and locates the witness by source atoms before
checking this mesh's IDs, reciprocal owners, flags and capacities. The priority
rubric is documentary work order, not incident severity. This strengthens the
evidence/acceptance record; #173 remains open for the actual book corrections.

## Final scientific-reader review — 2026-11-09

F6 now includes a prospective scientific-user walkthrough, page-specific reading
friction, inspected existing visuals, a proposed opening and a six-question
editorial completion check. The recommended introductory route presents the
scientific question and stored result before optional execution/provenance
detail, defines internal terms at first use and retains critical limits beside
their interpretation. This completes the requested audit reviews. Its judgments
are not a reader study, and the public corrections remain open under #173.
