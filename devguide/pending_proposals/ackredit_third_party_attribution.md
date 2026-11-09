---
summary: Record reached third-party calculations through optional Ackredit attribution.
issue: uibcdf/topomt#157
status: open
opened: 2026-11-08
closed:
severity: high
verification: inspected
area: [third-party, attribution]
guard:
normative: ACKREDIT_GUIDE.md
blocked_by: []
supersedes: []
---

# Ackredit attribution for actual third-party use

## What

Current TopoMT runtime source has no Ackredit registration/tracking boundary for
fpocket or other providers. A legacy unused citation module still imports
flowcite. Guide synchronization is not runtime adoption; automatic citation of
fpocket use through TopoMT is not established.

## How

Start with the real fpocket branch and the registered Ackredit optional-client
contract. Declare bibliography offline, track reached method/software branches
in the application session and retain detached result bibliography/producer
versions. Distinguish original executable, native reproduction and corrected
TopoMT variant. No implicit import hooks or import-time scientific credit.

## Why

Users need an attributed report of the methods their workflow actually used.
A shell executable cannot be inferred from Python import discovery alone.

## What was refuted

This is missing TopoMT consumer integration, not an observed Ackredit defect.
ACKREDIT_GUIDE publication under #91/#94 does not establish runtime use.
An isolated citation helper or mocked installed flag would not prove integration.

## Scope and exclusions

Bounded fpocket-first delivery and an inventory of other provider routes. Keep
Ackredit optional and preserve science when it is absent/broken. No provider
implementation, dependency-floor/public-extra or installed-matrix claim here.
The consulted Ackredit source is clean at 4beb850c8ba814e6103b4d303128a1a36eb57610.

## Acceptance criteria

Real-provider tests show applicable references after reached successful/empty
calculations, no unrelated credit, reused references across results and enclosing
sessions, absence/provider-failure diagnostics, lazy import, detached ownership
and persisted reading without another calculation credit. Verify bibliographic
records, actual original/software semantics and source/public qualification.
Document the user workflow and link remaining provider-specific tasks. #56/#16
retain their wider ownership.
