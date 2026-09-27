---
summary: Adopt the MolSysSuite issue-backed reporting lifecycle in TopoMT.
issue: uibcdf/topomt#54
status: resolved
opened: 2026-09-27
closed: 2026-09-27
verification: inspected
area: [governance, reporting]
guard: tests/test_reporting_protocol.py::test_devguide_records_and_generated_indexes_are_valid
normative: devguide/reporting_protocol.md
blocked_by: []
supersedes: []
---

# Adopt issue-backed reporting lifecycle

## What

TopoMT previously kept bug and proposal documents without owning issue
metadata, a permanent report archive, generated indexes, or an offline
validator. Its proposal guidance permitted deleting resolved records.

## How

The local `devguide/reporting_protocol.md` adopts the suite's lifecycle.
`devguide/templates/report.md` supplies common front matter. The local
`devtools/devguide_reports.py` and `devtools/devguide_index.py` validate
identity, metadata, state, addressable pytest guards, and generated indexes
without network access. Contributor guidance links the commands.

The annotation-policy proposal now belongs to `uibcdf/topomt#57`. The
historical add-on export defect belongs to `uibcdf/topomt#55` and is archived
with a focused regression guard. The broad GPU option catalog moved outside
the issue-backed queue because it is not an independently closable theme.
The separate Python adoption and ecosystem reviews use their existing or new
member issues.

## Why

An issue provides durable public identity while the local report retains
analysis and evidence. The validator prevents accidental untracked or
unarchived records from silently entering the queues.

## What was refuted

The old proposal README treated deletion after integration as a valid closure
path. The common suite protocol requires an archive instead. The GPU option
catalog is a planning reference rather than one closable proposal.

## Scope and exclusions

This change establishes local reporting governance. It does not modify
scientific algorithms or require TopoMT's product CI matrix to pass.

## Resolution

The focused reporting test and index check pass against all current records.
The validator rejects malformed identities and unresolved guards; the named
test is the stable local gate for future report lifecycle changes.
