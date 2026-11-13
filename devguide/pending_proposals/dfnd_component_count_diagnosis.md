---
summary: Review the historical dumbbell component-count monotonicity diagnosis.
issue: uibcdf/topomt#188
status: active
opened: 2026-11-11
closed:
severity: medium
verification: inspected
area: [dfnd, validation, docs]
guard:
normative:
blocked_by: []
supersedes: []
---

# Component count and physical fragmentation

## What

The historical pathology test/document treats an increase in native feature
counts from 1.4 to 2.0 Å as inherently spurious. Shrinking free sets can fragment;
component counts need not decrease with increasing probe radius. The diagnosis
is needs_review, not a demonstrated current failure.

## How

Preserve the original two-versus-five observation and inspect each domain/support
at 2.0 Å during the #187 joint review. Use independently checked physical sets
and distinguish native graph fragmentation, catalog promotion and physical
connected components. Do not impose count monotonicity as a physical oracle.

## Why

The #186 frozen dumbbell references prove connected enclosed named anchors at
1.4 Å and distinct enclosed named anchors at 2.2 Å. Native source 17a4c9a maps
them to one public Void and then two, with recoverable hierarchy. That supports
one genuine fragmentation event, without counting every region at either probe.

## What was refuted

Free-set inclusion does not imply monotone component counts. The reference at
2.2 Å does not diagnose all five native domains at 2.0 Å, nor prove every extra
feature valid. Neither blanket failure nor blanket validation is justified.

## Scope and exclusions

The historical monotonicity diagnosis and its supporting tests/docs. No native
operator retuning, exact global region-count proof, original comparator or
installed qualification. The original numerical observations remain history.

## Acceptance criteria

Provide a reference-scoped disposition of the five domains and revise the test/
documentation claim accordingly. Any actual defect needs an independently owned
regression/fix; legitimate fragmentation must not be suppressed. Reconcile the
finding card/hub/lifecycle/current case and report, preserving historical evidence.

## Joint-review disposition — 2026-11-12

The [six-case review](../../docs/content/benchlab/synthetic/six_case_review.md)
preserves the independently referenced 1.4/2.2/6 Å cases and explicitly retains
this separate 2.0 Å question. The misleading guard name is corrected to
`test_retained_dumbbell_domain_counts_increase_with_probe`; its numerical
assertion remains unchanged. The module introduction now distinguishes retained
diagnoses from independently established physical failures. No scientific
operator or domain-count rule is changed.

The original five-support physical disposition remains pending here. Before
comparing it with quantity-aware public receiving, inspect the legacy test's
direct-array/scalar internal-unit convention, numerical epsilon and exact source
maps; identical display IDs or generator names do not establish matched context.
The joint review does not make all domains physical or spurious and does not
close this issue. Finding status remains `needs_review`.
