# Reporting protocol

This repository implements the common issue-backed lifecycle defined by
`uibcdf/molsyssuite` in its `devguide/reporting_protocol.md`.

## Identity and ownership

Component-local work uses `uibcdf/topomt#<number>`. Suite-wide rules and coordinated
changes use `uibcdf/molsyssuite`. Open the owning issue before creating a queued record.
Every queued document has an issue, although an incoming issue may await triage without
a document.

## Local paths

- `pending_bugs/`: open defects;
- `pending_proposals/`: open proposals;
- `archive/`: all resolved, withdrawn and superseded records.

Every report starts from `templates/report.md`. The issue holds public state; the
document holds analysis, measurements, alternatives and refuted paths.
Plans and broad option catalogs live outside these queues until split into
independently closable themes.

## Closing

Set a closed status and date, name a durable test in `guard` or policy in `normative`,
move the record to `archive/`, regenerate indexes and close the issue with the outcome
and archived path. Archive, never delete. Append corrections to archived records rather
than rewriting their history.
For an issue linked from the [comparative-findings register](comparative_findings.md),
also reconcile its card, hub, lifecycle metadata and current method/case summaries.
Follow the guide's same-scope fix/partial-fix and live-readback workflow; closing
an issue does not by itself resolve a finding. An incomplete update becomes
`needs_review` and cannot support a current scientific claim. Keep historical
observations and fixing/source-release scope explicit.
For resolved reports, the offline validator also checks that a `guard` names a
statically declared pytest test in `tests/` or `devtools/tests/`. Reviewers must
still decide whether the assertion protects the reported outcome.

## Offline checks

```bash
python devtools/devguide_index.py
python devtools/devguide_index.py --check
python -m pytest --receptor=llm tests/test_reporting_protocol.py
```
