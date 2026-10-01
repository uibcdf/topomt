# Pending TopoMT Proposals

This directory holds open, issue-backed proposals that may change TopoMT.
Read [the reporting protocol](../reporting_protocol.md) and open the owning
GitHub issue before creating a record from
[`templates/report.md`](../templates/report.md).

## What Belongs Here

Use this directory for proposals concerning TopoMT or `molsysviewer_topomt` that
are not yet accepted contracts or executable backlog items, including:

- new scientific capabilities or algorithms;
- substantial API or object-model changes;
- cross-cutting refactors whose direction is not decided;
- performance strategies that require profiling or dependency decisions;
- exploratory integration designs.

Do not use this directory for:

- confirmed defects: add them to the active code-review backlog or issue tracker;
- accepted architecture: document it in the relevant authoritative `devguide/`
  contract;
- implementation checkpoints: place them with the relevant subsystem;
- broad option catalogs and plans: keep them outside the issue-backed queues
  until split into independently closable themes;
- improvements that belong in a sibling MolSysSuite repository: open the
  owning issue in that repository and follow its reporting protocol.

## Proposal Lifecycle

Every queued proposal has the common front matter, including its owning
`uibcdf/topomt#<number>` issue and an open status. The generated list below
is maintained with `python devtools/devguide_index.py`.

A pending proposal should state the problem, scientific or user value,
alternatives, risks, dependencies, validation plan, and decision questions. It
must not present unmeasured performance claims or speculative implementation
choices as established facts.

After evaluation, record the decision and its guard or normative rule, move
the report to `devguide/archive/`, regenerate indexes, and close the issue.
Archive every resolved, withdrawn, or superseded report; never delete one.

## Open reports

<!-- generated: devguide_index -->

### Active (1)

- [`review_python_ecosystem_policy_adoption.md`](review_python_ecosystem_policy_adoption.md) — [#56](https://github.com/uibcdf/topomt/issues/56) — Review TopoMT Python ecosystem policy adoption. *(active, measured)*

### Partial (1)

- [`track_python_matrix_evidence.md`](track_python_matrix_evidence.md) — [#16](https://github.com/uibcdf/topomt/issues/16) — Track TopoMT Python matrix evidence before a support or release claim. *(partial, measured)*

### Open (2)

- [`annotation_future_import_policy.md`](annotation_future_import_policy.md) — [#57](https://github.com/uibcdf/topomt/issues/57) — Decide TopoMT's future-annotation import rule for Python 3.11–3.13. *(open, inspected)*
- [`dfnd_reference_validation_panel.md`](dfnd_reference_validation_panel.md) — [#76](https://github.com/uibcdf/topomt/issues/76) — Reconcile DFND synthetic reference assumptions and freeze independent validation evidence. *(open, inspected)*

<!-- /generated -->
